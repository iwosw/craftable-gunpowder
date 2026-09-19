package dev.iwoss.craftablegunpowder;

import java.util.function.Supplier;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import @FORGE_PACKAGE@.registries.DeferredRegister;
import @BUS_PACKAGE@.IEventBus;
import @FML_PACKAGE@.common.Mod;
import @FORGE_PACKAGE@.event.BuildCreativeModeTabContentsEvent;
@CONTEXT_IMPORT@

@Mod(Content.MOD_ID)
public final class ForgeEntrypoint {
    private static final DeferredRegister<Block> BLOCKS = DeferredRegister.create(Registries.BLOCK, Content.MOD_ID);
    private static final DeferredRegister<Item> ITEMS = DeferredRegister.create(Registries.ITEM, Content.MOD_ID);

    public static final Supplier<Item> SULFUR = ITEMS.register("sulfur", () -> Content.item("sulfur"));
    public static final Supplier<Item> SALTPETER = ITEMS.register("saltpeter", () -> Content.item("saltpeter"));
    public static final Supplier<Item> HUMUS = ITEMS.register("humus", () -> Content.item("humus"));
    public static final Supplier<Block> SULFUR_ORE = BLOCKS.register("sulfur_ore", () -> Content.ore("sulfur_ore", false));
    public static final Supplier<Block> DEEPSLATE_SULFUR_ORE = BLOCKS.register("deepslate_sulfur_ore", () -> Content.ore("deepslate_sulfur_ore", true));
    public static final Supplier<Item> SULFUR_ORE_ITEM = ITEMS.register("sulfur_ore", () -> Content.blockItem("sulfur_ore", SULFUR_ORE.get()));
    public static final Supplier<Item> DEEPSLATE_SULFUR_ORE_ITEM = ITEMS.register("deepslate_sulfur_ore", () -> Content.blockItem("deepslate_sulfur_ore", DEEPSLATE_SULFUR_ORE.get()));

    public ForgeEntrypoint(@BUS_ARGUMENT@) {
        @BUS_LOOKUP@
        BLOCKS.register(bus);
        ITEMS.register(bus);
        bus.addListener(this::creativeTabs);
    }

    private void creativeTabs(BuildCreativeModeTabContentsEvent event) {
        if (event.getTabKey() == CreativeModeTabs.INGREDIENTS) {
            event.accept(SULFUR.get());
            event.accept(SALTPETER.get());
            event.accept(HUMUS.get());
        }
        if (event.getTabKey() == CreativeModeTabs.NATURAL_BLOCKS) {
            event.accept(SULFUR_ORE_ITEM.get());
            event.accept(DEEPSLATE_SULFUR_ORE_ITEM.get());
        }
    }
}
