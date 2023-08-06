"""CLI module."""

import asyncio
import logging
import os
from typing import Any

import appdirs
import click
import rich

from omoidasu import commands, config

# Default directories
app_dir_settings = {"appname": "omoidasu"}
_CONFIG_DIR = appdirs.user_config_dir(**app_dir_settings)
_DATA_DIR = appdirs.user_data_dir(**app_dir_settings)
_CACHE_DIR = appdirs.user_cache_dir(**app_dir_settings)
_STATE_DIR = appdirs.user_state_dir(**app_dir_settings)
_LOG_DIR = appdirs.user_log_dir(**app_dir_settings)
_FLASHCARDS_DIR = os.path.join(_STATE_DIR, "default_flashcards_dir")

# Environment variables
_PREFIX = "OMOIDASU"
_CONFIG_DIR = os.environ.get(_PREFIX + "_CONFIG_DIR", _CONFIG_DIR)
_DATA_DIR = os.environ.get(_PREFIX + "_DATA_DIR", _DATA_DIR)
_CACHE_DIR = os.environ.get(_PREFIX + "_CACHE_DIR", _CACHE_DIR)
_STATE_DIR = os.environ.get(_PREFIX + "_STATE_DIR", _STATE_DIR)
_LOG_DIR = os.environ.get(_PREFIX + "_LOG_DIR", _LOG_DIR)
_FLASHCARDS_DIR = os.environ.get(_PREFIX + "_FLASHCARDS_DIR", _FLASHCARDS_DIR)

logger = logging.getLogger(__name__)


INFO_TEXT = """CLI for Omoidasu."""


def _run_async_command(func: Any, *args, **kwargs) -> Any:
    context = args[0]
    if context.obj.debug:
        rich.inspect(context.obj, title="Context")
        rich.inspect(args, title="Args")
        rich.inspect(kwargs, title="Kwargs")
    return asyncio.run(func(*args, **kwargs))


@click.group(help=INFO_TEXT)
@click.option("--data-dir", type=str, default=_DATA_DIR, help="Data directory.")
@click.option("--config-dir", type=str, default=_CONFIG_DIR, help="Config directory.")
@click.option("--cache-dir", type=str, default=_CACHE_DIR, help="Cache directory.")
@click.option("--state-dir", type=str, default=_STATE_DIR, help="State directory.")
@click.option("--log-dir", type=str, default=_LOG_DIR, help="Log directory.")
@click.option(
    "--flashcards-dir", type=str, default=_FLASHCARDS_DIR, help="Flashcards directory."
)
@click.option("--verbose/--no-verbose", help="Show additional information.")
@click.option("--interactive/--no-interactive", help="Use interactive features.")
@click.option("--debug/--no-debug", help="Show debug information.")
@click.pass_context
def cli_commands(context, **kwargs):
    """CLI commands"""
    context.obj = config.AppConfig(**kwargs)
    if kwargs["debug"]:
        logger.setLevel(level=logging.DEBUG)
        logging.basicConfig(level=logging.DEBUG)
        rich.inspect(context.obj)


@cli_commands.command("list")
@click.argument("regular_expression", default=".*", required=True, type=str)
@click.option(
    "--max-cards", default=1000, type=int, help="Max number of cards to list."
)
@click.pass_context
def list_cards(*args, **kwargs):
    """Writes all cards to stdout."""
    return _run_async_command(commands.list_cards, *args, **kwargs)


@cli_commands.command("review")
@click.argument("regular_expression", default=".*", required=True, type=str)
@click.option(
    "--max-cards", default=1000, type=int, help="Max number of cards to review.")
@click.pass_context
def review_cards(*args, **kwargs):
    """Review all cards."""
    return _run_async_command(commands.review_cards, *args, **kwargs)


@cli_commands.command("new")
@click.argument("sides", nargs=-1)
@click.pass_context
def add_card(*args, **kwargs):
    """Add card."""
    return _run_async_command(commands.add_card, *args, **kwargs)

@cli_commands.command("add")
@click.option("--editor", type=str)
@click.pass_context
def add_cards_interactively(*args, **kwargs):
    """Add cards interactively using text editor.
Save empty file to finish adding cards.
"""
    return _run_async_command(
            commands.add_cards_interactively, *args, **kwargs)


def main():
    """Main function."""
    cli_commands()  # pylint: disable=no-value-for-parameter


if __name__ == "__main__":
    main()
