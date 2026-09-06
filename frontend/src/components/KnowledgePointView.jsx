import { useEffect, useState } from 'react';
import Diagram from './Diagram.jsx';
import { updateKnowledgePoint } from '../api.js';

export default function KnowledgePointView({
  knowledgePoint,
  generated,
  loading,
  onGenerate,
  onRegenerate,
  onUpdate,
}) {
  const [editTitle, setEditTitle] = useState(knowledgePoint.title);
  const [editBody, setEditBody] = useState(knowledgePoint.body_md);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    setEditTitle(knowledgePoint.title);
    setEditBody(knowledgePoint.body_md);
  }, [knowledgePoint]);

  async function saveEdits() {
    setSaving(true);
    setError('');
    try {
      const detail = await updateKnowledgePoint(knowledgePoint.id, {
        title: editTitle,
        body_md: editBody,
      });
      setEditing(false);
      onUpdate(detail);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <article className="kp-detail">
      <div className="kp-header">
        {editing ? (
          <input
            className="title-input"
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
          />
        ) : (
          <h1>{knowledgePoint.title}</h1>
        )}
        <div className="badges">
          {generated ? <span className="badge">已生成</span> : <span className="badge muted-badge">未生成</span>}
          {knowledgePoint.confidence === 'low' && <span className="badge warn">待审校</span>}
        </div>
        <div className="kp-actions">
          {generated ? (
            <button onClick={onRegenerate} disabled={loading}>重新生成</button>
          ) : (
            <button onClick={onGenerate} disabled={loading}>生成图示和解释</button>
          )}
          <button onClick={() => setEditing((v) => !v)}>
            {editing ? '完成' : '编辑标题'}
          </button>
          {editing && (
            <button onClick={saveEdits} disabled={saving}>保存修改</button>
          )}
        </div>
        {error && <div className="error">{error}</div>}
      </div>

      <section className="source-links">
        <h2>原文定位</h2>
        {knowledgePoint.source_refs?.map((ref, index) => (
          <div key={index} className="source-card">
            <strong>{ref.source_file || '来源文件'}</strong>
            {ref.page_start !== undefined && (
              <span> p{ref.page_start}-{ref.page_end}</span>
            )}
            <blockquote>{ref.excerpt}</blockquote>
          </div>
        ))}
      </section>

      <section className="body">
        <h2>原文</h2>
        {editing ? (
          <textarea
            className="body-input"
            value={editBody}
            onChange={(e) => setEditBody(e.target.value)}
            rows={10}
          />
        ) : (
          <pre>{knowledgePoint.body_md}</pre>
        )}
      </section>

      {knowledgePoint.artifact && (
        <section className="artifact">
          <h2>SVG 图示</h2>
          <Diagram artifact={knowledgePoint.artifact} title={knowledgePoint.title} />
          <h2>大白话解释</h2>
          <div className="explanation">{knowledgePoint.artifact.explanation}</div>
          {knowledgePoint.artifact.key_points?.length > 0 && (
            <>
              <h2>记忆要点</h2>
              <ul>
                {knowledgePoint.artifact.key_points.map((point) => (
                  <li key={point}>{point}</li>
                ))}
              </ul>
            </>
          )}
        </section>
      )}
    </article>
  );
}
