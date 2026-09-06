# 法考学习工具

一个本地运行的法考讲义学习工具：先用 `fakao-prep` Skill 把 PDF/Markdown 转成统一 Markdown，再导入 Web 应用，自动识别章节和知识点，为当前知识点生成 SVG 图示和大白话解释。

## 快速开始

```bash
scripts/setup.sh
scripts/start.sh
```

Windows 使用 `scripts\setup.bat` 和 `scripts\start.bat`。

打开 `http://127.0.0.1:5173`。默认是 Mock 模式；在右侧设置中填入 DeepSeek/OpenAI 兼容接口后关闭 Mock。

## 预处理 Skill

Skill 位于 `skills/fakao-prep`。用 Codex 运行：

```text
使用 fakao-prep 把 <输入文件> 转成统一 Markdown，输出到 <输出目录>
```

也可以直接执行：

```bash
python3 skills/fakao-prep/scripts/prepare.py 输入.pdf 输出目录
```

扫描版 PDF 需要安装 OCR 依赖，或使用支持图片输入的模型：

```bash
python3 skills/fakao-prep/scripts/prepare.py 输入.pdf 输出目录 \
  --base-url https://api.openai.com/v1 \
  --api-key sk-xxx \
  --vision-model gpt-4o-mini
```
