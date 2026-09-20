package dev.iwoss.craftablegunpowder;

import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.biome.v1.BiomeModifications;
import net.fabricmc.fabric.api.biome.v1.BiomeSelectors;
import net.fabricmc.fabric.api.@TAB_PACKAGE@.@TAB_EVENTS@;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.levelgen.GenerationStep;

public final class FabricEntrypoint implements ModInitializer {
    @Override
    public void onInitialize() {
        Item sulfur = item("sulfur");
        Item saltpeter = item("saltpeter");
        Item humus = item("humus");
        Item sulfurOre = ore("sulfur_ore", false);
        Item deepslateOre = ore("deepslate_sulfur_ore", true);

        @TAB_EVENTS@.@TAB_METHOD@(CreativeModeTabs.INGREDIENTS).register(tab -> {
            tab.accept(sulfur);
            tab.accept(saltpeter);
            tab.accept(humus);
        });
        @TAB_EVENTS@.@TAB_METHOD@(CreativeModeTabs.NATURAL_BLOCKS).register(tab -> {
            tab.accept(sulfurOre);
            tab.accept(deepslateOre);
        });
        BiomeModifications.addFeature(BiomeSelectors.foundInOverworld(),
                GenerationStep.Decoration.UNDERGROUND_ORES,
                ResourceKey.create(Registries.PLACED_FEATURE, Content.id("sulfur_ore")));
        @INTEGRATION_HOOK@
    }

    private static Item item(String name) {
        return Registry.register(BuiltInRegistries.ITEM, Content.id(name), Content.item(name));
    }

    private static Item ore(String name, boolean deepslate) {
        Block block = Registry.register(BuiltInRegistries.BLOCK, Content.id(name), Content.ore(name, deepslate));
        return Registry.register(BuiltInRegistries.ITEM, Content.id(name), Content.blockItem(name, block));
    }
}
