import { useRef, useState } from 'react';
import { importMarkdown } from '../api.js';

export default function ImportPanel({ projectId, onImported }) {
  const fileRef = useRef(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  async function handleUpload(event) {
    const file = event.target.files?.[0];
    if (!file || !projectId) return;
    setBusy(true);
    setError('');
    try {
      await importMarkdown(projectId, file);
      await onImported();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
      event.target.value = '';
    }
  }

  return (
    <section className="panel">
      <h2>导入讲义</h2>
      <p>支持统一 Markdown 或普通 Markdown。原始 PDF 请先用 fakao-prep Skill 转换。</p>
      <input
        ref={fileRef}
        type="file"
        accept=".md,.markdown,.txt,.pdf"
        onChange={handleUpload}
        disabled={busy || !projectId}
      />
      {busy && <div className="muted">导入中…</div>}
      {error && <div className="error">{error}</div>}
    </section>
  );
}
