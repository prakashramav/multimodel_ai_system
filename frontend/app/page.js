'use client';

import { useState, useEffect } from 'react';
import { 
  FileText, 
  CheckCircle2, 
  AlertCircle, 
  Sparkles, 
  Layers, 
  ArrowUpRight,
  TrendingUp,
  Clock,
  ShieldCheck,
  Cpu
} from 'lucide-react';
import UploadDropzone from '@/components/UploadDropzone';
import DocumentList from '@/components/DocumentList';

export default function HomePage() {
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchDocuments = async () => {
    try {
      const res = await fetch('/api/documents');
      if (res.ok) {
        const data = await res.json();
        setDocuments(data);
      }
    } catch (e) {
      console.error('Error fetching documents:', e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
    const interval = setInterval(fetchDocuments, 6000);
    return () => clearInterval(interval);
  }, []);

  const handleDeleteDocument = async (id) => {
    if (!confirm('Are you sure you want to delete this document?')) return;
    try {
      const res = await fetch(`/api/documents/${id}`, { method: 'DELETE' });
      if (res.ok) {
        setDocuments((prev) => prev.filter((d) => d.id !== id));
      }
    } catch (e) {
      alert(`Error deleting document: ${e.message}`);
    }
  };

  // Stats calculation
  const totalCount = documents.length;
  const reviewCount = documents.filter((d) => d.status === 'needs_review' || d.flagged_count > 0).length;
  const approvedCount = documents.filter((d) => d.status === 'auto_approved').length;
  const avgConfidence = totalCount > 0
    ? Math.round(
        (documents.reduce((acc, d) => acc + (d.type_confidence || 0.85), 0) / totalCount) * 100
      )
    : 95;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      
      {/* Workspace Header & Intro */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-slate-800/80 pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-sky-500/10 text-sky-400 border border-sky-500/20">
              Workspace
            </span>
            <span className="text-xs text-slate-500">·</span>
            <span className="text-xs text-slate-400">Multimodal Neural Vision</span>
          </div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-100">
            Document Intelligence Platform
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-2xl">
            Upload invoices, resumes, receipts, forms, or contracts. Extract structured fields with visual bounding boxes, 
            detect tabular data, query content via grounded Q&A, and triage low-confidence fields in the human review queue.
          </p>
        </div>

        {/* Live System Badge */}
        <div className="flex items-center gap-3 bg-slate-900/80 border border-slate-800 p-2.5 rounded-xl shrink-0">
          <div className="w-8 h-8 rounded-lg bg-sky-500/10 flex items-center justify-center text-sky-400">
            <Cpu className="w-4 h-4" />
          </div>
          <div className="text-xs">
            <p className="font-semibold text-slate-200">Claude Vision + PyMuPDF</p>
            <p className="text-[11px] text-slate-400">Schema Tool-Use Enforced</p>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
        
        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-medium">Total Ingested</span>
            <FileText className="w-3.5 h-3.5 text-slate-500" />
          </div>
          <div className="text-2xl font-bold text-slate-100 font-mono">{totalCount}</div>
          <p className="text-[11px] text-slate-500 mt-0.5">Documents indexed</p>
        </div>

        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-medium">Auto-Approved</span>
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-400 font-mono">{approvedCount}</div>
          <p className="text-[11px] text-slate-500 mt-0.5">Met confidence threshold</p>
        </div>

        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-medium">Needs Review</span>
            <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-amber-400 font-mono">{reviewCount}</div>
          <p className="text-[11px] text-slate-500 mt-0.5">Flagged low confidence</p>
        </div>

        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs font-medium">Avg Extraction Conf</span>
            <ShieldCheck className="w-3.5 h-3.5 text-sky-400" />
          </div>
          <div className="text-2xl font-bold text-sky-400 font-mono">{avgConfidence}%</div>
          <p className="text-[11px] text-slate-500 mt-0.5">Multi-field reliability</p>
        </div>

      </div>

      {/* Upload Dropzone Section */}
      <div className="bg-slate-900/30 border border-slate-800/80 rounded-2xl p-6">
        <UploadDropzone onUploadSuccess={fetchDocuments} />
      </div>

      {/* Document Library Section */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold text-slate-200">
            Recent Ingested Documents
          </h2>
          <span className="text-xs text-slate-400 font-mono">
            Auto-refresh active
          </span>
        </div>

        <DocumentList
          documents={documents}
          onDeleteDocument={handleDeleteDocument}
          isLoading={isLoading}
        />
      </div>

    </div>
  );
}
