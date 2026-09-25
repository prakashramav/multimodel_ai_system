export default function ClassificationBadge({ type, confidence, showConfidence = true }) {
  const normType = (type || 'other').toLowerCase();

  const configs = {
    invoice: {
      label: 'Invoice',
      bg: 'bg-sky-500/10',
      border: 'border-sky-500/30',
      text: 'text-sky-400',
    },
    resume: {
      label: 'Resume / CV',
      bg: 'bg-indigo-500/10',
      border: 'border-indigo-500/30',
      text: 'text-indigo-400',
    },
    receipt: {
      label: 'Receipt',
      bg: 'bg-emerald-500/10',
      border: 'border-emerald-500/30',
      text: 'text-emerald-400',
    },
    contract: {
      label: 'Contract',
      bg: 'bg-amber-500/10',
      border: 'border-amber-500/30',
      text: 'text-amber-400',
    },
    form: {
      label: 'Form',
      bg: 'bg-purple-500/10',
      border: 'border-purple-500/30',
      text: 'text-purple-400',
    },
    other: {
      label: 'Document',
      bg: 'bg-slate-500/10',
      border: 'border-slate-500/30',
      text: 'text-slate-400',
    },
  };

  const c = configs[normType] || configs.other;
  const pct = Math.round((confidence || 0) * 100);

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border ${c.bg} ${c.border} ${c.text}`}>
      <span>{c.label}</span>
      {showConfidence && confidence > 0 && (
        <>
          <span className="opacity-40">·</span>
          <span className="font-mono text-[11px] opacity-90">{pct}% conf</span>
        </>
      )}
    </span>
  );
}
