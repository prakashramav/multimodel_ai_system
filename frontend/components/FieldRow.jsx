'use client';

import { useState } from 'react';
import { 
  Check, 
  X, 
  Edit3, 
  AlertCircle, 
  CheckCircle2, 
  Loader2, 
  History 
} from 'lucide-react';

export default function FieldRow({
  documentId,
  field,
  isHovered,
  isActive,
  onHover,
  onLeave,
  onSelect,
  onFieldUpdated
}) {
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState(field.value || '');
  const [isSaving, setIsSaving] = useState(false);
  const [showAuditTrail, setShowAuditTrail] = useState(false);

  const confidencePct = Math.round((field.confidence || 0) * 100);
  const isFlagged = field.flagged;
  const isReviewed = field.reviewed;

  // Calm confidence indicator color
  const getConfidenceDot = (conf) => {
    if (conf >= 0.85) return 'bg-emerald-400';
    if (conf >= 0.75) return 'bg-sky-400';
    return 'bg-amber-400';
  };

  const handleSave = async () => {
    if (editValue === field.value && !isFlagged) {
      setIsEditing(false);
      return;
    }

    setIsSaving(true);
    try {
      const res = await fetch(`/api/documents/${documentId}/fields/${field.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          value: editValue,
          notes: 'Inline human review correction'
        })
      });

      if (!res.ok) {
        throw new Error('Failed to update field');
      }

      const data = await res.json();
      setIsEditing(false);
      if (onFieldUpdated) {
        onFieldUpdated(data.field, data.document_status, data.remaining_flagged_count);
      }
    } catch (e) {
      alert(`Error updating field: ${e.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSave();
    } else if (e.key === 'Escape') {
      setEditValue(field.value || '');
      setIsEditing(false);
    }
  };

  return (
    <div
      onMouseEnter={() => onHover(field)}
      onMouseLeave={() => onLeave(field)}
      onClick={() => onSelect(field)}
      className={`group relative text-xs p-2.5 rounded-lg transition border cursor-pointer ${
        isFlagged
          ? 'border-l-4 border-l-amber-500 border-t-slate-800 border-r-slate-800 border-b-slate-800 bg-amber-500/[0.04] hover:bg-amber-500/[0.08]'
          : 'border-slate-800 hover:border-slate-700 bg-slate-900/40 hover:bg-slate-800/50'
      } ${isActive ? 'ring-1 ring-sky-500/50 bg-slate-800/70' : ''}`}
    >
      <div className="flex items-start justify-between gap-2">
        
        {/* Label & Audit Indicator */}
        <div className="flex items-center gap-1.5 flex-1 min-w-0">
          <span className="font-medium text-slate-300 truncate">
            {field.field_label || field.field_name}
          </span>

          {isFlagged && (
            <span className="text-[10px] font-medium text-amber-400 bg-amber-500/10 px-1.5 py-0.2 rounded border border-amber-500/20 shrink-0">
              Needs Review
            </span>
          )}

          {isReviewed && (
            <span className="text-[10px] text-emerald-400 flex items-center gap-0.5 shrink-0" title="Verified by user">
              <CheckCircle2 className="w-3 h-3 text-emerald-400" />
              <span>Verified</span>
            </span>
          )}
        </div>

        {/* Confidence dot + percentage */}
        <div className="flex items-center gap-1.5 shrink-0">
          <span className={`w-1.5 h-1.5 rounded-full ${getConfidenceDot(field.confidence)}`} />
          <span className="font-mono text-[11px] text-slate-400">
            {confidencePct}%
          </span>
        </div>

      </div>

      {/* Field Value Display / Edit Form */}
      <div className="mt-1.5">
        {isEditing ? (
          <div className="flex items-center gap-1.5 mt-1" onClick={(e) => e.stopPropagation()}>
            <input
              type="text"
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              onKeyDown={handleKeyDown}
              autoFocus
              className="flex-1 bg-slate-950 border border-sky-500/50 rounded px-2 py-1 text-xs font-mono text-slate-100 focus:outline-none focus:ring-1 focus:ring-sky-400"
            />
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="p-1 rounded bg-sky-500 hover:bg-sky-400 text-slate-950 transition"
              title="Save correction"
            >
              {isSaving ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Check className="w-3.5 h-3.5" />}
            </button>
            <button
              onClick={() => {
                setEditValue(field.value || '');
                setIsEditing(false);
              }}
              className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 transition"
              title="Cancel"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        ) : (
          <div className="flex items-center justify-between group/val">
            <span 
              onDoubleClick={() => setIsEditing(true)}
              className="font-mono text-slate-200 break-all select-text"
            >
              {field.value || <span className="italic text-slate-500">Empty</span>}
            </span>

            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition shrink-0 ml-2">
              {field.original_value && field.original_value !== field.value && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setShowAuditTrail(!showAuditTrail);
                  }}
                  title="View original extracted value"
                  className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-slate-200"
                >
                  <History className="w-3 h-3 text-slate-400" />
                </button>
              )}

              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setIsEditing(true);
                }}
                title="Edit field value"
                className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-sky-400 transition"
              >
                <Edit3 className="w-3 h-3" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Audit trail detail dropdown */}
      {showAuditTrail && (
        <div className="mt-2 p-2 rounded bg-slate-950/80 border border-slate-800 text-[11px] text-slate-400">
          <div className="flex items-center justify-between text-slate-500 mb-0.5">
            <span>Audit History:</span>
            <span>Page {field.page_number}</span>
          </div>
          <div>Original: <span className="font-mono text-slate-300">{field.original_value}</span></div>
          {field.correction_notes && <div>Notes: <span className="italic text-slate-400">{field.correction_notes}</span></div>}
        </div>
      )}

    </div>
  );
}
