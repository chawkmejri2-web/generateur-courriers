"""Export DOCX avec python-docx."""
from io import BytesIO
from docx import Document
from docx.shared import Pt, Cm


def to_docx(text):
    doc = Document()
    for s in doc.sections:
        s.top_margin = s.bottom_margin = Cm(2.5)
        s.left_margin = s.right_margin = Cm(2.5)
    st = doc.styles["Normal"]
    st.font.name = "Times New Roman"
    st.font.size = Pt(12)
    for block in text.strip().split("\n\n"):
        p = doc.add_paragraph()
        lines = block.split("\n")
        for i, line in enumerate(lines):
            run = p.add_run(line)
            if line.startswith("Objet :"):
                run.bold = True
            if i < len(lines) - 1:
                run.add_break()
        p.paragraph_format.space_after = Pt(10)
    buf = BytesIO()
    doc.save(buf)
    return buf.getvalue()