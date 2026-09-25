'use client';

import { useState, useEffect, use } from 'react';
import Link from 'next/link';
import { 
  ArrowLeft, 
  MessageSquare, 
  CheckCircle2, 
  AlertCircle, 
  Loader2, 
  Sparkles, 
  Layers, 
  FileText,
  RotateCw,
  RefreshCw,
  ChevronRight
} from 'lucide-react';
import ClassificationBadge from '@/components/ClassificationBadge';
import PageViewer from '@/components/PageViewer';
import ExtractedFieldsPanel from '@/components/ExtractedFieldsPanel';
import TableExtractionView from '@/components/TableExtractionView';
import DocumentQAPanel from '@/components/DocumentQAPanel';
import ExportMenu from '@/components/ExportMenu';

export default function DocumentWorkspacePage({ params }) {
  const unwrappedParams = use(params);
  const documentId = unwrappedParams.id;

  const [documentData, setDocumentData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Viewer and focus state
  const [activePage, setActivePage] = useState(1);
  const [activeField, setActiveField] = useState(null);
  const [hoveredField, setHoveredField] = useState(null);
  
  // Q&A Drawer state
  const [isQAPanelOpen, setIsQAPanelOpen] = useState(false);

  // Active right pane tab: 'fields' or 'tables'
  const [activeTab, setActiveTab] = useState('fields');

  const fetchDocumentDetail = async () => {
    try {
      const res = await fetch(`/api/documents/${documentId}`);
      if (!res.ok) {
        throw new Error('Document not found or still initializing');
      }
      const data = await res.json();
      setDocumentData(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDocumentDetail();
  }, [documentId]);

  // Polling for pipeline progress if processing
  useEffect(() => {
    if (!documentData) return;
    const isProcessing = documentData.document.status === 'processing';
    if (!isProcessing) return;

    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/documents/${documentId}/status`);
        if (res.ok) {
          const statusData = await res.json();
          if (statusData.status !== 'processing') {
            clearInterval(interval);
            fetchDocumentDetail();
          } else {
            setDocumentData((prev) => ({
              ...prev,
              document: {
                ...prev.document,
                current_stage: statusData.current_stage,
                stage_message: statusData.stage_message,
                status: statusData.status,
              }
            }));
          }
        }
      } catch (e) {
        // Ignore polling error
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [documentId, documentData?.document?.status]);

  const handleFieldUpdated = (updatedField, newDocStatus, remainingFlaggedCount) => {
    setDocumentData((prev) => {
      if (!prev) return prev;

      // Update fields list
      const newFields = prev.fields.map((f) =>
        f.id === updatedField.id ? updatedField : f
      );

      // Update sections list
      const newSections = { ...prev.sections };
      for (const sec in newSections) {
        newSections[sec] = newSections[sec].map((f) =>
          f.id === updatedField.id ? updatedField : f
        );
      }

      return {
        ...prev,
        document: {
          ...prev.document,
          status: newDocStatus,
          flagged_count: remainingFlaggedCount,
        },
        fields: newFields,
        sections: newSections,
      };
    });
  };

  // Field selection from image overlay or field list
  const handleSelectField = (field) => {
    setActiveField(field);
    if (field.page_number && field.page_number !== activePage) {
      setActivePage(field.page_number);
    }
  };

  if (isLoading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center min-h-[60vh] gap-3 text-slate-400">
        <Loader2 className="w-8 h-8 animate-spin text-sky-400" />
        <p className="text-xs font-mono">Loading document workspace...</p>
      </div>
    );
  }

  if (error || !documentData) {
    return (
      <div className="max-w-xl mx-auto my-16 p-8 bg-slate-900 border border-slate-800 rounded-2xl text-center space-y-4">
        <AlertCircle className="w-10 h-10 text-red-400 mx-auto" />
        <h2 className="text-base font-semibold text-slate-200">Unable to load document</h2>
        <p className="text-xs text-slate-400">{error || 'Document record could not be found.'}</p>
        <Link
          href="/"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 text-slate-200 hover:bg-slate-700 text-xs font-medium transition"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Return to Workspace</span>
        </Link>
      </div>
    );
  }

  const { document: doc, pages, fields, sections, tables } = documentData;
  const isProcessing = doc.status === 'processing';
  const hasTables = tables && tables.length > 0;

  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-3.5rem)] overflow-hidden">
      
      {/* Top Workspace Header Bar */}
      <div className="px-4 py-2 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between gap-3 shrink-0">
        
        {/* Left: Back Link & Document Details */}
        <div className="flex items-center gap-3 min-w-0">
          <Link
            href="/"
            className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-100 transition shrink-0"
            title="Back to all documents"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>

          <div className="flex items-center gap-2 min-w-0">
            <h1 className="text-sm font-semibold text-slate-100 truncate max-w-[200px] sm:max-w-md">
              {doc.filename}
            </h1>

            {/* Classification pill */}
            <ClassificationBadge
              type={doc.type}
              confidence={doc.type_confidence}
            />

            {/* Review Status Pill */}
            {doc.status === 'needs_review' || doc.flagged_count > 0 ? (
              <span className="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-amber-500/10 text-amber-300 border border-amber-500/30">
                <AlertCircle className="w-3 h-3 text-amber-400" />
                <span>Needs Review ({doc.flagged_count} flagged)</span>
              </span>
            ) : doc.status === 'auto_approved' ? (
              <span className="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                <span>Auto-Approved</span>
              </span>
            ) : null}
          </div>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-2 shrink-0">
          
          {/* Grounded Q&A Drawer Toggle */}
          <button
            onClick={() => setIsQAPanelOpen(true)}
            className="px-3 py-1.5 rounded-md bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-medium flex items-center gap-1.5 transition"
          >
            <Sparkles className="w-3.5 h-3.5 text-sky-400" />
            <span className="hidden sm:inline">Ask Document</span>
          </button>

          {/* Export Dropdown */}
          <ExportMenu documentId={doc.id} filename={doc.filename} />

        </div>

      </div>

      {/* Real-time Pipeline Progress Banner (if still processing) */}
      {isProcessing && (
        <div className="px-4 py-2 bg-sky-950/70 border-b border-sky-800/80 text-sky-200 text-xs flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2">
            <Loader2 className="w-3.5 h-3.5 animate-spin text-sky-400" />
            <span className="font-medium">Pipeline running:</span>
            <span className="font-mono text-slate-300">{doc.stage_message || 'Processing document...'}</span>
          </div>
          <span className="font-mono text-[11px] text-sky-400 uppercase tracking-wider">
            Stage: {doc.current_stage}
          </span>
        </div>
      )}

      {/* Main Split View Area */}
      <div className="flex-1 flex flex-col md:flex-row overflow-hidden p-3 gap-3">
        
        {/* Left Pane: Page Image Viewer with Bounding Box Overlay */}
        <div className="w-full md:w-7/12 h-1/2 md:h-full">
          <PageViewer
            pages={pages}
            activePageNumber={activePage}
            onPageChange={setActivePage}
            fields={fields}
            activeField={activeField}
            hoveredField={hoveredField}
            onFieldClick={handleSelectField}
          />
        </div>

        {/* Right Pane: Structured Fields & Tables Tabs */}
        <div className="w-full md:w-5/12 h-1/2 md:h-full flex flex-col min-w-0">
          
          {/* Pane Switcher (Fields vs Tables) */}
          <div className="flex items-center justify-between bg-slate-900/80 p-1 rounded-t-xl border-t border-l border-r border-slate-800 shrink-0">
            <div className="flex items-center gap-1">
              <button
                onClick={() => setActiveTab('fields')}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                  activeTab === 'fields'
                    ? 'bg-slate-800 text-sky-400 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Extracted Fields ({fields.length})
              </button>

              <button
                onClick={() => setActiveTab('tables')}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition flex items-center gap-1 ${
                  activeTab === 'tables'
                    ? 'bg-slate-800 text-sky-400 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <span>Tables ({tables.length})</span>
                {hasTables && (
                  <span className="w-1.5 h-1.5 rounded-full bg-sky-400" />
                )}
              </button>
            </div>

            <div className="text-[11px] text-slate-500 font-mono pr-2 hidden sm:block">
              Click field to highlight on page
            </div>
          </div>

          {/* Active Tab Content */}
          <div className="flex-1 overflow-hidden">
            {activeTab === 'fields' ? (
              <ExtractedFieldsPanel
                documentId={doc.id}
                sections={sections}
                fields={fields}
                activeField={activeField}
                hoveredField={hoveredField}
                onHoverField={setHoveredField}
                onLeaveField={() => setHoveredField(null)}
                onSelectField={handleSelectField}
                onFieldUpdated={handleFieldUpdated}
              />
            ) : (
              <div className="h-full overflow-y-auto">
                <TableExtractionView
                  tables={tables}
                  documentId={doc.id}
                />
              </div>
            )}
          </div>

        </div>

      </div>

      {/* Slide-out Grounded Q&A Drawer */}
      <DocumentQAPanel
        isOpen={isQAPanelOpen}
        onClose={() => setIsQAPanelOpen(false)}
        documentId={doc.id}
        documentType={doc.type}
      />

    </div>
  );
}
