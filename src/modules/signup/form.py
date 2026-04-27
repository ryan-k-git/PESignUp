from typing import Union, Optional
from abc import ABC, abstractmethod
from discord import ui
import discord
from global_src.db import DATABASE


class ApprovalView(ui.View, ABC):
    def __init__(self, timeout:Optional[int]=20):
        super().__init__(timeout=timeout)

    async def _disable_buttons(self, interaction: discord.Interaction):
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        await interaction.message.edit(view=self)

    @abstractmethod
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button): ...

    @abstractmethod
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button): ...


class ListenerApproval(ApprovalView):
    def __init__(self):
        super().__init__(timeout=None)
        self.config = CONFIG

    async def _disable_buttons(self, interaction: discord.Interaction):
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        await interaction.message.edit(view=self)

    @ui.button(label="✅ Approve", style=discord.ButtonStyle.green, custom_id="listener_approve")
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = await DATABASE.get_application_from_message_id(interaction.message.id)
        if not data:
            await interaction.response.send_message("No application data found for this message.", ephemeral=True)
            return
        admin_no = data[0]
        await DATABASE.set_application_status(admin_no, 1)
        await interaction.response.send_message(f"Application - {admin_no} approved by {interaction.user.name}\nMessage Unpinned")
        await self._disable_buttons(interaction)
        try:
            await interaction.message.unpin(reason=f"Accepted by {interaction.user.name}")
        except Exception as e:
            print(f"Failed to unpin message: {e}")

    @ui.button(label="❌ Reject", style=discord.ButtonStyle.red, custom_id="listener_reject")
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = await DATABASE.get_application_from_message_id(interaction.message.id)
        if not data:
            await interaction.response.send_message("No application data found for this message.", ephemeral=True)
            return
        admin_no = data[0]
        await DATABASE.set_application_status(admin_no, 2)
        await interaction.response.send_message(f"Application - {admin_no} rejected by {interaction.user.name}\nMessage Unpinned")
        await self._disable_buttons(interaction)
        try:
            await interaction.message.unpin(reason=f"Rejected by {interaction.user.name}")
        except Exception as e:
            print(f"Failed to unpin message: {e}")

class CommandApproval(ApprovalView):
    def __init__(self, admin_no: str):
        super().__init__(timeout=None)
        self.admin_no = admin_no

    @ui.button(label="✅ Approve", style=discord.ButtonStyle.green, custom_id="command_approve")
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = await DATABASE.get_application_by_admin_no(self.admin_no)
        if not data:
            await interaction.response.send_message("No application data found for this user.", ephemeral=True)
            return
        admin_no = data[0]
        await DATABASE.set_application_status(admin_no, 1)

        await interaction.response.send_message(
            f"Application - {admin_no} approved by {interaction.user.name}\nMessage Unpinned")
        await self._disable_buttons(interaction)
        try:
            await interaction.message.unpin(reason=f"Accepted by {interaction.user.name}")
        except Exception as e:
            print(f"Failed to unpin message: {e}")


    @ui.button(label="❌ Reject", style=discord.ButtonStyle.red, custom_id="command_reject")
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = await DATABASE.get_application_by_admin_no(self.admin_no)
        if not data:
            await interaction.response.send_message("No application data found for this user.", ephemeral=True)
            return
        admin_no = data[0]
        await DATABASE.set_application_status(admin_no, 2)

        await interaction.response.send_message(
            f"Application - {admin_no} rejected by {interaction.user.name}\nMessage Unpinned")
        await self._disable_buttons(interaction)
        try:
            await interaction.message.unpin(reason=f"Rejected by {interaction.user.name}")
        except Exception as e:
            print(f"Failed to unpin message: {e}")


class SignUpForm(ui.Modal, title="Sign Up Form"):
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



    async def on_submit(self, interaction: discord.Interaction):
        user = await DATABASE.get_application_by_discord_id(interaction.user.id)
        if user:
            await interaction.response.send_message("You have already submitted an application. Please message an administrator if you have made a mistake", ephemeral=True)
            return
        self.user = interaction.user
        embed = discord.Embed(title="Form Info", description=f"Sent by {interaction.user.name}", color=discord.Color.blue())
        embed.add_field(name="Admin Number", value=self.adminNo.value, inline=False)
        embed.add_field(name="Full name", value=self.full_name.value, inline=False)
        embed.add_field(name="School", value=self.school.value, inline=False)
        embed.add_field(name="Phone number", value=self.phone_number.value, inline=False)
        channel = interaction.client.get_channel(CONFIG["channels"]["approvals"])
        await DATABASE.create_application(
            discord_id=interaction.user.id,
            full_name=self.full_name.value,
            school=self.school.value,
            phone_number=self.phone_number.value,
            admin_no=self.adminNo.value
        )
        valid = await authenticate_user_information(self.adminNo.value, self.full_name.value, self.school.value, self.phone_number.value)
        if not valid:
            self.message = await channel.send(embed=embed, view=ListenerApproval())
            await DATABASE.add_application_message(self.adminNo.value, self.message.id)
        else:
            await DATABASE.set_application_status(self.adminNo.value, 1)
            await channel.send(f"This Application has been automatically authenticated", embed=embed)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        try:
            await self.message.pin(reason="awaiting approval")
        except Exception as e:
            print(f"Failed to pin message: {e}")

