"""Hash released public files; exclude private, temporary and self-referential files."""
import hashlib
import json
from pathlib import Path
import subprocess

root=Path(__file__).resolve().parents[1]
names=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=root).decode().split('\0')
rows=[]
for name in sorted(set(names)):
    if not name or name=='manifest.sha256.json':continue
    p=root/name
    if not p.is_file():continue
    raw=p.read_bytes()
    rows.append({'path':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
out={'algorithm':'SHA-256','main_collection_commit':'d7247ff','files':rows}
(root/'manifest.sha256.json').write_text(json.dumps(out,indent=2)+'\n')
print('Hashed',len(rows),'public files.')
