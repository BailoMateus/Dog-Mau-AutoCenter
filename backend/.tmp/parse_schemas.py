import re
from pathlib import Path
root = Path('app/schemas')
for path in sorted(root.glob('*.py')):
    text = path.read_text(encoding='utf-8')
    classes = re.findall(r'class\s+(\w+)\((?:BaseModel|.*BaseModel.*)\):', text)
    if not classes:
        continue
    print(path.name)
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r'class\s+(\w+)\((?:BaseModel|.*BaseModel.*)\):', line)
        if m:
            class_name = m.group(1)
            print('  ' + class_name)
            i += 1
            while i < len(lines) and (not re.match(r'class\s+\w+\(', lines[i])):
                field_match = re.match(r'\s+(\w+)\s*:\s*([^#=]+)(?:\s*=\s*[^#]+)?', lines[i])
                if field_match:
                    fname = field_match.group(1)
                    ftype = field_match.group(2).strip()
                    print(f'    - {fname}: {ftype}')
                i += 1
            continue
        i += 1
    print()