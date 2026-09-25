'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  AlertCircle, 
  CheckCircle2, 
  Check, 
  X, 
  ExternalLink, 
  FileText, 
  ArrowRight, 
  Loader2,
  Edit3,
  Sparkles,
  Inbox
} from 'lucide-react';
import ClassificationBadge from '@/components/ClassificationBadge';

export default function ReviewQueuePage() {
  const [queueItems, setQueueItems] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [editingFieldId, setEditingFieldId] = useState(null);
  const [editingValue, setEditingValue] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchQueue = async () => {
    try {
      const res = await fetch('/api/review-queue');
      if (res.ok) {
        const data = await res.json();
        setQueueItems(data);
      }
    } catch (e) {
      console.error('Error fetching review queue:', e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchQueue();
    const interval = setInterval(fetchQueue, 6000);
    return () => clearInterval(interval);
  }, []);

  const handleInlineSave = async (docId, fieldId) => {
    setIsSubmitting(true);
    try {
      const res = await fetch(`/api/documents/${docId}/fields/${fieldId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          value: editingValue,
          notes: 'Resolved via Human Review Queue'
        })
      });

      if (!res.ok) throw new Error('Failed to resolve field');

      setEditingFieldId(null);
      await fetchQueue();
    } catch (e) {
      alert(`Error updating field: ${e.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleQuickApprove = async (docId, field) => {
    setIsSubmitting(true);
    try {
      const res = await fetch(`/api/documents/${docId}/fields/${field.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          value: field.value,
          notes: 'Approved as correct in Human Review Queue'
        })
      });

      if (!res.ok) throw new Error('Failed to approve field');
      await fetchQueue();
    } catch (e) {
      alert(`Error approving field: ${e.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const totalFlaggedFields = queueItems.reduce((acc, item) => acc + (item.flagged_count || 0), 0);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-amber-500/10 text-amber-300 border border-amber-500/20">
              Human-in-the-Loop
            </span>
            <span className="text-xs text-slate-500">·</span>
            <span className="text-xs text-slate-400">Low-Confidence Field Verification</span>
          </div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-100">
            Review Queue
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-2xl">
            Documents with extracted fields below the confidence threshold (0.75) are routed here for human verification.
            Correct values inline or click through to view the source bounding box in context.
          </p>
        </div>

        {/* Counter Pill */}
        <div className="flex items-center gap-2 bg-slate-900 border border-slate-800 px-3 py-2 rounded-xl shrink-0">
          <AlertCircle className="w-4 h-4 text-amber-400" />
          <div className="text-xs">
            <span className="font-bold text-slate-200 font-mono">{totalFlaggedFields}</span>
            <span className="text-slate-400 ml-1">fields awaiting triage</span>
          </div>
        </div>
      </div>

      {/* Main Review Queue Feed */}
      {isLoading ? (
        <div className="p-16 text-center text-slate-400 flex flex-col items-center justify-center gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-sky-400" />
          <p className="text-xs font-mono">Loading review queue...</p>
        </div>
      ) : queueItems.length === 0 ? (
        <div className="p-16 text-center bg-slate-900/40 border border-slate-800 rounded-2xl space-y-3">
          <div className="w-12 h-12 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mx-auto">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <h3 className="text-sm font-semibold text-slate-200">Review Queue Clear</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            All extracted fields currently satisfy the confidence threshold (or have been approved by human reviewers).
          </p>
          <div className="pt-2">
            <Link
              href="/"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition"
            >
              <span>Back to Documents Workspace</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {queueItems.map((item) => {
            const doc = item.document;
            const flaggedFields = item.flagged_fields || [];

            return (
              <div
                key={doc.id}
                className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-sm transition hover:border-slate-700"
              >
                {/* Document Card Header */}
                <div className="p-4 bg-slate-950/60 border-b border-slate-800/80 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
                  <div className="flex items-center gap-3 min-w-0">
                    {/* Thumbnail preview */}
                    {item.thumbnail_url ? (
                      <img
                        src={item.thumbnail_url}
                        alt="Doc preview"
                        className="w-10 h-14 object-cover rounded border border-slate-700 shrink-0 bg-white"
                      />
                    ) : (
                      <div className="w-10 h-14 rounded bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-500 shrink-0">
                        <FileText className="w-5 h-5" />
                      </div>
                    )}

                    <div className="min-w-0">
                      <div className="flex items-center gap-2">
                        <Link
                          href={`/documents/${doc.id}`}
                          className="font-semibold text-sm text-slate-200 hover:text-sky-300 transition truncate max-w-md"
                        >
                          {doc.filename}
                        </Link>
                        <ClassificationBadge type={doc.type} confidence={doc.type_confidence} />
                      </div>
                      <p className="text-xs text-slate-400 mt-0.5">
                        <span className="text-amber-400 font-medium">{item.flagged_count} field(s)</span> requiring review · Uploaded {new Date(doc.uploaded_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>

                  <Link
                    href={`/documents/${doc.id}`}
                    className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium flex items-center gap-1.5 transition shrink-0 self-end sm:self-center"
                  >
                    <span>Inspect in Split View</span>
                    <ArrowRight className="w-3.5 h-3.5 text-slate-400" />
                  </Link>
                </div>

                {/* Flagged Fields Table / List */}
                <div className="divide-y divide-slate-800/60">
                  {flaggedFields.map((field) => {
                    const isEditing = editingFieldId === field.id;
                    const confidencePct = Math.round((field.confidence || 0) * 100);

                    return (
                      <div
                        key={field.id}
                        className="p-3.5 sm:px-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 hover:bg-slate-800/30 transition"
                      >
                        {/* Field Info */}
                        <div className="space-y-0.5 min-w-[200px]">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-xs text-slate-200">
                              {field.field_label || field.field_name}
                            </span>
                            <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-slate-400">
                              {field.section}
                            </span>
                          </div>
                          <div className="flex items-center gap-1.5 text-[11px] text-amber-400">
                            <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                            <span>Confidence: {confidencePct}% (&lt; 75% threshold)</span>
                          </div>
                        </div>

                        {/* Value & Inline Correction */}
                        <div className="flex-1 w-full sm:w-auto min-w-0 sm:px-4">
                          {isEditing ? (
                            <div className="flex items-center gap-2">
                              <input
                                type="text"
                                value={editingValue}
                                onChange={(e) => setEditingValue(e.target.value)}
                                autoFocus
                                onKeyDown={(e) => {
                                  if (e.key === 'Enter') handleInlineSave(doc.id, field.id);
                                  if (e.key === 'Escape') setEditingFieldId(null);
                                }}
                                className="flex-1 bg-slate-950 border border-sky-400 rounded px-2.5 py-1 text-xs font-mono text-slate-100 focus:outline-none"
                              />
                              <button
                                onClick={() => handleInlineSave(doc.id, field.id)}
                                disabled={isSubmitting}
                                className="px-2.5 py-1 rounded bg-sky-500 hover:bg-sky-400 text-slate-950 text-xs font-medium flex items-center gap-1 transition"
                              >
                                {isSubmitting ? <Loader2 className="w-3 h-3 animate-spin" /> : <Check className="w-3 h-3" />}
                                <span>Save</span>
                              </button>
                              <button
                                onClick={() => setEditingFieldId(null)}
                                className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-slate-200"
                              >
                                <X className="w-3.5 h-3.5" />
                              </button>
                            </div>
                          ) : (
                            <div className="flex items-center gap-2">
                              <span className="font-mono text-xs text-slate-100 bg-slate-950 px-2.5 py-1 rounded border border-slate-800 truncate block max-w-sm">
                                {field.value || <span className="italic text-slate-500">Empty</span>}
                              </span>
                              <button
                                onClick={() => {
                                  setEditingFieldId(field.id);
                                  setEditingValue(field.value || '');
                                }}
                                title="Edit value"
                                className="p-1.5 rounded hover:bg-slate-800 text-slate-400 hover:text-sky-400 transition"
                              >
                                <Edit3 className="w-3.5 h-3.5" />
                              </button>
                            </div>
                          )}
                        </div>

                        {/* Fast Triage Approval */}
                        <div className="flex items-center gap-2 shrink-0">
                          <button
                            onClick={() => handleQuickApprove(doc.id, field)}
                            disabled={isSubmitting}
                            className="px-2.5 py-1 rounded-md bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-medium flex items-center gap-1 transition disabled:opacity-50"
                          >
                            <CheckCircle2 className="w-3 h-3" />
                            <span>Verify Correct</span>
                          </button>
                        </div>

                      </div>
                    );
                  })}
                </div>

              </div>
            );
          })}
        </div>
      )}

    </div>
  );
}
