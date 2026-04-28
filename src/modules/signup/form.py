from typing import Union

import discord
from discord import ui, Interaction
from discord._types import ClientT

from global_src.base_db_classes import Application
from modules.signup.embeds import ExistingApplicationEmbed, ExistingMemberEmbed


class SignUpForm(ui.Modal, title="Verification Form"):
    def __init__(self):
        super().__init__()
        self.user: Union[discord.Member, None] = None
        self.message: Union[discord.Message, None] = None

        self.adminNo = ui.TextInput(
            label="Admin Number",
            min_length=7,
            max_length=7,
            placeholder="123456A"
        )
        self.add_item(self.adminNo)

        self.full_name = ui.TextInput(
            label="Full Name",
            min_length=3,
            max_length=120,
            placeholder="Full Name as per ID"
        )
        self.add_item(self.full_name)

        self.school = ui.TextInput(
            label="School",
            min_length=3,
            max_length=4,
            placeholder="SIT/SHSS/SDM..."
        )
        self.add_item(self.school)

        self.phone_number = ui.TextInput(
            label="Phone Number",
            min_length=8,
            max_length=15,
            placeholder="12345678"
        )
        self.add_item(self.phone_number)

    async def on_submit(self, interaction: Interaction[ClientT], /) -> None:
        application = await Application.from_discord_id(interaction.user.id)
        if application:
            if application.status == 0:
                await interaction.response.send_message(embed=ExistingApplicationEmbed(), ephemeral=True)
                return
            else:
                if application.status == 1:
                    await interaction.response.send_message(embed=ExistingMemberEmbed(), ephemeral=True)
                    return
        new_application = Application(
            admin_no=self.adminNo,
            name=self.full_name,
            discord_id=interaction.user.id,
            school=self.school,
            phone_no=self.phone_number
        )
        await new_application.save()
        embed = new_application.embed()
        await interaction.response.send_message(embed=embed, ephemeral=True)


