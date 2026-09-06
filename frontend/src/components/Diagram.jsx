import { useEffect, useState } from 'react';
import mermaid from 'mermaid';

mermaid.initialize({ startOnLoad: false, theme: 'default' });

export default function Diagram({ artifact, title }) {
  const [svg, setSvg] = useState('');
  const [error, setError] = useState('');
  const diagram = artifact.diagram || {};

  useEffect(() => {
    if (!diagram || diagram.kind === 'comparison') {
      setSvg(renderComparisonSvg(diagram.comparison || {}, title));
      return;
    }
    if (!diagram.mermaid) {
      setError('图示数据为空');
      return;
    }
    const id = `mermaid-${artifact.id || Date.now()}`;
    mermaid
      .render(id, diagram.mermaid)
      .then((result) => setSvg(result.svg))
      .catch((err) => {
        setError(err.message);
        setSvg('');
      });
  }, [diagram, artifact.id, title]);

  function downloadSvg() {
    if (!svg) return;
    const blob = new Blob([svg], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title || 'diagram'}.svg`;
    a.click();
    URL.revokeObjectURL(url);
  }

  if (error) {
    return <div className="diagram-error">{error}</div>;
  }

  return (
    <div className="diagram-wrap">
      <div className="diagram-svg" dangerouslySetInnerHTML={{ __html: svg }} />
      {svg && <button onClick={downloadSvg}>下载 SVG</button>}
    </div>
  );
}

function renderComparisonSvg(comparison, title) {
  const headers = comparison.headers || ['对比项', 'A', 'B'];
  const rows = comparison.rows || [];
  const rowHeight = 42;
  const headerHeight = 50;
  const colWidths = headers.map((_, index) => (index === 0 ? 160 : 260));
  const width = colWidths.reduce((sum, value) => sum + value, 0);
  const height = headerHeight + rows.length * rowHeight;
  const escape = (value) =>
    String(value)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;');

  let rowsSvg = '';
  let x = 0;
  headers.forEach((header, index) => {
    rowsSvg += `<rect x="${x}" y="0" width="${colWidths[index]}" height="${headerHeight}" fill="#1f2937"/>
      <text x="${x + 12}" y="32" fill="#fff" font-size="16" font-family="sans-serif">${escape(header)}</text>`;
    x += colWidths[index];
  });

  rows.forEach((row, rowIndex) => {
    let cellX = 0;
    row.forEach((cell, colIndex) => {
      const y = headerHeight + rowIndex * rowHeight;
      rowsSvg += `<rect x="${cellX}" y="${y}" width="${colWidths[colIndex]}" height="${rowHeight}" fill="${rowIndex % 2 ? '#f3f4f6' : '#ffffff'}" stroke="#d1d5db"/>
        <text x="${cellX + 12}" y="${y + 28}" font-size="14" font-family="sans-serif">${escape(cell)}</text>`;
      cellX += colWidths[colIndex];
    });
  });

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" width="${width}" height="${height}">
    ${rowsSvg}
  </svg>`;
}
