"""Boot an isolated loopback-only development server and exercise content via RCON.

Runs only inside the generated target's run directory; never opens an existing world.
Pass --accept-eula to acknowledge https://aka.ms/MinecraftEULA for this test server.
"""
import argparse
import concurrent.futures
import json
import os
import re
import secrets
import socket
import struct
import subprocess
import time
from pathlib import Path
from prepare import CONFIG, ROOT, prepare

def free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

class Rcon:
    def __init__(self, port, password):
        self.socket = socket.create_connection(('127.0.0.1', port), timeout=15)
        self.counter = 0
        self.call(password, 3)

    def receive(self, n):
        result = b''
        while len(result) < n:
            chunk = self.socket.recv(n - len(result))
            if not chunk:
                raise ConnectionError('RCON closed unexpectedly')
            result += chunk
        return result

    def call(self, command, kind=2):
        self.counter += 1
        data = struct.pack('<ii', self.counter, kind) + command.encode() + b'\0\0'
        self.socket.sendall(struct.pack('<i', len(data)) + data)
        size = struct.unpack('<i', self.receive(4))[0]
        response = self.receive(size)
        if struct.unpack('<i', response[:4])[0] == -1:
            raise RuntimeError('RCON authentication failed')
        return response[8:-2].decode('utf-8', errors='replace')

def smoke(row, timeout):
    target = f"{row['minecraft']}-{row['loader']}"
    project = prepare(row)
    run = project / 'run'
    run.mkdir(exist_ok=True)
    (run / 'eula.txt').write_text('eula=true\n')
    port, rcon_port = free_port(), free_port()
    password = secrets.token_hex(16)
    (run / 'server.properties').write_text(f'''server-ip=127.0.0.1
server-port={port}
enable-rcon=true
rcon.port={rcon_port}
rcon.password={password}
online-mode=false
level-name=smoke-world
level-seed=1875423
view-distance=2
simulation-distance=2
spawn-protection=0
sync-chunk-writes=false
max-tick-time=120000
pause-when-empty-seconds=0
''')
    env = os.environ.copy()
    major = 25 if row['loader'] == 'fabric' or row['java'] == 25 else 21
    env['JAVA_HOME'] = env.get(f'JAVA_HOME_{major}', env.get(f'JAVA_HOME_{major}_X64', env.get('JAVA_HOME', '')))
    log = ROOT / '.local' / f'smoke-{target}.log'
    log.parent.mkdir(exist_ok=True)
    command = [str(project / ('gradlew.bat' if os.name == 'nt' else 'gradlew')), 'runServer', '--console', 'plain']
    record = {'target': target, 'passed': False, 'checks': {}}
    rcon = None
    with log.open('w', encoding='utf-8') as stream:
        process = subprocess.Popen(command, cwd=project, env=env, stdout=stream, stderr=subprocess.STDOUT)
        try:
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise RuntimeError('Server exited before RCON became available')
                try:
                    rcon = Rcon(rcon_port, password)
                    break
                except (OSError, ConnectionError):
                    time.sleep(2)
            if rcon is None:
                raise TimeoutError('Server startup timed out')
            record['checks']['startup'] = True
            rcon.call('forceload add 0 0')
            rcon.call('setblock 0 100 0 minecraft:chest')
            for index, name in enumerate(('sulfur', 'saltpeter', 'humus', 'sulfur_ore', 'deepslate_sulfur_ore')):
                response = rcon.call(f'item replace block 0 100 0 container.{index} with craftablegunpowder:{name}')
                record['checks'][name] = response
                if 'Replaced' not in response:
                    raise RuntimeError(f'Failed to register {name}: {response}')
            rcon.call('setblock 2 100 0 craftablegunpowder:sulfur_ore')
            response = rcon.call('loot replace block 0 100 0 container.9 mine 2 100 0 minecraft:stone_pickaxe')
            record['checks']['ore_drop'] = response
            if '1 ' not in response:
                raise RuntimeError('Ore drop failed: ' + response)
            response = rcon.call('data get block 0 100 0 Items')
            record['checks']['inventory'] = response
            if 'craftablegunpowder:sulfur' not in response:
                raise RuntimeError('Missing sulfur in loot result')
            rcon.call('fill 5 40 5 20 55 20 minecraft:stone')
            response = rcon.call('place feature craftablegunpowder:sulfur_ore 12 46 12')
            record['checks']['feature'] = response
            if 'Placed ' not in response:
                raise RuntimeError('Ore feature failed: ' + response)
            rcon.call('reload')
            time.sleep(4)
            content = log.read_text(encoding='utf-8', errors='replace')
            errors = [line for line in content.splitlines() if re.search(r'(ERROR|Failed to parse|Couldn.t parse)', line) and
                      ('craftablegunpowder' in line.lower() or 'recipe' in line.lower() or 'loot' in line.lower())]
            if errors:
                raise RuntimeError('\n'.join(errors))
            record['checks']['reload'] = True
            record['passed'] = True
        except Exception as exc:
            record['error'] = str(exc)
        finally:
            if rcon:
                try:
                    rcon.call('stop')
                except (OSError, ConnectionError):
                    pass
                rcon.socket.close()
            try:
                process.wait(timeout=45)
            except subprocess.TimeoutExpired:
                if os.name == 'nt':
                    subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], capture_output=True)
                else:
                    process.terminate()
    (ROOT / '.local' / f'smoke-result-{target}.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2), flush=True)
    return record['passed']

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', action='append')
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--jobs', type=int, default=2)
    parser.add_argument('--timeout', type=int, default=900)
    parser.add_argument('--accept-eula', action='store_true')
    args = parser.parse_args()
    if not args.accept_eula:
        parser.error('--accept-eula is required to start the local test server')
    rows = [r for r in CONFIG['targets'] if args.all or f"{r['minecraft']}-{r['loader']}" in (args.target or [])]
    if not rows:
        parser.error('Select --target or --all')
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        results = list(pool.map(lambda row: smoke(row, args.timeout), rows))
    raise SystemExit(0 if all(results) else 1)
