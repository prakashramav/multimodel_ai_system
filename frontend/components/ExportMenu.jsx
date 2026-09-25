'use client';

import { useState } from 'react';
import { Download, ChevronDown, FileJson, FileSpreadsheet } from 'lucide-react';

export default function ExportMenu({ documentId, filename }) {
  const [isOpen, setIsOpen] = useState(false);

  const baseName = filename ? filename.replace(/\.[^/.]+$/, '') : 'document';

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="px-3 py-1.5 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 hover:border-slate-600 text-xs font-medium flex items-center gap-1.5 transition"
      >
        <Download className="w-3.5 h-3.5 text-slate-400" />
        <span>Export</span>
        <ChevronDown className="w-3 h-3 text-slate-500" />
      </button>

      {isOpen && (
        <div
          className="absolute right-0 mt-1.5 w-44 rounded-lg bg-slate-900 border border-slate-700 shadow-xl py-1 text-xs z-50"
          onMouseLeave={() => setIsOpen(false)}
        >
          <div className="px-3 py-1 text-[10px] font-semibold text-slate-400 uppercase tracking-wider border-b border-slate-800">
            Export Format
          </div>

          <a
            href={`/api/documents/${documentId}/export?format=json`}
            download={`${baseName}_extracted.json`}
            onClick={() => setIsOpen(false)}
            className="flex items-center gap-2 px-3 py-2 text-slate-200 hover:bg-slate-800 hover:text-sky-300 transition"
          >
            <FileJson className="w-3.5 h-3.5 text-sky-400" />
            <span>Structured JSON</span>
          </a>

          <a
            href={`/api/documents/${documentId}/export?format=csv`}
            download={`${baseName}_extracted.csv`}
            onClick={() => setIsOpen(false)}
            className="flex items-center gap-2 px-3 py-2 text-slate-200 hover:bg-slate-800 hover:text-emerald-300 transition"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" />
            <span>Full CSV Table</span>
          </a>
        </div>
      )}
    </div>
  );
}
