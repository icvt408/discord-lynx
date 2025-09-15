import os
from typing import List, Optional

import discord
import dotenv
from discord import Embed, Intents, Interaction
from discord.app_commands import AppCommand, AppCommandError, errors
from discord.ext import commands

import error_handler
from admin_tools import AdminToolsCog
from logger import Logger, setup_logging

logger: Logger = setup_logging()

dotenv.load_dotenv()


class Lynx(commands.Bot):
    async def setup_hook(self) -> None:
        guild_id_str: str = os.getenv("DEBUG_GUILD_ID")
        guild_id: int = int(guild_id_str) if guild_id_str else None

        # 登録されているコマンドを削除(グローバルとギルドで重複するため)
        if guild_id:
            await self.tree.sync()
            logger.info("グローバルコマンドをリセットしました。")

        # 非extensionなcogの読み込み
        await self.add_cog(AdminToolsCog(self))
        logger.info("AdminToolsCogを読み込みました。")

        cog_dir: str = "./cogs"

        # cogのディレクトリがあるかチェックする
        if not os.path.exists(cog_dir):
            logger.warning("%sが見つかりませんでした。", cog_dir)
            return

        # ./cogsディレクトリのcogファイルを読み込む
        for filename in os.listdir(cog_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                cog_file: str = f"cogs.{filename[:-3]}"
                await self.load_extension(cog_file)
                logger.info("%sを読み込みました。", cog_file)

        await self.sync_command(guild_id)

    async def sync_command(
        self, guild_id: Optional[int] = None
    ) -> List[AppCommand]:

        logger.debug(
            "ボットのコマンドツリーに現在登録されているコマンド数: %s",
            len(self.tree.get_commands()),
        )

        for cmd in self.tree.get_commands():
            logger.debug("  - 登録済みコマンド: /%s", cmd.name)

        try:
            if guild_id:
                self.tree.copy_global_to(guild=discord.Object(guild_id))
                logger.info(
                    "コマンドをすべてギルド(%s)にコピーしました。",
                    guild_id,
                )

            synced_commands = await self.tree.sync(
                guild=discord.Object(guild_id) if guild_id else None
            )

            if synced_commands:
                logger.info(
                    "%s 個のコマンドを同期しました。",
                    len(synced_commands),
                )
                for command in synced_commands:
                    logger.debug(
                        "  - 同期されたコマンド: /%s (ID: %s)",
                        command.name,
                        command.id,
                    )

            else:
                logger.warning(
                    "コマンドは同期されませんでした（0個）。",
                )

        except discord.errors.Forbidden as e:
            logger.error(
                "コマンドを同期する権限がありません。"
                "Botに 'applications.commands' スコープがあるか確認してください。エラー: %s",
                e,
                exc_info=True,
            )
        except discord.app_commands.errors.CommandLimitReached as e:
            logger.error(
                "ギルドの最大コマンド数に達しました。: %s", e, exc_info=True
            )
        except Exception as e:
            logger.error(
                "コマンド同期中に予期せぬエラーが発生しました: %s",
                e,
                exc_info=True,
            )


intents: Intents = Intents.default()
intents.message_content = True
intents.guilds = True

bot: Lynx = Lynx(command_prefix="ln/", intents=intents)


@bot.event
async def on_ready() -> None:
    logger.info("%s(%s)としてログインしました。", bot.user, bot.user.id)


@bot.tree.error
async def on_app_command_error(
    interaction: Interaction, error: AppCommandError
):
    user = interaction.user
    channel = interaction.channel
    command = interaction.command

    logger.error(
        "コマンド '%s' の実行中にエラーが発生しました。"
        "\nUser         : %s (%s)"
        "\nChannel      : #%s (%s)"
        "\nError Type   : %s"
        "\nError Details: %s",
        command.name,
        user.name,
        user.id,
        channel.name,
        channel.id,
        type(error).__name__,
        error,
        exc_info=True,
    )

    embed: Embed = error_handler.parse_appcommand_error(error)
    embed.timestamp = interaction.created_at

    try:
        interaction.response.send_message(embed=embed, ephemeral=True)
    except errors.InteractionResponded:
        interaction.followup.send(embed=embed, ephemeral=True)


if __name__ == "__main__":
    logger.info("起動しています...")
    bot.run(os.environ["DISCORD_TOKEN"], log_handler=None)
