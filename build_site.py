from pathlib import Path
import hashlib, io, json, zipfile

base = Path(__file__).resolve().parent
manifest = json.loads((base / 'site-manifest.json').read_text(encoding='utf-8'))
chunks = []
for part in manifest['parts']:
    data = (base / part['name']).read_bytes()
    assert len(data) == part['bytes']
    assert hashlib.sha256(data).hexdigest() == part['sha256']
    chunks.append(data)
data = b''.join(chunks)
assert hashlib.sha256(data).hexdigest() == manifest['archive_sha256']
output = base / '_site'
output.mkdir(exist_ok=True)
with zipfile.ZipFile(io.BytesIO(data)) as archive:
    assert set(archive.namelist()) == {f['path'] for f in manifest['files']}
    for item in manifest['files']:
        path = (output / item['path']).resolve()
        assert path.is_relative_to(output.resolve())
        contents = archive.read(item['path'])
        assert hashlib.sha256(contents).hexdigest() == item['sha256']
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(contents)
print(f"Restored and verified {len(manifest['files'])} original website files")
