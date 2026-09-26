"""Render the packaged textures at integer scale for visual QA."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]

def preview():
    canvas = Image.new('RGB', (1040, 260), '#202328')
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype('DejaVuSans.ttf', 16)
    except OSError:
        font = ImageFont.load_default()
    items = [('item/sulfur', 'Sulfur'), ('block/sulfur_ore', 'Sulfur ore'),
             ('block/deepslate_sulfur_ore', 'Deepslate sulfur ore'),
             ('item/saltpeter', 'Saltpeter'), ('item/humus', 'Humus')]
    for index, (name, label) in enumerate(items):
        x = index * 208 + 24
        for row in range(10):
            for col in range(10):
                draw.rectangle((x + col * 16, 30 + row * 16, x + col * 16 + 15, 45 + row * 16),
                               fill='#363a40' if (row + col) % 2 else '#454a52')
        with Image.open(ROOT / f'shared/assets/craftablegunpowder/textures/{name}.png') as sprite:
            canvas.paste(sprite.resize((160, 160), Image.Resampling.NEAREST), (x, 30),
                         sprite.getchannel('A').resize((160, 160), Image.Resampling.NEAREST))
        draw.text((index * 208 + 104, 220), label, anchor='mm', fill='#eeeeee', font=font)
    canvas.save(ROOT / 'art/texture-preview.png')

if __name__ == '__main__':
    preview()
