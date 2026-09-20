"""Prepare one independent, reproducible Gradle project from shared sources."""
import argparse
import json
import shutil
from pathlib import Path
from resources import generate, ver, write_json

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / 'versions.json').read_text())
MOD = 'craftablegunpowder'

def substitute(template, values):
    text = (ROOT / 'src/templates' / template).read_text(encoding='utf-8')
    for key, value in values.items():
        text = text.replace('@' + key + '@', value)
    import re
    assert not re.search(r'@[A-Z_]+@', text), template
    return text

def prepare(row, integration=False):
    mc, loader = row['minecraft'], row['loader']
    v = ver(mc)
    modern = v >= (26, 1)
    neo = loader == 'neoforge' and mc != '1.20.1'
    oldneo = neo and v < (1, 21)
    forge = loader == 'forge' or (loader == 'neoforge' and mc == '1.20.1')
    out = ROOT / '.build' / f'{mc}-{loader}'
    out.mkdir(parents=True, exist_ok=True)
    java = out / 'src/main/java/dev/iwoss/craftablegunpowder'
    java.mkdir(parents=True, exist_ok=True)
    resources = out / 'src/main/resources'
    resources.mkdir(parents=True, exist_ok=True)

    identifier = 'Identifier' if v >= (1, 21, 11) else 'ResourceLocation'
    values = dict(IDENTIFIER=identifier,
                  INTEGRATION_HOOK='',
                  ID_FACTORY=f'{identifier}.fromNamespaceAndPath(MOD_ID, path)' if v >= (1, 21) else 'new ResourceLocation(MOD_ID, path)',
                  ITEM_ID='properties.setId(ResourceKey.create(Registries.ITEM, id(name)));' if v >= (1, 21, 2) else '',
                  BLOCK_ID='properties.setId(ResourceKey.create(Registries.BLOCK, id(name)));' if v >= (1, 21, 2) else '',
                  BLOCK_DESCRIPTION='properties.useBlockDescriptionPrefix();' if v >= (1, 21, 2) else '')
    (java / 'Content.java').write_text(substitute('Content.java', values), encoding='utf-8')
    (java / 'HumusItem.java').write_text(substitute('HumusItem.java', values), encoding='utf-8')
    integration_file = java / 'IntegrationChecks.java'
    if integration:
        shutil.copy2(ROOT / 'tests/java/IntegrationChecks.java', integration_file)
    else:
        integration_file.unlink(missing_ok=True)
    if loader == 'fabric':
        values.update(TAB_PACKAGE='creativetab.v1' if modern else 'itemgroup.v1',
                      TAB_EVENTS='CreativeModeTabEvents' if modern else 'ItemGroupEvents',
                      TAB_METHOD='modifyOutputEvent' if modern else 'modifyEntriesEvent')
        entry = 'FabricEntrypoint'
        if integration:
            values['INTEGRATION_HOOK'] = 'net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback.EVENT.register((dispatcher, access, environment) -> IntegrationChecks.register(dispatcher));'
    else:
        values.update(FORGE_PACKAGE='net.neoforged.neoforge' if neo else 'net.minecraftforge',
                      BUS_PACKAGE='net.neoforged.bus.api' if neo else 'net.minecraftforge.eventbus.api',
                      FML_PACKAGE='net.neoforged.fml' if neo else 'net.minecraftforge.fml',
                      CONTEXT_IMPORT='' if neo else 'import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;',
                      BUS_ARGUMENT='IEventBus bus' if neo else '',
                      BUS_LOOKUP='' if neo else 'IEventBus bus = FMLJavaModLoadingContext.get().getModEventBus();')
        entry = 'ForgeEntrypoint'
        if integration:
            bus_owner = 'net.neoforged.neoforge.common.NeoForge' if neo else 'net.minecraftforge.common.MinecraftForge'
            values['INTEGRATION_HOOK'] = f'{bus_owner}.EVENT_BUS.addListener(({values["FORGE_PACKAGE"]}.event.RegisterCommandsEvent event) -> IntegrationChecks.register(event.getDispatcher()));'
    (java / f'{entry}.java').write_text(substitute(f'{entry}.java', values), encoding='utf-8')
    generate(resources, mc, loader)

    if loader == 'fabric':
        write_json(resources / 'fabric.mod.json', {
            'schemaVersion': 1, 'id': MOD, 'version': CONFIG['mod_version'], 'name': 'Craftable Gunpowder',
            'description': 'Mine sulfur, use humus on a composter for saltpeter, and craft 8 gunpowder with charcoal.',
            'authors': ['iwoss'], 'contact': {'sources': 'https://github.com/iwosw/craftable-gunpowder',
                'issues': 'https://github.com/iwosw/craftable-gunpowder/issues'},
            'license': 'MIT', 'icon': 'icon.png', 'environment': '*',
            'entrypoints': {'main': ['dev.iwoss.craftablegunpowder.FabricEntrypoint']},
            'depends': {'fabricloader': '>=' + row['loader_version'], 'minecraft': mc,
                        'java': '>=' + str(row['java']), 'fabric-api': '*'}})
    else:
        dep_id = 'neoforge' if neo else 'forge'
        toml_name = 'neoforge.mods.toml' if neo and v >= (1, 20, 6) else 'mods.toml'
        required = 'type="required"' if neo else 'mandatory=true'
        loader_range = '[1,)' if neo else '[' + row['loader_version'].split('-')[-1].split('.')[0] + ',)'
        loader_version = row['loader_version'].split('-', 1)[1] if forge else row['loader_version']
        text = f'''modLoader="javafml"
loaderVersion="{loader_range}"
license="MIT"
issueTrackerURL="https://github.com/iwosw/craftable-gunpowder/issues"
[[mods]]
modId="{MOD}"
version="{CONFIG['mod_version']}"
displayName="Craftable Gunpowder"
displayURL="https://github.com/iwosw/craftable-gunpowder"
logoFile="icon.png"
authors="iwoss"
description=''' + "'''Mine sulfur, use humus on a composter for a 25% chance of saltpeter, and craft 8 gunpowder with charcoal.'''" + f'''
[[dependencies.{MOD}]]
modId="{dep_id}"
{required}
versionRange="[{loader_version},)"
ordering="NONE"
side="BOTH"
[[dependencies.{MOD}]]
modId="minecraft"
{required}
versionRange="[{mc}]"
ordering="NONE"
side="BOTH"
'''
        (resources / 'META-INF').mkdir(exist_ok=True)
        (resources / 'META-INF' / toml_name).write_text(text, encoding='utf-8')

    settings = '''pluginManagement {
    repositories {
        maven { url = 'https://maven.fabricmc.net/' }
        maven { url = 'https://maven.neoforged.net/releases' }
        maven { url = 'https://maven.minecraftforge.net/' }
        gradlePluginPortal()
    }
}
plugins { id 'org.gradle.toolchains.foojay-resolver-convention' version '1.0.0' }
rootProject.name = 'craftable-gunpowder'
'''
    (out / 'settings.gradle').write_text(settings, encoding='utf-8')
    if loader == 'fabric':
        plugin = 'net.fabricmc.fabric-loom' if modern else 'net.fabricmc.fabric-loom-remap'
        dependency = 'implementation' if modern else 'modImplementation'
        build = f"plugins {{ id '{plugin}' version '{CONFIG['loom']}' }}\n"
        build += f'''dependencies {{
    minecraft 'com.mojang:minecraft:{mc}'
    {dependency} 'net.fabricmc:fabric-loader:{row['loader_version']}'
    {dependency} 'net.fabricmc.fabric-api:fabric-api:{row['fabric_api']}'
'''
        if not modern:
            build += '    mappings loom.officialMojangMappings()\n'
        build += '}\n'
        build += f"loom {{ mods {{ {MOD} {{ sourceSet sourceSets.main }} }} }}\n"
    elif forge or oldneo:
        plugin = 'net.neoforged.gradle.userdev' if oldneo else 'net.minecraftforge.gradle'
        plugin_version = '7.1.38' if oldneo else '6.0.54'
        build = f"plugins {{ id 'java'; id '{plugin}' version '{plugin_version}' }}\n"
        if forge:
            group = 'net.neoforged' if loader == 'neoforge' else 'net.minecraftforge'
            build += f'''minecraft {{
    mappings channel: 'official', version: '{mc}'
    runs {{
        configureEach {{
            property 'terminal.jline', 'false'
            property 'terminal.ansi', 'false'
        }}
        server {{
            workingDirectory project.file('run')
            args '--nogui'
            mods {{ {MOD} {{ source sourceSets.main }} }}
        }}
        client {{
            workingDirectory project.file('run-client')
            mods {{ {MOD} {{ source sourceSets.main }} }}
        }}
    }}
}}
repositories {{ maven {{ url = 'https://maven.neoforged.net/releases' }} }}
dependencies {{ minecraft '{group}:forge:{row['loader_version']}' }}
'''
            if v < (1, 20, 6):
                build += "tasks.named('jar').configure { finalizedBy 'reobfJar' }\n"
        else:
            build += f'''dependencies {{ implementation 'net.neoforged:neoforge:{row['loader_version']}' }}
runs {{
    configureEach {{ modSource sourceSets.main; workingDirectory file('run') }}
    server {{ arguments '--nogui' }}
    client {{ }}
}}
'''
    else:
        build = f'''plugins {{ id 'net.neoforged.moddev' version '2.0.147' }}
neoForge {{
    enable {{ version = '{row['loader_version']}'; disableRecompilation = true }}
    runs {{
        server {{ server(); gameDirectory = file('run'); programArgument '--nogui' }}
        client {{ client() }}
    }}
    mods {{ {MOD} {{ sourceSet sourceSets.main }} }}
}}
'''
    build += f'''
group = 'dev.iwoss'
version = '{CONFIG['mod_version']}'
base {{ archivesName = 'craftable-gunpowder-{mc}-{loader}' }}
java {{ toolchain.languageVersion = JavaLanguageVersion.of({row['java']}); withSourcesJar() }}
tasks.withType(JavaCompile).configureEach {{ options.encoding = 'UTF-8' }}
tasks.withType(AbstractArchiveTask).configureEach {{
    preserveFileTimestamps = false
    reproducibleFileOrder = true
}}
jar {{ from('LICENSE') }}
'''
    if forge and v >= (1, 20, 4):
        # Current Forge's module finder requires each source set's classes and
        # resources to share one directory (also used by the official MDK).
        build += '''sourceSets.each {
    def merged = layout.buildDirectory.dir("sourceSets/${it.name}")
    it.output.resourcesDir = merged
    it.java.destinationDirectory = merged
}
'''
    (out / 'build.gradle').write_text(build, encoding='utf-8')
    (out / 'gradle.properties').write_text('org.gradle.jvmargs=-Xmx2G\norg.gradle.workers.max=2\norg.gradle.daemon=false\n', encoding='utf-8')
    for file in ('gradlew', 'gradlew.bat', 'LICENSE'):
        shutil.copy2(ROOT / file, out / file)
    (out / 'gradle/wrapper').mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / 'gradle/wrapper/gradle-wrapper.jar', out / 'gradle/wrapper/gradle-wrapper.jar')
    gradle = '8.14.3' if forge or oldneo else '9.6.0'
    (out / 'gradle/wrapper/gradle-wrapper.properties').write_text(
        f'distributionBase=GRADLE_USER_HOME\ndistributionPath=wrapper/dists\n'
        f'distributionUrl=https\\://services.gradle.org/distributions/gradle-{gradle}-bin.zip\n'
        'networkTimeout=60000\nvalidateDistributionUrl=true\nzipStoreBase=GRADLE_USER_HOME\nzipStorePath=wrapper/dists\n')
    return out

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--minecraft')
    parser.add_argument('--loader', choices=['fabric', 'forge', 'neoforge'])
    parser.add_argument('--all', action='store_true')
    args = parser.parse_args()
    rows = [r for r in CONFIG['targets'] if args.all or
            (r['minecraft'] == args.minecraft and r['loader'] == args.loader)]
    if not rows:
        parser.error('Select a supported --minecraft / --loader pair, or --all')
    for row in rows:
        print(prepare(row).relative_to(ROOT).as_posix())
