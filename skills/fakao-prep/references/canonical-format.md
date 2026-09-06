# Canonical Markdown Format

The fakao web app imports either this canonical format or ordinary Markdown.

## File front matter

Optional YAML block at the top of the file:

```markdown
---
title: 刑法总论
source_file: 刑法讲义.pdf
page_start: 12
page_end: 15
chapter_path: ["第一章", "第一节"]
---
```

Fields:

- `title`: document/section title.
- `source_file`: original filename.
- `page_start`, `page_end`: optional page range.
- `chapter_path`: optional hierarchical path used when H1 headings alone are insufficient.

## Knowledge points

Each knowledge point is an H2 section. Add an HTML comment marker immediately before the H2 heading when source details differ from the file-level front matter:

```markdown
<!-- kp id="kp-01" page="12-13" confidence="high" -->
## 犯罪构成
> source: 刑法讲义.pdf p12-13
```

Supported marker attributes:

- `id`: stable identifier within the document.
- `page`: page number or `start-end` range.
- `confidence`: `high`, `medium`, or `low`.

The web app stores the first non-empty lines under each H2 as the source excerpt.
