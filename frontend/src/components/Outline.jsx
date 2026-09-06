import { useState } from 'react';

export default function Outline({
  chapters,
  knowledgePoints,
  selectedId,
  onSelect,
  onClear,
  onEditChapter,
  onDeleteChapter,
}) {
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
      <div className="outline-header">
        <h2>章节目录</h2>
        {chapters.length > 0 && (
          <button className="clear-button" onClick={onClear}>清空目录</button>
        )}
      </div>
      {chapters.map((chapter) => (
        <div key={chapter.id} className="chapter-group">
          <div className="chapter-row">
            <button className="chapter-title" onClick={() => toggleChapter(chapter.id)}>
              <span className="chevron">{collapsedChapters.has(chapter.id) ? '▸' : '▾'}</span>
              <span>{chapter.title}</span>
              <span className="chapter-count">{byChapter(chapter.id).length}</span>
            </button>
            <div className="chapter-actions">
              <button
                className="icon-button"
                title="修改章节"
                onClick={() => onEditChapter(chapter.id, chapter.title)}
              >
                改
              </button>
              <button
                className="icon-button danger"
                title="删除章节"
                onClick={() => onDeleteChapter(chapter.id)}
              >
                删
              </button>
            </div>
          </div>
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
