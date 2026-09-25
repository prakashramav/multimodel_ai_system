'use client';

import { useState } from 'react';
import { 
  Table, 
  Download, 
  Plus, 
  Trash2, 
  Check, 
  Edit2 
} from 'lucide-react';

export default function TableExtractionView({ tables = [], documentId }) {
  const [activeTableIdx, setActiveTableIdx] = useState(0);
  const [editableRows, setEditableRows] = useState(null);
  const [editingCell, setEditingCell] = useState(null); // { rowIndex, colKey }

  if (!tables || tables.length === 0) {
    return (
      <div className="p-4 bg-slate-900/40 rounded-xl border border-slate-800 text-center text-slate-500 text-xs">
        No tabular regions detected in this document.
      </div>
    );
  }

  const currentTable = tables[activeTableIdx] || tables[0];
  const columns = currentTable.columns || [];
  const rows = editableRows || currentTable.rows || [];

  const handleCellChange = (rowIndex, colKey, newValue) => {
    const updated = [...rows];
    updated[rowIndex] = { ...updated[rowIndex], [colKey]: newValue };
    setEditableRows(updated);
  };

  const handleAddRow = () => {
    const newRow = {};
    columns.forEach((c) => {
      const key = c.toLowerCase().replace(/[^a-z0-9]/g, '_');
      newRow[key] = '';
    });
    setEditableRows([...rows, newRow]);
  };

  const handleDeleteRow = (idx) => {
    const updated = rows.filter((_, i) => i !== idx);
    setEditableRows(updated);
  };

  const exportTableCSV = () => {
    let csvContent = 'data:text/csv;charset=utf-8,';
    csvContent += columns.map(c => `"${c}"`).join(',') + '\n';
    rows.forEach(r => {
      const rowVals = columns.map(col => {
        const val = r[col] || r[col.toLowerCase().replace(/[^a-z0-9]/g, '_')] || '';
        return `"${String(val).replace(/"/g, '""')}"`;
      });
      csvContent += rowVals.join(',') + '\n';
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `${currentTable.table_name || 'table'}_export.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="bg-slate-900/50 rounded-xl border border-slate-800 overflow-hidden">
      
      {/* Table Header Bar */}
      <div className="px-4 py-2.5 bg-slate-900 border-b border-slate-800 flex items-center justify-between gap-3">
        
        {/* Table Selector (if multiple) */}
        <div className="flex items-center gap-2">
          <Table className="w-4 h-4 text-sky-400" />
          <span className="text-xs font-semibold text-slate-200">
            {currentTable.table_name || 'Tabular Extraction'}
          </span>
          <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-slate-400">
            {rows.length} rows
          </span>
        </div>

        {/* Action buttons */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={handleAddRow}
            className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-slate-100 text-[11px] font-medium flex items-center gap-1 transition"
          >
            <Plus className="w-3 h-3 text-sky-400" />
            <span>Add Row</span>
          </button>

          <button
            onClick={exportTableCSV}
            className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-slate-100 text-[11px] font-medium flex items-center gap-1 transition"
            title="Download table CSV"
          >
            <Download className="w-3 h-3 text-emerald-400" />
            <span>CSV</span>
          </button>
        </div>

      </div>

      {/* Editable Table Content */}
      <div className="overflow-x-auto max-h-72">
        <table className="w-full text-left text-xs border-collapse">
          <thead className="bg-slate-950/70 text-slate-400 border-b border-slate-800 sticky top-0 font-medium">
            <tr>
              <th className="py-2 px-3 w-8 text-center text-slate-600 font-mono text-[10px]">#</th>
              {columns.map((col, idx) => (
                <th key={idx} className="py-2 px-3 whitespace-nowrap">
                  {col}
                </th>
              ))}
              <th className="py-2 px-2 w-10 text-right"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {rows.map((row, rIdx) => (
              <tr key={rIdx} className="hover:bg-slate-800/30 transition group">
                <td className="py-2 px-3 text-center text-slate-500 font-mono text-[10px]">
                  {rIdx + 1}
                </td>
                {columns.map((col, cIdx) => {
                  const key = col.toLowerCase().replace(/[^a-z0-9]/g, '_');
                  const val = row[col] || row[key] || '';
                  const isEditingThis = editingCell && editingCell.rowIndex === rIdx && editingCell.colKey === key;

                  return (
                    <td 
                      key={cIdx} 
                      className="py-2 px-3 font-mono text-slate-200 whitespace-nowrap cursor-pointer hover:bg-slate-800/60 transition"
                      onClick={() => setEditingCell({ rowIndex: rIdx, colKey: key })}
                    >
                      {isEditingThis ? (
                        <input
                          type="text"
                          value={val}
                          autoFocus
                          onChange={(e) => handleCellChange(rIdx, key, e.target.value)}
                          onBlur={() => setEditingCell(null)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter' || e.key === 'Escape') setEditingCell(null);
                          }}
                          className="bg-slate-950 border border-sky-400 rounded px-1.5 py-0.5 text-xs font-mono text-slate-100 focus:outline-none"
                        />
                      ) : (
                        <span>{val || <span className="text-slate-600 italic">-</span>}</span>
                      )}
                    </td>
                  );
                })}
                <td className="py-2 px-2 text-right">
                  <button
                    onClick={() => handleDeleteRow(rIdx)}
                    className="p-1 rounded text-slate-500 hover:text-red-400 hover:bg-red-500/10 opacity-0 group-hover:opacity-100 transition"
                    title="Delete row"
                  >
                    <Trash2 className="w-3 h-3" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

    </div>
  );
}
