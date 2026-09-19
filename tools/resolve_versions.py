"""Resolve published loader coordinates from official Maven metadata."""
import concurrent.futures
import json
import subprocess
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSIONS = ['1.20.1', '1.20.4', '1.20.6', '1.21.1', '1.21.4', '1.21.5', '1.21.8', '1.21.11', '26.1', '26.2']
URLS = {
    'forge': 'https://maven.minecraftforge.net/net/minecraftforge/forge/maven-metadata.xml',
    'neo': 'https://maven.neoforged.net/releases/net/neoforged/neoforge/maven-metadata.xml',
    'neo_legacy': 'https://maven.neoforged.net/releases/net/neoforged/forge/maven-metadata.xml',
    'fabric_api': 'https://maven.fabricmc.net/net/fabricmc/fabric-api/fabric-api/maven-metadata.xml',
    'loom': 'https://maven.fabricmc.net/net/fabricmc/fabric-loom/maven-metadata.xml',
    'loader': 'https://meta.fabricmc.net/v2/versions/loader',
    'minecraft': 'https://piston-meta.mojang.com/mc/game/version_manifest_v2.json',
}

def fetch(pair):
    key, url = pair
    data = subprocess.check_output(['curl', '-fsSL', '--retry', '3', url])
    if key in ('loader', 'minecraft'):
        return key, json.loads(data)
    return key, [n.text for n in ET.fromstring(data).findall('./versioning/versions/version')]

def sortkey(version):
    import re
    return tuple(int(n) for n in re.findall(r'\d+', version))

def latest(versions, prefix='', suffix=''):
    candidates = [v for v in versions if v.startswith(prefix) and v.endswith(suffix) and 'snapshot' not in v.lower()]
    stable = [v for v in candidates if not any(s in v for s in ('alpha', 'beta', 'rc'))]
    return max(stable or candidates, key=sortkey) if candidates else None

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=7) as pool:
        data = dict(pool.map(fetch, URLS.items()))
    (ROOT / '.local').mkdir(exist_ok=True)
    (ROOT / '.local/metadata.json').write_text(json.dumps(data, indent=2))
    rows = []
    for mc in VERSIONS:
        era = 'modern' if mc.startswith('26.') else 'legacy' if mc in ('1.20.1', '1.20.4') else 'components'
        neo_prefix = {'1.20.1': '1.20.1-', '26.1': '26.1.0.', '26.2': '26.2.0.'}.get(mc, '.'.join(mc.split('.')[1:]) + '.')
        loaders = ['fabric', 'neoforge'] + (['forge'] if mc in VERSIONS[:4] else [])
        for loader in loaders:
            version = (next(v['version'] for v in data['loader'] if v['stable']) if loader == 'fabric' else
                       latest(data['neo_legacy'] if mc == '1.20.1' else data['neo'], neo_prefix) if loader == 'neoforge' else
                       latest(data['forge'], mc + '-'))
            if not version:
                raise RuntimeError(f'No published loader for {mc}/{loader}')
            rows.append(dict(minecraft=mc, loader=loader, loader_version=version,
                             java=25 if era == 'modern' else 17 if era == 'legacy' else 21,
                             fabric_api=latest(data['fabric_api'], suffix='+'+mc) if loader == 'fabric' else None))
    result = dict(mod_version='1.0.0', loom=latest(data['loom']), targets=rows)
    (ROOT / 'versions.json').write_text(json.dumps(result, indent=2) + '\n')
    for row in rows:
        print(row)
