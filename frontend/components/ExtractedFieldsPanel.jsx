'use client';

import { useState } from 'react';
import { 
  CheckCircle2, 
  AlertCircle, 
  Search, 
  ChevronDown, 
  ChevronRight, 
  SlidersHorizontal,
  CheckCheck
} from 'lucide-react';
import FieldRow from '@/components/FieldRow';

export default function ExtractedFieldsPanel({
  documentId,
  sections = {},
  fields = [],
  activeField = null,
  hoveredField = null,
  onHoverField,
  onLeaveField,
  onSelectField,
  onFieldUpdated
}) {
  const [filterMode, setFilterMode] = useState('ALL'); // 'ALL' or 'FLAGGED'
  const [searchQuery, setSearchQuery] = useState('');
  const [collapsedSections, setCollapsedSections] = useState({});

  const toggleSection = (sectionName) => {
    setCollapsedSections((prev) => ({
      ...prev,
      [sectionName]: !prev[sectionName],
    }));
  };

  const flaggedCount = fields.filter((f) => f.flagged).length;

  return (
    <div className="flex flex-col h-full bg-slate-900/50 rounded-xl border border-slate-800 overflow-hidden">
      
      {/* Panel Header */}
      <div className="p-3.5 bg-slate-900/90 border-b border-slate-800 shrink-0 space-y-2.5">
        
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h2 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">
              Structured Extraction
            </h2>
            <span className="text-[11px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-slate-400">
              {fields.length} fields
            </span>
          </div>

          {/* Filter Mode Toggle */}
          <div className="flex items-center gap-1 bg-slate-950 p-0.5 rounded-lg border border-slate-800 text-[11px]">
            <button
              onClick={() => setFilterMode('ALL')}
              className={`px-2.5 py-1 rounded font-medium transition ${
                filterMode === 'ALL'
                  ? 'bg-slate-800 text-sky-400 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setFilterMode('FLAGGED')}
              className={`px-2.5 py-1 rounded font-medium transition flex items-center gap-1 ${
                filterMode === 'FLAGGED'
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Needs Review
              {flaggedCount > 0 && (
                <span className="px-1 py-0.2 rounded-full text-[9px] bg-amber-500/30 text-amber-200 font-bold">
                  {flaggedCount}
                </span>
              )}
            </button>
          </div>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Filter fields by name or value..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-8 pr-2.5 py-1 bg-slate-950/80 border border-slate-800 rounded-md text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500/50"
          />
        </div>

      </div>

      {/* Sections & Fields List */}
      <div className="flex-1 overflow-y-auto p-3.5 space-y-4">
        {Object.entries(sections).map(([sectionName, sectionFields]) => {
          // Filter section fields
          const displayedFields = sectionFields.filter((f) => {
            if (filterMode === 'FLAGGED' && !f.flagged) return false;
            if (searchQuery.trim()) {
              const q = searchQuery.toLowerCase();
              const lMatch = (f.field_label || f.field_name || '').toLowerCase().includes(q);
              const vMatch = (f.value || '').toLowerCase().includes(q);
              if (!lMatch && !vMatch) return false;
            }
            return true;
          });

          if (displayedFields.length === 0) return null;

          const isCollapsed = !!collapsedSections[sectionName];
          const sectionFlagged = displayedFields.filter((f) => f.flagged).length;

          return (
            <div key={sectionName} className="space-y-1.5">
              {/* Section Header */}
              <button
                onClick={() => toggleSection(sectionName)}
                className="w-full flex items-center justify-between text-left py-1 px-1 text-xs font-medium text-slate-400 hover:text-slate-200 transition group"
              >
                <div className="flex items-center gap-1.5">
                  {isCollapsed ? (
                    <ChevronRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-slate-300" />
                  ) : (
                    <ChevronDown className="w-3.5 h-3.5 text-slate-500 group-hover:text-slate-300" />
                  )}
                  <span className="text-slate-200">{sectionName}</span>
                </div>

                <div className="flex items-center gap-1.5 text-[11px]">
                  {sectionFlagged > 0 && (
                    <span className="px-1.5 py-0.2 rounded text-[10px] bg-amber-500/20 text-amber-300 font-mono">
                      {sectionFlagged} flagged
                    </span>
                  )}
                  <span className="text-slate-500 font-mono">
                    {displayedFields.length}
                  </span>
                </div>
              </button>

              {/* Section Field Items */}
              {!isCollapsed && (
                <div className="space-y-1.5 pl-1">
                  {displayedFields.map((field) => (
                    <FieldRow
                      key={field.id || field.field_name}
                      documentId={documentId}
                      field={field}
                      isHovered={hoveredField && (hoveredField.id === field.id || hoveredField.field_name === field.field_name)}
                      isActive={activeField && (activeField.id === field.id || activeField.field_name === field.field_name)}
                      onHover={onHoverField}
                      onLeave={onLeaveField}
                      onSelect={onSelectField}
                      onFieldUpdated={onFieldUpdated}
                    />
                  ))}
                </div>
              )}
            </div>
          );
        })}

        {fields.length === 0 && (
          <div className="p-8 text-center text-slate-500 text-xs">
            No extracted fields available for this document.
          </div>
        )}
      </div>

    </div>
  );
}
