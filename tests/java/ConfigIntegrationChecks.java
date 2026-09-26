package dev.iwoss.craftablegunpowder;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.nio.file.Files;
import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.util.RandomSource;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.phys.AABB;

/** Runs on the real game server; mutates settings only during this dev command. */
public final class ConfigIntegrationChecks {
    public static void run(MinecraftServer server) {
        ModConfig active = ModConfig.get();
        ModConfig saved = new Gson().fromJson(new Gson().toJson(active), ModConfig.class);
        var level = server.overworld();
        BlockPos pos = new BlockPos(8, 100, 8);
        try {
            for (String name : new String[] {"root", "saltpeter", "sulfur", "ingredients", "gunpowder"}) {
                check((server.getAdvancements().get(Content.id(name)) != null) == active.advancementsEnabled,
                        "Advancement enabled state: " + name);
            }
            var temp = Files.createTempDirectory("craftablegunpowder-config-test");
            var file = temp.resolve("config.json");
            try {
                check(ModConfig.load(file).gunpowderCount == 8 && Files.exists(file), "Creates defaults");
                Files.writeString(file, "{\"saltpeterChance\":1,\"saltpeterMin\":3,\"saltpeterMax\":3}");
                check(ModConfig.load(file).saltpeterMin == 3 && ModConfig.load(file).humusCount == 4, "Partial config keeps defaults");
                for (String invalid : new String[] {"null", "[]", "{", "{\"saltpeterChance\":2}",
                        "{\"veinSize\":0}", "{\"minY\":100,\"maxY\":50}", "{\"sulfurMin\":4,\"sulfurMax\":2}",
                        "{\"gunpowderCount\":1.5}", "{\"gunpowderCount\":4294967304}",
                        "{\"compostingEnabled\":null}", "{\"compostingEnabled\":\"false\"}"}) {
                    Files.writeString(file, invalid);
                    boolean rejected = false;
                    try { ModConfig.load(file); } catch (IllegalStateException expected) { rejected = true; }
                    check(rejected && Files.readString(file).equals(invalid), "Rejects and preserves bad config: " + invalid);
                }
            } finally {
                Files.deleteIfExists(file);
                Files.deleteIfExists(temp);
            }

            active.compostingEnabled = true;
            active.saltpeterChance = 1;
            active.saltpeterMin = 3;
            active.saltpeterMax = 3;
            active.humusConsumed = 2;
            ItemStack input = new ItemStack(Content.humus, 4);
            check(HumusItem.compost(level, pos, input, false, RandomSource.create(1)) && input.getCount() == 2,
                    "Configured guaranteed success and input cost");
            var drops = level.getEntitiesOfClass(ItemEntity.class, new AABB(pos).inflate(2));
            check(drops.stream().anyMatch(e -> e.getItem().is(Content.saltpeter) && e.getItem().getCount() == 3),
                    "Configured saltpeter count");
            active.saltpeterChance = 0;
            active.consumeHumusOnFailure = false;
            check(!HumusItem.compost(level, pos, input, false, RandomSource.create(1)) && input.getCount() == 2,
                    "Failed roll can preserve input");
            active.consumeHumusOnFailure = true;
            check(!HumusItem.compost(level, pos, input, false, RandomSource.create(1)) && input.isEmpty(),
                    "Failed roll can consume configured cost");
            active.saltpeterChance = 1;
            input = new ItemStack(Content.humus);
            check(!HumusItem.compost(level, pos, input, false, RandomSource.create(1)) && input.getCount() == 1,
                    "Insufficient humus cannot produce output");
            active.compostingEnabled = false;
            check(!HumusItem.compost(level, pos, input, true, RandomSource.create(1)), "Disabled composting");

            ModConfig data = new ModConfig();
            data.gunpowderCount = 16;
            JsonObject recipe = JsonParser.parseString("{\"result\":{\"count\":8}}").getAsJsonObject();
            check(ConfigPack.configure("data/craftablegunpowder/recipe/gunpowder.json", recipe, data)
                    && recipe.getAsJsonObject("result").get("count").getAsInt() == 16, "Recipe count transformation");
            data.gunpowderRecipeEnabled = false;
            check(!ConfigPack.configure("data/craftablegunpowder/recipe/gunpowder.json", recipe, data), "Disabled recipe omitted");
            check(!ConfigPack.configure("data/craftablegunpowder/advancement/recipes/gunpowder.json", recipe, data), "Disabled recipe unlock omitted");
            data.advancementsEnabled = false;
            check(!ConfigPack.configure("data/craftablegunpowder/advancement/root.json", new JsonObject(), data), "Disabled advancement omitted");
            data.humusRecipeEnabled = false;
            data.sulfurDropsEnabled = false;
            data.silkTouchEnabled = false;
            data.oreGenerationEnabled = false;
            data.veinSize = 12;
            data.minY = -32;
            data.maxY = 48;
            try (var index = ConfigPack.class.getResourceAsStream("/config_defaults/index.txt")) {
                check(index != null, "Pack resource index");
                for (String path : new String(index.readAllBytes(), java.nio.charset.StandardCharsets.UTF_8).split("\\R")) {
                    if (!path.endsWith(".json")) continue;
                    try (var inputStream = ConfigPack.class.getResourceAsStream("/config_defaults/" + path)) {
                        JsonObject object = JsonParser.parseString(new String(inputStream.readAllBytes(), java.nio.charset.StandardCharsets.UTF_8)).getAsJsonObject();
                        boolean included = ConfigPack.configure(path, object, data);
                        if (path.contains("/recipe") || path.contains("/advancement")) check(!included, "Disabled data omitted: " + path);
                        if (path.contains("/loot_table")) check(object.getAsJsonArray("pools").size() == 0, "Disabled ore has no loot");
                        if (path.contains("/placed_feature/")) check(object.getAsJsonArray("placement").get(0).getAsJsonObject().get("count").getAsInt() == 0, "Disabled generation has zero attempts");
                        if (path.contains("/configured_feature/")) check(object.getAsJsonObject("config").get("size").getAsInt() == 12, "Configured vein size");
                    }
                }
            }
            System.out.println("CRAFTABLE_GUNPOWDER_CONFIG_TEST_PASS");
        } catch (Exception e) {
            throw new IllegalStateException("Configuration integration check failed", e);
        } finally {
            try {
                for (var field : ModConfig.class.getFields()) field.set(active, field.get(saved));
            } catch (IllegalAccessException e) { throw new IllegalStateException(e); }
            for (ItemEntity drop : level.getEntitiesOfClass(ItemEntity.class, new AABB(pos).inflate(2))) drop.discard();
        }
    }

    private static void check(boolean condition, String message) {
        if (!condition) throw new IllegalStateException(message);
    }
}
