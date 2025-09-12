import traceback

import discord
from discord import Interaction, app_commands
from discord.ext import commands
from discord.ext.commands import errors
from discord.ext.commands.context import Context

from logger import get_child_logger

logger = get_child_logger(__name__)


# デバック用コマンド群
class AdminToolsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # コマンドが正常に実行されたらリアクションをつける
    @commands.Cog.listener()
    async def on_command_completion(self, ctx: Context) -> None:
        ctx.message.add_reaction("✅")

    async def cog_command_error(
        self, ctx: Context, error: errors.CommandError
    ) -> None:
        if isinstance(error, (errors.CommandNotFound, errors.CheckAnyFailure)):
            return

        logger.error("例外が発生しました: %s", error, exc_info=True)

        footer: str = type(error).__name__

        if isinstance(error, errors.CommandInvokeError):
            error = error.original

        exce_info = traceback.format_exception(
            type(error), error, error.__traceback__
        )

        embed = (
            discord.Embed(
                title=type(error).__name__,
                description=format(error.with_traceback(exce_info[2])),
                timestamp=ctx.message.created_at,
                colour=0xFF0000,
            )
            .add_field(name="詳細", value=f"```py\n{''.join(exce_info)}\n```")
            .set_footer(text=footer)
        )

        await ctx.message.add_reaction("❌")
        await ctx.reply(embed=embed)

    @commands.command(name="load", aliases=["l"])
    @commands.dm_only()
    @commands.is_owner()
    async def load_cog_extension(self, _, cog_name: str) -> None:
        extension: str = f"cogs.{cog_name}"
        await self.bot.load_extension(extension)

    @commands.command(name="unload", aliases=["u"])
    @commands.dm_only()
    @commands.is_owner()
    async def unload_cog_extension(self, _, cog_name: str) -> None:
        extension: str = f"cogs.{cog_name}"
        await self.bot.unload_extension(extension)

    @commands.command(name="reload", aliases=["r"])
    @commands.dm_only()
    @commands.is_owner()
    async def reload_cog_extension(self, _, cog_name: str) -> None:
        extension: str = f"cogs.{cog_name}"
        await self.bot.reload_extension(extension)

    @app_commands.command()
    async def test(self, interaction: Interaction) -> None:
        await interaction.response.send_message("テストコマンドだよ")
