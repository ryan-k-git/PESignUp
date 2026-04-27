import datetime
from abc import ABC
from typing import Literal
import re
from rapidfuzz import fuzz

from global_src.db import DATABASE
from global_src.general_utils.string_cleaning import normalize

class BaseClass(ABC):
    pass

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

    async def get_member_info(self):
        return await self.from_admin_no(self.admin_no)

