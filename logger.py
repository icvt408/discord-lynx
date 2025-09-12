import logging
import os
from logging import Formatter, Logger, StreamHandler
from logging.handlers import RotatingFileHandler


def setup_logging() -> Logger:
    log_directory: str = "logs"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    logger: Logger = logging.getLogger("Lynx")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    datefmt: str = "%Y-%m-%d %H:%M:%S"
    fmt: str = "[{asctime}] [{levelname:<8}] {name}: {message}"
    formatter: Formatter = Formatter(fmt=fmt, datefmt=datefmt, style="{")

    log_file_path: str = os.path.join(log_directory, "bot.log")
    file_handler: RotatingFileHandler = RotatingFileHandler(
        log_file_path,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler: StreamHandler = StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    discord_logger: Logger = logging.getLogger("discord")
    discord_logger.setLevel(logging.DEBUG)

    discord_log_file_path: str = os.path.join(log_directory, "discord.log")
    discord_file_handler: RotatingFileHandler = RotatingFileHandler(
        discord_log_file_path,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    discord_file_handler.setFormatter(formatter)
    discord_logger.addHandler(discord_file_handler)

    logging.getLogger("discord.http").setLevel(logging.WARNING)

    return logger


def get_child_logger(name: str) -> Logger:
    logger: Logger = logging.getLogger("Lynx")

    if not logger.handlers:
        logger = setup_logging()

    return logger.getChild(name)


if __name__ == "__main__":
    logger = setup_logging()
    logger.info("loggerがセットアップされました")
    logger.warning("警告メッセージ")
    try:
        raise ValueError("テストメッセージ")
    except ValueError as e:
        logger.error("エラーが発生しました: %s", e, exc_info=True)

    child_logger = get_child_logger("test")
    child_logger.info("子ロガーがセットアップされました")
    child_logger.warning("子ロガーの警告メッセージ")
    try:
        raise ValueError("子ロガーだよ")
    except ValueError as e:
        child_logger.error(
            "子ロガーでエラーが発生しました: %s", e, exc_info=True
        )
