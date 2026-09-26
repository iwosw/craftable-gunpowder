package dev.iwoss.craftablegunpowder;

import com.google.gson.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.function.Consumer;
import net.minecraft.network.chat.Component;
import net.minecraft.server.packs.PathPackResources;
import net.minecraft.server.packs.PackType;
import net.minecraft.server.packs.repository.Pack;
import net.minecraft.server.packs.repository.PackSource;

/** Materializes only this mod's data, before worldgen registries and recipes load. */
public final class ConfigPack {
    private static Path directory;

    public static synchronized void add(Consumer<Pack> consumer) {
        if (directory == null) directory = generate();
        Path root = directory;
        Pack pack = @CREATE_PACK@;
        if (pack == null) throw new IllegalStateException("Cannot load Craftable Gunpowder configuration pack");
        consumer.accept(pack);
    }

    private static Path generate() {
        ModConfig config = ModConfig.get();
        Path root = @CONFIG_DIR@.resolve("craftablegunpowder-generated/@TARGET@");
        try {
            String[] paths = new String(read("index.txt"), StandardCharsets.UTF_8).split("\\R");
            for (String path : paths) {
                if (path.isBlank()) continue;
                Path destination = root.resolve(path);
                if (!destination.normalize().startsWith(root.normalize())) throw new IOException("Invalid resource path");
                Files.createDirectories(destination.getParent());
                if (path.endsWith(".json")) {
                    JsonObject json = JsonParser.parseString(new String(read(path), StandardCharsets.UTF_8)).getAsJsonObject();
                    if (configure(path, json, config)) Files.writeString(destination, json.toString());
                    else Files.deleteIfExists(destination);
                } else Files.write(destination, read(path));
            }
            return root;
        } catch (IOException e) {
            throw new IllegalStateException("Cannot create Craftable Gunpowder configuration pack", e);
        }
    }

    private static byte[] read(String path) throws IOException {
        try (InputStream stream = ConfigPack.class.getResourceAsStream("/config_defaults/" + path)) {
            if (stream == null) throw new IOException("Missing packaged resource: " + path);
            return stream.readAllBytes();
        }
    }

    static boolean configure(String path, JsonObject json, ModConfig c) {
        if (path.contains("/recipe/") || path.contains("/recipes/")) {
            boolean gunpowder = path.endsWith("/gunpowder.json");
            if (!(gunpowder ? c.gunpowderRecipeEnabled : c.humusRecipeEnabled)) return false;
            if (json.has("result")) json.getAsJsonObject("result").addProperty("count", gunpowder ? c.gunpowderCount : c.humusCount);
        }
        if (path.contains("/advancement")) {
            if (!path.contains("/recipes/")) {
                if (!c.advancementsEnabled) return false;
                if (path.endsWith("/gunpowder.json")) json.getAsJsonObject("rewards").addProperty("experience", c.finalAdvancementExperience);
            }
        }
        if (path.contains("/loot_table")) {
            JsonArray pools = json.getAsJsonArray("pools");
            JsonArray children = pools.get(0).getAsJsonObject().getAsJsonArray("entries").get(0).getAsJsonObject().getAsJsonArray("children");
            JsonObject sulfur = children.get(1).getAsJsonObject();
            if (!c.sulfurDropsEnabled) children.remove(1);
            else {
                JsonArray conditions = new JsonArray();
                JsonObject chance = new JsonObject();
                chance.addProperty("condition", "minecraft:random_chance");
                chance.addProperty("chance", c.sulfurDropChance);
                conditions.add(chance);
                sulfur.add("conditions", conditions);
                JsonArray functions = new JsonArray();
                JsonObject count = new JsonObject();
                count.addProperty("function", "minecraft:set_count");
                JsonObject uniform = new JsonObject();
                uniform.addProperty("type", "minecraft:uniform");
                uniform.addProperty("min", c.sulfurMin);
                uniform.addProperty("max", c.sulfurMax);
                count.add("count", uniform);
                functions.add(count);
                for (JsonElement function : sulfur.getAsJsonArray("functions")) {
                    String type = function.getAsJsonObject().get("function").getAsString();
                    if (type.equals("minecraft:apply_bonus") && !c.fortuneEnabled) continue;
                    if (type.equals("minecraft:explosion_decay") && !c.explosionDecay) continue;
                    functions.add(function);
                }
                sulfur.add("functions", functions);
            }
            if (!c.silkTouchEnabled) children.remove(0);
            if (children.isEmpty()) pools.remove(0);
        }
        if (path.contains("/configured_feature/")) {
            JsonObject feature = json.getAsJsonObject("config");
            feature.addProperty("size", c.veinSize);
            feature.addProperty("discard_chance_on_air_exposure", c.discardOnAirExposure);
        }
        if (path.contains("/placed_feature/")) {
            JsonArray placement = json.getAsJsonArray("placement");
            placement.get(0).getAsJsonObject().addProperty("count", c.oreGenerationEnabled ? c.veinsPerChunk : 0);
            JsonObject height = placement.get(2).getAsJsonObject().getAsJsonObject("height");
            height.getAsJsonObject("min_inclusive").addProperty("absolute", c.minY);
            height.getAsJsonObject("max_inclusive").addProperty("absolute", c.maxY);
        }
        return true;
    }
}
