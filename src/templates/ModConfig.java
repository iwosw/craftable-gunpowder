package dev.iwoss.craftablegunpowder;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonParser;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

/** One server-authoritative, restart-only configuration for all loaders. */
public final class ModConfig {
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    private static ModConfig instance;
    public boolean compostingEnabled = true;
    public double saltpeterChance = 0.25;
    public int saltpeterMin = 1;
    public int saltpeterMax = 1;
    public int humusConsumed = 1;
    public boolean consumeHumusOnFailure = true;
    public boolean allowFullComposter = false;
    public boolean sulfurDropsEnabled = true;
    public double sulfurDropChance = 1.0;
    public int sulfurMin = 1;
    public int sulfurMax = 1;
    public boolean fortuneEnabled = true;
    public boolean silkTouchEnabled = true;
    public boolean explosionDecay = true;
    public boolean oreGenerationEnabled = true;
    public int veinSize = 8;
    public int veinsPerChunk = 6;
    public int minY = -48;
    public int maxY = 80;
    public double discardOnAirExposure = 0.0;
    public float oreHardness = 3.0F;
    public float deepslateOreHardness = 4.5F;
    public float oreBlastResistance = 3.0F;
    public boolean gunpowderRecipeEnabled = true;
    public int gunpowderCount = 8;
    public boolean humusRecipeEnabled = true;
    public int humusCount = 4;
    public boolean advancementsEnabled = true;
    public int finalAdvancementExperience = 50;

    public static synchronized ModConfig get() {
        if (instance == null) instance = load(@CONFIG_DIR@.resolve("craftablegunpowder.json"));
        return instance;
    }

    static ModConfig load(Path file) {
        try {
            ModConfig config = new ModConfig();
            if (Files.exists(file)) {
                var json = JsonParser.parseString(Files.readString(file));
                if (!json.isJsonObject()) throw new IllegalArgumentException("Expected a JSON object");
                // Reject nulls and wrong primitive types instead of silently coercing them.
                for (var field : ModConfig.class.getFields()) {
                    if (!json.getAsJsonObject().has(field.getName())) continue;
                    var value = json.getAsJsonObject().get(field.getName());
                    if (!value.isJsonPrimitive() || (field.getType() == boolean.class
                            ? !value.getAsJsonPrimitive().isBoolean() : !value.getAsJsonPrimitive().isNumber()))
                        throw new IllegalArgumentException("Invalid type for " + field.getName());
                    if (field.getType() == int.class && value.getAsBigDecimal().stripTrailingZeros().scale() > 0)
                        throw new IllegalArgumentException("Expected an integer for " + field.getName());
                    if (field.getType() == int.class) value.getAsBigDecimal().intValueExact();
                }
                config = GSON.fromJson(json, ModConfig.class);
            }
            config.validate();
            if (!Files.exists(file)) {
                Files.createDirectories(file.getParent());
                Files.writeString(file, GSON.toJson(config) + "\n");
            }
            return config;
        } catch (IOException | RuntimeException e) {
            throw new IllegalStateException("Invalid Craftable Gunpowder config: " + file + ": " + e.getMessage(), e);
        }
    }

    void validate() {
        range("saltpeterChance", saltpeterChance, 0, 1);
        range("sulfurDropChance", sulfurDropChance, 0, 1);
        range("saltpeterMin", saltpeterMin, 1, 64);
        range("saltpeterMax", saltpeterMax, saltpeterMin, 64);
        range("humusConsumed", humusConsumed, 1, 64);
        range("sulfurMin", sulfurMin, 1, 64);
        range("sulfurMax", sulfurMax, sulfurMin, 64);
        range("veinSize", veinSize, 1, 64);
        range("veinsPerChunk", veinsPerChunk, 0, 256);
        range("minY", minY, -64, 319);
        range("maxY", maxY, minY, 319);
        range("discardOnAirExposure", discardOnAirExposure, 0, 1);
        range("oreHardness", oreHardness, 0, 1000);
        range("deepslateOreHardness", deepslateOreHardness, 0, 1000);
        range("oreBlastResistance", oreBlastResistance, 0, 3600000);
        range("gunpowderCount", gunpowderCount, 1, 64);
        range("humusCount", humusCount, 1, 64);
        range("finalAdvancementExperience", finalAdvancementExperience, 0, 1000000);
    }

    private static void range(String name, double value, double min, double max) {
        if (!Double.isFinite(value) || value < min || value > max)
            throw new IllegalArgumentException(name + " must be in [" + min + ", " + max + "]");
    }
}
