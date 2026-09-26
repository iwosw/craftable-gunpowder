<p align="center">
  <img src="art/icon.png" width="96" alt="Craftable Gunpowder">
</p>

<h1 align="center">Craftable Gunpowder</h1>
<p align="center">Mine sulfur. Compost humus. Craft gunpowder.</p>
<p align="center">
  <a href="https://github.com/iwosw/craftable-gunpowder/actions/workflows/build.yml"><img src="https://github.com/iwosw/craftable-gunpowder/actions/workflows/build.yml/badge.svg" alt="Build and tests"></a>
  <a href="https://github.com/iwosw/craftable-gunpowder/releases"><img src="https://img.shields.io/github/v/release/iwosw/craftable-gunpowder" alt="Latest release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/author-iwoss-yellow" alt="Author: iwoss">
</p>
<p align="center"><b>English</b> · <a href="README.ru.md">Русский</a> · <a href="https://github.com/iwosw/craftable-gunpowder/releases">Download</a> · <a href="https://github.com/iwosw/craftable-gunpowder/issues">Report an issue</a></p>

![Sulfur, sulfur ore, deepslate sulfur ore, saltpeter and humus](art/texture-preview.png)

A small Minecraft Java mod by **iwoss**, adding a resource-based way to obtain gunpowder.

**1 sulfur + 1 saltpeter + 1 charcoal → 8 gunpowder.** Regular coal is not accepted.

## Features

Version **1.1.0** adds a shared `config/craftablegunpowder.json` for drops, composting, recipe output, ore generation, block properties and feature toggles, plus five localized advancements. Restart after editing settings. [Configuration reference](docs/CONFIG.md). Gameplay quantities below are the defaults.

- Sulfur ore and deepslate sulfur ore in the Overworld.
- Humus crafted from plant materials; saltpeter obtained from a vanilla composter.
- **25% chance** to receive one saltpeter per humus used on a composter.
- Crafting-table recipes, recipe-book unlocks, Fortune and Silk Touch support.
- Original 16×16 textures, English and Russian translations.
- Separate builds for Fabric, Forge and NeoForge.

## Installation

1. Install a supported loader for your **exact Minecraft version** from the table below.
2. Download the matching JAR from [Releases](https://github.com/iwosw/craftable-gunpowder/releases) and put it in `mods`.
3. **Fabric requires Fabric API.** Forge and NeoForge need no additional mods.

Install on **both the client and the server**. Use only one Craftable Gunpowder JAR per installation. Example: `craftable-gunpowder-1.21.1-neoforge-1.1.0.jar` is for Minecraft 1.21.1 with NeoForge.

## Getting started

### 1. Mine sulfur

Find sulfur ore in **new Overworld chunks**, between **Y −48 and 80**. Mine it with a **stone pickaxe or better**. Fortune increases sulfur drops; Silk Touch preserves the ore block.

### 2. Craft humus

Combine **6 leaves, 1 wheat, 1 dirt and 1 wheat seed** at a crafting table to obtain **4 humus**:

| | | |
|---|---|---|
| Leaves | Wheat | Leaves |
| Leaves | Dirt | Leaves |
| Leaves | Wheat Seeds | Leaves |

Any leaves in the `minecraft:leaves` tag work.

### 3. Use a composter

**Right-click a non-full vanilla composter while holding humus.** Each attempt consumes one humus and has a **25% chance** to drop **one saltpeter** above the composter. Unsuccessful attempts still consume humus.

This special interaction processes humus directly without filling the vanilla composting bar. Empty a full composter before using humus. Dropping items with Q or feeding a hopper does not trigger the interaction. Saltpeter has **no crafting recipe**.

### 4. Craft gunpowder

Place the ingredients in **one horizontal row** of a crafting table:

| | | |
|---|---|---|
| Sulfur | Saltpeter | **Charcoal** |

**Output: 8 vanilla gunpowder.** Any row and the mirrored arrangement work. The inventory's 2×2 grid is too small. Vanilla crafters also support the recipe in versions that have them.

## Supported versions

**10 Minecraft releases · 24 separate builds.** Only the exact versions listed here are supported.

| Minecraft | Fabric | Forge | NeoForge | Java |
|---|:---:|:---:|:---:|:---:|
| 1.20.1 | ✓ | ✓ | ✓¹ | 17 |
| 1.20.4 | ✓ | ✓ | ✓ | 17 |
| 1.20.6 | ✓ | ✓ | ✓ | 21 |
| 1.21.1 | ✓ | ✓ | ✓ | 21 |
| 1.21.4 | ✓ | — | ✓ | 21 |
| 1.21.5 | ✓ | — | ✓ | 21 |
| 1.21.8 | ✓ | — | ✓ | 21 |
| 1.21.11 | ✓ | — | ✓ | 21 |
| 26.1 | ✓ | — | ✓² | 25 |
| 26.2 | ✓ | — | ✓ | 25 |

¹ NeoForge 1.20.1 uses its original Forge-compatible branch.

² Minecraft 26.1 uses **NeoForge 26.1.0.19-beta**. This is not a 26.1.2 build.

Exact loader and Fabric API versions are pinned in [versions.json](versions.json). The mod's sulfur uses its own namespace, including on Minecraft 26.2.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for build instructions and automated checks. GitHub Actions builds each target and boots an isolated test server. Client visuals and compatibility with other mods are not covered by those server checks.

[1.1.0 local verification results: all 24 builds and server checks passed.](docs/VALIDATION.md)

## Credits & license

Created by **iwoss**. The icon was supplied by the author; all five textures were generated for this project with ImageGen. [Artwork sources and prompts](art/README.md).

Released under the [MIT License](LICENSE). Modpack inclusion is welcome under the license terms.

Not an official Minecraft product. Not approved by or associated with Mojang or Microsoft.
