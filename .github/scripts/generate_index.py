import json
import os
import sys

ext_dir = "Extensions"
index_file = "index.json"
required_fields = ["name", "version"]

old_index = {}
if os.path.isfile(index_file):
    try:
        with open(index_file, 'r', encoding='utf-8') as f:
            old_index = json.load(f)
    except Exception as e:
        print(f"⚠️ Warning: cannot load old index: {e}")

new_index = {}
warnings = []
errors = []

for folder in sorted(os.listdir(ext_dir)):
    subdir = os.path.join(ext_dir, folder)
    json_path = os.path.join(subdir, 'extensions.json')
    zip_path = os.path.join(subdir, 'extensions.zip')

    if not os.path.isdir(subdir) or not os.path.isfile(json_path):
        continue

    try:
        data = json.load(open(json_path, 'r', encoding='utf-8'))
    except Exception as e:
        errors.append(f"{folder}: failed to parse extensions.json ({e})")
        continue

    for field in required_fields:
        if field not in data:
            warnings.append(f"{folder}: missing required field '{field}' in extensions.json")

    entry = data.copy()
    entry['json'] = json_path.replace('\\', '/')
    if os.path.isfile(zip_path):
        entry['zip'] = zip_path.replace('\\', '/')

    new_index[folder] = entry

old_keys = set(old_index.keys())
new_keys = set(new_index.keys())
new_plugins = new_keys - old_keys
removed_plugins = old_keys - new_keys
updated = []
for folder in old_keys & new_keys:
    old_ver = old_index[folder].get('version')
    new_ver = new_index[folder].get('version')
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


with open(index_file, 'w', encoding='utf-8') as f:
    json.dump(new_index, f, indent=2, ensure_ascii=False)
print(f"📦 {index_file} updated, {len(new_index)} entries.")