-- CreateTable
CREATE TABLE "CosmicLaw" (
    "id" TEXT NOT NULL,
    "key" TEXT NOT NULL,
    "value" JSONB NOT NULL,
    "description" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "CosmicLaw_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ExpansionProtocol" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "version" TEXT NOT NULL,
    "metadata" JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "ExpansionProtocol_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ContinuityRecord" (
    "id" TEXT NOT NULL,
    "event" TEXT NOT NULL,
    "details" JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "ContinuityRecord_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "CosmicLaw_key_key" ON "CosmicLaw"("key");

-- CreateIndex
CREATE UNIQUE INDEX "ExpansionProtocol_name_key" ON "ExpansionProtocol"("name");
