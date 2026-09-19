"""Build selected target(s), saving logs and SHA-256 checked distributable jars."""
import argparse
import concurrent.futures
import hashlib
import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from prepare import CONFIG, ROOT, prepare

def build(row):
    target = f"{row['minecraft']}-{row['loader']}"
    project = prepare(row)
    log = ROOT / '.local' / f'build-{target}.log'
    log.parent.mkdir(exist_ok=True)
    env = os.environ.copy()
    for major in (17, 21, 25):
        if not env.get(f'JAVA_HOME_{major}') and env.get(f'JAVA_HOME_{major}_X64'):
            env[f'JAVA_HOME_{major}'] = env[f'JAVA_HOME_{major}_X64']
    # An explicit JAVA_HOME_<major> overrides the caller's default Java.
    if env.get(f"JAVA_HOME_{row['java']}"):
        env['JAVA_HOME'] = env[f"JAVA_HOME_{row['java']}"]
    if row['loader'] == 'fabric' and env.get('JAVA_HOME_25'):
        env['JAVA_HOME'] = env['JAVA_HOME_25']  # Current Loom itself needs a recent JVM.
    elif row['java'] == 17 and env.get('JAVA_HOME_21'):
        env['JAVA_HOME'] = env['JAVA_HOME_21']
    command = [str(project / ('gradlew.bat' if os.name == 'nt' else 'gradlew')), 'build', '--console', 'plain']
    start = time.time()
    print('BUILD', target, flush=True)
    with log.open('w', encoding='utf-8') as stream:
        result = subprocess.run(command, cwd=project, env=env, stdout=stream, stderr=subprocess.STDOUT)
    record = {'target': target, 'exit_code': result.returncode, 'seconds': round(time.time() - start)}
    if result.returncode == 0:
        dest = ROOT / 'dist'
        dest.mkdir(exist_ok=True)
        jars = [p for p in (project / 'build/libs').glob('*.jar') if not any(s in p.name for s in ('-sources', '-dev', '-javadoc'))]
        if len(jars) != 1:
            raise RuntimeError(f'{target}: expected one runtime jar, found {jars}')
        final = dest / jars[0].name
        shutil.copy2(jars[0], final)
        record.update(jar=final.name, sha256=hashlib.sha256(final.read_bytes()).hexdigest())
    (ROOT / '.local' / f'result-{target}.json').write_text(json.dumps(record, indent=2) + '\n')
    print('PASS' if result.returncode == 0 else 'FAIL', target, f"({record['seconds']}s)", flush=True)
    if result.returncode:
        print('\n'.join(log.read_text(encoding='utf-8', errors='replace').splitlines()[-35:]), flush=True)
    return record

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', action='append', help='e.g. 1.21.1-neoforge; repeatable')
    parser.add_argument('--jobs', type=int, default=2)
    args = parser.parse_args()
    rows = [r for r in CONFIG['targets'] if not args.target or f"{r['minecraft']}-{r['loader']}" in args.target]
    if not rows:
        parser.error('No matching targets')
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        results = list(pool.map(build, rows))
    raise SystemExit(1 if any(r['exit_code'] for r in results) else 0)
