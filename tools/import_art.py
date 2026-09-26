"""Mechanical nearest-neighbour export of the generated art to Minecraft PNGs."""
import argparse
import shutil
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('name', choices=['sulfur', 'sulfur_ore', 'deepslate_sulfur_ore', 'saltpeter', 'humus'])
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    original = ROOT / 'art/source' / f'{args.name}.png'
    original.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(args.source, original)
    kind = 'block' if args.name.endswith('_ore') else 'item'
    dest = ROOT / 'shared/assets/craftablegunpowder/textures' / kind / f'{args.name}.png'
    dest.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(original) as source:
        sprite = source.convert('RGBA').resize((16, 16), Image.Resampling.NEAREST)
        # Minecraft extrudes item boundaries from alpha. Near-opaque generated
        # pixels otherwise leave translucent sides even without antialiasing.
        if kind == 'item':
            sprite.putalpha(sprite.getchannel('A').point(lambda alpha: 255 if alpha >= 128 else 0))
            bounds = sprite.getbbox()
            if bounds and (bounds[0] == 0 or bounds[1] == 0 or bounds[2] == 16 or bounds[3] == 16):
                cropped = sprite.crop(bounds)
                cropped.thumbnail((14, 14), Image.Resampling.NEAREST)
                sprite = Image.new('RGBA', (16, 16))
                sprite.paste(cropped, ((16 - cropped.width) // 2, (16 - cropped.height) // 2))
        sprite.save(dest)
    print(dest.relative_to(ROOT))
