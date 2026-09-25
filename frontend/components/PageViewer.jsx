'use client';

import { useState, useRef, useEffect } from 'react';
import { 
  ZoomIn, 
  ZoomOut, 
  Maximize2, 
  RotateCcw, 
  ChevronLeft, 
  ChevronRight, 
  FileText,
  Eye
} from 'lucide-react';

export default function PageViewer({
  pages = [],
  activePageNumber = 1,
  onPageChange,
  fields = [],
  activeField = null,
  hoveredField = null,
  onFieldClick
}) {
  const containerRef = useRef(null);
  const imgRef = useRef(null);
  const [zoomLevel, setZoomLevel] = useState(1.0);
  const [imgNaturalSize, setImgNaturalSize] = useState({ width: 0, height: 0 });

  const currentPage = pages.find((p) => p.page_number === activePageNumber) || pages[0];

  // Zoom handlers
  const handleZoomIn = () => setZoomLevel((z) => Math.min(2.5, +(z + 0.2).toFixed(1)));
  const handleZoomOut = () => setZoomLevel((z) => Math.max(0.6, +(z - 0.2).toFixed(1)));
  const handleResetZoom = () => setZoomLevel(1.0);

  const handleImageLoad = (e) => {
    setImgNaturalSize({
      width: e.target.naturalWidth,
      height: e.target.naturalHeight,
    });
  };

  // Filter fields on the active page that have bounding boxes
  const pageFields = fields.filter(
    (f) => f.page_number === activePageNumber && f.bbox && f.bbox.ymin !== undefined
  );

  return (
    <div className="flex flex-col h-full bg-[#0a0e17] rounded-xl border border-slate-800 overflow-hidden select-none">
      
      {/* Viewer Toolbar */}
      <div className="px-4 py-2.5 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between gap-2 shrink-0">
        
        {/* Page Switcher */}
        <div className="flex items-center gap-1.5 text-xs text-slate-300">
          <button
            onClick={() => onPageChange(Math.max(1, activePageNumber - 1))}
            disabled={activePageNumber <= 1}
            className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-slate-200 disabled:opacity-30 transition"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>

          <span className="font-mono text-slate-200">
            Page {activePageNumber} <span className="text-slate-500">/ {pages.length || 1}</span>
          </span>

          <button
            onClick={() => onPageChange(Math.min(pages.length || 1, activePageNumber + 1))}
            disabled={activePageNumber >= (pages.length || 1)}
            className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-slate-200 disabled:opacity-30 transition"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>

        {/* Zoom Controls */}
        <div className="flex items-center gap-1">
          <button
            onClick={handleZoomOut}
            title="Zoom Out"
            className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>

          <span className="font-mono text-xs text-slate-400 w-12 text-center">
            {Math.round(zoomLevel * 100)}%
          </span>

          <button
            onClick={handleZoomIn}
            title="Zoom In"
            className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>

          <div className="h-4 w-px bg-slate-800 mx-1" />

          <button
            onClick={handleResetZoom}
            title="Reset Zoom"
            className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition text-[11px] font-mono"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>

      </div>

      {/* Main Viewport Container */}
      <div 
        ref={containerRef}
        className="flex-1 overflow-auto relative p-6 flex items-center justify-center bg-[#070a10]"
      >
        {currentPage ? (
          <div 
            className="relative shadow-2xl transition-transform duration-150 origin-center bg-white rounded-sm"
            style={{
              transform: `scale(${zoomLevel})`,
            }}
          >
            {/* The Document Page Image */}
            <img
              ref={imgRef}
              src={`/api/pages/${currentPage.image_path}`}
              alt={`Page ${currentPage.page_number}`}
              onLoad={handleImageLoad}
              className="max-w-none block object-contain pointer-events-none"
              style={{
                width: '680px',
                height: 'auto'
              }}
            />

            {/* Bounding Box Highlights Overlay */}
            <div className="absolute inset-0 pointer-events-none">
              {pageFields.map((field) => {
                const b = field.bbox;
                const isHovered = hoveredField && (hoveredField.id === field.id || hoveredField.field_name === field.field_name);
                const isActive = activeField && (activeField.id === field.id || activeField.field_name === field.field_name);
                const isFlagged = field.flagged;

                // Normalized coordinate conversion (0 to 1000 scale -> %)
                const topPct = (b.ymin / 1000) * 100;
                const leftPct = (b.xmin / 1000) * 100;
                const heightPct = Math.max(1.8, ((b.ymax - b.ymin) / 1000) * 100);
                const widthPct = Math.max(3.0, ((b.xmax - b.xmin) / 1000) * 100);

                let borderColor = 'rgba(56, 189, 248, 0.4)';
                let bgColor = 'rgba(56, 189, 248, 0.08)';

                if (isFlagged) {
                  borderColor = 'rgba(245, 158, 11, 0.7)';
                  bgColor = 'rgba(245, 158, 11, 0.12)';
                }

                if (isActive || isHovered) {
                  borderColor = isFlagged ? '#f59e0b' : '#38bdf8';
                  bgColor = isFlagged ? 'rgba(245, 158, 11, 0.28)' : 'rgba(56, 189, 248, 0.25)';
                }

                return (
                  <div
                    key={field.id || field.field_name}
                    onClick={(e) => {
                      e.stopPropagation();
                      if (onFieldClick) onFieldClick(field);
                    }}
                    style={{
                      top: `${topPct}%`,
                      left: `${leftPct}%`,
                      width: `${widthPct}%`,
                      height: `${heightPct}%`,
                      borderColor: borderColor,
                      backgroundColor: bgColor,
                    }}
                    className={`absolute border rounded-[2px] pointer-events-auto cursor-pointer transition-all ${
                      isActive || isHovered ? 'box-highlight-active z-20' : 'z-10 hover:border-sky-400'
                    }`}
                  >
                    {/* Floating tag label if active or hovered */}
                    {(isActive || isHovered) && (
                      <div 
                        className={`absolute -top-6 left-0 text-[10px] font-medium font-mono px-1.5 py-0.5 rounded shadow-lg whitespace-nowrap z-30 ${
                          isFlagged 
                            ? 'bg-amber-900/90 text-amber-200 border border-amber-500/40' 
                            : 'bg-sky-950/90 text-sky-200 border border-sky-500/40'
                        }`}
                      >
                        {field.field_label || field.field_name} ({Math.round(field.confidence * 100)}%)
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

          </div>
        ) : (
          <div className="text-center text-slate-500">
            <FileText className="w-8 h-8 mx-auto mb-2 opacity-40" />
            <p className="text-xs">No page image available</p>
          </div>
        )}
      </div>

      {/* Multi-page Thumbnails rail (if more than 1 page) */}
      {pages.length > 1 && (
        <div className="px-4 py-2 bg-slate-900 border-t border-slate-800 flex items-center gap-2 overflow-x-auto shrink-0">
          {pages.map((p) => (
            <button
              key={p.page_number}
              onClick={() => onPageChange(p.page_number)}
              className={`p-1 rounded border transition relative shrink-0 ${
                p.page_number === activePageNumber
                  ? 'border-sky-400 bg-sky-500/10'
                  : 'border-slate-800 hover:border-slate-700 bg-slate-950'
              }`}
            >
              <img
                src={`/api/pages/${p.image_path}`}
                alt={`Thumb ${p.page_number}`}
                className="w-10 h-14 object-cover rounded-sm"
              />
              <span className="block text-[10px] font-mono text-center text-slate-400 mt-0.5">
                p.{p.page_number}
              </span>
            </button>
          ))}
        </div>
      )}

    </div>
  );
}
