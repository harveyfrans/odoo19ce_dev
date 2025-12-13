# Odoo 19 CE – Developer Ops Cheat Sheet

This cheat sheet consolidates **all practical commands** we touched (and a few you *should* know) during this thread. It is **IDE‑terminal friendly**, **PowerShell‑safe**, and optimized for **Odoo Community development**.

---

## 1. Git – Daily Commands

### Initialize & connect repo

```bash
git init
git remote add origin <repo_url>
```

### Fix wrong remote

```bash
git remote -v
git remote remove origin
git remote add origin <correct_repo_url>
```

### Status & diff

```bash
git status
git diff
git diff --staged
```

### Add files (IMPORTANT VARIANTS)

```bash
# Add everything
git add .

# Add only one module
git add custom_addons/rc_weather_api

# Add specific files
git add custom_addons/rc_travel_ai/controllers/main.py

# Add all except deleted files
git add -u
```

### Commit

```bash
git commit -m "feat: add rc_travel_helpdesk module"
```

### Push

```bash
git branch -M main
git push -u origin main
```

### Reset mistakes

```bash
# Undo staged files
git reset

# Undo last commit (keep files)
git reset --soft HEAD~1

# Hard reset (DANGEROUS)
git reset --hard HEAD~1
```

---

## 2. Git Ignore (Mandatory for Odoo)

```
__pycache__/
*.pyc
.env
.odoo
.idea/
.vscode/
```

---

## 3. Docker – Odoo 19 CE

### Common lifecycle

```bash
docker compose up -d
docker compose down
docker compose down -v   # IMPORTANT when DB/volume breaks
docker compose restart
```

### Inspect containers

```bash
docker ps
docker logs odoo
```

### Exec into Odoo

```bash
docker exec -it odoo bash
```

### Rebuild after code changes

```bash
docker compose down -v
docker compose up --build -d
```

---

## 4. Odoo – Dev Commands

### Update module (CLI)

```bash
odoo -d <db_name> -u rc_weather_api --stop-after-init
```

### Update all custom modules

```bash
odoo -d <db_name> -u all --stop-after-init
```

### Enable dev mode

```text
Settings → Activate Developer Mode
```

### Clear assets (frontend issues)

```bash
rm -rf ~/.local/share/Odoo/web/assets/*
```

---

## 5. Odoo – Module Structure (Correct)

```
custom_addons/
└── rc_travel_helpdesk/
    ├── __init__.py
    ├── __manifest__.py
    ├── models/
    │   ├── __init__.py
    │   └── ticket.py
    ├── controllers/
    │   ├── __init__.py
    │   └── main.py
    ├── views/
    │   └── views.xml
    └── security/
        └── ir.model.access.csv
```

---

## 6. Generate Markdown With Full Module Source (PowerShell)

### Single‑line (battle‑tested)

```````powershell
$MODULE="rc_travel_helpdesk"; $OUT="docs\03_travel_helpdesk\$MODULE`_source.md"; New-Item -ItemType Directory -Force -Path (Split-Path $OUT) | Out-Null; "# $MODULE – Full Source Code`n" | Set-Content -Encoding UTF8 $OUT; Get-ChildItem -Recurse -File "custom_addons\$MODULE" | Where-Object { $_.FullName -notmatch "__pycache__" -and $_.Extension -ne ".pyc" } | Sort-Object FullName | ForEach-Object { Add-Content -Encoding UTF8 $OUT "`n---`n`n## $($_.FullName)`n`n``````"; Add-Content -Encoding UTF8 $OUT (Get-Content -Raw $_.FullName); Add-Content -Encoding UTF8 $OUT "`n``````" }
```````

### Result

- One clean `.md`
- All files
- Ordered
- No cache noise

---

## 7. Filesystem – PowerShell Basics

### Create directory

```powershell
New-Item -ItemType Directory docs\screenshots
```

### Create empty file

```powershell
New-Item docs\README.md
```

### Copy screenshots

```powershell
Copy-Item screenshots\*.png docs\screenshots
```

---

## 8. VS Code – Sanity Settings

### Always open files in new tab

```json
"workbench.editor.enablePreview": false
```

### Disable one‑click preview

```json
"workbench.editor.enablePreviewFromQuickOpen": false
```

---

## 9. Website / Controller Debugging (Odoo)

### Common mistakes checklist

- ❌ Template `page="True"` without controller
- ❌ Missing CSRF token in POST form
- ❌ Wrong template XMLID
- ❌ Missing `website=True` on route

### Correct route pattern

```python
@http.route('/travel/ai', type='http', auth='public', website=True, methods=['GET','POST'])
```

---

## 10. Versioning Rule (You were right 😉)

**Never keep the same version after changes**

Recommended bump:

```
19.0.1.0.0 → initial
19.0.1.1.0 → feature
19.0.1.1.1 → bugfix
```

---

## 11. Interview‑Grade Hygiene Checklist

- ✅ One module = one responsibility
- ✅ No Enterprise dependency leaks
- ✅ Clean README
- ✅ Screenshots
- ✅ Git history readable
- ✅ No magic, no hacks

---

This cheat sheet is intentionally **boring, explicit, and reproducible** — which is exactly what senior Odoo reviewers respect.

