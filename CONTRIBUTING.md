# Building Craftable Gunpowder

## Requirements

- Python 3.10 or newer.
- Java 21 for Forge and older NeoForge build tooling; Java 25 for Fabric tooling and Minecraft 26.x.
- Java toolchains 17, 21 and 25 are resolved by Gradle as required by the target. Gradle itself is provided by the wrapper.
- Pillow is only needed to re-export the original generated artwork.

## One target

```sh
python tools/prepare.py --minecraft 1.21.1 --loader neoforge
cd .build/1.21.1-neoforge
./gradlew build
```

On Windows use `gradlew.bat`. `runClient` starts a development client; `runServer` starts a development server. The generated `.build/` directory is disposable; edit the shared sources instead.

## Build matrix

From the repository root:

```sh
python -m unittest discover -s tests -v
python tools/build_matrix.py --target 1.21.1-neoforge
python tools/build_matrix.py --jobs 2
python tools/audit_jars.py
```

Set `JAVA_HOME_17`, `JAVA_HOME_21` and `JAVA_HOME_25` to override local JDK paths. The equivalent `JAVA_HOME_<version>_X64` variables from setup-java are also recognized.

Runtime artifacts go to `dist/`; logs and build records go to `.local/`. Artifact auditing verifies exact Minecraft dependencies, author metadata, bytecode versions, remapping, textures, recipes and exclusion of development-only checks. It writes `SHA256SUMS.txt` and `manifest.json`.

## Integration checks

```sh
python tools/smoke_server.py --target 1.21.1-neoforge --accept-eula
python tools/smoke_server.py --all --jobs 2 --accept-eula
```

`--accept-eula` acknowledges the [Minecraft EULA](https://aka.ms/MinecraftEULA) for the local test server. Each target uses an isolated `run/smoke-world` directory and binds only to `127.0.0.1`. The script stops its server afterward.

Checks cover item registration, the actual humus item interaction, consumption on successful and unsuccessful attempts, deterministic 25% saltpeter rolls, drop identity/count, creative behavior, full-composter rejection, ore loot, Silk Touch, placed ore features and data reloads. On Minecraft 1.21.1 and newer, the vanilla crafter also tests the humus/gunpowder recipes, coal rejection and rejection of a 2×2 ingredient layout.

`tests/java/IntegrationChecks.java` and its command registration are included only in the generated development project used by the smoke runner. They are **never included in release JARs**. Always prepare/build normally before producing distribution artifacts.

These checks do not cover client rendering, manual player interaction or compatibility with third-party mods.

## Source layout

| Path | Purpose |
|---|---|
| `src/templates/` | Shared Java sources and loader entrypoints |
| `tools/prepare.py` | Version-specific API and Gradle adaptation |
| `tools/resources.py` | Recipes, loot, world generation, models and translations |
| `versions.json` | Pinned Minecraft/loader matrix |
| `shared/assets/` | Packaged textures |
| `art/source/` | Original generated artwork |
| `tests/` | Resource contracts and development-only integration checks |

`tools/resolve_versions.py` refreshes dependency versions from official metadata. Review and test all changed targets before committing a dependency update.
