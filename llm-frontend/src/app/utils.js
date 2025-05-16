/**
 * 处理SVG相关的工具函数
 */

/**
 * 创建SVG URL对象
 * @param {string} svgContent - SVG内容字符串
 * @returns {string} - 创建的blob URL
 */
export function createSvgUrl(svgContent) {
  if (!svgContent) return null;
  const blob = new Blob([svgContent], { type: 'image/svg+xml' });
  return URL.createObjectURL(blob);
}

/**
 * 清理SVG URL对象
 * @param {string} url - 要清理的URL对象
 */
export function cleanupSvgUrl(url) {
  if (url) {
    URL.revokeObjectURL(url);
  }
}

/**
 * 验证字符串是否是有效的SVG
 * @param {string} content - 要验证的SVG内容
 * @returns {boolean} - 是否有效
 */
export function isValidSvg(content) {
  if (!content) return false;

  // 验证SVG基本格式
  const hasSvgTags = content.includes('<svg') && content.includes('</svg>');
  const hasDoctype = content.includes('<!DOCTYPE svg') || content.includes('<?xml');

  // 检查是否包含关键属性
  const hasXmlns = content.includes('xmlns="http://www.w3.org/2000/svg"');

  return (hasSvgTags || hasDoctype) && hasXmlns;
}

/**
 * 转义HTML内容
 * @param {string} unsafe - 不安全的HTML内容
 * @returns {string} - 转义后的内容
 */
export function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

/**
 * 从GitHub URL中提取仓库名
 * @param {string} url - GitHub URL
 * @returns {string} - 仓库名称
 */
export function extractRepoName(url) {
  if (!url) return '';
  try {
    // 移除 .git 后缀
    const urlWithoutGit = url.replace(/\.git$/, '');
    // 分割URL并获取最后一部分
    const parts = urlWithoutGit.split('/');
    return parts[parts.length - 1] || '';
  } catch (e) {
    console.error('Error extracting repo name:', e);
    return '';
  }
} 