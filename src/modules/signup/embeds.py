from global_src.base_embeds import BaseEmbed


class ExistingApplicationEmbed(BaseEmbed):
    def __init__(self):
        super().__init__(
            title="Existing Application Found",
            description="""
            You have already submitted an application. Please wait for an Exco member to review and approve your request.
            You may approach an Exco if you have made a mistake or wish to update your application.
            """,
            color=0xFF0000
        )

class ExistingMemberEmbed(BaseEmbed):
    def __init__(self):
        super().__init__(
            title="Existing Member Already",
            description="""
            You are already a member and cannot send another application
            """
        )