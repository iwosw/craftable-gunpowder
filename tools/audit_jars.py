"""Validate distributable metadata, resources, bytecode targets and remapping."""
import argparse
import hashlib
import json
import struct
import zipfile
from pathlib import Path
from prepare import CONFIG, ROOT

def audit(directory):
    records = []
    for row in CONFIG['targets']:
        mc, loader = row['minecraft'], row['loader']
        name = f"craftable-gunpowder-{mc}-{loader}-{CONFIG['mod_version']}.jar"
        path = directory / name
        if not path.exists():
            raise AssertionError('Missing runtime artifact: ' + name)
        with zipfile.ZipFile(path) as jar:
            names = set(jar.namelist())
            assert jar.testzip() is None, name
            assert 'LICENSE' in names and 'icon.png' in names, name
            for material in ('item/sulfur', 'item/saltpeter', 'item/humus', 'block/sulfur_ore', 'block/deepslate_sulfur_ore'):
                texture = jar.read('assets/craftablegunpowder/textures/' + material + '.png')
                assert struct.unpack('>II', texture[16:24]) == (16, 16), name
            entrypoint = 'FabricEntrypoint' if loader == 'fabric' else 'ForgeEntrypoint'
            for cls in ('Content', entrypoint):
                bytecode = jar.read('dev/iwoss/craftablegunpowder/' + cls + '.class')
                assert struct.unpack('>H', bytecode[6:8])[0] == row['java'] + 44, (name, cls)
            content = jar.read('dev/iwoss/craftablegunpowder/Content.class')
            if loader == 'fabric':
                metadata = json.loads(jar.read('fabric.mod.json'))
                assert metadata['authors'] == ['iwoss'], name
                assert metadata['depends']['minecraft'] == mc, name
                if not mc.startswith('26.'):
                    assert b'net/minecraft/class_' in content, 'Unremapped Fabric jar: ' + name
            else:
                metadata_file = 'META-INF/neoforge.mods.toml' if loader == 'neoforge' and mc not in ('1.20.1', '1.20.4') else 'META-INF/mods.toml'
                metadata = jar.read(metadata_file).decode()
                assert 'authors="iwoss"' in metadata, name
                assert f'versionRange="[{mc}]"' in metadata, name
            if mc in ('1.20.1', '1.20.4', '1.20.6'):
                recipe_path = 'data/craftablegunpowder/recipes/gunpowder.json'
            else:
                recipe_path = 'data/craftablegunpowder/recipe/gunpowder.json'
            recipe = json.loads(jar.read(recipe_path))
            assert recipe['result']['count'] == 8, name
            assert 'minecraft:charcoal' in json.dumps(recipe) and 'minecraft:coal' not in json.dumps(recipe), name
            for resource in names:
                if resource.endswith('.json'):
                    json.loads(jar.read(resource))
        records.append({'target': mc + '-' + loader, 'jar': name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size})
    (directory / 'SHA256SUMS.txt').write_text(''.join(r['sha256'] + '  ' + r['jar'] + '\n' for r in records))
    (directory / 'manifest.json').write_text(json.dumps(records, indent=2) + '\n')
    return records

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', nargs='?', type=Path, default=ROOT / 'dist')
    args = parser.parse_args()
    for row in audit(args.directory):
        print('PASS', row['target'], row['bytes'], 'bytes')
