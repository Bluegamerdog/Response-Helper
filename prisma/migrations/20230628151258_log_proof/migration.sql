-- RedefineTables
PRAGMA foreign_keys=OFF;
CREATE TABLE "new_logs" (
    "logID" TEXT NOT NULL PRIMARY KEY,
    "timeStarted" TEXT NOT NULL,
    "timeEnded" TEXT NOT NULL,
    "timeElapsed" TEXT NOT NULL,
    "logProof" TEXT NOT NULL DEFAULT 'No proof provided',
    "operativeDiscordID" TEXT,
    "operativeName" TEXT,
    CONSTRAINT "logs_operativeDiscordID_fkey" FOREIGN KEY ("operativeDiscordID") REFERENCES "operative" ("discordID") ON DELETE SET NULL ON UPDATE CASCADE
);
INSERT INTO "new_logs" ("logID", "operativeDiscordID", "operativeName", "timeElapsed", "timeEnded", "timeStarted") SELECT "logID", "operativeDiscordID", "operativeName", "timeElapsed", "timeEnded", "timeStarted" FROM "logs";
DROP TABLE "logs";
ALTER TABLE "new_logs" RENAME TO "logs";
CREATE UNIQUE INDEX "logs_logID_key" ON "logs"("logID");
PRAGMA foreign_key_check;
PRAGMA foreign_keys=ON;
