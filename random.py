import React, { useState, useRef, useEffect, useCallback } from 'react';
import { 
  Upload, Trash2, Download, FileText, ChevronLeft, ChevronRight, 
  ArrowUp, ArrowDown, ArrowLeft, ArrowRight, Settings, MousePointer2, 
  Crosshair, Plus, Tag, Image as ImageIcon, Type, Table as TableIcon
} from 'lucide-react';

// Pre-defined colors for different questions to easily distinguish chunks visually
const QUESTION_COLORS = [
  '#ef4444', '#f97316', '#f59e0b', '#84cc16', '#10b981', 
  '#06b6d4', '#3b82f6', '#8b5cf6', '#d946ef', '#f43f5e'
];

export default function App() {
  // --- State ---
  const [pdfJsLoaded, setPdfJsLoaded] = useState(false);
  const [pdfDoc, setPdfDoc] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [numPages, setNumPages] = useState(0);
  
  const [annotations, setAnnotations] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  
  // Page-specific questions: { pageNum: [{ id, label, color }] }
  const [pageQuestions, setPageQuestions] = useState({});
  const [activeQuestionId, setActiveQuestionId] = useState(null);
  const [newQuestionLabel, setNewQuestionLabel] = useState('');

  // Interaction modes
  const [toolMode, setToolMode] = useState('select'); // 'select', 'draw'
  const [interactionState, setInteractionState] = useState({ type: 'none' }); // none, drawing, resizing, moving
  const [startPos, setStartPos] = useState(null);
  const [originalBox, setOriginalBox] = useState(null);

  const scale = 1.5; // Fixed zoom for simplicity

  // --- Refs ---
  const bgCanvasRef = useRef(null);
  const fgCanvasRef = useRef(null);
  const containerRef = useRef(null);

  // --- Load PDF.js Dynamically ---
  useEffect(() => {
    const loadPdfJs = async () => {
      if (!window.pdfjsLib) {
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js';
        script.async = true;
        document.body.appendChild(script);
        
        script.onload = () => {
          window.pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
          setPdfJsLoaded(true);
        };
      } else {
        setPdfJsLoaded(true);
      }
    };
    loadPdfJs();
  }, []);

  // --- Render PDF Page ---
  const renderPdfPage = useCallback(async () => {
    if (!pdfDoc || !bgCanvasRef.current || !fgCanvasRef.current) return;
    try {
      const page = await pdfDoc.getPage(currentPage);
      const viewport = page.getViewport({ scale });
      
      const bgCanvas = bgCanvasRef.current;
      const fgCanvas = fgCanvasRef.current;
      bgCanvas.width = viewport.width;
      bgCanvas.height = viewport.height;
      fgCanvas.width = viewport.width;
      fgCanvas.height = viewport.height;

      await page.render({ canvasContext: bgCanvas.getContext('2d'), viewport }).promise;
      drawAnnotations();
    } catch (error) {
      console.error("Error rendering page:", error);
    }
  }, [pdfDoc, currentPage, scale]);

  useEffect(() => {
    renderPdfPage();
    // Auto-clear active tag when changing pages
    setActiveQuestionId(null); 
  }, [renderPdfPage, currentPage]);

  // --- Get Color for a Box ---
  const getBoxColor = useCallback((questionId) => {
    if (!questionId) return '#9ca3af'; // Gray for unassigned
    const questions = pageQuestions[currentPage] || [];
    const q = questions.find(q => q.id === questionId);
    return q ? q.color : '#9ca3af';
  }, [pageQuestions, currentPage]);

  // --- Draw Annotations ---
  const drawAnnotations = useCallback(() => {
    const canvas = fgCanvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const pageAnnotations = annotations.filter(ann => ann.page === currentPage);

    pageAnnotations.forEach(box => {
      const isSelected = box.id === selectedId;
      const color = getBoxColor(box.questionId);
      
      ctx.strokeStyle = isSelected ? '#000000' : color;
      ctx.lineWidth = isSelected ? 2 : 2;
      ctx.setLineDash(isSelected ? [4, 4] : []);
      
      // Fill
      ctx.fillStyle = isSelected ? `${color}40` : `${color}20`; // Hex alpha
      ctx.fillRect(box.x, box.y, box.w, box.h);

      // Stroke
      ctx.beginPath();
      ctx.rect(box.x, box.y, box.w, box.h);
      ctx.stroke();
      ctx.setLineDash([]); // Reset

      // Label
      if (box.questionId) {
        const questions = pageQuestions[currentPage] || [];
        const q = questions.find(q => q.id === box.questionId);
        if (q) {
          ctx.fillStyle = color;
          const labelText = `${q.label} ${box.type !== 'text' ? `(${box.type})` : ''}`;
          ctx.font = 'bold 12px sans-serif';
          const textWidth = ctx.measureText(labelText).width;
          ctx.fillRect(box.x, box.y - 18, textWidth + 8, 18);
          ctx.fillStyle = '#ffffff';
          ctx.textAlign = 'left';
          ctx.textBaseline = 'middle';
          ctx.fillText(labelText, box.x + 4, box.y - 9);
        }
      }

      // Draw Resize Handles if Selected
      if (isSelected) {
        ctx.fillStyle = '#ffffff';
        ctx.strokeStyle = '#000000';
        ctx.lineWidth = 1;
        const hw = 6; // Handle width
        const drawHandle = (hx, hy) => {
          ctx.fillRect(hx - hw/2, hy - hw/2, hw, hw);
          ctx.strokeRect(hx - hw/2, hy - hw/2, hw, hw);
        };
        drawHandle(box.x, box.y); // NW
        drawHandle(box.x + box.w, box.y); // NE
        drawHandle(box.x, box.y + box.h); // SW
        drawHandle(box.x + box.w, box.y + box.h); // SE
      }
    });

  }, [annotations, currentPage, selectedId, getBoxColor, pageQuestions]);

  useEffect(() => {
    drawAnnotations();
  }, [annotations, selectedId, drawAnnotations]);

  // --- Mouse Interactions ---
  const getMousePos = (e) => {
    const canvas = fgCanvasRef.current;
    const rect = canvas.getBoundingClientRect();
    return {
      x: (e.clientX - rect.left) * (canvas.width / rect.width),
      y: (e.clientY - rect.top) * (canvas.height / rect.height)
    };
  };

  const getResizeHandle = (pos, box) => {
    const threshold = 8;
    const onCorner = (hx, hy) => Math.abs(pos.x - hx) <= threshold && Math.abs(pos.y - hy) <= threshold;
    if (onCorner(box.x, box.y)) return 'nw';
    if (onCorner(box.x + box.w, box.y)) return 'ne';
    if (onCorner(box.x, box.y + box.h)) return 'sw';
    if (onCorner(box.x + box.w, box.y + box.h)) return 'se';
    return null;
  };

  const handleMouseDown = (e) => {
    if (!pdfDoc) return;
    const pos = getMousePos(e);
    const pageAnns = annotations.filter(a => a.page === currentPage);

    // 1. Check for resize handle click on the currently selected box
    if (selectedId && toolMode === 'select') {
      const selectedBox = pageAnns.find(a => a.id === selectedId);
      if (selectedBox) {
        const handle = getResizeHandle(pos, selectedBox);
        if (handle) {
          setInteractionState({ type: 'resizing', handle });
          setStartPos(pos);
          setOriginalBox({ ...selectedBox });
          return;
        }
      }
    }

    // 2. Check for box click
    const clickedBox = [...pageAnns].reverse().find(
      b => pos.x >= b.x && pos.x <= b.x + b.w && pos.y >= b.y && pos.y <= b.y + b.h
    );

    if (toolMode === 'select') {
      if (clickedBox) {
        setSelectedId(clickedBox.id);
        
        // **TAGGING WORKFLOW**: If an active question is selected in sidebar, instantly assign it
        if (activeQuestionId && clickedBox.questionId !== activeQuestionId) {
          updateAnnotation(clickedBox.id, { questionId: activeQuestionId });
        }
      } else {
        setSelectedId(null);
      }
    } else if (toolMode === 'draw') {
      // Start Drawing new box
      setInteractionState({ type: 'drawing' });
      setStartPos(pos);
      const newBox = {
        id: Date.now().toString(),
        page: currentPage,
        x: pos.x, y: pos.y, w: 0, h: 0,
        questionId: activeQuestionId || null,
        type: 'text'
      };
      setAnnotations([...annotations, newBox]);
      setSelectedId(newBox.id);
    }
  };

  const handleMouseMove = (e) => {
    if (interactionState.type === 'none' || !selectedId) return;
    const pos = getMousePos(e);

    if (interactionState.type === 'drawing') {
      setAnnotations(prev => prev.map(ann => {
        if (ann.id !== selectedId) return ann;
        return {
          ...ann,
          w: pos.x - startPos.x,
          h: pos.y - startPos.y
        };
      }));
    } else if (interactionState.type === 'resizing') {
      setAnnotations(prev => prev.map(ann => {
        if (ann.id !== selectedId) return ann;
        let { x, y, w, h } = originalBox;
        const dx = pos.x - startPos.x;
        const dy = pos.y - startPos.y;

        switch (interactionState.handle) {
          case 'nw': x += dx; y += dy; w -= dx; h -= dy; break;
          case 'ne': y += dy; w += dx; h -= dy; break;
          case 'sw': x += dx; w -= dx; h += dy; break;
          case 'se': w += dx; h += dy; break;
          default: break;
        }
        return { ...ann, x, y, w, h };
      }));
    }
  };

  const handleMouseUp = () => {
    if (interactionState.type === 'drawing') {
      // Normalize width/height to positive values
      setAnnotations(prev => prev.map(ann => {
        if (ann.id !== selectedId) return ann;
        let finalAnn = { ...ann };
        if (finalAnn.w < 0) { finalAnn.x += finalAnn.w; finalAnn.w = Math.abs(finalAnn.w); }
        if (finalAnn.h < 0) { finalAnn.y += finalAnn.h; finalAnn.h = Math.abs(finalAnn.h); }
        return finalAnn;
      }));
      setToolMode('select'); // Snap back to select mode after drawing
    }
    setInteractionState({ type: 'none' });
    setStartPos(null);
    setOriginalBox(null);
  };

  // --- Keyboard Shortcuts (Nudge & Resize) ---
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!selectedId || e.target.tagName === 'INPUT') return;
      const step = 2; // px
      let moved = false;

      setAnnotations(prev => prev.map(ann => {
        if (ann.id !== selectedId) return ann;
        let { x, y, w, h } = ann;
        
        // Shift + Arrow = Resize
        if (e.shiftKey) {
          if (e.key === 'ArrowUp') { h = Math.max(5, h - step); moved = true; }
          if (e.key === 'ArrowDown') { h += step; moved = true; }
          if (e.key === 'ArrowLeft') { w = Math.max(5, w - step); moved = true; }
          if (e.key === 'ArrowRight') { w += step; moved = true; }
        } 
        // Normal Arrow = Nudge
        else {
          if (e.key === 'ArrowUp') { y -= step; moved = true; }
          if (e.key === 'ArrowDown') { y += step; moved = true; }
          if (e.key === 'ArrowLeft') { x -= step; moved = true; }
          if (e.key === 'ArrowRight') { x += step; moved = true; }
        }
        return { ...ann, x, y, w, h };
      }));

      if (moved) e.preventDefault();
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedId]);

  // --- File Uploads ---
  const handlePdfUpload = async (e) => {
    const file = e.target.files[0];
    if (!file || !window.pdfjsLib) return;
    const arrayBuffer = await file.arrayBuffer();
    const pdf = await window.pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    setPdfDoc(pdf);
    setNumPages(pdf.numPages);
    setCurrentPage(1);
    setAnnotations([]);
    setPageQuestions({});
  };

  const handleJsonUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const data = JSON.parse(event.target.result);
        if (Array.isArray(data)) {
          const formattedData = data.map(ann => ({
            id: ann.id || Date.now().toString() + Math.random(),
            page: ann.page || 1,
            x: ann.x || ann.bbox?.[0] || 0,
            y: ann.y || ann.bbox?.[1] || 0,
            w: ann.w || ann.bbox?.[2] || 100,
            h: ann.h || ann.bbox?.[3] || 100,
            questionId: ann.questionId || null,
            type: ann.type || 'text'
          }));
          setAnnotations(prev => [...prev, ...formattedData]);
        }
      } catch (err) { alert("Invalid JSON format."); }
    };
    reader.readAsText(file);
  };

  // --- Helpers ---
  const addPageQuestion = () => {
    if (!newQuestionLabel.trim()) return;
    const qList = pageQuestions[currentPage] || [];
    const color = QUESTION_COLORS[qList.length % QUESTION_COLORS.length];
    const newQ = { id: `q_${Date.now()}`, label: newQuestionLabel.trim(), color };
    
    setPageQuestions(prev => ({
      ...prev,
      [currentPage]: [...qList, newQ]
    }));
    setNewQuestionLabel('');
    setActiveQuestionId(newQ.id); // Auto select the new question
  };

  const updateAnnotation = (id, updates) => {
    setAnnotations(prev => prev.map(ann => ann.id === id ? { ...ann, ...updates } : ann));
  };

  const exportData = () => {
    // Reconstruct data, attaching actual question labels
    const exportData = annotations.map(ann => {
      const pageQs = pageQuestions[ann.page] || [];
      const q = pageQs.find(q => q.id === ann.questionId);
      return {
        id: ann.id,
        page: ann.page,
        bbox: [Math.round(ann.x), Math.round(ann.y), Math.round(ann.w), Math.round(ann.h)],
        label: q ? q.label : 'unassigned', // e.g., "1a"
        type: ann.type
      };
    });

    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportData, null, 2));
    const a = document.createElement('a');
    a.href = dataStr;
    a.download = "annotated_document.json";
    a.click();
  };

  const selectedAnnotation = annotations.find(ann => ann.id === selectedId);
  const currentQuestions = pageQuestions[currentPage] || [];

  return (
    <div className="flex h-screen bg-gray-50 text-gray-800 font-sans overflow-hidden">
      
      {/* --- Sidebar --- */}
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col z-10 flex-shrink-0">
        <div className="p-4 border-b border-gray-200">
          <h1 className="text-lg font-bold flex items-center gap-2">
            <Settings className="text-blue-600" size={20} />
            Doc Labeler
          </h1>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          
          {/* 1. Uploads */}
          <div className="space-y-2">
            <h2 className="text-xs font-bold text-gray-400 uppercase tracking-wider">1. Documents</h2>
            <div className="flex gap-2">
              <label className="flex-1 flex flex-col items-center justify-center p-3 border border-dashed border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50 text-xs font-medium">
                <Upload size={16} className="text-blue-500 mb-1" />
                Upload PDF
                <input type="file" accept="application/pdf" className="hidden" onChange={handlePdfUpload} disabled={!pdfJsLoaded} />
              </label>
              <label className="flex-1 flex flex-col items-center justify-center p-3 border border-dashed border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50 text-xs font-medium">
                <FileText size={16} className="text-emerald-500 mb-1" />
                Import JSON
                <input type="file" accept="application/json" className="hidden" onChange={handleJsonUpload} />
              </label>
            </div>
          </div>

          {/* 2. Page Questions (Tagging Workflow) */}
          <div className="space-y-3">
            <h2 className="text-xs font-bold text-gray-400 uppercase tracking-wider">2. Questions on Page {currentPage}</h2>
            
            <div className="flex gap-2">
              <input 
                type="text" 
                placeholder="e.g. Q1a" 
                className="flex-1 text-sm p-2 border border-gray-300 rounded focus:ring-1 focus:ring-blue-500"
                value={newQuestionLabel}
                onChange={(e) => setNewQuestionLabel(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && addPageQuestion()}
              />
              <button onClick={addPageQuestion} className="p-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                <Plus size={18} />
              </button>
            </div>

            <div className="space-y-1 mt-2">
              {currentQuestions.length === 0 ? (
                <p className="text-xs text-gray-400 italic">Add a question. Then select it and click lines on the PDF to tag them.</p>
              ) : (
                currentQuestions.map(q => (
                  <div 
                    key={q.id}
                    onClick={() => setActiveQuestionId(activeQuestionId === q.id ? null : q.id)}
                    className={`flex items-center gap-2 p-2 rounded cursor-pointer border transition-colors ${
                      activeQuestionId === q.id ? 'bg-blue-50 border-blue-300 shadow-sm' : 'border-transparent hover:bg-gray-50'
                    }`}
                  >
                    <div className="w-4 h-4 rounded-full border border-gray-200 shadow-sm" style={{ backgroundColor: q.color }}></div>
                    <span className="text-sm font-medium flex-1">{q.label}</span>
                    {activeQuestionId === q.id && <Tag size={14} className="text-blue-500" />}
                  </div>
                ))
              )}
            </div>
          </div>

          {/* 3. Selected Element */}
          <div className="space-y-3 pt-4 border-t border-gray-100">
            <h2 className="text-xs font-bold text-gray-400 uppercase tracking-wider">3. Selected Element</h2>
            {selectedAnnotation ? (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 space-y-4">
                
                {/* Element Type */}
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">Content Type</label>
                  <div className="flex bg-white rounded border border-gray-300 overflow-hidden">
                    {[
                      { id: 'text', icon: Type, label: 'Text' },
                      { id: 'image', icon: ImageIcon, label: 'Image' },
                      { id: 'table', icon: TableIcon, label: 'Table' }
                    ].map(type => (
                      <button
                        key={type.id}
                        onClick={() => updateAnnotation(selectedAnnotation.id, { type: type.id })}
                        className={`flex-1 flex flex-col items-center py-1.5 text-xs ${
                          selectedAnnotation.type === type.id ? 'bg-blue-100 text-blue-700 font-bold' : 'text-gray-500 hover:bg-gray-50'
                        }`}
                      >
                        <type.icon size={14} className="mb-0.5" />
                        {type.label}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="text-[10px] text-gray-500 space-y-1">
                  <p><strong>To Move:</strong> Drag box or Arrow Keys</p>
                  <p><strong>To Resize:</strong> Drag corners or Shift+Arrow Keys</p>
                </div>

                <button 
                  onClick={() => {
                    setAnnotations(prev => prev.filter(a => a.id !== selectedAnnotation.id));
                    setSelectedId(null);
                  }}
                  className="w-full flex items-center justify-center gap-1 text-xs text-red-600 bg-red-50 hover:bg-red-100 p-2 rounded border border-red-100"
                >
                  <Trash2 size={14}/> Delete Annotation
                </button>
              </div>
            ) : (
              <div className="text-xs text-gray-400 p-3 bg-gray-50 rounded border border-dashed border-gray-200">
                Click a bounding box to edit its type, resize, or delete it.
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200">
          <button
            onClick={exportData}
            disabled={annotations.length === 0}
            className={`w-full flex items-center justify-center gap-2 py-2.5 rounded-md font-medium text-sm transition-all ${
              annotations.length > 0 ? 'bg-gray-900 text-white hover:bg-gray-800' : 'bg-gray-200 text-gray-400'
            }`}
          >
            <Download size={16} /> Export JSON
          </button>
        </div>
      </div>

      {/* --- Main Workspace --- */}
      <div className="flex-1 flex flex-col min-w-0 bg-gray-100">
        
        {/* Top Toolbar */}
        <div className="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-4 shadow-sm z-10">
          <div className="flex bg-gray-100 p-1 rounded-md">
            <button 
              onClick={() => setToolMode('select')}
              className={`p-1.5 rounded flex items-center gap-1 text-sm ${toolMode === 'select' ? 'bg-white shadow text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
            >
              <MousePointer2 size={16} /> Select / Tag
            </button>
            <button 
              onClick={() => { setToolMode('draw'); setSelectedId(null); setActiveQuestionId(null); }}
              className={`p-1.5 rounded flex items-center gap-1 text-sm ${toolMode === 'draw' ? 'bg-white shadow text-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
            >
              <Crosshair size={16} /> Draw Box
            </button>
          </div>

          {/* Pagination */}
          {numPages > 0 && (
            <div className="flex items-center gap-3">
              <button 
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="p-1 rounded hover:bg-gray-100 disabled:opacity-50 text-gray-600"
              >
                <ChevronLeft size={20} />
              </button>
              <span className="text-sm font-medium text-gray-700">Page {currentPage} of {numPages}</span>
              <button 
                onClick={() => setCurrentPage(p => Math.min(numPages, p + 1))}
                disabled={currentPage === numPages}
                className="p-1 rounded hover:bg-gray-100 disabled:opacity-50 text-gray-600"
              >
                <ChevronRight size={20} />
              </button>
            </div>
          )}
        </div>

        {/* Canvas Area */}
        <div className="flex-1 overflow-auto p-8 flex justify-center items-start relative">
          {!pdfDoc ? (
             <div className="flex flex-col items-center justify-center h-full text-gray-400">
                <FileText size={64} className="opacity-20 mb-4" />
                <p>Upload a PDF to get started</p>
             </div>
          ) : (
            <div 
              ref={containerRef}
              className="relative shadow-2xl bg-white select-none"
              style={{ 
                cursor: toolMode === 'draw' ? 'crosshair' : 'default',
                width: bgCanvasRef.current ? bgCanvasRef.current.width : 'auto',
                height: bgCanvasRef.current ? bgCanvasRef.current.height : 'auto'
              }}
            >
              <canvas ref={bgCanvasRef} className="block pointer-events-none" />
              <canvas 
                ref={fgCanvasRef} 
                className="absolute top-0 left-0 outline-none" 
                tabIndex={0}
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
                onMouseLeave={handleMouseUp}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}


