# -*- coding: utf-8 -*-
"""
Применяет правки h1/title/description из build/meta_overrides/*.json прямо в
исходники build/d_arch.py (страницы) и build/d_art_*.py (статьи), находя старое
значение поля (как оно сейчас в site/src/data/pages.json / articles.json) и
заменяя его на новое — ровно одно вхождение в файле, иначе с ошибкой.
После этого нужно пересобрать JSON: python build/export_site.py
Запуск: python scripts/apply_meta_overrides.py [--dry]
"""
import sys, os, json, glob, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRY = '--dry' in sys.argv

pages = json.load(open(ROOT + '/site/src/data/pages.json', encoding='utf-8'))
arts = json.load(open(ROOT + '/site/src/data/articles.json', encoding='utf-8'))
hubs = json.load(open(ROOT + '/site/src/data/hubs.json', encoding='utf-8'))
by_page = {p['id']: p for p in pages}
by_art = {a['id']: a for a in arts}
by_hub = {h['id']: h for h in hubs}

overrides = {}
for f in glob.glob(ROOT + '/build/meta_overrides/*.json'):
    d = json.load(open(f, encoding='utf-8'))
    for k, v in d.items():
        overrides.setdefault(k, {}).update(v)
print(f'overrides: {len(overrides)} id из {len(glob.glob(ROOT + "/build/meta_overrides/*.json"))} файлов')

arch_src = open(ROOT + '/build/d_arch.py', encoding='utf-8').read()
art_files = {f: open(f, encoding='utf-8').read() for f in glob.glob(ROOT + '/build/d_art_*.py')}

applied, skipped = [], []

for pid, fields in sorted(overrides.items()):
    if pid.startswith('P'):
        cur = by_page.get(pid)
        if not cur:
            skipped.append((pid, 'нет такого id в pages.json')); continue
        text = arch_src
        changed = False
        for field, new in fields.items():
            if field not in ('h1', 'title', 'description'):
                continue
            old = cur[field]
            if old == new:
                continue
            n = text.count(f'"{old}"')
            if n != 1:
                skipped.append((pid, f'{field}: старое значение встречается {n} раз(а), пропуск')); continue
            text = text.replace(f'"{old}"', f'"{new}"', 1)
            changed = True
        if changed:
            arch_src = text
            applied.append(pid)
    elif pid.startswith('A'):
        cur = by_art.get(pid)
        if not cur:
            skipped.append((pid, 'нет такого id в articles.json')); continue
        found_file = None
        for fp, text in art_files.items():
            if f'a("{pid}",' in text:
                found_file = fp; break
        if not found_file:
            skipped.append((pid, 'статья не найдена ни в одном d_art_*.py (ещё не написана в build)')); continue
        text = art_files[found_file]
        changed = False
        for field, new in fields.items():
            if field not in ('h1', 'title', 'description'):
                continue
            old = cur[field]
            if old == new:
                continue
            n = text.count(f'"{old}"')
            if n != 1:
                skipped.append((pid, f'{field}: старое значение встречается {n} раз(а), пропуск')); continue
            text = text.replace(f'"{old}"', f'"{new}"', 1)
            changed = True
        if changed:
            art_files[found_file] = text
            applied.append(pid)
    elif pid.startswith('H'):
        cur = by_hub.get(pid)
        if not cur:
            skipped.append((pid, 'нет такого id в hubs.json')); continue
        text = arch_src
        changed = False
        for field, new in fields.items():
            if field not in ('h1', 'title', 'description'):
                continue
            old = cur[field]
            if old == new:
                continue
            n = text.count(f'"{old}"')
            if n != 1:
                skipped.append((pid, f'{field}: старое значение встречается {n} раз(а), пропуск')); continue
            text = text.replace(f'"{old}"', f'"{new}"', 1)
            changed = True
        if changed:
            arch_src = text
            applied.append(pid)
    else:
        skipped.append((pid, 'неизвестный префикс id'))

print(f'применено: {len(applied)}')
print(f'пропущено: {len(skipped)}')
for pid, why in skipped:
    print(f'  {pid}: {why}')

if not DRY:
    open(ROOT + '/build/d_arch.py', 'w', encoding='utf-8').write(arch_src)
    for fp, text in art_files.items():
        open(fp, 'w', encoding='utf-8').write(text)
    print('записано. Теперь пересобери JSON: python build/export_site.py')
else:
    print('--dry: файлы не изменены')
