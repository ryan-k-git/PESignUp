import datetime
from abc import ABC, abstractmethod
from typing import Literal
from rapidfuzz import fuzz

from global_src.base_embeds import BaseEmbed
from global_src.db import DATABASE
from global_src.general_utils.string_cleaning import normalize

class BaseClass(ABC):

    @abstractmethod
    async def save(self):
        raise NotImplementedError("Subclasses must implement the save method")

    @abstractmethod
    async def embed(self):
        raise NotImplementedError("Subclasses must implement the embed method")


class MemberInfo(BaseClass):
    def __init__(self, discord_id: int, admin_no: str):
        self.id = discord_id
        self.admin_no = admin_no.upper()

    @classmethod
    async def from_discord_id(cls, discord_id: int):
        admin_no = await DATABASE.fetch_one("SELECT AdminNo FROM MemberInfo WHERE DiscordID=?", (discord_id,))
        if not admin_no:
            return None
        return cls(discord_id, admin_no[0])

    @classmethod
    async def from_admin_no(cls, admin_no: int):
        discord_id = await DATABASE.fetch_one("SELECT DiscordID FROM MemberInfo WHERE AdminNo=?", (admin_no,))
        if not discord_id:
            return None
        return cls(discord_id[0], admin_no)

    async def embed(self):
        embed = BaseEmbed(title="Member Info")
        embed.add_field(name="Admin Number", value=self.admin_no, inline=False)
        embed.add_field(name="Discord ID", value=self.id, inline=False)
        return embed

    async def save(self):
        await DATABASE.execute("""
        INSERT INTO MemberInfo (AdminNo, DiscordID)
        VALUES (?, ?)
        ON CONFLICT(AdminNo) DO UPDATE SET
            DiscordID=excluded.DiscordID
        """, (self.admin_no, self.id))
        return


class MemberListInfo(BaseClass):
    def __init__(
            self,
            admin_no: str,
            name: str=None,
            gender: Literal["M", "F", "O"]=None,
            school: str=None,
            study_stage: int=None,
            phone_number: str=None,
            reg_date: str=None,
            reg_status: str=None,
            appointment_date: str=None,
                 ):
        super().__init__()
        self.admin_no = admin_no.upper()
        self.name = name
        self.gender = gender
        self.school = school
        self.study_stage = study_stage
        self.phone_number = phone_number
        self.reg_date = reg_date
        self.reg_status = reg_status
        self.appointment_date = appointment_date

    @classmethod
    async def from_admin_no(cls, admin_no: str):
        data = await DATABASE.fetch_one("SELECT Name, Gender, School, StudyStage, PhoneNo, RegDate, RegStatus, AppointmentDate FROM MemberListInfo WHERE AdminNo=?", (admin_no,))
        if not data:
            return None
        name, gender, school, study_stage, phone_number, reg_date, reg_status, appointment_date = data
        return cls(
            admin_no=admin_no,
            name=name,
            gender=gender,
            school=school,
            study_stage=study_stage,
            phone_number=phone_number,
            reg_date=reg_date,
            reg_status=reg_status,
            appointment_date=appointment_date
        )

    @classmethod
    async def from_name(cls, name: str):
        all_members = await DATABASE.fetch_all("SELECT AdminNo, Name FROM MemberListInfo")
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

    async def embed(self):
        embed = BaseEmbed(title="Member List Info")
        embed.add_field(name="Admin Number", value=self.admin_no, inline=False)
        embed.add_field(name="Name", value=self.name, inline=False)
        embed.add_field(name="Gender", value=self.gender, inline=False)
        embed.add_field(name="School", value=self.school, inline=False)
        embed.add_field(name="Study Stage", value=self.study_stage, inline=False)
        embed.add_field(name="Phone No", value=self.phone_number, inline=False)
        embed.add_field(name="Reg Date", value=self.reg_date, inline=False)
        embed.add_field(name="Reg Status", value=self.reg_status, inline=False)
        embed.add_field(name="Appointment Date", value=self.appointment_date, inline=False)
        return embed

    async def save(self):
        await DATABASE.execute("""
        INSERT INTO MemberListInfo (
AdminNo, Name, Gender, School, Study, PhoneNo, RegDate, RegStatus, AppointmentDate
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(AdminNo) DO UPDATE SET
Name=excluded.Name,
Gender=excluded.Gender,
School=excluded.School,
Study=excluded.Study,
PhoneNo=excluded.PhoneNo,
RegDate=excluded.RegDate,
RegStatus=excluded.RegStatus,
AppointmentDate=excluded.AppointmentDate
                               """,
                               (self.name, self.gender, self.school,
                                self.study_stage, self.phone_number, self.reg_date,
                                self.reg_status, self.appointment_date, self.admin_no))

    async def get_member_info(self):
        return await self.from_admin_no(self.admin_no)

class Application(BaseClass):
    def __init__(self, admin_no: str, name: str, discord_id: int, school: str, phone_no: str, status: int = 0, created: datetime.datetime = None, last_modified: datetime.datetime = None, message_id: int = None):
        self.admin_no = admin_no.upper()
        self.discord_id = discord_id
        self.name = name
        self.school = school
        self.phone_no = phone_no
        self.status = status
        self.created = created or datetime.datetime.now()
        self.last_modified = last_modified
        self.message_id = message_id

    @classmethod
    async def from_admin_no(cls, admin_no: str):
        data = await DATABASE.fetch_one(
            "SELECT DiscordID, Name, School, PhoneNo, Status, Created, LastModified, MessageID FROM Application WHERE AdminNo=?",
            (admin_no,)
        )
        if not data:
            return None
        discord_id, name, school, phone_no, status, created, last_modified, message_id = data
        return cls(
            admin_no=admin_no,
            discord_id=discord_id,
            name=name,
            school=school,
            phone_no=phone_no,
            status=status,
            created=created,
            last_modified=last_modified,
            message_id=message_id,
        )

    @classmethod
    async def from_discord_id(cls, discord_id: int):
        data = await DATABASE.fetch_one(
            "SELECT AdminNo, Name, School, PhoneNo, Status, Created, LastModified, MessageID FROM Application WHERE DiscordID=?",
            (discord_id,)
        )
        if not data:
            return None
        admin_no, name, school, phone_no, status, created, last_modified, message_id = data
        return cls(
            admin_no=admin_no,
            discord_id=discord_id,
            name=name,
            school=school,
            phone_no=phone_no,
            status=status,
            created=created,
            last_modified=last_modified,
            message_id=message_id,
        )

    async def embed(self):
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

    async def save(self):
        await DATABASE.execute(
            """
            INSERT INTO Application (AdminNo, DiscordID, Name, School, PhoneNo, Status, Created, LastModified, MessageID)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(AdminNo) DO UPDATE SET
                DiscordID=excluded.DiscordID,
                Name=excluded.Name,
                School=excluded.School,
                PhoneNo=excluded.PhoneNo,
                Status=excluded.Status,
                LastModified=excluded.LastModified,
                MessageID=excluded.MessageID
            """,
            (
                self.admin_no,
                self.discord_id,
                self.name,
                self.school,
                self.phone_no,
                self.status,
                self.created,
                self.last_modified,
                self.message_id,
            ),
        )
