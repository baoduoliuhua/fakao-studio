import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  createProject,
  exportProject,
  generateKnowledgePoint,
  getKnowledgePoint,
  getOutline,
  getSettings,
  listProjects,
  regenerateKnowledgePoint,
  updateKnowledgePoint,
} from './api.js';
import ImportPanel from './components/ImportPanel.jsx';
import KnowledgePointView from './components/KnowledgePointView.jsx';
import Outline from './components/Outline.jsx';
import SettingsPanel from './components/SettingsPanel.jsx';

export default function App() {
  const [projects, setProjects] = useState([]);
  const [projectId, setProjectId] = useState(null);
  const [outline, setOutline] = useState({ chapters: [], knowledge_points: [] });
  const [selectedKp, setSelectedKp] = useState(null);
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const refreshProjects = useCallback(async () => {
    const data = await listProjects();
    setProjects(data);
    return data;
  }, []);

  useEffect(() => {
    getSettings().then(setSettings).catch((err) => setError(err.message));
    refreshProjects()
      .then(async (data) => {
        if (data.length > 0) {
          setProjectId(data[0].id);
        } else {
          const project = await createProject('法考讲义项目');
          setProjectId(project.id);
          setProjects([project]);
        }
      })
      .catch((err) => setError(err.message));
  }, [refreshProjects]);

  const refreshOutline = useCallback(async (id = projectId) => {
    if (!id) return;
    const data = await getOutline(id);
    setOutline(data);
    return data;
  }, [projectId]);

  useEffect(() => {
    if (projectId) {
      refreshOutline(projectId).catch((err) => setError(err.message));
    }
  }, [projectId, refreshOutline]);

  const openKnowledgePoint = useCallback(async (id) => {
    setError('');
    setLoading(true);
    try {
      const detail = await getKnowledgePoint(id);
      setSelectedKp(detail);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleGenerated = useCallback(async (detail) => {
    setSelectedKp(detail);
    await refreshOutline(projectId);
  }, [projectId, refreshOutline]);

  const handleGenerate = useCallback(async () => {
    if (!selectedKp) return;
    setLoading(true);
    try {
      const detail = await generateKnowledgePoint(selectedKp.id);
      await handleGenerated(detail);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [selectedKp, handleGenerated]);

  const handleRegenerate = useCallback(async () => {
    if (!selectedKp) return;
    setLoading(true);
    try {
      const detail = await regenerateKnowledgePoint(selectedKp.id);
      await handleGenerated(detail);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [selectedKp, handleGenerated]);

  const handleUpdate = useCallback((detail) => {
    setSelectedKp(detail);
  }, []);

  const handleExport = useCallback(async (format) => {
    if (!projectId) return;
    try {
      const response = await exportProject(projectId, format);
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `法考讲义.${format === 'pdf' ? 'pdf' : 'html'}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message);
    }
  }, [projectId]);

  const selectedSummary = useMemo(
    () => outline.knowledge_points.find((kp) => kp.id === selectedKp?.id),
    [outline.knowledge_points, selectedKp],
  );

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <strong>法考学习工具</strong>
          <span>结构化讲义 + 图示 + 大白话解释</span>
        </div>
        <div className="actions">
          <button onClick={() => handleExport('html')} disabled={!projectId}>导出 HTML</button>
          <button onClick={() => handleExport('pdf')} disabled={!projectId}>导出 PDF</button>
        </div>
      </header>
      {error && <div className="error">{error}</div>}
      <div className="layout">
        <aside className="sidebar">
          <ImportPanel
            projectId={projectId}
            onImported={async () => {
              await refreshOutline(projectId);
              await refreshProjects();
            }}
          />
          <Outline
            chapters={outline.chapters}
            knowledgePoints={outline.knowledge_points}
            selectedId={selectedKp?.id}
            onSelect={openKnowledgePoint}
          />
        </aside>
        <main className="content">
          {selectedKp ? (
            <KnowledgePointView
              knowledgePoint={selectedKp}
              generated={selectedSummary?.generated}
              loading={loading}
              onGenerate={handleGenerate}
              onRegenerate={handleRegenerate}
              onUpdate={handleUpdate}
            />
          ) : (
            <div className="empty">
              请先导入 Markdown 文件，然后从左侧选择一个知识点。
            </div>
          )}
        </main>
        <aside className="rightbar">
          <SettingsPanel settings={settings} onSaved={setSettings} />
        </aside>
      </div>
    </div>
  );
}
