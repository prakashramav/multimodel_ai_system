'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  FileText, 
  CheckCircle2, 
  AlertCircle, 
  Sparkles, 
  Layers, 
  ExternalLink,
  ChevronDown,
  Loader2
} from 'lucide-react';

export default function Navbar() {
  const pathname = usePathname();
  const [reviewCount, setReviewCount] = useState(0);
  const [isSeeding, setIsSeeding] = useState(false);
  const [seedDropdownOpen, setSeedDropdownOpen] = useState(false);

  const fetchReviewCount = async () => {
    try {
      const res = await fetch('/api/review-queue');
      if (res.ok) {
        const data = await res.json();
        setReviewCount(data.length);
      }
    } catch (e) {
      // Ignore background error
    }
  };

  useEffect(() => {
    fetchReviewCount();
    const interval = setInterval(fetchReviewCount, 8000);
    return () => clearInterval(interval);
  }, []);

  const handleSeed = async (sampleType) => {
    setIsSeeding(true);
    setSeedDropdownOpen(false);
    try {
      const res = await fetch(`/api/documents/seed-sample/${sampleType}`, {
        method: 'POST',
      });
      if (res.ok) {
        const data = await res.json();
        window.location.href = `/documents/${data.id}`;
      } else {
        alert(`Failed to load ${sampleType} sample.`);
      }
    } catch (e) {
      alert(`Error loading sample: ${e.message}`);
    } finally {
      setIsSeeding(false);
    }
  };

  return (
    <header className="sticky top-0 z-50 bg-[#0f172a]/95 backdrop-blur border-b border-slate-800 text-slate-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
        
        {/* Brand */}
        <div className="flex items-center gap-6">
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-lg bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400 group-hover:bg-sky-500/20 transition">
              <Layers className="w-4 h-4" />
            </div>
            <div>
              <span className="font-semibold text-slate-100 tracking-tight text-sm flex items-center gap-1.5">
                DocIntel
                <span className="text-[10px] font-mono uppercase px-1.5 py-0.2 rounded bg-sky-950 text-sky-400 border border-sky-800">
                  Multimodal
                </span>
              </span>
              <p className="text-[11px] text-slate-400 leading-none">Document Intelligence</p>
            </div>
          </Link>

          {/* Nav Links */}
          <nav className="hidden sm:flex items-center gap-1 text-xs font-medium">
            <Link 
              href="/"
              className={`px-3 py-1.5 rounded-md transition ${
                pathname === '/' 
                  ? 'bg-slate-800 text-sky-400' 
                  : 'text-slate-300 hover:text-slate-100 hover:bg-slate-800/50'
              }`}
            >
              Workspace
            </Link>

            <Link 
              href="/review"
              className={`px-3 py-1.5 rounded-md transition flex items-center gap-1.5 ${
                pathname.startsWith('/review')
                  ? 'bg-slate-800 text-amber-400'
                  : 'text-slate-300 hover:text-slate-100 hover:bg-slate-800/50'
              }`}
            >
              Review Queue
              {reviewCount > 0 && (
                <span className="px-1.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  {reviewCount}
                </span>
              )}
            </Link>
          </nav>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-3">
          {/* Quick Seed Dropdown */}
          <div className="relative">
            <button
              onClick={() => setSeedDropdownOpen(!seedDropdownOpen)}
              disabled={isSeeding}
              className="text-xs font-medium px-3 py-1.5 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 flex items-center gap-1.5 transition disabled:opacity-50"
            >
              {isSeeding ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin text-sky-400" />
              ) : (
                <Sparkles className="w-3.5 h-3.5 text-amber-400" />
              )}
              <span>Demo Fixtures</span>
              <ChevronDown className="w-3 h-3 text-slate-400" />
            </button>

            {seedDropdownOpen && (
              <div 
                className="absolute right-0 mt-1.5 w-48 rounded-lg bg-slate-900 border border-slate-700 shadow-xl py-1 text-xs z-50"
                onMouseLeave={() => setSeedDropdownOpen(false)}
              >
                <div className="px-3 py-1.5 text-[10px] font-semibold text-slate-400 uppercase tracking-wider border-b border-slate-800">
                  Instant Test Samples
                </div>
                <button
                  onClick={() => handleSeed('invoice')}
                  className="w-full text-left px-3 py-2 text-slate-200 hover:bg-slate-800 flex items-center justify-between"
                >
                  <span>Commercial Invoice</span>
                  <span className="text-[10px] text-slate-400">PDF</span>
                </button>
                <button
                  onClick={() => handleSeed('resume')}
                  className="w-full text-left px-3 py-2 text-slate-200 hover:bg-slate-800 flex items-center justify-between"
                >
                  <span>Software CV / Resume</span>
                  <span className="text-[10px] text-slate-400">PDF</span>
                </button>
                <button
                  onClick={() => handleSeed('receipt')}
                  className="w-full text-left px-3 py-2 text-slate-200 hover:bg-slate-800 flex items-center justify-between"
                >
                  <span>Retail Store Receipt</span>
                  <span className="text-[10px] text-slate-400">PDF</span>
                </button>
              </div>
            )}
          </div>

          <div className="h-4 w-px bg-slate-800 hidden sm:block" />

          {/* Engine indicator */}
          <div className="hidden sm:flex items-center gap-1.5 text-[11px] text-slate-400 bg-slate-900/60 px-2.5 py-1 rounded-md border border-slate-800">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>FastAPI Multimodal Engine</span>
          </div>
        </div>

      </div>
    </header>
  );
}
