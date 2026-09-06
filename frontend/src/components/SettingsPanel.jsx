import { useEffect, useState } from 'react';
import { updateSettings } from '../api.js';

export default function SettingsPanel({ settings, onSaved }) {
  const [form, setForm] = useState({
    mock: settings?.mock ?? true,
    base_url: settings?.base_url || 'https://api.deepseek.com/v1',
    api_key: '',
    model: settings?.model || 'deepseek-chat',
  });
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!settings) return;
    setForm({
      mock: settings.mock,
      base_url: settings.base_url,
      api_key: '',
      model: settings.model,
    });
  }, [settings]);

  if (!settings) return <section className="panel"><h2>AI 设置</h2><p>加载中…</p></section>;

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    try {
      const data = await updateSettings({
        mock: form.mock,
        base_url: form.base_url,
        model: form.model,
        api_key: form.api_key || undefined,
      });
      onSaved(data);
      setForm((prev) => ({ ...prev, api_key: '' }));
      setSaved(true);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="panel">
      <h2>AI 设置</h2>
      <form onSubmit={handleSubmit}>
        <label>
          <input
            type="checkbox"
            checked={form.mock}
            onChange={(e) => setForm({ ...form, mock: e.target.checked })}
          />
          Mock 模式
        </label>
        <label>
          Base URL
          <input
            value={form.base_url}
            onChange={(e) => setForm({ ...form, base_url: e.target.value })}
            placeholder="https://api.deepseek.com/v1"
          />
        </label>
        <label>
          API Key
          <input
            type="password"
            value={form.api_key}
            onChange={(e) => setForm({ ...form, api_key: e.target.value })}
            placeholder={settings.api_key_set ? '已保存，留空则不修改' : '请输入 Key'}
          />
        </label>
        <label>
          模型
          <input
            value={form.model}
            onChange={(e) => setForm({ ...form, model: e.target.value })}
            placeholder="deepseek-chat"
          />
        </label>
        <button type="submit">保存设置</button>
        {saved && <div className="muted">已保存</div>}
        {error && <div className="error">{error}</div>}
      </form>
    </section>
  );
}
