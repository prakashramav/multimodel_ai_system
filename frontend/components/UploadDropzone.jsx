'use client';

import { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { 
  UploadCloud, 
  FileUp, 
  Sparkles, 
  Loader2, 
  FileText, 
  AlertCircle 
} from 'lucide-react';

export default function UploadDropzone({ onUploadSuccess }) {
  const router = useRouter();
  const fileInputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [loadingSample, setLoadingSample] = useState(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      await processUpload(files[0]);
    }
  };

  const handleFileChange = async (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      await processUpload(files[0]);
    }
  };

  const processUpload = async (file) => {
    setIsUploading(true);
    setUploadError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/documents/upload', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const data = await res.json();
      if (onUploadSuccess) {
        onUploadSuccess(data);
      }
      router.push(`/documents/${data.id}`);
    } catch (err) {
      setUploadError(err.message);
      setIsUploading(false);
    }
  };

  const handleSeedSample = async (sampleType) => {
    setLoadingSample(sampleType);
    setUploadError(null);

    try {
      const res = await fetch(`/api/documents/seed-sample/${sampleType}`, {
        method: 'POST',
      });

      if (!res.ok) {
        throw new Error(`Failed to load ${sampleType} sample`);
      }

      const data = await res.json();
      if (onUploadSuccess) {
        onUploadSuccess(data);
      }
      router.push(`/documents/${data.id}`);
    } catch (err) {
      setUploadError(err.message);
      setLoadingSample(null);
    }
  };

  return (
    <div className="w-full">
      {/* Drop Area */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`relative cursor-pointer border-2 border-dashed rounded-xl p-8 transition-all flex flex-col items-center justify-center text-center group ${
          isDragging
            ? 'border-sky-400 bg-sky-500/10'
            : 'border-slate-700 hover:border-slate-600 bg-slate-900/40 hover:bg-slate-900/70'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.png,.jpg,.jpeg,.tiff,.webp"
          className="hidden"
          onChange={handleFileChange}
        />

        <div className="w-12 h-12 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 group-hover:scale-105 group-hover:text-sky-400 group-hover:border-sky-500/40 transition mb-3">
          {isUploading ? (
            <Loader2 className="w-6 h-6 animate-spin text-sky-400" />
          ) : (
            <UploadCloud className="w-6 h-6" />
          )}
        </div>

        <h3 className="text-sm font-semibold text-slate-200 mb-1">
          {isUploading ? 'Uploading and queuing pipeline...' : 'Upload document for multimodal extraction'}
        </h3>
        
        <p className="text-xs text-slate-400 max-w-sm mb-3">
          Drag and drop PDF, scanned documents, receipts, or invoices, or click to browse.
        </p>

        <div className="flex items-center gap-2 text-[11px] text-slate-400">
          <span className="px-2 py-0.5 rounded bg-slate-800 font-mono">PDF</span>
          <span className="px-2 py-0.5 rounded bg-slate-800 font-mono">PNG / JPG</span>
          <span className="px-2 py-0.5 rounded bg-slate-800 font-mono">Up to 25MB</span>
        </div>
      </div>

      {uploadError && (
        <div className="mt-3 p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0 text-red-400" />
          <span>{uploadError}</span>
        </div>
      )}

      {/* Instant Demo Fixture Buttons */}
      <div className="mt-4 pt-4 border-t border-slate-800/80">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-2.5">
          <span className="text-xs text-slate-400 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>Or test immediately with pre-built sample fixtures:</span>
          </span>

          <div className="flex items-center gap-2 w-full sm:w-auto">
            <button
              onClick={() => handleSeedSample('invoice')}
              disabled={loadingSample !== null || isUploading}
              className="flex-1 sm:flex-none text-xs px-3 py-1.5 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 hover:border-slate-600 transition flex items-center justify-center gap-1.5 disabled:opacity-50"
            >
              {loadingSample === 'invoice' ? <Loader2 className="w-3 h-3 animate-spin text-sky-400" /> : <FileText className="w-3 h-3 text-sky-400" />}
              <span>Invoice</span>
            </button>

            <button
              onClick={() => handleSeedSample('resume')}
              disabled={loadingSample !== null || isUploading}
              className="flex-1 sm:flex-none text-xs px-3 py-1.5 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 hover:border-slate-600 transition flex items-center justify-center gap-1.5 disabled:opacity-50"
            >
              {loadingSample === 'resume' ? <Loader2 className="w-3 h-3 animate-spin text-indigo-400" /> : <FileText className="w-3 h-3 text-indigo-400" />}
              <span>Resume</span>
            </button>

            <button
              onClick={() => handleSeedSample('receipt')}
              disabled={loadingSample !== null || isUploading}
              className="flex-1 sm:flex-none text-xs px-3 py-1.5 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 hover:border-slate-600 transition flex items-center justify-center gap-1.5 disabled:opacity-50"
            >
              {loadingSample === 'receipt' ? <Loader2 className="w-3 h-3 animate-spin text-emerald-400" /> : <FileText className="w-3 h-3 text-emerald-400" />}
              <span>Receipt</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
