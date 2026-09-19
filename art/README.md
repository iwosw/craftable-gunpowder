# Artwork

Five original textures were generated with the built-in **ImageGen** tool. The supplied icon is preserved as `icon.png`.

The original generated PNGs are in `source/`; the actual Minecraft textures are in `../shared/assets/craftablegunpowder/textures/`. `tools/import_art.py` performs only nearest-neighbour resizing to 16×16 RGBA, preserving generated transparency. It does not draw replacement artwork.

![Texture preview](texture-preview.png)

## Generation prompts

### Sulfur

Use case: stylized-concept. Asset type: actual Minecraft mod inventory texture, sulfur item. Generate a single small bright golden-yellow sulfur mineral powder clump, recognizable angular chunky silhouette, rich yellow and ochre shading, flat front-facing Minecraft pixel art. Square canvas with a 16 by 16 pixel logical grid enlarged with exact hard square pixels, no antialiasing, limited 6-color palette. Centered item fills 12x12 logical pixels, with 2-pixel transparent padding. Actual transparent background. No text, no border, no UI, no shadow outside sprite, no other items. The output will be used directly as the mod's sulfur texture.

### Sulfur ore

Use case: stylized-concept. Asset type: Minecraft mod block face texture sulfur_ore.png. A single square seamless flat orthographic stone texture with scattered golden lemon-yellow sulfur flecks embedded in neutral gray stone. Authentic low resolution Minecraft pixel-art material, 16x16 logical square pixels enlarged sharply, limited muted gray and gold palette, about 25 percent yellow mineral. Texture fills entire canvas edge to edge, opaque. No perspective, no 3D cube, no border, no text, no UI, no lighting gradients, no margins. Only one tile.

### Saltpeter

Use case: stylized-concept. Asset type: Minecraft inventory texture saltpeter.png. Single small off-white saltpeter crystal dust heap, light ivory angular grains, cool pale gray shadow pixels, tiny white crystalline highlights. Flat front-facing authentic Minecraft pixel art, exactly 16 by 16 logical square pixels enlarged sharply, hard edges, limited 6-color palette. Compact asymmetrical pile fills 12x12 logical pixels centered, 2-pixel transparent padding. Actual transparent background. No text, no lettering, no border, no UI, no gradient, no separate shadow, only one item sprite.

### Humus

Use case: stylized-concept. Asset type: Minecraft inventory texture humus.png. Single small dark brown humus compost clump with three tiny muted olive-green plant flecks and tan organic speckles. Flat front-facing authentic Minecraft pixel art, 16 by 16 logical square pixels enlarged sharply, hard edges, limited six-color palette. Compact asymmetrical earthy clump fills 12x12 logical pixels centered with 2-pixel transparent padding. Actual transparent background. No text, no lettering, no border, no UI, no gradient, no separate shadow, only one item sprite.

### Deepslate sulfur ore

Use case: stylized-concept. Asset type: Minecraft mod block face texture deepslate_sulfur_ore.png. A single square seamless flat orthographic texture of dark charcoal-gray deepslate stone with scattered golden lemon-yellow sulfur mineral flecks. Recognizable subtle horizontal layered stone grain, authentic low resolution Minecraft pixel-art material, 16x16 logical square pixels enlarged sharply, limited dark gray and yellow palette, about 25 percent yellow mineral. Texture fills entire canvas edge to edge, opaque. No perspective, no 3D cube, no border, no text, no UI, no gradients, no margins. Only one tile.
