"""Contracts that catch accidental ingredient, version-format and asset regressions."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from prepare import CONFIG, ROOT
from resources import generate, ver

class ResourceContracts(unittest.TestCase):
    def test_exact_matrix(self):
        targets = CONFIG['targets']
        self.assertEqual(len({r['minecraft'] for r in targets}), 10)
        self.assertEqual(len(targets), 24)
        self.assertTrue(all(ver(r['minecraft']) <= (1, 21, 1) for r in targets if r['loader'] == 'forge'))
        for mc in ('26.1', '26.2'):
            self.assertEqual({r['loader'] for r in targets if r['minecraft'] == mc}, {'fabric', 'neoforge'})

    def test_each_target_data(self):
        for row in CONFIG['targets']:
            with self.subTest(row=row), tempfile.TemporaryDirectory() as directory:
                out = Path(directory)
                generate(out, row['minecraft'], row['loader'])
                files = {p.relative_to(out).as_posix(): json.loads(p.read_text(encoding='utf-8')) for p in out.rglob('*.json')}
                singular = ver(row['minecraft']) >= (1, 21)
                recipe_dir = 'recipe' if singular else 'recipes'
                base = f'data/craftablegunpowder/{recipe_dir}/'
                recipe = files[base + 'gunpowder.json']
                self.assertEqual(recipe['type'], 'minecraft:crafting_shaped')
                self.assertEqual(recipe['pattern'], ['SNC'])
                # Width 3 prevents crafting in the player's 2x2 inventory grid.
                self.assertEqual(max(map(len, recipe['pattern'])), 3)
                key = recipe['key']
                ingredient_ids = {v if isinstance(v, str) else v['item'] for v in key.values()}
                self.assertEqual(ingredient_ids, {'craftablegunpowder:sulfur', 'craftablegunpowder:saltpeter', 'minecraft:charcoal'})
                self.assertNotIn('minecraft:coal', ingredient_ids)
                self.assertEqual(recipe['result']['count'], 8)
                result_field = 'id' if ver(row['minecraft']) >= (1, 20, 5) else 'item'
                self.assertEqual(recipe['result'][result_field], 'minecraft:gunpowder')
                self.assertEqual(files[base + 'humus.json']['type'], 'minecraft:crafting_shaped')
                self.assertNotIn(base + 'saltpeter.json', files)
                # Worldgen has both stone and deepslate replacements and only an overworld modifier.
                feature = files['data/craftablegunpowder/worldgen/configured_feature/sulfur_ore.json']
                self.assertEqual(len(feature['config']['targets']), 2)
                self.assertEqual(feature['config']['size'], 8)
                modifiers = [v for k, v in files.items() if '/biome_modifier/' in k]
                self.assertEqual(len(modifiers), 0 if row['loader'] == 'fabric' else 1)
                for modifier in modifiers:
                    self.assertEqual(modifier['biomes'], '#minecraft:is_overworld')
                # Every referenced texture/model points to a packaged mod asset.
                for path, model in files.items():
                    if '/models/' not in path:
                        continue
                    for texture in model.get('textures', {}).values():
                        namespace, location = texture.split(':')
                        self.assertTrue((out / 'assets' / namespace / 'textures' / (location + '.png')).is_file(), texture)
                if ver(row['minecraft']) >= (1, 21, 4):
                    self.assertEqual(len([p for p in files if p.startswith('assets/craftablegunpowder/items/')]), 5)

    def test_texture_png_headers_and_alpha(self):
        import struct
        textures = list((ROOT / 'shared/assets/craftablegunpowder/textures').rglob('*.png'))
        self.assertEqual(len(textures), 5)
        for path in textures:
            data = path.read_bytes()
            self.assertEqual(data[:8], b'\x89PNG\r\n\x1a\n')
            self.assertEqual(struct.unpack('>II', data[16:24]), (16, 16))
            self.assertEqual(data[25], 6, 'Textures must preserve RGBA data')

if __name__ == '__main__':
    unittest.main()
