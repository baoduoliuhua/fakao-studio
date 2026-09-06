from __future__ import annotations

import html
from typing import Any


def build_html(project: Any, knowledge_points: list[Any]) -> str:
    cards = []
    for kp in knowledge_points:
        artifact = kp.artifact
        diagram_html = ""
        if artifact and artifact.diagram:
            diagram_html = _diagram_html(artifact.diagram)
        explanation = html.escape(artifact.explanation) if artifact else ""
        key_points = (
            "".join(f"<li>{html.escape(p)}</li>" for p in (artifact.key_points or []))
            if artifact
            else ""
        )
        source = "".join(
            f"<li>{html.escape(_format_source(s))}</li>" for s in (kp.source_refs or [])
        )
        cards.append(
            f"""
            <article class="card">
              <h2>{html.escape(kp.title)}</h2>
              <div class="diagram">{diagram_html}</div>
              <section class="explanation"><h3>大白话解释</h3><p>{explanation}</p></section>
              <section class="key-points"><h3>记忆要点</h3><ul>{key_points}</ul></section>
              <section class="source"><h3>原文定位</h3><ul>{source}</ul></section>
            </article>
            """
        )

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(project.name)}</title>
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 0; background: #f6f7fb; color: #1f2937; }}
    header {{ padding: 24px; background: #ffffff; border-bottom: 1px solid #e5e7eb; }}
    main {{ max-width: 980px; margin: 24px auto; padding: 0 16px; }}
    .card {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 24px; margin-bottom: 24px; }}
    .diagram {{ overflow-x: auto; }}
    .explanation {{ background: #f9fafb; border-radius: 10px; padding: 16px; line-height: 1.8; }}
    h2, h3 {{ margin-top: 0; }}
    ul {{ padding-left: 22px; }}
  </style>
</head>
<body>
  <header><h1>{html.escape(project.name)}</h1></header>
  <main>{"".join(cards)}</main>
  <script>mermaid.initialize({{ startOnLoad: true }});</script>
</body>
</html>"""


def build_pdf(project: Any, knowledge_points: list[Any]) -> bytes:
    html_content = build_html(project, knowledge_points)
    from weasyprint import HTML

    return HTML(string=html_content).write_pdf()


def _diagram_html(diagram: dict[str, Any]) -> str:
    kind = diagram.get("kind")
    if kind == "comparison":
        comparison = diagram.get("comparison") or {}
        headers = comparison.get("headers", [])
        rows = comparison.get("rows", [])
        head = "".join(f"<th>{html.escape(h)}</th>" for h in headers)
        body = "".join(
            "<tr>" + "".join(f"<td>{html.escape(c)}</td>" for c in row) + "</tr>"
            for row in rows
        )
        return f'<table border="1" cellpadding="8"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'
    mermaid = diagram.get("mermaid", "")
    return f'<div class="mermaid">{html.escape(mermaid)}</div>'


def _format_source(source: dict[str, Any]) -> str:
    parts = []
    if source.get("source_file"):
        parts.append(str(source["source_file"]))
    if source.get("page_start") is not None or source.get("page_end") is not None:
        parts.append(f"p{source.get('page_start', '?')}-{source.get('page_end', '?')}")
    if source.get("heading"):
        parts.append(str(source["heading"]))
    return " | ".join(parts)
