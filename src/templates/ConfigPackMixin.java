package dev.iwoss.craftablegunpowder.mixin;

import dev.iwoss.craftablegunpowder.ConfigPack;

import java.util.function.Consumer;
import net.minecraft.server.packs.repository.BuiltInPackSource;
import net.minecraft.server.packs.repository.ServerPacksSource;
import net.minecraft.server.packs.repository.Pack;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/** Fabric pack discovery hook; also runs for the integrated server/new-world screen. */
@Mixin(BuiltInPackSource.class)
public abstract class ConfigPackMixin {
    @Inject(method = "loadPacks", at = @At("TAIL"))
    private void craftablegunpowder$add(Consumer<Pack> consumer, CallbackInfo ci) {
        if ((Object) this instanceof ServerPacksSource) ConfigPack.add(consumer);
    }
}
