from __future__ import annotations

import json
import re
from typing import Any

from .settings import get_settings


SYSTEM_PROMPT = """
你是法考助教。请根据给定的知识点，用中文生成一个 SVG 学习卡片所需的结构化内容。

只返回合法 JSON，不要使用 Markdown 代码块。JSON 必须包含：
- diagram: 对象，包含 kind（flowchart|mindmap|timeline|comparison）。
  - 当 kind 是 flowchart/mindmap/timeline 时，给出 mermaid 字符串。
  - 当 kind 是 comparison 时，给出 comparison 对象：{"headers":["对比项","A","B"],"rows":[["维度","...","..."]]}。
- explanation: 用大白话、口语化地解释这个知识点，避免法言法语堆砌。
- key_points: 3 到 5 个便于记忆的要点。
- source_citations: 从给定来源中摘出的原句，若没有则返回空数组。

图示必须紧扣知识点，不要生成与知识点无关的节点。
""".strip()


def generate_for_knowledge_point(knowledge_point: Any) -> dict[str, Any]:
    settings = get_settings()
    if settings.get("mock") or not settings.get("api_key"):
        return _mock_result(knowledge_point)

    prompt = _build_prompt(knowledge_point)
    try:
        result = _call_model(settings, prompt)
        return _validate_result(result, knowledge_point)
    except Exception:
        try:
            result = _call_model(settings, prompt, retry=True)
            return _validate_result(result, knowledge_point)
        except Exception:
            fallback = _mock_result(knowledge_point)
            fallback["explanation"] = (
                "AI 生成失败，已返回备用内容。请检查接口配置后重试。\n\n" + fallback["explanation"]
            )
            return fallback


def _build_prompt(knowledge_point: Any) -> str:
    source = knowledge_point.body_md or ""
    source_refs = knowledge_point.source_refs or []
    return (
        f"知识点标题：{knowledge_point.title}\n"
        f"知识点原文：\n{source[:4000]}\n\n"
        f"来源引用：{json.dumps(source_refs, ensure_ascii=False)}"
    )


def _call_model(settings: dict, prompt: str, retry: bool = False) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=settings["api_key"], base_url=settings["base_url"] or None)
    kwargs: dict[str, Any] = {
        "model": settings.get("model", "deepseek-chat"),
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt + ("\n请只返回合法 JSON。" if retry else "")},
        ],
        "temperature": 0.3,
    }
    if not retry:
        kwargs["response_format"] = {"type": "json_object"}
    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content or ""


def _validate_result(raw: str, knowledge_point: Any) -> dict[str, Any]:
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.MULTILINE)
    data = json.loads(cleaned)
    if not isinstance(data, dict):
        raise ValueError("result is not an object")
    if "explanation" not in data or "diagram" not in data:
        raise ValueError("missing explanation or diagram")
    diagram = data.get("diagram") or {}
    kind = diagram.get("kind")
    if kind not in {"flowchart", "mindmap", "timeline", "comparison"}:
        raise ValueError("unsupported diagram kind")
    if kind == "comparison" and not isinstance(diagram.get("comparison"), dict):
        raise ValueError("comparison is invalid")
    if kind != "comparison" and not isinstance(diagram.get("mermaid"), str):
        raise ValueError("mermaid is missing")
    data["source_citations"] = data.get("source_citations") or []
    data["key_points"] = data.get("key_points") or []
    return data


def _mock_result(knowledge_point: Any) -> dict[str, Any]:
    title = knowledge_point.title or "知识点"
    source = knowledge_point.source_refs or []
    return {
        "diagram": {
            "kind": "flowchart",
            "mermaid": (
                "flowchart TD\n"
                f"  A[\"{title}\"] --> B[\"核心概念\"]\n"
                "  B --> C[\"构成要件\"]\n"
                "  C --> D[\"法律后果\"]"
            ),
            "comparison": None,
        },
        "explanation": f"（Mock 模式）{title} 的核心是先把概念拆开理解，再记住它需要满足哪些条件，最后落到法律后果上。",
        "key_points": ["概念拆解", "构成要件", "法律后果"],
        "source_citations": [
            {"page_start": item.get("page_start"), "quote": item.get("excerpt", "")[:120]}
            for item in source[:2]
        ],
    }
