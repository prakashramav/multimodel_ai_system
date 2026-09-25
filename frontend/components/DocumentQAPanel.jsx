'use client';

import { useState, useRef, useEffect } from 'react';
import { 
  MessageSquare, 
  Send, 
  X, 
  Sparkles, 
  Loader2, 
  Bot, 
  User, 
  CheckCircle2, 
  AlertCircle,
  FileText
} from 'lucide-react';

export default function DocumentQAPanel({
  isOpen,
  onClose,
  documentId,
  documentType = 'invoice'
}) {
  const [messages, setMessages] = useState([]);
  const [inputQuestion, setInputQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const chatBottomRef = useRef(null);

  // Suggestions based on document type
  const promptSuggestions = {
    invoice: [
      "What is the payment due date?",
      "What is the total amount due?",
      "Who is the customer billed?",
      "What line items are included?"
    ],
    resume: [
      "What is the candidate's highest degree & GPA?",
      "What are their primary technical skills?",
      "How many years of experience do they have?",
      "Where did they work previously?"
    ],
    receipt: [
      "What is the total amount paid?",
      "What items were purchased?",
      "What payment method was used?",
      "What is the date and store address?"
    ],
    contract: [
      "Does this contract have an auto-renewal clause?",
      "What is the governing jurisdiction?",
      "What is the limitation of liability cap?",
      "What is the termination notice period?"
    ],
    other: [
      "What is the main summary of this document?",
      "What are the key dates mentioned?",
      "What are the parties involved?"
    ]
  };

  const currentSuggestions = promptSuggestions[documentType] || promptSuggestions.other;

  // Load existing QA history on mount or open
  useEffect(() => {
    if (!documentId || !isOpen) return;

    const loadHistory = async () => {
      try {
        const res = await fetch(`/api/documents/${documentId}/qa-history`);
        if (res.ok) {
          const data = await res.json();
          if (data && data.length > 0) {
            const formatted = data.map((d) => [
              { role: 'user', content: d.question },
              { role: 'assistant', content: d.answer, sources: d.grounded_sources }
            ]).flat();
            setMessages(formatted);
          }
        }
      } catch (e) {
        // Ignore error
      }
    };

    loadHistory();
  }, [documentId, isOpen]);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleAsk = async (questionText) => {
    const q = (questionText || inputQuestion).trim();
    if (!q || isLoading) return;

    setInputQuestion('');
    setMessages((prev) => [...prev, { role: 'user', content: q }]);
    setIsLoading(true);

    try {
      const res = await fetch(`/api/documents/${documentId}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q }),
      });

      if (!res.ok) {
        throw new Error('Failed to get answer from QA engine');
      }

      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.answer,
          sources: data.sources || [],
        },
      ]);
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `Error: ${e.message}`,
          sources: [],
          isError: true,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 w-full sm:w-[460px] bg-[#0c101b] border-l border-slate-800 shadow-2xl z-50 flex flex-col animate-in slide-in-from-right duration-200">
      
      {/* Drawer Header */}
      <div className="p-4 bg-slate-900 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-semibold text-slate-100 flex items-center gap-1.5">
              Grounded Document Q&A
            </h3>
            <p className="text-[11px] text-slate-400">
              Answers strictly grounded in extracted content & source text
            </p>
          </div>
        </div>

        <button
          onClick={onClose}
          className="p-1 rounded-md text-slate-400 hover:text-slate-100 hover:bg-slate-800 transition"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="py-8 text-center space-y-4">
            <div className="w-10 h-10 rounded-full bg-slate-800/80 border border-slate-700 flex items-center justify-center text-sky-400 mx-auto">
              <MessageSquare className="w-5 h-5 opacity-80" />
            </div>
            <div>
              <p className="text-xs font-medium text-slate-200">Ask any question about this document</p>
              <p className="text-[11px] text-slate-500 mt-1 max-w-xs mx-auto">
                Responses are verified against the original text layer and structured fields.
              </p>
            </div>

            {/* Suggested Prompt Chips */}
            <div className="pt-2 text-left">
              <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block mb-2 px-1">
                Suggested Prompts
              </span>
              <div className="flex flex-col gap-1.5">
                {currentSuggestions.map((prompt, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleAsk(prompt)}
                    className="text-left text-xs p-2 rounded-lg bg-slate-900/60 hover:bg-slate-800 border border-slate-800/80 hover:border-slate-700 text-slate-300 hover:text-sky-300 transition flex items-center justify-between group"
                  >
                    <span>{prompt}</span>
                    <Sparkles className="w-3 h-3 text-slate-600 group-hover:text-sky-400 transition" />
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          messages.map((m, idx) => (
            <div
              key={idx}
              className={`flex flex-col ${m.role === 'user' ? 'items-end' : 'items-start'}`}
            >
              <div
                className={`max-w-[88%] rounded-xl px-3.5 py-2.5 text-xs leading-relaxed ${
                  m.role === 'user'
                    ? 'bg-sky-600 text-white rounded-br-none'
                    : 'bg-slate-800/80 border border-slate-700/80 text-slate-200 rounded-bl-none'
                }`}
              >
                <div className="whitespace-pre-wrap">{m.content}</div>

                {/* Grounded Citation Sources */}
                {m.sources && m.sources.length > 0 && (
                  <div className="mt-2.5 pt-2 border-t border-slate-700/60 text-[10px] text-slate-400 space-y-1">
                    <div className="font-semibold text-sky-400 flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3" />
                      <span>Grounded Citations:</span>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {m.sources.map((src, sIdx) => (
                        <span
                          key={sIdx}
                          className="px-1.5 py-0.5 rounded bg-slate-900 border border-slate-700 text-slate-300 font-mono"
                        >
                          {src}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))
        )}

        {isLoading && (
          <div className="flex items-start">
            <div className="bg-slate-800/80 border border-slate-700/80 rounded-xl rounded-bl-none px-3.5 py-2.5 text-xs text-slate-300 flex items-center gap-2">
              <Loader2 className="w-3.5 h-3.5 animate-spin text-sky-400" />
              <span>Analyzing document and grounding answer...</span>
            </div>
          </div>
        )}

        <div ref={chatBottomRef} />
      </div>

      {/* Input Form */}
      <div className="p-3 bg-slate-900 border-t border-slate-800">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleAsk();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            placeholder="Ask a question about this document..."
            value={inputQuestion}
            onChange={(e) => setInputQuestion(e.target.value)}
            disabled={isLoading}
            className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-500/50"
          />

          <button
            type="submit"
            disabled={!inputQuestion.trim() || isLoading}
            className="p-2 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 font-medium transition disabled:opacity-40"
          >
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>
      </div>

    </div>
  );
}
