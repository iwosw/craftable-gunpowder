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
    public static final float SALTPETER_CHANCE = 0.25F;

    public HumusItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResult useOn(UseOnContext context) {
        BlockPos pos = context.getClickedPos();
        var state = context.getLevel().getBlockState(pos);
        if (!state.is(Blocks.COMPOSTER) || state.getValue(ComposterBlock.LEVEL) >= 7) {
            return InteractionResult.PASS;
        }
        if (context.getLevel() instanceof ServerLevel server) {
            boolean creative = context.getPlayer() != null && context.getPlayer().getAbilities().instabuild;
            compost(server, pos, context.getItemInHand(), creative, server.getRandom());
        }
        return InteractionResult.SUCCESS;
    }

    /** Shared server-side action; kept separate for deterministic integration checks. */
    static boolean compost(ServerLevel level, BlockPos pos, ItemStack stack, boolean creative, RandomSource random) {
        if (stack.isEmpty()) return false;
        if (!creative) stack.shrink(1);
        boolean success = random.nextFloat() < SALTPETER_CHANCE;
        level.levelEvent(1500, pos, success ? 1 : 0);
        if (success) {
            ItemEntity drop = new ItemEntity(level, pos.getX() + 0.5, pos.getY() + 1.1, pos.getZ() + 0.5,
                    new ItemStack(Content.saltpeter));
            drop.setDefaultPickUpDelay();
            level.addFreshEntity(drop);
        }
        return success;
    }
}
