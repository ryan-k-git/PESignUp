CREATE TABLE IF NOT EXISTS MemberListInfo (
    AdminNo CHAR(7) PRIMARY KEY,
    Name VARCHAR(120) NOT NULL,
    Gender CHAR(1),
    School VARCHAR(4),
    StudyStage TINYINT,
    PhoneNo VARCHAR(15),
    RegDate VARCHAR(16),
    RegStatus VARCHAR(10),
    Appointment VARCHAR(24)
);

CREATE TABLE IF NOT EXISTS Applications (
    AdminNo CHAR(7) PRIMARY KEY,
    DiscordID INT NOT NULL,
    FullName CHAR(120) NOT NULL,
    School CHAR(4) NOT NULL,
    PhoneNo VARCHAR(15) NOT NULL,
    Status TINYINT DEFAULT 0,
    Created DATETIME DEFAULT (DATETIME('now', 'localtime')),
    LastModified DATETIME,
    MessageID INT,

    FOREIGN KEY (AdminNo) REFERENCES MemberListInfo(AdminNo)
);

CREATE TABLE IF NOT EXISTS GroupApplication (
    AdminNo CHAR(7) PRIMARY KEY,
    DiscordID INT NOT NULL,
    Qualifications VARCHAR(512),
    JoinReasons VARCHAR(512),
    HeardFrom VARCHAR(256),
    Others VARCHAR(1024),
    Status TINYINT DEFAULT 0,
    MessageID INT,
    Created DATETIME DEFAULT (DATETIME('now', 'localtime')),
    LastModified DATETIME,

    FOREIGN KEY (AdminNo) REFERENCES MemberListInfo(AdminNo)
);

CREATE TABLE IF NOT EXISTS MemberInfo (
    AdminNo CHAR(7) PRIMARY KEY,
    DiscordID INT NOT NULL,
    Created DATETIME DEFAULT (DATETIME('now', 'localtime')),
    LastModified DATETIME,

    FOREIGN KEY (AdminNo) REFERENCES MemberListInfo(AdminNo)
);


CREATE TABLE IF NOT EXISTS OrganizedSession (
    SessionID INTEGER PRIMARY KEY AUTOINCREMENT,
    Title VARCHAR(120) NOT NULL,
    SessionType VARCHAR(32) DEFAULT 'practice',
    Organizer CHAR(7) NOT NULL,
    IsCompulsory BOOLEAN NOT NULL CHECK(IsCompulsory IN (0, 1)),
    MessageID INT,
    Created DATETIME DEFAULT (DATETIME('now', 'localtime')),
    LastModified DATETIME,

    FOREIGN KEY (Organizer) REFERENCES MemberInfo(AdminNo)
);

CREATE TABLE IF NOT EXISTS SessionSlot (
    SessionSlotID INTEGER PRIMARY KEY AUTOINCREMENT,
    SessionID INT NOT NULL,
    InternalSlotID INTEGER NOT NULL,
    AvailableSpots TINYINT NOT NULL,
    StartUnix INT NOT NULL,
    EndUnix INT NOT NULL,
    Created DATETIME DEFAULT (DATETIME('now', 'localtime')),
    LastModified DATETIME,

    FOREIGN KEY (SessionID) REFERENCES OrganizedSession(SessionID),

    UNIQUE(SessionID, InternalSlotID)
);

CREATE TABLE IF NOT EXISTS SlotAttendee (
    SessionSlotID INTEGER NOT NULL,
    AdminNo CHAR(7) NOT NULL,
    Status TEXT DEFAULT 'pending',
    Created DATETIME DEFAULT (DATETIME('now', 'localtime')),
    LastModified DATETIME,

    FOREIGN KEY (SessionSlotID) REFERENCES SessionSlot(SessionSlotID),
    FOREIGN KEY (AdminNo) REFERENCES MemberInfo(AdminNo),

    UNIQUE(SessionSlotID, AdminNo)
);

CREATE TABLE IF NOT EXISTS SessionAttendee (
    SessionID INT NOT NULL,
    SessionSlotID INT NOT NULL,
    AdminNo CHAR(7) NOT NULL,
    Created DATETIME DEFAULT (DATETIME('now', 'localtime')),
    LastModified DATETIME,

    FOREIGN KEY (SessionID) REFERENCES OrganizedSession(SessionID),
    FOREIGN KEY (SessionSlotID) REFERENCES SessionSlot(SessionSlotID),
    FOREIGN KEY (AdminNo) REFERENCES SlotAttendee(AdminNo),

    UNIQUE(SessionID, AdminNo),
    UNIQUE(SessionSlotID, AdminNo)
);

CREATE TABLE IF NOT EXISTS SecretSessionCodes(
    SessionID INT PRIMARY KEY,
    SecretCode INT CHECK(SecretCode > 0),
    Link TEXT,
    Expiry DATETIME,
    Created DATETIME DEFAULT (DATETIME('now', 'localtime')),
    LastModified DATETIME,

    FOREIGN KEY (SessionID) REFERENCES OrganizedSession(SessionID)
);

CREATE TRIGGER IF NOT EXISTS Set_SessionCode_Expiry
AFTER INSERT ON SecretSessionCodes
FOR EACH ROW
WHEN NEW.Expiry IS NULL
BEGIN
    UPDATE SecretSessionCodes
    SET Expiry=(
        SELECT DATETIME(
               StartUnix,
               'unixepoch',
               'localtime',
               'start of day',
               '+1 day'
               )
        FROM SessionSlot
        WHERE SessionSlot.SessionID = NEW.SessionID
        ORDER BY StartUnix
        LIMIT 1
        )
    WHERE SessionID=NEW.SessionID
            and Expiry is null;
end;
