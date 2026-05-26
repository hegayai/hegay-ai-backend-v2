/*
  Warnings:

  - You are about to drop the `Usage` table. If the table is not empty, all the data it contains will be lost.

*/
-- DropForeignKey
ALTER TABLE "Usage" DROP CONSTRAINT "Usage_userId_fkey";

-- DropTable
DROP TABLE "Usage";

-- CreateTable
CREATE TABLE "UsageMonthly" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "periodStart" TIMESTAMP(3) NOT NULL,
    "imagesUsed" INTEGER NOT NULL DEFAULT 0,
    "videosUsed" INTEGER NOT NULL DEFAULT 0,
    "chatUsed" INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT "UsageMonthly_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "MusicProject" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "language" TEXT NOT NULL,
    "genre" TEXT NOT NULL,
    "voiceActorId" TEXT,
    "lyrics" TEXT,
    "structure" JSONB,
    "settings" JSONB,
    "audioUrl" TEXT,
    "stemsUrl" TEXT,
    "videoUrl" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "MusicProject_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "VoiceActor" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "language" TEXT NOT NULL,
    "gender" TEXT NOT NULL,
    "styles" JSONB NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "VoiceActor_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "VoiceClone" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "sampleUrl" TEXT NOT NULL,
    "modelId" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "VoiceClone_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "InstrumentPreset" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "genre" TEXT NOT NULL,
    "settings" JSONB NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "InstrumentPreset_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "MixSettings" (
    "id" TEXT NOT NULL,
    "projectId" TEXT NOT NULL,
    "loudness" INTEGER NOT NULL,
    "bass" INTEGER NOT NULL,
    "brightness" INTEGER NOT NULL,
    "space" INTEGER NOT NULL,
    "presetName" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "MixSettings_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "VideoSync" (
    "id" TEXT NOT NULL,
    "projectId" TEXT NOT NULL,
    "lyricsJson" JSONB NOT NULL,
    "beatMapJson" JSONB NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "VideoSync_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "UsageMonthly_userId_periodStart_key" ON "UsageMonthly"("userId", "periodStart");

-- CreateIndex
CREATE UNIQUE INDEX "MixSettings_projectId_key" ON "MixSettings"("projectId");

-- CreateIndex
CREATE UNIQUE INDEX "VideoSync_projectId_key" ON "VideoSync"("projectId");

-- AddForeignKey
ALTER TABLE "UsageMonthly" ADD CONSTRAINT "UsageMonthly_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "MusicProject" ADD CONSTRAINT "MusicProject_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "MusicProject" ADD CONSTRAINT "MusicProject_voiceActorId_fkey" FOREIGN KEY ("voiceActorId") REFERENCES "VoiceActor"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "VoiceClone" ADD CONSTRAINT "VoiceClone_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "MixSettings" ADD CONSTRAINT "MixSettings_projectId_fkey" FOREIGN KEY ("projectId") REFERENCES "MusicProject"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "VideoSync" ADD CONSTRAINT "VideoSync_projectId_fkey" FOREIGN KEY ("projectId") REFERENCES "MusicProject"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
