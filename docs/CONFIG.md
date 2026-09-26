# Configuration

Craftable Gunpowder 1.1.0 creates `config/craftablegunpowder.json` on first launch. Stop the game/server, edit it, then restart. `/reload` does not reread configuration. Missing keys keep their defaults. Invalid types, fractional counts and out-of-range values stop loading with a descriptive error, preserving the file.

[Complete default configuration](config-example.json).

Server settings control drops, composting, recipes, world generation and advancements. Use matching block hardness/resistance settings on clients and servers for consistent mining progress. World generation affects new chunks only. Existing items and blocks remain registered when features are disabled.

| Keys | Default | Range / purpose |
|---|---|---|
| `compostingEnabled` | `true` | Humus processing |
| `saltpeterChance` | `0.25` | 0…1 |
| `saltpeterMin`, `saltpeterMax` | `1`, `1` | 1…64 per success, uniform random |
| `humusConsumed` | `1` | 1…64 per attempt; insufficient stacks cannot be used |
| `consumeHumusOnFailure` | `true` | Consume input after failed rolls |
| `allowFullComposter` | `false` | Allow full vanilla composters |
| `sulfurDropsEnabled`, `sulfurDropChance` | `true`, `1.0` | Sulfur drops and probability 0…1 |
| `sulfurMin`, `sulfurMax` | `1`, `1` | 1…64 before vanilla Fortune multiplication |
| `fortuneEnabled`, `silkTouchEnabled` | `true`, `true` | Fortune bonus / intact ore with Silk Touch |
| `explosionDecay` | `true` | Vanilla explosion reduction for sulfur drops |
| `oreGenerationEnabled` | `true` | Overworld ore generation |
| `veinSize`, `veinsPerChunk` | `8`, `6` | 1…64 blocks; 0…256 attempts |
| `minY`, `maxY` | `-48`, `80` | −64…319 |
| `discardOnAirExposure` | `0.0` | 0…1 |
| `oreHardness`, `deepslateOreHardness` | `3.0`, `4.5` | 0…1000 |
| `oreBlastResistance` | `3.0` | 0…3600000 |
| `gunpowderRecipeEnabled`, `humusRecipeEnabled` | `true`, `true` | Recipes and their book unlocks |
| `gunpowderCount`, `humusCount` | `8`, `4` | 1…64 items per craft |
| `advancementsEnabled` | `true` | Five visible advancements |
| `finalAdvancementExperience` | `50` | 0…1000000 XP |

Every minimum must be ≤ its maximum. Creative players never consume humus. Both ore variants share drop settings. Silk Touch takes precedence over sulfur rolls; disable both sulfur drops and Silk Touch for no loot.

Example partial config:

```json
{"saltpeterChance": 1.0, "sulfurMin": 2, "sulfurMax": 3, "gunpowderCount": 16}
```

The final advancement requires a player to craft the mod's gunpowder recipe. Creeper drops and automated crafters do not award it. Disabling visible advancements does not disable the recipe book or reclaim XP already awarded.

`config/craftablegunpowder-generated/` is generated automatically; do not edit it. The required `craftablegunpowder_config` data pack loads for existing worlds, new worlds and integrated servers. Higher-priority ordinary data packs can replace recipe ingredients/layouts or other advanced data.
