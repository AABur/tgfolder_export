#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
#     "telethon",
#     "tqdm"
# ]
# ///

from __future__ import annotations

import argparse
import json
import logging
import os
from datetime import UTC, datetime, timedelta
from importlib.metadata import version
from pathlib import Path
from typing import Any, cast

from dotenv import load_dotenv
from telethon import functions, types
from telethon.errors.rpcerrorlist import (
    AuthKeyError,
    ChannelPrivateError,
    FloodWaitError,
)
from telethon.sync import TelegramClient
from tqdm import tqdm

# Default file names
DEFAULT_JSON_FILE = "tgf-list.json"
DEFAULT_TEXT_FILE = "tgf-list.txt"
DEFAULT_SESSION_DIR = ".tempts"
DEFAULT_SESSION_FILE = "tg.session"
SESSION_TTL_DAYS = 7


def get_config() -> dict[str, Any]:
    """Load and validate Telegram API configuration from environment variables.

    Returns:
        Configuration dictionary with Telegram API credentials.

    Raises:
        ValueError: If required environment variables are missing or invalid.
    """
    load_dotenv()

    api_id = os.getenv("app_api_id")
    api_hash = os.getenv("app_api_hash")

    if not api_id or not api_hash:
        raise ValueError(
            "Missing required environment variables: app_api_id and app_api_hash. "
            "Please copy .env.sample to .env and set these values"
        )

    try:
        app_id = int(api_id)
        if app_id <= 0:
            raise ValueError(f"app_api_id must be a positive integer, got: {app_id}")
    except ValueError as e:
        if "invalid literal" in str(e).lower():
            raise ValueError(
                f"app_api_id must be a valid integer, got: {api_id!r}"
            ) from e
        raise

    return {
        "tg": {
            "app_id": app_id,
            "app_hash": api_hash,
        }
    }


def get_session_path() -> Path:
    """Get session file path, creating directory if needed.

    Returns:
        Path to the session file in hidden .tempts directory.
    """
    session_dir = Path(DEFAULT_SESSION_DIR)
    session_dir.mkdir(exist_ok=True)
    return session_dir / DEFAULT_SESSION_FILE


def is_session_expired(session_path: Path) -> bool:
    """Check if session file is older than SESSION_TTL_DAYS.

    Args:
        session_path: Path to the session file.

    Returns:
        True if session is expired or doesn't exist, False otherwise.
    """
    if not session_path.exists():
        return False

    session_age = datetime.now(UTC) - datetime.fromtimestamp(
        session_path.stat().st_mtime, UTC
    )
    return session_age > timedelta(days=SESSION_TTL_DAYS)


def cleanup_expired_session(session_path: Path) -> None:
    """Delete expired session file and related files.

    Args:
        session_path: Path to the session file to clean up.
    """
    if not session_path.exists():
        return

    LOG.info("Removing expired session file (older than %d days)", SESSION_TTL_DAYS)

    # Remove main session file
    session_path.unlink(missing_ok=True)

    # Remove journal file if exists
    journal_file = session_path.with_suffix(".session-journal")
    journal_file.unlink(missing_ok=True)


def force_clear_session() -> None:
    """Force clear Telegram session files.

    Deletes session file and related files, printing status message.
    Used when user explicitly requests session cleanup via --clear-session.
    """
    session_path = get_session_path()

    if not session_path.exists():
        print("No session found to clear.")
        return

    print(f"Clearing session: {session_path}")

    # Remove main session file
    session_path.unlink(missing_ok=True)

    # Remove journal file if exists
    journal_file = session_path.with_suffix(".session-journal")
    journal_file.unlink(missing_ok=True)

    print("Session cleared successfully.")


LOG = logging.getLogger(__name__)


def get_entity_type_name(ent: types.TLObject) -> str:
    """Determine entity type from Telegram API object.

    Args:
        ent: Telegram API entity (User, Channel, or Chat).

    Returns:
        Entity type: "user", "channel", or "group".

    Raises:
        TypeError: If entity type is not supported.
    """
    if isinstance(ent, types.User):
        return "user"
    if isinstance(ent, types.Channel):
        return "channel" if ent.broadcast else "group"
    if isinstance(ent, types.Chat):
        return "group"
    raise TypeError(f"Unknown entity type: {type(ent)}")


def get_entity_name(ent: types.TLObject) -> str | None:
    """Extract display name from Telegram entity.

    Args:
        ent: Telegram API entity.

    Returns:
        Display name or None if not available.

    Raises:
        TypeError: If entity type is not supported.
    """
    if isinstance(ent, types.Channel | types.Chat):
        return None if ent.title is None else cast("str", ent.title)
    if isinstance(ent, types.User):
        return ((ent.first_name or "") + " " + (ent.last_name or "")).strip()
    raise TypeError(f"Unknown entity type: {type(ent)}")


def export_entity(ent: types.TLObject) -> dict[str, Any]:
    """Convert Telegram entity to standardized export format.

    Args:
        ent: Telegram API entity to export.

    Returns:
        Dictionary with entity data: type, id, name, username.
    """
    result = {
        "type": get_entity_type_name(ent),
        "id": ent.id,
        "name": get_entity_name(ent),
    }

    # Only User and Channel entities have username attribute
    result["username"] = ent.username if hasattr(ent, "username") else None
    return result


def export_dialog_filter(
    client: TelegramClient, dlg_filter: types.DialogFilter
) -> dict[str, Any]:
    """Export Telegram folder and its peers to structured format.

    Args:
        client: Authenticated Telegram client.
        dlg_filter: Telegram dialog filter (folder) to export.

    Returns:
        Dictionary with folder data: id, title, and list of peers.
    """
    result = {
        "id": dlg_filter.id,
        "title": dlg_filter.title.text,
        "peers": [],
    }
    for input_peer in dlg_filter.include_peers:
        try:
            ent = client.get_entity(input_peer)
        except (ChannelPrivateError, FloodWaitError, AuthKeyError) as ex:
            LOG.error(
                "Telegram API error for peer in folder '%s': %s - %s",
                dlg_filter.title.text,
                type(ex).__name__,
                ex,
            )
            continue
        result["peers"].append(export_entity(ent))
    return result


def render_result(result: list[dict[str, Any]]) -> str:
    """Render results as JSON."""
    return json.dumps(result, indent=2, ensure_ascii=False)


def render_text_result(result: list[dict[str, Any]]) -> str:
    """Render results as formatted text."""
    lines = ["TELEGRAM FOLDERS EXPORT", "=======================", ""]
    total_folders = len(result)
    total_channels = 0
    total_groups = 0
    total_users = 0

    folder_prefix_length = 8  # "Folder: "
    for folder in result:
        lines.extend(
            (
                f"Folder: {folder['title']}",
                "-" * (folder_prefix_length + len(folder["title"])),
            )
        )
        # Distribute peers into separate lists by type (channel, group, user)
        channels: list[dict[str, Any]] = []
        groups: list[dict[str, Any]] = []
        users: list[dict[str, Any]] = []
        type_map = {"channel": channels, "group": groups, "user": users}
        for peer in folder["peers"]:
            type_map.get(peer["type"], []).append(peer)

        total_channels += len(channels)
        total_groups += len(groups)
        total_users += len(users)

        if channels:
            lines.append(f"Channels ({len(channels)}):")
            for peer in channels:
                username_part = f" (@{peer['username']})" if peer["username"] else ""
                name = peer["name"] or "Unnamed Channel"
                lines.append(f"  • {name}{username_part} [ID: {peer['id']}]")
            lines.append("")

        if groups:
            lines.append(f"Groups ({len(groups)}):")
            for peer in groups:
                username_part = f" (@{peer['username']})" if peer["username"] else ""
                name = peer["name"] or "Unnamed Group"
                lines.append(f"  • {name}{username_part} [ID: {peer['id']}]")
            lines.append("")

        if users:
            lines.append(f"Users ({len(users)}):")
            for peer in users:
                username_part = f" (@{peer['username']})" if peer["username"] else ""
                name = peer["name"] or "Unnamed User"
                lines.append(f"  • {name}{username_part} [ID: {peer['id']}]")
            lines.append("")

        if not (channels or groups or users):
            lines.extend(("No items", ""))
    lines.extend(
        (
            "=======================",
            f"Total: {total_folders} folders, {total_channels} channels, {total_groups} groups, {total_users} users",
            f"Generated: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC",
        )
    )
    return "\n".join(lines)


def setup_logging() -> None:
    """Configure logging settings."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

    if log_level not in valid_levels:
        log_level = "INFO"

    logging.basicConfig(level=getattr(logging, log_level))


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    try:
        __version__ = version("tgfolder_export")
    except Exception:
        __version__ = "unknown"

    parser = argparse.ArgumentParser(
        description="Export Telegram folder contents to file"
    )
    parser.add_argument(
        "--version", action="version", version=f"tgfolder_export {__version__}"
    )

    # Session management
    parser.add_argument(
        "--clear-session",
        action="store_true",
        help="Clear saved Telegram session and exit",
    )

    # Output format options (required unless --clear-session is used)
    output_group = parser.add_mutually_exclusive_group(required=False)
    output_group.add_argument(
        "-j",
        "--json",
        nargs="?",
        const=DEFAULT_JSON_FILE,
        metavar="FILE",
        help=f"Export to JSON format (default: {DEFAULT_JSON_FILE})",
    )
    output_group.add_argument(
        "-t",
        "--text",
        nargs="?",
        const=DEFAULT_TEXT_FILE,
        metavar="FILE",
        help=f"Export to text format (default: {DEFAULT_TEXT_FILE})",
    )
    return parser


def process_telegram_data(client: TelegramClient) -> list[dict[str, Any]]:
    """Process Telegram folder data and return structured results."""
    result = []
    dlg_filters = client(functions.messages.GetDialogFiltersRequest())

    # Filter out default folder and show progress
    custom_filters = [
        f for f in dlg_filters.filters if not isinstance(f, types.DialogFilterDefault)
    ]

    for dlg_filter in tqdm(custom_filters, desc="Processing folders"):
        LOG.info("Processing folder %s", dlg_filter.title.text)
        result.append(export_dialog_filter(client, dlg_filter))
    return result


def write_output(filename: str, content: str) -> None:
    """Write content to file and log completion."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    LOG.info("Export completed successfully")


def save_results(data: list[dict[str, Any]], args: argparse.Namespace) -> None:
    """Save results in the requested format."""
    if args.json:
        output_file = args.json
        content = render_result(data)
        LOG.info("Writing JSON output to %s", output_file)
        write_output(output_file, content)
    elif args.text:
        output_file = args.text
        content = render_text_result(data)
        LOG.info("Writing text output to %s", output_file)
        write_output(output_file, content)


def main() -> None:
    """Main entry point."""
    parser = create_argument_parser()
    args = parser.parse_args()

    # Handle session clearing
    if args.clear_session:
        force_clear_session()
        return

    # Validate that output format is specified
    if not args.json and not args.text:
        parser.error("One of -j/--json or -t/--text is required")

    setup_logging()
    config = get_config()

    session_path = get_session_path()

    if is_session_expired(session_path):
        cleanup_expired_session(session_path)

    client = TelegramClient(
        str(session_path),
        config["tg"]["app_id"],
        config["tg"]["app_hash"],
    )

    with client:
        result = process_telegram_data(client)

    save_results(result, args)


if __name__ == "__main__":
    main()
