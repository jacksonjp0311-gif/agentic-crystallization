"""Render the Markdown whitepaper as a readable PDF with ReportLab.

Math is shown as source LaTeX in a clearly marked, monospaced panel; the
Markdown source remains canonical for editable equations.
"""
from pathlib import Path
from reportlab.platypus import (SimpleDocTemplate,Paragraph,Spacer,Preformatted,Table,
                                TableStyle,Image,KeepTogether,PageBreak)
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER,TA_LEFT
from xml.sax.saxutils import escape
import re
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'docs/WHITE_PAPER.md'
DEST=ROOT/'Agentic_Crystallization_2.3.pdf'
style=getSampleStyleSheet()
style.add(ParagraphStyle(name='AC_Title',parent=style['Title'],fontName='Helvetica-Bold',fontSize=20,leading=25,spaceAfter=15,textColor=colors.HexColor('#153A53')))
style.add(ParagraphStyle(name='AC_Subtitle',parent=style['Normal'],fontSize=11,leading=16,spaceAfter=10,textColor=colors.HexColor('#516B7C')))
style.add(ParagraphStyle(name='AC_H1',parent=style['Heading1'],fontName='Helvetica-Bold',fontSize=13.2,leading=17,spaceBefore=13,spaceAfter=7,textColor=colors.HexColor('#145B79'),keepWithNext=True))
style.add(ParagraphStyle(name='AC_H2',parent=style['Heading2'],fontName='Helvetica-Bold',fontSize=11,leading=15,spaceBefore=10,spaceAfter=6,textColor=colors.HexColor('#145B79'),keepWithNext=True))
style.add(ParagraphStyle(name='AC_Body',parent=style['BodyText'],fontName='Helvetica',fontSize=8.9,leading=13.7,spaceAfter=7))
style.add(ParagraphStyle(name='AC_Small',parent=style['BodyText'],fontSize=7.4,leading=10.2,spaceAfter=5))
style.add(ParagraphStyle(name='AC_Table',parent=style['BodyText'],fontSize=6.6,leading=9.0))
style.add(ParagraphStyle(name='AC_Code',fontName='Courier',fontSize=7.5,leading=11,backColor=colors.HexColor('#EFF4F7'),leftIndent=8,spaceBefore=6,spaceAfter=7))
style.add(ParagraphStyle(name='AC_Quote',parent=style['BodyText'],leftIndent=15,spaceAfter=7,textColor=colors.HexColor('#234F6A')))


def clean(s):
    s=re.sub(r'\[([^\]]+)\]\([^\)]+\)',r'\1',s)
    s=escape(s)
    s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
    s=re.sub(r'`([^`]+)`',r'<font color="#245B73">\1</font>',s)
    return s


def foot(canvas,doc):
    canvas.saveState()
    w,h=doc.pagesize
    canvas.setStrokeColor(colors.HexColor('#B5C9D5'))
    canvas.line(42,38,w-42,38)
    canvas.setFont('Helvetica',7.2)
    canvas.setFillColor(colors.HexColor('#5B7383'))
    canvas.drawString(42,27,'AGENTIC CRYSTALLIZATION 2.3  |  Synthetic research / not a deployment guarantee')
    canvas.drawRightString(w-42,27,str(doc.page))
    canvas.restoreState()

story=[];lines=SRC.read_text(encoding='utf-8').splitlines();i=0
while i<len(lines):
    raw=lines[i];s=raw.strip()
    if not s:i+=1;continue
    if s.startswith('!['):
        match=re.match(r'!\[[^\]]*\]\(([^)]+)\)',s)
        if match:
            path=(SRC.parent/match.group(1)).resolve()
            if path.is_file():
                from PIL import Image as PILImage
                with PILImage.open(path) as im:
                    w,h=im.size
                width=min(490.,float(w));height=width*h/w
                story.append(Image(str(path),width=width,height=height))
        i+=1;continue
    if s.startswith('```'):
        code=[];i+=1
        while i<len(lines) and not lines[i].strip().startswith('```'):
            code.append(lines[i]);i+=1
        if code:story.append(Preformatted('\n'.join(code),style['AC_Code'],maxLineLength=100,splitChars=' '))
        i+=1;continue
    if s.startswith('\\[') or s.startswith('$$'):
        closing='\\]' if s.startswith('\\[') else '$$'
        eq=[];i+=1
        while i<len(lines) and not lines[i].strip().startswith(closing):
            eq.append(lines[i].strip());i+=1
        text=' '.join(eq)
        # Source LaTeX is kept intact for readers and cross-checking.
        story.append(Preformatted(text,style['AC_Code'],maxLineLength=92,splitChars=' '))
        i+=1;continue
    if s.startswith('|'):
        table=[]
        while i<len(lines) and lines[i].strip().startswith('|'):
            row=lines[i].strip()
            if not re.fullmatch(r'[\|\-\:\s]+',row):
                table.append([v.strip() for v in row.strip('|').split('|')])
            i+=1
        if table:
            n=max(map(len,table));width=528/n
            data=[]
            for row in table:
                data.append([Paragraph(clean(c),style['AC_Table']) for c in row]+['']*(n-len(row)))
            t=Table(data,colWidths=[width]*n,repeatRows=1,hAlign='LEFT')
            t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#DCE9F0')),
                ('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#4D7A94')),
                ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F7FAFC')]),
                ('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),
                ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
            story.append(t);story.append(Spacer(1,8))
        continue
    if s.startswith('# '):story.append(Paragraph(clean(s[2:]),style['AC_Title']))
    elif s.startswith('## '):story.append(Paragraph(clean(s[3:]),style['AC_H1']))
    elif s.startswith('### '):story.append(Paragraph(clean(s[4:]),style['AC_H2']))
    elif s.startswith('- '):story.append(Paragraph('&#8226; '+clean(s[2:]),style['AC_Body']))
    elif s.startswith('> '):story.append(Paragraph(clean(s[2:]),style['AC_Quote']))
    else:story.append(Paragraph(clean(s),style['AC_Body']))
    i+=1

pdf=SimpleDocTemplate(str(DEST),pagesize=(612,792),leftMargin=42,rightMargin=42,topMargin=40,bottomMargin=49,
                      title='Agentic Crystallization v2.3 — Feedback Integrity',author='Agentic Crystallization Research')
pdf.build(story,onFirstPage=foot,onLaterPages=foot)
print(DEST,DEST.stat().st_size)
