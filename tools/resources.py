"""Version-aware vanilla data and assets. No runtime recipe handlers required."""
import json
import shutil
from pathlib import Path

MOD = 'craftablegunpowder'
ROOT = Path(__file__).resolve().parents[1]

def ver(mc):
    return tuple(map(int, mc.split('.')))

def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

def generate(out, mc, loader):
    version = ver(mc)
    singular = version >= (1, 21)
    components = version >= (1, 20, 5)
    simple = version >= (1, 21, 2)
    data = out / 'data' / MOD
    assets = out / 'assets' / MOD
    recipe_dir = 'recipe' if singular else 'recipes'
    loot_dir = 'loot_table' if singular else 'loot_tables'
    advancement_dir = 'advancement' if singular else 'advancements'
    block_tag_dir = 'block' if singular else 'blocks'

    def ingredient(name):
        return name if simple else {('tag' if name.startswith('#') else 'item'): name.removeprefix('#')}

    def recipe(name, pattern, keys, result, count, unlock):
        write_json(data / recipe_dir / (name + '.json'), {
            'type': 'minecraft:crafting_shaped', 'category': 'misc',
            'pattern': pattern, 'key': {k: ingredient(v) for k, v in keys.items()},
            'result': {('id' if components else 'item'): result, 'count': count}})
        write_json(data / advancement_dir / 'recipes' / (name + '.json'), {
            'parent': 'minecraft:recipes/root',
            'criteria': {'has_material': {'trigger': 'minecraft:inventory_changed',
                'conditions': {'items': [{'items': [unlock]}]}},
                'has_recipe': {'trigger': 'minecraft:recipe_unlocked', 'conditions': {'recipe': f'{MOD}:{name}'}}},
            'requirements': [['has_material', 'has_recipe']], 'rewards': {'recipes': [f'{MOD}:{name}']}})

    recipe('gunpowder', ['SNC'], {'S': f'{MOD}:sulfur', 'N': f'{MOD}:saltpeter',
           'C': 'minecraft:charcoal'}, 'minecraft:gunpowder', 8, f'{MOD}:sulfur')
    recipe('humus', ['LWL', 'LDL', 'LSL'], {'L': '#minecraft:leaves', 'W': 'minecraft:wheat',
           'D': 'minecraft:dirt', 'S': 'minecraft:wheat_seeds'}, f'{MOD}:humus', 4, 'minecraft:dirt')
    # Saltpeter is obtained exclusively by using humus on a composter.
    # Remove obsolete generated recipes when updating an existing target.
    (data / recipe_dir / 'saltpeter.json').unlink(missing_ok=True)
    (data / advancement_dir / 'recipes/saltpeter.json').unlink(missing_ok=True)

    milestones = [
        ('root', None, 'humus', 'task'),
        ('saltpeter', 'root', 'saltpeter', 'task'),
        ('sulfur', 'root', 'sulfur', 'task'),
        ('ingredients', 'saltpeter', 'sulfur', 'goal'),
        ('gunpowder', 'ingredients', 'minecraft:gunpowder', 'challenge'),
    ]
    for name, parent, icon, frame in milestones:
        icon_id = icon if ':' in icon else f'{MOD}:{icon}'
        display = {'icon': {('id' if components else 'item'): icon_id},
                   'title': {'translate': f'advancements.{MOD}.{name}.title'},
                   'description': {'translate': f'advancements.{MOD}.{name}.description'},
                   'frame': frame, 'show_toast': True, 'announce_to_chat': True, 'hidden': False}
        if parent is None:
            display['background'] = 'minecraft:textures/block/stone.png'
        items = ([f'{MOD}:sulfur', f'{MOD}:saltpeter', 'minecraft:charcoal'] if name == 'ingredients' else [icon_id])
        criterion = {'trigger': 'minecraft:inventory_changed',
                     'conditions': {'items': [{'items': [item]} for item in items]}}
        if name == 'gunpowder':
            criterion = {'trigger': 'minecraft:recipe_crafted', 'conditions': {'recipe_id': f'{MOD}:gunpowder'}}
        value = {'display': display, 'criteria': {'complete': criterion}, 'requirements': [['complete']]}
        if parent:
            value['parent'] = f'{MOD}:{parent}'
        if name == 'gunpowder':
            value['rewards'] = {'experience': 50}
        write_json(data / advancement_dir / f'{name}.json', value)

    silk = {'enchantments': 'minecraft:silk_touch', 'levels': {'min': 1}}
    silk_predicate = ({'predicates': {'minecraft:enchantments': [silk]}} if components else
                      {'enchantments': [{'enchantment': 'minecraft:silk_touch', 'levels': {'min': 1}}]})
    for name in ('sulfur_ore', 'deepslate_sulfur_ore'):
        write_json(data / loot_dir / 'blocks' / f'{name}.json', {
            'type': 'minecraft:block', 'pools': [{'rolls': 1, 'entries': [{
                'type': 'minecraft:alternatives', 'children': [
                    {'type': 'minecraft:item', 'name': f'{MOD}:{name}', 'conditions': [{
                        'condition': 'minecraft:match_tool', 'predicate': silk_predicate}]},
                    {'type': 'minecraft:item', 'name': f'{MOD}:sulfur', 'functions': [
                        {'function': 'minecraft:apply_bonus', 'enchantment': 'minecraft:fortune',
                         'formula': 'minecraft:ore_drops'}, {'function': 'minecraft:explosion_decay'}]}]}]}]})
        write_json(assets / 'blockstates' / f'{name}.json', {'variants': {'': {'model': f'{MOD}:block/{name}'}}})
        write_json(assets / 'models/block' / f'{name}.json', {
            'parent': 'minecraft:block/cube_all', 'textures': {'all': f'{MOD}:block/{name}'}})
        write_json(assets / 'models/item' / f'{name}.json', {'parent': f'{MOD}:block/{name}'})
    for name in ('sulfur', 'saltpeter', 'humus'):
        write_json(assets / 'models/item' / f'{name}.json', {
            'parent': 'minecraft:item/generated', 'textures': {'layer0': f'{MOD}:item/{name}'}})
    if version >= (1, 21, 4):
        for name in ('sulfur', 'saltpeter', 'humus', 'sulfur_ore', 'deepslate_sulfur_ore'):
            write_json(assets / 'items' / f'{name}.json', {'model': {
                'type': 'minecraft:model', 'model': f'{MOD}:item/{name}'}})
    for tag in ('mineable/pickaxe', 'needs_stone_tool'):
        write_json(out / 'data/minecraft/tags' / block_tag_dir / f'{tag}.json', {
            'replace': False, 'values': [f'{MOD}:sulfur_ore', f'{MOD}:deepslate_sulfur_ore']})

    write_json(data / 'worldgen/configured_feature/sulfur_ore.json', {'type': 'minecraft:ore', 'config': {
        'size': 8, 'discard_chance_on_air_exposure': 0.0, 'targets': [
            {'target': {'predicate_type': 'minecraft:tag_match', 'tag': f'minecraft:{stone}_ore_replaceables'},
             'state': {'Name': f'{MOD}:{ore}'}} for stone, ore in
            [('stone', 'sulfur_ore'), ('deepslate', 'deepslate_sulfur_ore')]]}})
    write_json(data / 'worldgen/placed_feature/sulfur_ore.json', {'feature': f'{MOD}:sulfur_ore', 'placement': [
        {'type': 'minecraft:count', 'count': 6}, {'type': 'minecraft:in_square'},
        {'type': 'minecraft:height_range', 'height': {'type': 'minecraft:trapezoid',
            'min_inclusive': {'absolute': -48}, 'max_inclusive': {'absolute': 80}}},
        {'type': 'minecraft:biome'}]})
    if loader != 'fabric':
        namespace = 'forge' if loader == 'forge' or mc == '1.20.1' else 'neoforge'
        write_json(data / namespace / 'biome_modifier/add_sulfur_ore.json', {
            'type': f'{namespace}:add_features', 'biomes': '#minecraft:is_overworld',
            'features': f'{MOD}:sulfur_ore', 'step': 'underground_ores'})

    for lang, names in {
        'en_us': ['Sulfur', 'Saltpeter', 'Humus', 'Sulfur Ore', 'Deepslate Sulfur Ore'],
        'ru_ru': ['Сера', 'Селитра', 'Перегной', 'Серная руда', 'Глубинная серная руда'],
    }.items():
        keys = ['item.' + MOD + '.' + i for i in ('sulfur', 'saltpeter', 'humus')]
        keys += ['block.' + MOD + '.' + b for b in ('sulfur_ore', 'deepslate_sulfur_ore')]
        translations = dict(zip(keys, names))
        texts = ([('Craftable Gunpowder', 'Craft humus to start making your own gunpowder'),
                  ('Composter chemistry', 'Obtain saltpeter by processing humus'),
                  ('Yellow treasure', 'Obtain sulfur from sulfur ore'),
                  ('All the ingredients', 'Carry sulfur, saltpeter and charcoal together'),
                  ('Home-made fireworks', 'Craft gunpowder from sulfur, saltpeter and charcoal')]
                 if lang == 'en_us' else
                 [('Порох своими руками', 'Создайте перегной — первый шаг к собственному пороху'),
                  ('Химия в компостнице', 'Получите селитру, переработав перегной'),
                  ('Жёлтое сокровище', 'Добудьте серу из серной руды'),
                  ('Всё по рецепту', 'Соберите в инвентаре серу, селитру и древесный уголь'),
                  ('Сам себе крипер', 'Создайте порох из серы, селитры и древесного угля')])
        for (name, *_), (title, description) in zip(milestones, texts):
            translations[f'advancements.{MOD}.{name}.title'] = title
            translations[f'advancements.{MOD}.{name}.description'] = description
        write_json(assets / 'lang' / f'{lang}.json', translations)
    if (ROOT / 'shared/assets').exists():
        shutil.copytree(ROOT / 'shared/assets', out / 'assets', dirs_exist_ok=True)
    if (ROOT / 'art/icon.png').exists():
        shutil.copy2(ROOT / 'art/icon.png', out / 'icon.png')

    formats = {'1.20.1': 15, '1.20.4': 26, '1.20.6': 41, '1.21.1': 48,
               '1.21.4': 61, '1.21.5': 71, '1.21.8': 81, '1.21.11': 94, '26.1': 101, '26.2': 107}
    resource_formats = {'1.20.1': 15, '1.20.4': 22, '1.20.6': 32, '1.21.1': 34,
                        '1.21.4': 46, '1.21.5': 55, '1.21.8': 64, '1.21.11': 75, '26.1': 84, '26.2': 88}
    # A mod carries both a client resource pack and server data pack. The range
    # must include both format numbers, which Mojang versions independently.
    pack = {'pack_format': resource_formats[mc], 'description': 'Craftable Gunpowder by iwoss'}
    if version >= (1, 21, 11):
        pack.update(min_format=[resource_formats[mc], 0], max_format=[formats[mc], 1])
        if resource_formats[mc] < 82:
            # The combined mod pack spans the transition to fractional data
            # versions; Minecraft also requires a legacy range below 82.
            pack['supported_formats'] = [resource_formats[mc], 81]
    elif version >= (1, 20, 2):
        pack['supported_formats'] = {'min_inclusive': resource_formats[mc], 'max_inclusive': formats[mc]}
    write_json(out / 'pack.mcmeta', {'pack': pack})
