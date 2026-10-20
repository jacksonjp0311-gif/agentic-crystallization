"""Build v2.4 complete PDF with real LaTeX mathematics via Pandoc + XeLaTeX.

Run from an extracted source tree. Rebuilding may differ in PDF metadata bytes.
Requires local pandoc, xelatex, and DejaVu fonts; never distributes fonts.
"""
from pathlib import Path
import subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
parts=[ROOT/'docs/WHITE_PAPER.md',ROOT/'docs/MATHEMATICS_2.4.md',
       ROOT/'docs/ALGORITHM_CARD_2.4.md']
front='''---
title: "Agentic Crystallization v2.4"
subtitle: "Independent Verification, Adaptive Trust, and Mathematical Cooling"
author: "Agentic Crystallization Research"
date: "October 2026"
---

![Agentic Crystallization](assets/crystal_banner.png)

\\newpage

'''
md=front+'\n\n\\newpage\n\n'.join(p.read_text(encoding='utf-8') for p in parts)
with tempfile.TemporaryDirectory() as td:
    src=Path(td)/'complete_paper.md'
    src.write_text(md,encoding='utf-8')
    cmd=['pandoc',str(src),'--from=markdown+tex_math_dollars+raw_tex',
         '--toc','--toc-depth=2','--pdf-engine=xelatex',
         '--resource-path='+':'.join([str(ROOT),str(ROOT/'docs'),str(ROOT/'assets')]),
         '-V','geometry:margin=0.68in','-V','fontsize=10pt',
         '-V','mainfont=DejaVu Serif','-V','monofont=DejaVu Sans Mono',
         '-V','colorlinks=true','-o',str(ROOT/'Agentic_Crystallization_2.4.pdf')]
    subprocess.run(cmd,cwd=ROOT,check=True)
print(ROOT/'Agentic_Crystallization_2.4.pdf')
