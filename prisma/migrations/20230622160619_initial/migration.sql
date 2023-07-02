-- CreateTable
CREATE TABLE "operative" (
    "discordID" TEXT NOT NULL PRIMARY KEY,
    "userName" TEXT NOT NULL,
    "rank" TEXT NOT NULL,
    "profileLink" TEXT NOT NULL,
    "activeLog" BOOLEAN NOT NULL,
    "activeLogID" TEXT NOT NULL
);

-- CreateTable
CREATE TABLE "quotas" (
    "rankName" TEXT NOT NULL PRIMARY KEY,
    "logRequirement" TEXT NOT NULL,
    "responseRequirement" TEXT NOT NULL,
    "quotaActive" BOOLEAN NOT NULL
);

-- CreateTable
CREATE TABLE "quota_blocks" (
    "blockNum" TEXT NOT NULL PRIMARY KEY,
    "unix_starttime" TEXT NOT NULL,
    "unix_endtime" TEXT NOT NULL,
    "blockActive" BOOLEAN NOT NULL
);

-- CreateTable
CREATE TABLE "response" (
    "responseID" TEXT NOT NULL PRIMARY KEY,
    "responseType" TEXT NOT NULL,
    "timeStarted" TEXT NOT NULL,
    "timeEnded" TEXT NOT NULL,
    "started" BOOLEAN NOT NULL,
    "cancelled" BOOLEAN NOT NULL,
    "spontaneous" BOOLEAN NOT NULL,
    "trellocardID" TEXT NOT NULL,
    "operativeDiscordID" TEXT,
    "operativeName" TEXT,
    CONSTRAINT "response_operativeDiscordID_fkey" FOREIGN KEY ("operativeDiscordID") REFERENCES "operative" ("discordID") ON DELETE SET NULL ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "ranks" (
    "rankName" TEXT NOT NULL,
    "discordRoleID" TEXT NOT NULL PRIMARY KEY,
    "RobloxRankID" TEXT NOT NULL
);

-- CreateTable
CREATE TABLE "logs" (
    "logID" TEXT NOT NULL PRIMARY KEY,
    "timeStarted" TEXT NOT NULL,
    "timeEnded" TEXT NOT NULL,
    "timeElapsed" TEXT NOT NULL,
    "operativeDiscordID" TEXT,
    "operativeName" TEXT,
    CONSTRAINT "logs_operativeDiscordID_fkey" FOREIGN KEY ("operativeDiscordID") REFERENCES "operative" ("discordID") ON DELETE SET NULL ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "server" (
    "serverID" TEXT NOT NULL PRIMARY KEY,
    "announceRole" TEXT NOT NULL,
    "announceChannel" TEXT NOT NULL,
    "logPermissionRole" TEXT NOT NULL,
    "announcePermissionRole" TEXT NOT NULL,
    "commandRole" TEXT NOT NULL,
    "developerRole" TEXT NOT NULL
);

-- CreateIndex
CREATE UNIQUE INDEX "operative_discordID_key" ON "operative"("discordID");

-- CreateIndex
CREATE UNIQUE INDEX "operative_userName_key" ON "operative"("userName");

-- CreateIndex
CREATE UNIQUE INDEX "operative_profileLink_key" ON "operative"("profileLink");

-- CreateIndex
CREATE UNIQUE INDEX "operative_activeLogID_key" ON "operative"("activeLogID");

-- CreateIndex
CREATE UNIQUE INDEX "quotas_rankName_key" ON "quotas"("rankName");

-- CreateIndex
CREATE UNIQUE INDEX "quota_blocks_blockNum_key" ON "quota_blocks"("blockNum");

-- CreateIndex
CREATE UNIQUE INDEX "response_responseID_key" ON "response"("responseID");

-- CreateIndex
CREATE UNIQUE INDEX "ranks_rankName_key" ON "ranks"("rankName");

-- CreateIndex
CREATE UNIQUE INDEX "ranks_discordRoleID_key" ON "ranks"("discordRoleID");

-- CreateIndex
CREATE UNIQUE INDEX "ranks_RobloxRankID_key" ON "ranks"("RobloxRankID");

-- CreateIndex
CREATE UNIQUE INDEX "logs_logID_key" ON "logs"("logID");

-- CreateIndex
CREATE UNIQUE INDEX "server_serverID_key" ON "server"("serverID");
