import re
from pathlib import Path
root = Path('app/controllers')
out = Path('route_list.tsv')
with out.open('w', encoding='utf-8') as f:
    f.write('FILE\tPREFIX\tMETHOD\tPATH\tFUNC\n')
    for path in sorted(root.glob('*.py')):
        text = path.read_text(encoding='utf-8')
        prefix_match = re.search(r'router\s*=\s*APIRouter\(prefix\s*=\s*"([^"]*)"', text)
        prefix = prefix_match.group(1) if prefix_match else ''
        for line in text.splitlines():
            m = re.search(r'@router\.(get|post|put|patch|delete)\(\"([^\"]*)\"', line)
            if m:
                f.write(f'{path.name}\t{prefix}\t{m.group(1).upper()}\t{m.group(2)}\tUNKNOWN\n')
print('WROTE', out.resolve())
