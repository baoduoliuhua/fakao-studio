export default function Outline({ chapters, knowledgePoints, selectedId, onSelect }) {
  const byChapter = (chapterId) =>
    knowledgePoints.filter((kp) => kp.chapter_id === chapterId);

  return (
    <section className="panel outline">
      <h2>章节目录</h2>
      {chapters.map((chapter) => (
        <div key={chapter.id} className="chapter-group">
          <div className="chapter-title">{chapter.title}</div>
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
      ))}
      {chapters.length === 0 && <div className="muted">暂无目录</div>}
    </section>
  );
}
