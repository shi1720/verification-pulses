"""Build the complete manuscript and portable arXiv source archive."""
from pathlib import Path
import shutil
import subprocess
import tarfile
import sys

root=Path(__file__).resolve().parents[1]
assert (root/'data/processed/raw_audit.json').exists(), 'Audit the complete raw records first.'
subprocess.run([sys.executable,str(root/'scripts/write_paper_tables.py')],cwd=root,check=True)
build=root/'tmp/tex-build';build.mkdir(parents=True,exist_ok=True)
subprocess.run(['tectonic','--keep-logs','--outdir',str(build),'main.tex'],cwd=root/'paper',check=True)
out=root/'output';(out/'pdf').mkdir(parents=True,exist_ok=True)
shutil.copy2(build/'main.pdf',out/'pdf/verification-pulses.pdf')
stage=root/'tmp/arxiv-source';stage.mkdir(parents=True,exist_ok=True)
(stage/'figures').mkdir(exist_ok=True)
s=(root/'paper/main.tex').read_text().replace(r'\graphicspath{{../figures/}}',r'\graphicspath{{figures/}}')
(stage/'main.tex').write_text(s)
shutil.copy2(root/'paper/generated.tex',stage/'generated.tex')
for p in (root/'figures').glob('*.pdf'):shutil.copy2(p,stage/'figures'/p.name)
# Fixed member metadata makes the uncompressed tar contents portable.
with tarfile.open(out/'arxiv-source.tar.gz','w:gz') as tar:
    for p in sorted(stage.rglob('*')):
        if p.is_file():
            info=tar.gettarinfo(str(p),arcname=str(p.relative_to(stage)))
            info.uid=info.gid=0;info.uname=info.gname='';info.mtime=1790121600
            with p.open('rb') as f:tar.addfile(info,f)
print(out/'pdf/verification-pulses.pdf')
print(out/'arxiv-source.tar.gz')
