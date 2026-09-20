package dev.iwoss.craftablegunpowder;

import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.@IDENTIFIER@;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;

/** Shared block/item properties; only version-sensitive API names are substituted. */
public final class Content {
    public static final String MOD_ID = "craftablegunpowder";
    static Item saltpeter;
    static Item humus;

    private Content() {}

    public static @IDENTIFIER@ id(String path) {
        return @ID_FACTORY@;
    }

    public static Item item(String name) {
        Item.Properties properties = new Item.Properties();
        @ITEM_ID@
        Item item = name.equals("humus") ? new HumusItem(properties) : new Item(properties);
        if (name.equals("saltpeter")) saltpeter = item;
        if (name.equals("humus")) humus = item;
        return item;
    }

    public static Block ore(String name, boolean deepslate) {
        BlockBehaviour.Properties properties = BlockBehaviour.Properties.of()
                .strength(deepslate ? 4.5F : 3.0F, 3.0F)
                .sound(deepslate ? SoundType.DEEPSLATE : SoundType.STONE)
                .requiresCorrectToolForDrops();
        @BLOCK_ID@
        return new Block(properties);
    }

    public static Item blockItem(String name, Block block) {
        Item.Properties properties = new Item.Properties();
        @ITEM_ID@
        @BLOCK_DESCRIPTION@
        return new BlockItem(block, properties);
    }
}
