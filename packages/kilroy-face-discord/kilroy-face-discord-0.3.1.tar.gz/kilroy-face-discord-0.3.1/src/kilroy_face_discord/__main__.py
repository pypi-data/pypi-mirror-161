"""Main script.

This module provides basic CLI entrypoint.

"""
import asyncio
import logging
from enum import Enum
from logging import Logger

import typer
from kilroy_ws_server_py_sdk import Server

from kilroy_face_discord.config import FaceConfig, ServerConfig
from kilroy_face_discord.controller import DiscordController
from kilroy_face_discord.face import DiscordFace

cli = typer.Typer()  # this is actually callable and thus can be an entry point


class Verbosity(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


def get_logger(verbosity: Verbosity) -> Logger:
    logging.basicConfig()
    logger = logging.getLogger("kilroy-face-discord")
    logger.setLevel(verbosity.value)
    return logger


async def run(
    face_config: FaceConfig, server_config: ServerConfig, logger: Logger
) -> None:
    face = await DiscordFace.build(face_config)
    controller = DiscordController(face)
    server = Server(controller, logger)
    await server.run(**server_config.dict())


@cli.command()
def main(
    verbosity: Verbosity = typer.Option(
        default="INFO", help="Verbosity level."
    )
) -> None:
    """Command line interface for kilroy-face-discord."""

    face_config = FaceConfig.build()
    server_config = ServerConfig.build()
    logger = get_logger(verbosity)

    asyncio.run(run(face_config, server_config, logger))


if __name__ == "__main__":
    # entry point for "python -m"
    cli()
