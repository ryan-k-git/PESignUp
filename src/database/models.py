import datetime

from rapidfuzz import fuzz
from sqlalchemy import CheckConstraint, Text, UniqueConstraint, text
from sqlmodel import Field, SQLModel, select

from database.db import DATABASE
from core.embeds import BaseEmbed
from utils.string_cleaning import normalize

NOW_DEFAULT = text("(DATETIME('now', 'localtime'))")


class MemberListInfo(SQLModel, table=True):
    __tablename__ = "MemberListInfo"

    admin_no: str = Field(primary_key=True, max_length=7, sa_column_kwargs={"name": "AdminNo"})
    name: str = Field(max_length=120, sa_column_kwargs={"name": "Name"})
    gender: str | None = Field(default=None, max_length=1, sa_column_kwargs={"name": "Gender"})
    school: str | None = Field(default=None, max_length=4, sa_column_kwargs={"name": "School"})
    study_stage: int | None = Field(default=None, sa_column_kwargs={"name": "StudyStage"})
    phone_no: str | None = Field(default=None, max_length=15, sa_column_kwargs={"name": "PhoneNo"})
    reg_date: str | None = Field(default=None, max_length=16, sa_column_kwargs={"name": "RegDate"})
    reg_status: str | None = Field(default=None, max_length=10, sa_column_kwargs={"name": "RegStatus"})
    appointment_date: str | None = Field(default=None, max_length=24, sa_column_kwargs={"name": "Appointment"})

    @classmethod
    async def from_admin_no(cls, admin_no: str) -> "MemberListInfo | None":
        async with DATABASE.session() as session:
            return await session.get(cls, admin_no.upper())

    @classmethod
    async def from_name(cls, name: str) -> "MemberListInfo | None":
        async with DATABASE.session() as session:
            result = await session.exec(select(cls.admin_no, cls.name))
            all_members = result.all()
        best_match = None
        highest_score = 0
        normalized_name = normalize(name)
        for admin_no, member_name in all_members:
            similarity = fuzz.token_set_ratio(normalized_name, normalize(member_name))
            typo = fuzz.ratio(normalized_name, normalize(member_name))
            if similarity < 85 and typo < 80:
                continue
            score = max(similarity, typo)
            if score > highest_score:
                highest_score = score
                best_match = admin_no
        if best_match:
            return await cls.from_admin_no(best_match)
        return None

    async def embed(self) -> BaseEmbed:
        embed = BaseEmbed(title="Member List Info")
        embed.add_field(name="Admin Number", value=self.admin_no, inline=False)
        embed.add_field(name="Name", value=self.name, inline=False)
        embed.add_field(name="Gender", value=self.gender, inline=False)
        embed.add_field(name="School", value=self.school, inline=False)
        embed.add_field(name="Study Stage", value=self.study_stage, inline=False)
        embed.add_field(name="Phone No", value=self.phone_no, inline=False)
        embed.add_field(name="Reg Date", value=self.reg_date, inline=False)
        embed.add_field(name="Reg Status", value=self.reg_status, inline=False)
        embed.add_field(name="Appointment Date", value=self.appointment_date, inline=False)
        return embed

    async def save(self) -> None:
        self.admin_no = self.admin_no.upper()
        async with DATABASE.session() as session:
            record = await session.get(type(self), self.admin_no)
            if record is None:
                session.add(self)
            else:
                record.name = self.name
                record.gender = self.gender
                record.school = self.school
                record.study_stage = self.study_stage
                record.phone_no = self.phone_no
                record.reg_date = self.reg_date
                record.reg_status = self.reg_status
                record.appointment_date = self.appointment_date
            await session.commit()

    async def get_member_info(self) -> "MemberListInfo | None":
        return await self.from_admin_no(self.admin_no)


class MemberInfo(SQLModel, table=True):
    __tablename__ = "MemberInfo"

    admin_no: str = Field(
        primary_key=True,
        max_length=7,
        foreign_key="MemberListInfo.AdminNo",
        sa_column_kwargs={"name": "AdminNo"},
    )
    discord_id: int = Field(sa_column_kwargs={"name": "DiscordID"})
    created: datetime.datetime | None = Field(
        default_factory=datetime.datetime.now,
        sa_column_kwargs={"name": "Created", "server_default": NOW_DEFAULT},
    )
    last_modified: datetime.datetime | None = Field(default=None, sa_column_kwargs={"name": "LastModified"})

    @classmethod
    async def from_discord_id(cls, discord_id: int) -> "MemberInfo | None":
        async with DATABASE.session() as session:
            result = await session.exec(select(cls).where(cls.discord_id == discord_id))
            return result.first()

    @classmethod
    async def from_admin_no(cls, admin_no: str) -> "MemberInfo | None":
        async with DATABASE.session() as session:
            return await session.get(cls, admin_no.upper())

    async def embed(self) -> BaseEmbed:
        embed = BaseEmbed(title="Member Info")
        embed.add_field(name="Admin Number", value=self.admin_no, inline=False)
        embed.add_field(name="Discord ID", value=self.discord_id, inline=False)
        return embed

    async def save(self) -> None:
        self.admin_no = self.admin_no.upper()
        async with DATABASE.session() as session:
            record = await session.get(type(self), self.admin_no)
            if record is None:
                session.add(self)
            else:
                record.discord_id = self.discord_id
            await session.commit()


class Application(SQLModel, table=True):
    __tablename__ = "Applications"

    admin_no: str = Field(
        primary_key=True,
        max_length=7,
        foreign_key="MemberListInfo.AdminNo",
        sa_column_kwargs={"name": "AdminNo"},
    )
    discord_id: int = Field(sa_column_kwargs={"name": "DiscordID"})
    name: str = Field(max_length=120, sa_column_kwargs={"name": "FullName"})
    school: str = Field(max_length=4, sa_column_kwargs={"name": "School"})
    phone_no: str = Field(max_length=15, sa_column_kwargs={"name": "PhoneNo"})
    status: int = Field(default=0, sa_column_kwargs={"name": "Status"})
    created: datetime.datetime | None = Field(
        default_factory=datetime.datetime.now,
        sa_column_kwargs={"name": "Created", "server_default": NOW_DEFAULT},
    )
    last_modified: datetime.datetime | None = Field(default=None, sa_column_kwargs={"name": "LastModified"})
    message_id: int | None = Field(default=None, sa_column_kwargs={"name": "MessageID"})

    @classmethod
    async def from_admin_no(cls, admin_no: str) -> "Application | None":
        async with DATABASE.session() as session:
            return await session.get(cls, admin_no.upper())

    @classmethod
    async def from_discord_id(cls, discord_id: int) -> "Application | None":
        async with DATABASE.session() as session:
            result = await session.exec(select(cls).where(cls.discord_id == discord_id))
            return result.first()

    async def embed(self) -> BaseEmbed:
        embed = BaseEmbed(title="Application Info")
        embed.add_field(name="Admin No", value=self.admin_no, inline=False)
        embed.add_field(name="Discord ID", value=f"<@{self.discord_id}>", inline=False)
        embed.add_field(name="Name", value=self.name, inline=False)
        embed.add_field(name="School", value=self.school, inline=False)
        embed.add_field(name="Phone No", value=self.phone_no, inline=False)
        embed.add_field(name="Status", value=self.status, inline=False)
        embed.add_field(name="Created", value=self.created, inline=False)
        embed.add_field(name="Last Modified", value=self.last_modified, inline=False)
        embed.add_field(name="Message ID", value=self.message_id, inline=False)
        return embed

    async def save(self) -> None:
        self.admin_no = self.admin_no.upper()
        async with DATABASE.session() as session:
            record = await session.get(type(self), self.admin_no)
            if record is None:
                session.add(self)
            else:
                record.discord_id = self.discord_id
                record.name = self.name
                record.school = self.school
                record.phone_no = self.phone_no
                record.status = self.status
                record.last_modified = self.last_modified
                record.message_id = self.message_id
            await session.commit()


class OrganizedSession(SQLModel, table=True):
    __tablename__ = "OrganizedSession"

    session_id: int | None = Field(default=None, primary_key=True, sa_column_kwargs={"name": "SessionID"})
    title: str = Field(max_length=120, sa_column_kwargs={"name": "Title"})
    session_type: str | None = Field(
        default="practice",
        max_length=32,
        sa_column_kwargs={"name": "SessionType"},
    )
    organizer: str = Field(
        max_length=7,
        foreign_key="MemberInfo.AdminNo",
        sa_column_kwargs={"name": "Organizer"},
    )
    is_compulsory: bool = Field(sa_column_kwargs={"name": "IsCompulsory"})
    message_id: int | None = Field(default=None, sa_column_kwargs={"name": "MessageID"})
    created: datetime.datetime | None = Field(
        default_factory=datetime.datetime.now,
        sa_column_kwargs={"name": "Created", "server_default": NOW_DEFAULT},
    )
    last_modified: datetime.datetime | None = Field(default=None, sa_column_kwargs={"name": "LastModified"})

    __table_args__ = (CheckConstraint("IsCompulsory IN (0, 1)"),)


class SessionSlot(SQLModel, table=True):
    __tablename__ = "SessionSlot"

    session_slot_id: int | None = Field(default=None, primary_key=True, sa_column_kwargs={"name": "SessionSlotID"})
    session_id: int = Field(foreign_key="OrganizedSession.SessionID", sa_column_kwargs={"name": "SessionID"})
    internal_slot_id: int = Field(sa_column_kwargs={"name": "InternalSlotID"})
    available_spots: int = Field(sa_column_kwargs={"name": "AvailableSpots"})
    start_unix: int = Field(sa_column_kwargs={"name": "StartUnix"})
    end_unix: int = Field(sa_column_kwargs={"name": "EndUnix"})
    created: datetime.datetime | None = Field(
        default_factory=datetime.datetime.now,
        sa_column_kwargs={"name": "Created", "server_default": NOW_DEFAULT},
    )
    last_modified: datetime.datetime | None = Field(default=None, sa_column_kwargs={"name": "LastModified"})

    __table_args__ = (UniqueConstraint("SessionID", "InternalSlotID"),)


class SlotAttendee(SQLModel, table=True):
    __tablename__ = "SlotAttendee"

    session_slot_id: int = Field(
        primary_key=True,
        foreign_key="SessionSlot.SessionSlotID",
        sa_column_kwargs={"name": "SessionSlotID"},
    )
    admin_no: str = Field(
        primary_key=True,
        max_length=7,
        foreign_key="MemberInfo.AdminNo",
        sa_column_kwargs={"name": "AdminNo"},
    )
    status: str | None = Field(
        default="pending",
        sa_type=Text,
        sa_column_kwargs={"name": "Status"},
    )
    created: datetime.datetime | None = Field(
        default_factory=datetime.datetime.now,
        sa_column_kwargs={"name": "Created", "server_default": NOW_DEFAULT},
    )
    last_modified: datetime.datetime | None = Field(default=None, sa_column_kwargs={"name": "LastModified"})


class SessionAttendee(SQLModel, table=True):
    __tablename__ = "SessionAttendee"

    session_id: int = Field(
        primary_key=True,
        foreign_key="OrganizedSession.SessionID",
        sa_column_kwargs={"name": "SessionID"},
    )
    session_slot_id: int = Field(foreign_key="SessionSlot.SessionSlotID", sa_column_kwargs={"name": "SessionSlotID"})
    admin_no: str = Field(
        primary_key=True,
        max_length=7,
        foreign_key="MemberInfo.AdminNo",
        sa_column_kwargs={"name": "AdminNo"},
    )
    created: datetime.datetime | None = Field(
        default_factory=datetime.datetime.now,
        sa_column_kwargs={"name": "Created", "server_default": NOW_DEFAULT},
    )
    last_modified: datetime.datetime | None = Field(default=None, sa_column_kwargs={"name": "LastModified"})

    __table_args__ = (UniqueConstraint("SessionSlotID", "AdminNo"),)


class SecretSessionCode(SQLModel, table=True):
    __tablename__ = "SecretSessionCodes"

    session_id: int = Field(
        primary_key=True,
        foreign_key="OrganizedSession.SessionID",
        sa_column_kwargs={"name": "SessionID"},
    )
    secret_code: int | None = Field(default=None, sa_column_kwargs={"name": "SecretCode"})
    link: str | None = Field(default=None, sa_type=Text, sa_column_kwargs={"name": "Link"})
    expiry: datetime.datetime | None = Field(default=None, sa_column_kwargs={"name": "Expiry"})
    created: datetime.datetime | None = Field(
        default_factory=datetime.datetime.now,
        sa_column_kwargs={"name": "Created", "server_default": NOW_DEFAULT},
    )
    last_modified: datetime.datetime | None = Field(default=None, sa_column_kwargs={"name": "LastModified"})

    __table_args__ = (CheckConstraint("SecretCode > 0"),)


TRIGGERS = (
    """
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
    """,
)
