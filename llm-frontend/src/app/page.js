'use client';

import { useState, useEffect, useRef, useCallback, useTransition } from 'react';
import { v4 as uuidv4 } from 'uuid';
import SvgDisplay from './components/SvgDisplay';
import { isValidSvg } from './utils';

export default function HomePage() {
  const [githubLink, setGithubLink] = useState('');
  const [chatSessions, setChatSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const processingStateRef = useRef({
    isSending: false,
    requestNumber: 0
  });
  const [isPending, startTransition] = useTransition();
  const [apiError, setApiError] = useState(null);
  
  // Architecture diagram state
  const [architectureSvg, setArchitectureSvg] = useState(null);
  const [hasInitialRepo, setHasInitialRepo] = useState(false);
  
  // Navigation state for hierarchical architecture
  const [currentLevel, setCurrentLevel] = useState('overview'); // 'overview' or 'module'
  const [currentModule, setCurrentModule] = useState(null);
  const [navigationPath, setNavigationPath] = useState([]);
  const [repoLink, setRepoLink] = useState('');
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatSessions, currentSessionId]);

  useEffect(() => {
    setApiError(null);
  }, [currentSessionId]);

  const startNewSession = () => {
    const newId = uuidv4();
    setCurrentSessionId(newId);
    setChatSessions((prev) => [...prev, { id: newId, title: 'New Session', messages: [] }]);
    
    // Clear architecture data when starting a new session
    setHasInitialRepo(false);
    setArchitectureSvg(null);
    setCurrentLevel('overview');
    setCurrentModule(null);
    setNavigationPath([]);
    setRepoLink('');
  };

  // Function to handle drilling down into a module
  const handleDrillDown = useCallback(async (moduleName) => {
    console.log(`Drilling down into module: ${moduleName}`);
    
    if (!repoLink || processingStateRef.current.isSending) {
      return;
    }
    
    const requestNumber = processingStateRef.current.requestNumber + 1;
    processingStateRef.current.requestNumber = requestNumber;
    processingStateRef.current.isSending = true;
    
    setLoading(true);
    setApiError(null);
    
    // Update navigation state
    const newPath = [...navigationPath, moduleName];
    setNavigationPath(newPath);
    setCurrentLevel('module');
    setCurrentModule(moduleName);
    
    try {
      const payload = {
        github_link: repoLink,
        history: [],
        force_initial: false,
        drill_down_module: moduleName,
        current_path: newPath
      };
      
      const res = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      
      const data = await res.json();
      
      // Update architecture diagram with module-specific content
      if (data.svg && data.svg.trim() !== '') {
        if (isValidSvg(data.svg)) {
          setArchitectureSvg(data.svg);
        } else {
          setApiError('Invalid module diagram data.');
        }
      }
      
      // Add message to chat if we have a session
      if (currentSessionId) {
        const drillDownMsg = {
          role: 'assistant',
          content: data.text || `Showing detailed view of ${moduleName} module.`,
          svg: data.svg || '',
        };
        
        startTransition(() => {
          setChatSessions(prev => {
            const updated = [...prev];
            const index = updated.findIndex(s => s.id === currentSessionId);
            if (index !== -1) {
              updated[index] = {
                ...updated[index],
                messages: [...updated[index].messages, drillDownMsg]
              };
            }
            return updated;
          });
        });
      }
      
    } catch (err) {
      setApiError(`Failed to drill down into ${moduleName}: ${err.message}`);
      // Revert navigation state on error
      setNavigationPath(navigationPath);
      setCurrentLevel('overview');
      setCurrentModule(null);
    } finally {
      if (processingStateRef.current.requestNumber === requestNumber) {
        processingStateRef.current.isSending = false;
        setLoading(false);
      }
    }
  }, [repoLink, navigationPath, currentSessionId, startTransition]);

  // Function to go back to overview
  const handleBackToOverview = useCallback(async () => {
    console.log('Going back to overview');
    
    if (!repoLink || processingStateRef.current.isSending) {
      return;
    }
    
    const requestNumber = processingStateRef.current.requestNumber + 1;
    processingStateRef.current.requestNumber = requestNumber;
    processingStateRef.current.isSending = true;
    
    setLoading(true);
    setApiError(null);
    
    // Reset navigation state
    setNavigationPath([]);
    setCurrentLevel('overview');
    setCurrentModule(null);
    
    try {
      const payload = {
        github_link: repoLink,
        history: [],
        force_initial: true, // Force regeneration of overview
        current_path: []
      };
      
      const res = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      
      const data = await res.json();
      
      // Update architecture diagram with overview content
      if (data.svg && data.svg.trim() !== '') {
        if (isValidSvg(data.svg)) {
          setArchitectureSvg(data.svg);
        }
      }
      
    } catch (err) {
      setApiError(`Failed to return to overview: ${err.message}`);
    } finally {
      if (processingStateRef.current.requestNumber === requestNumber) {
        processingStateRef.current.isSending = false;
        setLoading(false);
      }
    }
  }, [repoLink, startTransition]);

  const handleSend = useCallback(async () => {
    setApiError(null);
    
    if (!githubLink.trim() || processingStateRef.current.isSending) {
      return;
    }
    
    const linkToSend = githubLink;
    const requestNumber = processingStateRef.current.requestNumber + 1;
    processingStateRef.current.requestNumber = requestNumber;
    processingStateRef.current.isSending = true;
    
    setLoading(true);
    setGithubLink('');
    
    let sessionId = currentSessionId;
    // If no session or repository not initialized yet
    const isInitialRequest = !hasInitialRepo;
    
    // Store repo link for navigation
    if (isInitialRequest) {
      setRepoLink(linkToSend);
    }
    
    if (!sessionId) {
      sessionId = uuidv4();
      startTransition(() => {
        setCurrentSessionId(sessionId);
        setChatSessions(prev => [...prev, { 
          id: sessionId, 
          title: linkToSend, 
          messages: [] 
        }]);
      });
    }
    
    const newMessage = { role: 'user', content: linkToSend };
    startTransition(() => {
      setChatSessions(prev => {
        const updated = [...prev];
        const index = updated.findIndex(s => s.id === sessionId);
        if (index !== -1) {
          updated[index] = {
            ...updated[index],
            messages: [...updated[index].messages, newMessage]
          };
        }
        return updated;
      });
    });
    
    try {
      if (processingStateRef.current.requestNumber !== requestNumber) {
        return;
      }
      
      const currentSession = chatSessions.find(s => s.id === sessionId);
      const history = currentSession ? [...currentSession.messages, newMessage] : [newMessage];
      
      // Add flag to force initial request
      const payload = { 
        github_link: linkToSend, 
        history,
        // Force as initial request when hasInitialRepo is false
        force_initial: isInitialRequest
      };
      
      const res = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      
      if (processingStateRef.current.requestNumber !== requestNumber) {
        return;
      }
      
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      
      const data = await res.json();
      
      // Update architecture diagram state with clearer conditions
      if (data.svg && data.svg.trim() !== '') {
        // Validate SVG before updating state
        if (isValidSvg(data.svg)) {
          setArchitectureSvg(data.svg);
          setHasInitialRepo(true);
        } else {
          setApiError('Invalid architecture diagram data. Please refresh the page or try a different repository link.');
        }
      } else if (isInitialRequest) {
        // If initial request but no SVG received, show error
        setApiError('Failed to generate architecture diagram. Please try another repository link.');
      }
      
      const assistantMsg = {
        role: 'assistant',
        content: data.text || 'No response received.',
        svg: data.svg || '',
      };
      
      startTransition(() => {
        setChatSessions(prev => {
          const updated = [...prev];
          const index = updated.findIndex(s => s.id === sessionId);
          if (index !== -1) {
            updated[index] = {
              ...updated[index],
              messages: [...updated[index].messages, assistantMsg]
            };
          }
          return updated;
        });
      });
      
    } catch (err) {
      setApiError(`Request failed: ${err.message}. Please check the backend is running.`);
    } finally {
      if (processingStateRef.current.requestNumber === requestNumber) {
        processingStateRef.current.isSending = false;
        setLoading(false);
      }
    }
  }, [githubLink, chatSessions, currentSessionId, hasInitialRepo, startTransition]);

  // Make drillDown function globally available
  useEffect(() => {
    window.drillDown = handleDrillDown;
    return () => {
      delete window.drillDown;
    };
  }, [handleDrillDown]);

  const currentMessages =
    chatSessions.find((s) => s.id === currentSessionId)?.messages || [];

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-800 text-white p-4 space-y-2 overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Sessions</h2>
          <button
            onClick={startNewSession}
            className="px-2 py-1 text-sm bg-blue-500 rounded hover:bg-blue-600"
          >
            + New
          </button>
        </div>
        {chatSessions.map((s) => (
          <button
            key={s.id}
            onClick={() => setCurrentSessionId(s.id)}
            className={`block w-full text-left p-2 rounded hover:bg-gray-700 ${
              s.id === currentSessionId ? 'bg-gray-700' : ''
            }`}
          >
            {s.title.length > 30 ? s.title.slice(0, 30) + '...' : s.title}
          </button>
        ))}
      </aside>

      {/* Main Content Area */}
      <div className="flex flex-col flex-1 bg-gray-100">
        <header className="p-4 bg-white shadow flex justify-between items-center">
          <span className="text-xl font-bold">🧠 GitHub Architecture Assistant</span>
        </header>

        {apiError && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded m-2">
            <p>{apiError}</p>
            <button 
              className="underline ml-2"
              onClick={() => setApiError(null)}
            >
              Dismiss
            </button>
          </div>
        )}

        {/* Architecture diagram area - always visible */}
        <div className="p-4 bg-white border-b border-gray-200">
          {hasInitialRepo && architectureSvg ? (
            <div className="architecture-diagram-container">
              {/* Navigation breadcrumb and controls */}
              <div className="flex justify-between items-center mb-2">
                <div className="flex items-center space-x-2">
                  <h2 className="text-lg font-semibold">
                    {currentLevel === 'overview' ? 'Project Architecture Diagram' : `Module: ${currentModule}`}
                  </h2>
                  {currentLevel === 'module' && (
                    <button
                      onClick={handleBackToOverview}
                      disabled={loading}
                      className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600 disabled:opacity-50"
                    >
                      ← Back to Overview
                    </button>
                  )}
                </div>
                <div className="text-sm text-gray-600">
                  {currentLevel === 'overview' ? 'Click modules to explore' : 'Detailed module view'}
                </div>
              </div>
              
              {/* Breadcrumb navigation */}
              {navigationPath.length > 0 && (
                <div className="mb-2 text-sm text-gray-600">
                  <span>Path: </span>
                  <span className="font-mono">
                    Project → {navigationPath.join(' → ')}
                  </span>
                </div>
              )}
              
              <div className="bg-gray-50 border border-gray-200 rounded p-3" style={{ minHeight: "300px" }}>
                <SvgDisplay 
                  svgContent={architectureSvg} 
                  className="w-full"
                  isArchitectureDiagram={true}
                  style={{ minHeight: "280px" }}
                />
              </div>
              <div className="flex justify-between mt-2">
                <span className="text-xs text-gray-500">
                  {architectureSvg ? `SVG size: ${architectureSvg.length} characters` : 'No architecture diagram'}
                </span>
                <span className="text-xs text-gray-500 italic">
                  {currentLevel === 'overview' 
                    ? 'Click on components to drill down into modules'
                    : 'Showing internal structure of the selected module'
                  }
                </span>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-10 text-center">
              <h2 className="text-xl font-semibold mb-3">Welcome to GitHub Architecture Assistant</h2>
              <p className="text-gray-600 mb-4">
                Enter a GitHub repository link below to generate a project architecture diagram
              </p>
              <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-gray-400 mb-4">
                <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
              </svg>
              <div className="flex items-center">
                <div className="arrow-down animate-bounce text-gray-400 text-4xl">↓</div>
              </div>
            </div>
          )}
        </div>

        {/* Chat area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {currentMessages.length === 0 && !hasInitialRepo && (
              <div className="text-center text-gray-500 mt-4">
                Enter a GitHub repository link to start a conversation
              </div>
            )}
            {currentMessages.map((msg, idx) => (
              <div
                key={idx}
                className={`max-w-xl p-3 rounded-lg whitespace-pre-line text-black ${
                  msg.role === 'user'
                    ? 'bg-blue-100 self-end ml-auto'
                    : 'bg-green-100 self-start mr-auto'
                }`}
              >
                <p>
                  <strong>{msg.role === 'user' ? 'You:' : 'Assistant:'}</strong>{' '}
                  {msg.content}
                </p>
                {/* Don't display SVG for subsequent messages */}
                {idx === 1 && msg.svg && msg.svg.trim() !== '' && !hasInitialRepo && (
                  <SvgDisplay 
                    svgContent={msg.svg} 
                    className="mt-4 border rounded bg-white p-2"
                  />
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          <div className="p-4 bg-white border-t flex gap-2">
            <input
              type="text"
              className="flex-1 border p-2 rounded shadow-sm"
              placeholder={hasInitialRepo ? "Enter your question..." : "Enter GitHub repository link..."}
              value={githubLink}
              onChange={(e) => setGithubLink(e.target.value)}
              disabled={loading}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
            />
            <button
              type="button"
              onClick={handleSend}
              disabled={loading || processingStateRef.current.isSending || isPending}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {loading || isPending ? 'Analyzing...' : 'Send'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
} 