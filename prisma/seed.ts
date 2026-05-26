// prisma/seed.ts
import { prisma } from "@/src/core/db/client";
import bcrypt from "bcryptjs";

async function main() {
  console.log("🌱 Seeding database...");

  // ------------------------------------------------------
  // 1. Create Admin User
  // ------------------------------------------------------
  const passwordHash = await bcrypt.hash("password123", 10);

  const user = await prisma.user.create({
    data: {
      email: "admin@hegay.ai",
      passwordHash,
      name: "Admin User",
      emailVerified: true,
      planId: "free",
    },
  });

  // ------------------------------------------------------
  // 2. Creator Profile
  // ------------------------------------------------------
  await prisma.creatorProfile.create({
    data: {
      userId: user.id,
      displayName: "Admin",
      bio: "System administrator",
    },
  });

  // ------------------------------------------------------
  // 3. Roles + Permissions
  // ------------------------------------------------------
  const role = await prisma.role.create({
    data: {
      name: "admin",
      description: "Full system access",
    },
  });

  const permission = await prisma.permission.create({
    data: {
      name: "all",
      description: "All permissions",
    },
  });

  await prisma.rolePermission.create({
    data: {
      roleId: role.id,
      permissionId: permission.id,
    },
  });

  await prisma.userRole.create({
    data: {
      userId: user.id,
      roleId: role.id,
    },
  });

  // ------------------------------------------------------
  // 4. Subscription Plan
  // ------------------------------------------------------
  await prisma.subscriptionPlan.create({
    data: {
      name: "Free",
      price: 0,
      credits: 50,
      perks: { basic: true },
    },
  });

  // ------------------------------------------------------
  // 5. Tier System
  // ------------------------------------------------------
  const tier = await prisma.tier.create({
    data: {
      name: "Bronze",
      minEarnings: 0,
      perks: { badge: "bronze" },
    },
  });

  await prisma.userTier.create({
    data: {
      userId: user.id,
      tierId: tier.id,
    },
  });

  // ------------------------------------------------------
  // 6. Cosmic Law + Expansion Protocol
  // ------------------------------------------------------
  await prisma.cosmicLaw.create({
    data: {
      key: "core.identity",
      value: { version: 1 },
      description: "Base identity law",
    },
  });

  await prisma.expansionProtocol.create({
    data: {
      name: "Genesis",
      version: "1.0.0",
      metadata: { initialized: true },
    },
  });

  console.log("🌱 Seed complete!");
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
