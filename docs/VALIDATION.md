# Release validation — 1.0.0

Tested implementation: [`af68663`](https://github.com/iwosw/craftable-gunpowder/commit/af68663012c9181005bed88990b624fad1fede45).

[GitHub Actions run](https://github.com/iwosw/craftable-gunpowder/actions/runs/35497362262): **passed**, September 20, 2026.

- **24/24** runtime JARs built successfully.
- **24/24** isolated servers started and passed content checks.
- **24/24** composter integration checks passed: humus interaction, consumption, fixed-seed 25% rolls, saltpeter item/count, creative handling and invalid-target rejection.
- **24/24** ore-drop, Silk Touch, feature-placement and data-reload checks passed.
- **15/15** targets with a vanilla crafter passed real recipe-manager checks: 8 gunpowder, 4 humus, coal rejection and rejection of a 2×2 ingredient layout.
- Resource-contract tests passed for all 24 targets.
- All 24 downloaded artifacts passed metadata, PNG, Java bytecode, Fabric remapping, recipe and development-code exclusion audits. No obsolete saltpeter crafting recipe is packaged.

| Minecraft | Loader | Build | Server + composter | In-game crafting |
|---|---|:---:|:---:|:---:|
| 1.20.1 | Fabric | Pass | Pass | — |
| 1.20.1 | Forge | Pass | Pass | — |
| 1.20.1 | NeoForge | Pass | Pass | — |
| 1.20.4 | Fabric | Pass | Pass | — |
| 1.20.4 | Forge | Pass | Pass | — |
| 1.20.4 | NeoForge | Pass | Pass | — |
| 1.20.6 | Fabric | Pass | Pass | — |
| 1.20.6 | Forge | Pass | Pass | — |
| 1.20.6 | NeoForge | Pass | Pass | — |
| 1.21.1 | Fabric | Pass | Pass | Pass |
| 1.21.1 | Forge | Pass | Pass | Pass |
| 1.21.1 | NeoForge | Pass | Pass | Pass |
| 1.21.4 | Fabric | Pass | Pass | Pass |
| 1.21.4 | NeoForge | Pass | Pass | Pass |
| 1.21.5 | Fabric | Pass | Pass | Pass |
| 1.21.5 | NeoForge | Pass | Pass | Pass |
| 1.21.8 | Fabric | Pass | Pass | Pass |
| 1.21.8 | NeoForge | Pass | Pass | Pass |
| 1.21.11 | Fabric | Pass | Pass | Pass |
| 1.21.11 | NeoForge | Pass | Pass | Pass |
| 26.1 | Fabric | Pass | Pass | Pass |
| 26.1 | NeoForge | Pass | Pass | Pass |
| 26.2 | Fabric | Pass | Pass | Pass |
| 26.2 | NeoForge | Pass | Pass | Pass |

The 1.20.x targets have recipe data/schema checks and successful game data loading; the automatic vanilla-crafter test runs only on 1.21.1 and newer. Servers run the development variant of each target. Distributed runtime JARs are built separately and audited; development-only test classes and command hooks are excluded.

**Not covered:** manual mouse interaction, client rendering and compatibility with third-party mods. Server checks do not establish those properties.

Per-target logs and JSON reports are attached to the linked Actions run as `build-log-*` artifacts. Release files include `SHA256SUMS.txt` and `manifest.json` for integrity verification.
