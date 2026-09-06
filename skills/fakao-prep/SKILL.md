---
name: fakao-prep
description: Convert law-exam PDF or Markdown study materials into a canonical Markdown format for the fakao learning tool. Use when preparing a textbook, lecture note, or study document for import into that tool.
---

# Fakao Prep

Convert a source PDF or Markdown file into the canonical Markdown accepted by the fakao learning tool. Do not generate diagrams, explanations, or study content here; this skill only cleans, structures, and adds source citations.

## Workflow

1. Confirm the input path and output directory. Do not overwrite the source file.
2. Run the deterministic converter:

```bash
python3 scripts/prepare.py <input> <output_dir>
```

3. Read the generated Markdown and the canonical format guide at [references/canonical-format.md](references/canonical-format.md). Fix obvious chapter and knowledge-point boundary errors caused by PDF layout or OCR noise.
4. Ensure every knowledge point keeps a `kp` source marker or inherited front matter with page numbers, and that headings match the hierarchy in the source material.
5. If the input is a scanned PDF and the converter cannot recover text, use an available vision model or OCR tool to produce page text, then rerun the converter or repair the output manually.
6. Write the final file as `<output_dir>/<source_stem>.md` and do not modify the source file.

## Rules

- Prefer deterministic extraction first; use AI only to correct missing or broken structure.
- Preserve Chinese legal terms and section numbering exactly.
- Keep one knowledge point per H2 section unless the source clearly requires otherwise.
- Include `page_start`/`page_end` when available. For Markdown without page numbers, use heading/line references instead.
- Mark uncertain boundaries with `confidence="low"` so the web app can surface them for review.
