import { useState } from 'react';

export default function Outline({ chapters, knowledgePoints, selectedId, onSelect }) {
  const [collapsedChapters, setCollapsedChapters] = useState(new Set());

  const byChapter = (chapterId) =>
    knowledgePoints.filter((kp) => kp.chapter_id === chapterId);

  function toggleChapter(chapterId) {
    setCollapsedChapters((prev) => {
      const next = new Set(prev);
      if (next.has(chapterId)) {
        next.delete(chapterId);
      } else {
        next.add(chapterId);
      }
      return next;
    });
  }

  return (
    <section className="panel outline">
      <h2>章节目录</h2>
      {chapters.map((chapter) => (
        <div key={chapter.id} className="chapter-group">
          <button className="chapter-title" onClick={() => toggleChapter(chapter.id)}>
            <span className="chevron">{collapsedChapters.has(chapter.id) ? '▸' : '▾'}</span>
            <span>{chapter.title}</span>
            <span className="chapter-count">{byChapter(chapter.id).length}</span>
          </button>
          {!collapsedChapters.has(chapter.id) && (
            <div className="kp-list">
              {byChapter(chapter.id).map((kp) => (
                <button
                  key={kp.id}
                  className={`kp-item ${selectedId === kp.id ? 'active' : ''}`}
                  onClick={() => onSelect(kp.id)}
                >
                  <span>{kp.title}</span>
                  {kp.generated && <span className="badge">已生成</span>}
                  {kp.confidence === 'low' && <span className="badge warn">待审校</span>}
                </button>
              ))}
            </div>
          )}
        </div>
      ))}
      {chapters.length === 0 && <div className="muted">暂无目录</div>}
    </section>
  );
}
