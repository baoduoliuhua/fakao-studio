const BASE = '/api';

async function request(path, options = {}) {
  const response = await fetch(`${BASE}${path}`, {
    headers: options.body instanceof FormData ? undefined : { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `Request failed: ${response.status}`);
  }
  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    return response.json();
  }
  return response;
}

export const listProjects = () => request('/projects');
export const createProject = (name = '法考讲义项目') =>
  request('/projects', { method: 'POST', body: JSON.stringify({ name }) });
export const importMarkdown = (projectId, file) => {
  const form = new FormData();
  form.append('file', file);
  return request(`/projects/${projectId}/import`, { method: 'POST', body: form });
};
export const getOutline = (projectId) => request(`/projects/${projectId}/outline`);
export const clearProjectContent = (projectId) =>
  request(`/projects/${projectId}/content`, { method: 'DELETE' });
export const updateChapter = (chapterId, title) =>
  request(`/chapters/${chapterId}`, { method: 'PATCH', body: JSON.stringify({ title }) });
export const deleteChapter = (chapterId) =>
  request(`/chapters/${chapterId}`, { method: 'DELETE' });
export const getKnowledgePoint = (id) => request(`/knowledge-points/${id}`);
export const generateKnowledgePoint = (id) =>
  request(`/knowledge-points/${id}/generate`, { method: 'POST' });
export const regenerateKnowledgePoint = (id) =>
  request(`/knowledge-points/${id}/regenerate`, { method: 'POST' });
export const updateKnowledgePoint = (id, payload) =>
  request(`/knowledge-points/${id}`, { method: 'PATCH', body: JSON.stringify(payload) });
export const getSettings = () => request('/settings');
export const updateSettings = (payload) =>
  request('/settings', { method: 'PUT', body: JSON.stringify(payload) });
export const exportProject = (projectId, format = 'html') =>
  request(`/projects/${projectId}/export?format=${format}`);
