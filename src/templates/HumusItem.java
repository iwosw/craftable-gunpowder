package dev.iwoss.craftablegunpowder;

import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.ComposterBlock;

/** Humus is processed by using it on a non-full vanilla composter. */
public final class HumusItem extends Item {
    public HumusItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResult useOn(UseOnContext context) {
        BlockPos pos = context.getClickedPos();
        var state = context.getLevel().getBlockState(pos);
        ModConfig config = ModConfig.get();
        boolean creative = context.getPlayer() != null && context.getPlayer().getAbilities().instabuild;
        if (!config.compostingEnabled || !state.is(Blocks.COMPOSTER)
                || (!config.allowFullComposter && state.getValue(ComposterBlock.LEVEL) >= 7)
                || context.getItemInHand().isEmpty()
                || (!creative && context.getItemInHand().getCount() < config.humusConsumed)) {
            return InteractionResult.PASS;
        }
        if (context.getLevel() instanceof ServerLevel server) {
            compost(server, pos, context.getItemInHand(), creative, server.getRandom());
        }
        return InteractionResult.SUCCESS;
    }

    /** Shared server-side action; kept separate for deterministic integration checks. */
    static boolean compost(ServerLevel level, BlockPos pos, ItemStack stack, boolean creative, RandomSource random) {
        ModConfig config = ModConfig.get();
        if (!config.compostingEnabled || stack.isEmpty() || (!creative && stack.getCount() < config.humusConsumed)) return false;
        boolean success = random.nextFloat() < config.saltpeterChance;
        if (!creative && (success || config.consumeHumusOnFailure)) stack.shrink(config.humusConsumed);
        level.levelEvent(1500, pos, success ? 1 : 0);
        if (success) {
            ItemEntity drop = new ItemEntity(level, pos.getX() + 0.5, pos.getY() + 1.1, pos.getZ() + 0.5,
                    new ItemStack(Content.saltpeter, config.saltpeterMin == config.saltpeterMax ? config.saltpeterMin
                            : config.saltpeterMin + random.nextInt(config.saltpeterMax - config.saltpeterMin + 1)));
            drop.setDefaultPickUpDelay();
            level.addFreshEntity(drop);
        }
        return success;
    }
}
