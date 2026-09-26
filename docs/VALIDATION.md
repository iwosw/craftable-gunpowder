# Release validation — 1.1.0

These results cover the local checks for version 1.1.0. The GitHub Actions link at the end refers to the previous 1.0.0 validation.

- **24/24** target builds completed successfully (local logs from September 22, 2026).
- **24/24** target servers started and passed integration checks. The saved reports include 27 successful runs total: the 24-target matrix and three additional custom-configuration runs.
- The server checks cover mod content, humus use and consumption, saltpeter rolls, ore drops, Silk Touch, feature placement and data reload.
- **15/15** targets with the vanilla crafter passed recipe checks for the configured gunpowder and humus output counts, rejection of regular coal and rejection of the 2×2 layout.
- Three custom configurations passed on Forge 1.20.1, NeoForge 1.21.1 and Fabric 26.2. They exercised guaranteed saltpeter, custom sulfur drops, disabled Fortune and Silk Touch, altered recipe outputs, ore generation and block properties, and advancement experience.
- **5/5** resource-contract tests passed locally on September 26, 2026.
- **24/24** distributable 1.1.0 JARs passed the artifact audit on September 26, 2026. The audit checked archive integrity, loader metadata, target versions, bytecode, remapping, textures, default config-pack resources, recipes and exclusion of development-only integration hooks.
- A local NeoForge 1.21.1 client session started, loaded the built-in config data pack and created a world. This was a single client check, not a visual test across every target or a compatibility test with third-party mods.

The server integration runs use each target's development build. The separate release JARs passed the artifact audit; the tests do not establish compatibility with every modpack.

The previous [GitHub Actions validation](https://github.com/iwosw/craftable-gunpowder/actions/runs/35497362262) applies to **version 1.0.0**, not 1.1.0.
