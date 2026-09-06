from app.services.markdown_parser import parse_markdown


def test_plain_markdown_headings():
    content = "# 第一章\n\n## 知识点一\n正文一\n\n## 知识点二\n正文二\n"
    parsed = parse_markdown(content, "讲义.md")
    assert len(parsed.chapters) == 1
    assert [kp.title for kp in parsed.knowledge_points] == ["知识点一", "知识点二"]


def test_canonical_front_matter_and_marker():
    content = """---
title: 刑法总论
source_file: 刑法讲义.pdf
page_start: 12
page_end: 15
---

# 第一章

<!-- kp id="kp-01" page="12-13" confidence="high" -->
## 犯罪构成
> source: 刑法讲义.pdf p12-13
犯罪构成包括主体、行为、结果。
"""
    parsed = parse_markdown(content, "统一.md")
    assert parsed.source_file == "刑法讲义.pdf"
    assert parsed.page_start == 12
    assert parsed.knowledge_points[0].source_refs[0]["page_start"] == 12
    assert parsed.knowledge_points[0].source_refs[0]["page_end"] == 13
