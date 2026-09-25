'use client';

import { useState } from 'react';
import Link from 'next/link';
import { 
  FileText, 
  CheckCircle2, 
  AlertCircle, 
  ExternalLink, 
  Download, 
  Trash2, 
  Search,
  Filter,
  ArrowRight,
  Loader2
} from 'lucide-react';
import ClassificationBadge from '@/components/ClassificationBadge';

export default function DocumentList({ documents, onDeleteDocument, isLoading }) {
  const [filterType, setFilterType] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const filterTabs = [
    { id: 'ALL', label: 'All Documents' },
    { id: 'NEEDS_REVIEW', label: 'Needs Review' },
    { id: 'invoice', label: 'Invoices' },
    { id: 'resume', label: 'Resumes' },
    { id: 'receipt', label: 'Receipts' },
  ];

  const filtered = documents.filter((doc) => {
    // Type/Status filter
    if (filterType === 'NEEDS_REVIEW') {
      if (doc.status !== 'needs_review' && doc.flagged_count === 0) return false;
    } else if (filterType !== 'ALL') {
      if (doc.type !== filterType) return false;
    }

    // Search query filter
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const nameMatch = (doc.filename || '').toLowerCase().includes(q);
      const typeMatch = (doc.type || '').toLowerCase().includes(q);
      if (!nameMatch && !typeMatch) return false;
    }

    return true;
  });

  const getStatusBadge = (doc) => {
    if (doc.status === 'processing') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-sky-500/10 text-sky-400 border border-sky-500/30">
          <Loader2 className="w-3 h-3 animate-spin text-sky-400" />
          <span>Processing</span>
        </span>
      );
    }
    if (doc.status === 'needs_review' || doc.flagged_count > 0) {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-500/10 text-amber-300 border border-amber-500/30">
          <AlertCircle className="w-3 h-3 text-amber-400" />
          <span>Needs Review ({doc.flagged_count || 1})</span>
        </span>
      );
    }
    if (doc.status === 'auto_approved') {
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
          <CheckCircle2 className="w-3 h-3 text-emerald-400" />
          <span>Auto-Approved</span>
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-800 text-slate-400 border border-slate-700">
        <span>{doc.status || 'Pending'}</span>
      </span>
    );
  };

  const formatDate = (isoStr) => {
    if (!isoStr) return '-';
    try {
      const d = new Date(isoStr);
      return d.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return isoStr;
    }
  };

  return (
    <div className="w-full space-y-4">
      {/* Controls Bar: Filters & Search */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        {/* Tabs */}
        <div className="flex items-center gap-1 bg-slate-900/60 p-1 rounded-lg border border-slate-800 overflow-x-auto max-w-full">
          {filterTabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setFilterType(tab.id)}
              className={`text-xs px-3 py-1.5 rounded-md font-medium whitespace-nowrap transition ${
                filterType === tab.id
                  ? 'bg-slate-800 text-sky-400 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
              }`}
            >
              {tab.label}
              {tab.id === 'NEEDS_REVIEW' && (
                <span className="ml-1.5 px-1.5 py-0.2 rounded-full text-[10px] bg-amber-500/20 text-amber-300">
                  {documents.filter(d => d.status === 'needs_review' || d.flagged_count > 0).length}
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Search Input */}
        <div className="relative w-full sm:w-64">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search documents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-8 pr-3 py-1.5 bg-slate-900/80 border border-slate-800 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500/50"
          />
        </div>
      </div>

      {/* Table / List */}
      <div className="bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        {isLoading ? (
          <div className="p-12 text-center text-slate-400 flex flex-col items-center justify-center gap-3">
            <Loader2 className="w-6 h-6 animate-spin text-sky-400" />
            <p className="text-xs">Loading documents...</p>
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-12 text-center text-slate-400">
            <FileText className="w-8 h-8 text-slate-600 mx-auto mb-2 opacity-60" />
            <p className="text-sm font-medium text-slate-300">No documents found</p>
            <p className="text-xs text-slate-500 mt-1">Upload a document or seed one of the demo fixtures to begin.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950/60 text-slate-400 border-b border-slate-800 font-medium">
                <tr>
                  <th className="py-3 px-4">Document</th>
                  <th className="py-3 px-4">Classification</th>
                  <th className="py-3 px-4">Review Status</th>
                  <th className="py-3 px-4">Uploaded</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {filtered.map((doc) => (
                  <tr 
                    key={doc.id}
                    className="hover:bg-slate-800/40 transition group"
                  >
                    <td className="py-3 px-4">
                      <Link 
                        href={`/documents/${doc.id}`}
                        className="flex items-center gap-2.5 group-hover:text-sky-400 transition"
                      >
                        <div className="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-400 group-hover:border-sky-500/40 group-hover:text-sky-400 shrink-0">
                          <FileText className="w-4 h-4" />
                        </div>
                        <div>
                          <p className="font-medium text-slate-200 group-hover:text-sky-300 transition truncate max-w-[220px] sm:max-w-xs">
                            {doc.filename}
                          </p>
                          <p className="text-[11px] text-slate-500">
                            {doc.page_count ? `${doc.page_count} page(s)` : 'Rasterizing'} · {(doc.file_size / 1024).toFixed(1)} KB
                          </p>
                        </div>
                      </Link>
                    </td>

                    <td className="py-3 px-4 whitespace-nowrap">
                      <ClassificationBadge 
                        type={doc.type} 
                        confidence={doc.type_confidence} 
                      />
                    </td>

                    <td className="py-3 px-4 whitespace-nowrap">
                      {getStatusBadge(doc)}
                    </td>

                    <td className="py-3 px-4 text-slate-400 whitespace-nowrap font-mono text-[11px]">
                      {formatDate(doc.uploaded_at)}
                    </td>

                    <td className="py-3 px-4 text-right whitespace-nowrap">
                      <div className="flex items-center justify-end gap-1.5">
                        <Link
                          href={`/documents/${doc.id}`}
                          className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition flex items-center gap-1 text-[11px]"
                        >
                          <span>Workspace</span>
                          <ArrowRight className="w-3 h-3 text-slate-400" />
                        </Link>

                        <a
                          href={`/api/documents/${doc.id}/export?format=json`}
                          download
                          title="Export JSON"
                          className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 transition"
                        >
                          <Download className="w-3.5 h-3.5" />
                        </a>

                        <button
                          onClick={() => onDeleteDocument(doc.id)}
                          title="Delete document"
                          className="p-1 rounded bg-slate-800 hover:bg-red-500/20 text-slate-400 hover:text-red-400 transition"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
