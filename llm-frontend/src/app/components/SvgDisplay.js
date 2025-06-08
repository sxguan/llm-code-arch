'use client';

import { useState, useEffect, useRef, memo, useCallback } from 'react';
import { createSvgUrl, isValidSvg, cleanupSvgUrl } from '../utils';

/**
 * Component for safely displaying SVG content
 * 
 * @param {Object} props - Component props
 * @param {string} props.svgContent - SVG content as a string
 * @param {string} props.className - Additional CSS classes
 * @param {Object} props.style - Additional inline styles
 * @param {boolean} props.isArchitectureDiagram - Whether this is the main architecture diagram
 */
function SvgDisplay({ svgContent, className, style, isArchitectureDiagram = false }) {
  const [svgUrl, setSvgUrl] = useState(null);
  const [error, setError] = useState(null);
  const [renderMethod, setRenderMethod] = useState('object'); // 'object', 'img', or 'inline'
  const [zoomLevel, setZoomLevel] = useState(1.0); // Zoom scale factor
  const containerRef = useRef(null);
  const objectRef = useRef(null);

  // Zoom functions
  const handleZoomIn = () => {
    const newZoom = Math.min(zoomLevel * 1.2, 3.0); // Max zoom 3x
    setZoomLevel(newZoom);
  };

  const handleZoomOut = () => {
    const newZoom = Math.max(zoomLevel / 1.2, 0.3); // Min zoom 0.3x
    setZoomLevel(newZoom);
  };

  const handleResetZoom = () => {
    setZoomLevel(1.0);
  };

  // Handle mouse wheel zoom
  const handleWheel = useCallback((e) => {
    if (isArchitectureDiagram && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      const delta = e.deltaY > 0 ? 0.9 : 1.1;
      const newZoom = Math.max(0.3, Math.min(3.0, zoomLevel * delta));
      setZoomLevel(newZoom);
    }
  }, [zoomLevel, isArchitectureDiagram]);
  
  // 添加调试日志
  useEffect(() => {
    console.log('SvgDisplay received svgContent:', {
      hasContent: !!svgContent,
      length: svgContent ? svgContent.length : 0,
      isValid: isValidSvg(svgContent),
      isArchitectureDiagram,
      preview: svgContent ? svgContent.substring(0, 100) + '...' : 'none'
    });
    
    // 如果前面的SVG渲染失败，尝试切换渲染方法
    if (error && svgContent) {
      const nextMethod = renderMethod === 'object' ? 'img' : 
                         renderMethod === 'img' ? 'inline' : 'object';
      console.log(`Switching render method from ${renderMethod} to ${nextMethod} due to error`);
      setRenderMethod(nextMethod);
    }
  }, [svgContent, error, renderMethod, isArchitectureDiagram]);

  // 处理SVG URL创建
  useEffect(() => {
    // 清理之前的URL
    if (svgUrl) {
      cleanupSvgUrl(svgUrl);
    }

    if (!svgContent) {
      setError('No SVG content provided');
      setSvgUrl(null);
      return;
    }
    
    try {
      // 检查是否需要编码修复
      let processedSvg = svgContent;
      
      // 确保SVG内容是UTF-8编码
      if (!svgContent.includes('<?xml') && !svgContent.includes('encoding=')) {
        processedSvg = `<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n${processedSvg}`;
      }
      
      // 检查并确保内容是有效的SVG
      if (!isValidSvg(processedSvg)) {
        console.warn('SVG validation failed, attempting content fix');
        
        // 尝试修复一些常见的SVG格式问题
        if (!processedSvg.includes('<svg')) {
          // 如果没有svg标签，尝试创建一个基本的svg
          processedSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600">
            <text x="50" y="50" font-size="20" fill="red">SVG内容无效，无法显示</text>
          </svg>`;
        } else if (!processedSvg.includes('xmlns=')) {
          // 如果缺少xmlns属性，添加它
          processedSvg = processedSvg.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"');
        }
      }
      
      // 创建SVG URL
      const url = createSvgUrl(processedSvg);
      console.log('Created SVG URL:', !!url);
      setSvgUrl(url);
      setError(null);
    } catch (err) {
      console.error('Error creating SVG URL:', err);
      setError(`Failed to create SVG URL: ${err.message}`);
    }

    // 清理函数
    return () => {
      if (svgUrl) {
        cleanupSvgUrl(svgUrl);
      }
    };
  }, [svgContent]);

  // 监听object加载错误
  useEffect(() => {
    if (renderMethod === 'object' && objectRef.current) {
      const handleError = () => {
        console.error('SVG object failed to load');
        setError('SVG object failed to load');
        // 尝试切换到图片渲染
        setRenderMethod('img');
      };
      
      objectRef.current.addEventListener('error', handleError);
      return () => {
        if (objectRef.current) {
          objectRef.current.removeEventListener('error', handleError);
        }
      };
    }
  }, [renderMethod, objectRef.current]);

  // 错误状态渲染
  if (error && renderMethod === 'inline') {
    // 当所有方法都失败时，尝试直接插入SVG内容
    return (
      <div className={`svg-container relative ${className || ''} ${isArchitectureDiagram ? 'architecture-svg' : ''}`} style={style}>
        {renderZoomControls}
        <div 
          className="svg-wrapper overflow-auto border border-gray-200 rounded"
          style={{ 
            minHeight: isArchitectureDiagram ? '280px' : '300px',
            maxHeight: '600px'
          }}
          onWheel={handleWheel}
        >
          <div
            style={{
              transform: `scale(${zoomLevel})`,
              transformOrigin: 'top left',
              transition: 'transform 0.2s ease-in-out'
            }}
            dangerouslySetInnerHTML={{ __html: svgContent }}
          />
        </div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className={`svg-error ${className || ''}`} style={style}>
        <p>Error: {error}</p>
        <p>SVG Content Preview: {svgContent ? svgContent.substring(0, 100) + '...' : 'none'}</p>
        <button 
          onClick={() => setRenderMethod(renderMethod === 'object' ? 'img' : 'inline')}
          className="px-2 py-1 mt-2 text-xs bg-blue-500 text-white rounded"
        >
          Try alternate render method
        </button>
      </div>
    );
  }

  if (!svgUrl) {
    return (
      <div className={`svg-loading ${className || ''}`} style={style}>
        <p>Loading SVG...</p>
      </div>
    );
  }

  // 为架构图添加控制功能
  const renderZoomControls = isArchitectureDiagram && (
    <div className="absolute top-2 right-2 bg-white bg-opacity-90 rounded p-1 flex flex-col space-y-1 shadow-md">
      <div className="flex space-x-1">
        <button 
          onClick={handleZoomOut}
          disabled={zoomLevel <= 0.3}
          className="p-1 bg-gray-200 rounded hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
          title="Zoom Out"
        >
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          <line x1="8" y1="11" x2="14" y2="11"></line>
        </svg>
      </button>
      <button 
        onClick={handleResetZoom}
        className="px-2 py-1 bg-gray-200 rounded hover:bg-gray-300 text-xs font-mono"
        title="Reset Zoom"
      >
        {Math.round(zoomLevel * 100)}%
      </button>
      <button 
        onClick={handleZoomIn}
        disabled={zoomLevel >= 3.0}
        className="p-1 bg-gray-200 rounded hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
        title="Zoom In"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          <line x1="11" y1="8" x2="11" y2="14"></line>
          <line x1="8" y1="11" x2="14" y2="11"></line>
        </svg>
      </button>
      </div>
      <div className="text-xs text-gray-500 text-center px-1" title="Hold Ctrl/Cmd + scroll to zoom">
        Ctrl+scroll
      </div>
    </div>
  );

  // 根据渲染方法选择不同的渲染策略
  if (renderMethod === 'img') {
    return (
      <div className={`svg-container relative ${className || ''} ${isArchitectureDiagram ? 'architecture-svg' : ''}`} ref={containerRef} style={style}>
        {renderZoomControls}
        <div 
          className="svg-wrapper overflow-auto border border-gray-200 rounded"
          style={{ 
            minHeight: isArchitectureDiagram ? '280px' : '300px',
            maxHeight: '600px'
          }}
          onWheel={handleWheel}
        >
          <img
            src={svgUrl}
            alt="Architecture Diagram"
            className="svg-image"
            style={{ 
              width: '100%',
              minHeight: isArchitectureDiagram ? '280px' : '300px',
              transform: `scale(${zoomLevel})`,
              transformOrigin: 'top left',
              transition: 'transform 0.2s ease-in-out'
            }}
            onError={() => {
              console.error('SVG image failed to load');
              setError('SVG image failed to load');
              setRenderMethod('inline');
            }}
          />
        </div>
      </div>
    );
  }
  
  // 默认使用object渲染
  return (
    <div className={`svg-container relative ${className || ''} ${isArchitectureDiagram ? 'architecture-svg' : ''}`} ref={containerRef} style={style}>
      {renderZoomControls}
      <div 
        className="svg-wrapper overflow-auto border border-gray-200 rounded"
        style={{ 
          minHeight: isArchitectureDiagram ? '280px' : '300px',
          maxHeight: '600px'
        }}
      >
        <object
          ref={objectRef}
          type="image/svg+xml"
          data={svgUrl}
          className="svg-object"
          width="100%"
          style={{ 
            minHeight: isArchitectureDiagram ? '280px' : '300px',
            transform: `scale(${zoomLevel})`,
            transformOrigin: 'top left',
            transition: 'transform 0.2s ease-in-out'
          }}
        >
          <p>Your browser cannot display this SVG.</p>
        </object>
      </div>
    </div>
  );
}

// Memoize the component to prevent unnecessary rerenders
export default memo(SvgDisplay); 