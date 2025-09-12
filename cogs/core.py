from discord import Color, Embed, Interaction, app_commands
from discord.ext import commands


class Core(commands.GroupCog, group_name="lynx"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command()
    async def help(self, interaction: Interaction):
        embed: Embed = Embed(
            title="利用可能なコマンドの一覧",
            description="以下は現在利用可能なコマンドの一覧です。",
            color=Color.green,
        )

        command_list = await self.bot.tree.fetch_commands()

        if not command_list:
            embed.description = "現在利用可能なコマンドはありません。"

        else:
            for command in command_list:
                desc: str = command.description or "説明無し"

            embed.add_field(name=f"/{command.name}", value=desc, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Core(bot))
