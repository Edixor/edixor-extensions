import json
import os
import sys
from datetime import datetime

ext_dir = "Extensions"
index_file = "index.json"
required_fields = ["name", "version"]

repo_resources = "repository/resources"
standard_icon = os.path.join(repo_resources, "standard_icon.png").replace('\\', '/')
standard_preview = os.path.join(repo_resources, "standard_preview.png").replace('\\', '/')
standard_description = os.path.join(repo_resources, "standard_descriptions.md").replace('\\', '/')

old_index = {}
if os.path.isfile(index_file):
    try:
        with open(index_file, 'r', encoding='utf-8') as f:
            old_index = json.load(f).get("entries", {})
    except Exception as e:
        print(f"⚠️ Warning: cannot load old index: {e}")

new_entries = {}
warnings = []
errors = []

for folder in sorted(os.listdir(ext_dir)):
    subdir = os.path.join(ext_dir, folder)
    json_path = os.path.join(subdir, 'extensions.json')
    zip_path = os.path.join(subdir, 'extensions.zip')
    icon_path = os.path.join(subdir, 'icon.png')
    preview_path = os.path.join(subdir, 'preview.png')
    description_path = os.path.join(subdir, 'descriptions.md')

    if not os.path.isdir(subdir) or not os.path.isfile(json_path):
        continue

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        errors.append(f"{folder}: failed to parse extensions.json ({e})")
        continue

    for field in required_fields:
        if field not in data:
            warnings.append(f"{folder}: missing required field '{field}' in extensions.json")

    entry = data.copy()

    if 'type' not in entry or not entry['type']:
        entry['type'] = "plugin"

    if not entry.get('description'):
        warnings.append(f"{folder}: description field is empty or missing, set to default")
        entry['description'] = "no description..."

    entry['icon'] = icon_path.replace('\\', '/') if os.path.isfile(icon_path) else standard_icon
    if not os.path.isfile(icon_path):
        warnings.append(f"{folder}: icon.png not found, using standard icon")

    entry['preview'] = preview_path.replace('\\', '/') if os.path.isfile(preview_path) else standard_preview
    if not os.path.isfile(preview_path):
        warnings.append(f"{folder}: preview.png not found, using standard preview")

    entry['inspection'] = description_path.replace('\\', '/') if os.path.isfile(description_path) else standard_description
    if not os.path.isfile(description_path):
        warnings.append(f"{folder}: descriptions.md not found, using standard description")

    entry['json'] = json_path.replace('\\', '/')
    if os.path.isfile(zip_path):
        entry['zip'] = zip_path.replace('\\', '/')

    new_entries[folder] = entry

old_keys = set(old_index.keys())
new_keys = set(new_entries.keys())
new_plugins = new_keys - old_keys
removed_plugins = old_keys - new_keys
updated = []
for folder in old_keys & new_keys:
    old_ver = old_index[folder].get('version')
    new_ver = new_entries[folder].get('version')
    if old_ver and new_ver and old_ver != new_ver:
        updated.append(f"{folder}: version {old_ver} → {new_ver}")

if new_plugins:
    print("✅ New plugins:", ", ".join(sorted(new_plugins)))
if removed_plugins:
    print("❌ Removed plugins:", ", ".join(sorted(removed_plugins)))
if updated:
    print("🔄 Updated plugins:")
    for u in updated:
        print("  -", u)

if warnings:
    print("⚠️ Warnings:")
    for w in warnings:
        print("  -", w)

if errors:
    print("❌ Errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

version = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
final_output = {
    "version": version,
    "entries": new_entries
}

with open(index_file, 'w', encoding='utf-8') as f:
    json.dump(final_output, f, indent=2, ensure_ascii=False)

print(f"📦 {index_file} updated, {len(new_entries)} entries. Version: {version}")
