package dev.iwoss.craftablegunpowder;

import com.mojang.brigadier.CommandDispatcher;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.util.RandomSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.item.ItemEntity;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.ComposterBlock;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.Vec3;

/** Dev-only server integration checks. Never packaged in release jars. */
public final class IntegrationChecks {
    public static void register(CommandDispatcher<CommandSourceStack> dispatcher) {
        dispatcher.register(Commands.literal("craftablegunpowder_test").executes(context -> {
            run(context.getSource().getServer());
            context.getSource().sendSuccess(() -> Component.literal("CRAFTABLE_GUNPOWDER_COMPOST_TEST_PASS"), false);
            return 1;
        }));
    }

    public static void run(MinecraftServer server) {
        ServerLevel level = server.overworld();
        BlockPos pos = new BlockPos(8, 100, 8);
        HumusItem humus = (HumusItem) Content.humus;
        ItemStack input = new ItemStack(humus, 2);
        level.setBlockAndUpdate(pos, Blocks.STONE.defaultBlockState());
        check(humus.useOn(new Context(level, pos, input)) == InteractionResult.PASS, "Non-composter interaction must pass");
        check(input.getCount() == 2, "Non-composter must not consume humus");
        for (int fill : new int[] {7, 8}) {
            level.setBlockAndUpdate(pos, Blocks.COMPOSTER.defaultBlockState().setValue(ComposterBlock.LEVEL, fill));
            check(humus.useOn(new Context(level, pos, input)) == InteractionResult.PASS, "Full composter must pass");
            check(input.getCount() == 2, "Full composter must not consume humus");
        }
        level.setBlockAndUpdate(pos, Blocks.COMPOSTER.defaultBlockState());
        check(humus.useOn(new Context(level, pos, input)) == InteractionResult.SUCCESS, "Composter must handle humus");
        check(input.getCount() == 1, "One use must consume exactly one humus");
        clearDrops(level, pos);

        RandomSource random = RandomSource.create(830145L);
        RandomSource expected = RandomSource.create(830145L);
        int successes = 0;
        int expectedSuccesses = 0;
        for (int i = 0; i < 256; i++) {
            ItemStack attempt = new ItemStack(humus);
            if (HumusItem.compost(level, pos, attempt, false, random)) successes++;
            if (expected.nextFloat() < 0.25F) expectedSuccesses++;
            check(attempt.isEmpty(), "Every attempt must consume one humus, including failures");
        }
        check(successes == expectedSuccesses && successes > 0 && successes < 256, "Saltpeter chance must be exactly 25 percent");
        var drops = level.getEntitiesOfClass(ItemEntity.class, new AABB(pos).inflate(2));
        check(drops.size() == successes, "One drop entity must spawn for each successful attempt");
        for (ItemEntity drop : drops) {
            check(drop.getItem().is(Content.saltpeter) && drop.getItem().getCount() == 1, "Each success must give one saltpeter");
        }
        ItemStack creative = new ItemStack(humus, 2);
        HumusItem.compost(level, pos, creative, true, random);
        check(creative.getCount() == 2, "Creative interaction must preserve humus");
        check(!HumusItem.compost(level, pos, ItemStack.EMPTY, false, random), "Empty stack must not produce saltpeter");
        clearDrops(level, pos);
        System.out.println("CRAFTABLE_GUNPOWDER_COMPOST_TEST_PASS successes=" + successes + "/256");
    }

    private static void clearDrops(ServerLevel level, BlockPos pos) {
        for (ItemEntity drop : level.getEntitiesOfClass(ItemEntity.class, new AABB(pos).inflate(2))) drop.discard();
    }

    private static void check(boolean condition, String message) {
        if (!condition) throw new IllegalStateException("Craftable Gunpowder integration check: " + message);
    }

    private static final class Context extends UseOnContext {
        private Context(ServerLevel level, BlockPos pos, ItemStack stack) {
            super(level, null, InteractionHand.MAIN_HAND, stack,
                    new BlockHitResult(Vec3.atCenterOf(pos), Direction.UP, pos, false));
        }
    }
}
