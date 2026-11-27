"""Create an editable local declaration; this does not complete Elsevier's declarations tool."""
from pathlib import Path
import re
from docx import Document
from docx.shared import Inches, Pt

HERE = Path(__file__).resolve().parent


def main():
    meta = (HERE.parents[1] / "content/meta.tex").read_text()
    title = re.search(r"\\newcommand\{\\papertitle\}\{([^}]+)\}", meta)
    if title is None:
        raise ValueError("Manuscript title not found in content/meta.tex")
    statement = (HERE / "competing_interests.txt").read_text().strip()
    if statement != "The author declares no competing interests.":
        raise ValueError("Review the changed declaration before generating the DOCX")
    document = Document()
    for section in document.sections:
        section.top_margin = section.bottom_margin = Inches(1)
    document.styles["Normal"].font.name = "Arial"
    document.styles["Normal"].font.size = Pt(11)
    document.add_heading("Declaration of competing interest", level=0)
    document.add_paragraph(title.group(1))
    document.add_paragraph("Hossein Mohasel Arjomandi")
    document.add_paragraph(statement)
    document.core_properties.title = "Declaration of competing interest"
    document.core_properties.author = "Hossein Mohasel Arjomandi"
    target = HERE / "competing_interests.docx"
    document.save(target)
    actual = [p.text for p in Document(target).paragraphs]
    expected = ["Declaration of competing interest", title.group(1), "Hossein Mohasel Arjomandi", statement]
    if actual != expected:
        raise ValueError("DOCX text does not match its sources")
    print(f"{target.name}: editable local declaration; Elsevier tool completion still required")
    items = (HERE / "highlights.txt").read_text().splitlines()
    if not 3 <= len(items) <= 5 or any(len(item) > 85 for item in items):
        raise ValueError("Highlights must contain 3-5 bullets of at most 85 characters")
    highlights = Document()
    highlights.core_properties.title = "Highlights"
    highlights.core_properties.author = "Hossein Mohasel Arjomandi"
    for item in items:
        highlights.add_paragraph(item, style="List Bullet")
    highlights.save(HERE / "highlights.docx")
    if [p.text for p in Document(HERE / "highlights.docx").paragraphs] != items:
        raise ValueError("Highlights DOCX differs from the editable text source")
    print("highlights.docx: editable Word highlights verified")


if __name__ == "__main__":
    main()
