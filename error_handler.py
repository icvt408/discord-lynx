from discord import Color, Embed
from discord.app_commands import errors

from logger import get_child_logger

logger = get_child_logger(__name__)


def parse_appcommand_error(error: errors.AppCommandError) -> Embed:
    title: str = "エラー"
    desc: str = ""
    color: Color = Color.red()
    if isinstance(error, errors.CommandInvokeError):
        title = "コマンドの実行中にエラーが発生しました"
        desc = "数分後にもう一度お試しください。"

    elif isinstance(error, errors.TransformerError):
        desc = "データの変換に失敗しました。"

    elif isinstance(error, errors.TranslationError):
        desc = "文字列の翻訳に失敗しました。"

    elif isinstance(error, errors.CheckFailure):
        title = "コマンドの実行に必要な条件を満たしていません"
        if isinstance(error, errors.NoPrivateMessage):
            desc = "このコマンドはDM専用です。"

        elif isinstance(error, errors.MissingRole):
            desc = f"ロール`{str(error.missing_role)}`が必要です。"

        elif isinstance(error, errors.MissingAnyRole):
            missing_roles: list[str] = map(
                lambda x: f"`{str(x)}`", error.missing_roles
            )
            desc = f"以下のロールが必要です:\n{"\n".join(missing_roles)}"

        elif isinstance(error, errors.MissingPermissions):
            missing_parmissons: list[str] = map(
                lambda x: f"`{x}`", error.missing_permissions
            )
            desc = f"以下の権限が必要です:\n {"\n".join(missing_parmissons)}"

        elif isinstance(error, errors.BotMissingPermissions):
            missing_parmissons: list[str] = map(
                lambda x: f"`{x}`", error.missing_permissions
            )
            desc = f"Botが以下の権限を有していません。:\n{"\n".join(missing_parmissons)}"

        elif isinstance(error, errors.CommandOnCooldown):
            title = "クールダウン中です"
            desc = f"{error.retry_after:.1f}秒後にもう一度お試しください。"
            color = Color.blue()

    elif isinstance(error, errors.CommandLimitReached):
        desc = "コマンドの最大登録数に達しました"

    elif isinstance(error, errors.CommandAlreadyRegistered):
        desc = "指定されたコマンドはすでに登録されています。"

    elif isinstance(error, errors.CommandSignatureMismatch):
        desc = "コマンドのシグネチャが一致しません。"

    elif isinstance(error, errors.CommandNotFound):
        title = "コマンドが見つかりませんでした"
        desc = "`/lynx help`で利用可能なコマンドを確認できます。"

    elif isinstance(error, errors.MissingApplicationID):
        desc = "クライアントにアプリケーションIDが設定されていません。"

    elif isinstance(error, errors.CommandSyncFailure):
        desc = "コマンドの同期に失敗しました。"
    else:
        title = "予期せぬエラーが発生しました。"
        desc = "サーバーで問題が発生しました。管理者にご連絡ください。"
        color = Color.dark_red()

    return Embed(
        title=title,
        description=desc,
        colour=color,
    ).set_footer(
        text=type(error).__name__,
    )
