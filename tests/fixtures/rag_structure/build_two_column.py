"""Rebuild the deterministic, synthetic two-column parser regression PDF.

Requires reportlab only for fixture authoring, NOT for running repository tests.
"""
from pathlib import Path
from textwrap import wrap
from reportlab.pdfgen.canvas import Canvas

path = Path(__file__).with_name('two_column.pdf')
c = Canvas(str(path), pagesize=(612, 792), invariant=1)
c.setTitle('Synthetic two-column security handbook')
c.setAuthor('Agent-forselftry test fixture')
c.setFont('Helvetica-Bold', 16)
c.drawString(48, 744, 'Two-column security handbook')


def paragraph(x, y, text):
    c.setFont('Helvetica', 11)
    for line in wrap(text, width=41):
        c.drawString(x, y, line)
        y -= 16
    return y - 16


for x, title in [(48, '1. Detection'), (318, '2. Response')]:
    c.setFont('Helvetica-Bold', 12)
    c.drawString(x, 704, title)
y = paragraph(48, 676, 'Repeated authentication failures are detection signals, not proof that any account was compromised. Record the source address and affected account before drawing an incident conclusion.')
y = paragraph(48, y, 'The following numbered items are operational steps, not new document sections.')
paragraph(48, y, '1. Check firewall configuration. 2. Collect authentication logs.')
y = paragraph(318, 676, 'Containment requires an explicit response decision. A recommendation to block a source is not evidence that a block has already been executed. Record any approval and verify the outcome.')
paragraph(318, y, 'Response recommendations must remain separate from observed event facts. No production commands are executed by this synthetic example.')
c.setFont('Helvetica', 8)
c.drawString(48, 36, 'Synthetic regression fixture. No real incident data. Two independent reading columns.')
c.showPage()
c.save()
print(path)
