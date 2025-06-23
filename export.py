#!/usr/bin/env python3
import argparse
import json
import logging
import os
from datetime import UTC, datetime
from importlib.metadata import version
from typing import Any, cast

from dotenv import load_dotenv
from telethon import functions, types
from telethon.errors.rpcerrorlist import ChannelPrivateError
from telethon.sync import TelegramClient


def get_config() -> dict[str, Any]:
    load_dotenv()

    api_id = os.getenv("app_api_id")
    api_hash = os.getenv("app_api_hash")

    if not api_id or not api_hash:
        raise ValueError(
            "Missing required environment variables. "
            "Please copy .env.sample to .env and set app_api_id and app_api_hash"
        )

    return {
        "tg": {
            "app_id": int(api_id),
            "app_hash": api_hash,
        }
    }


LOG = logging.getLogger(__name__)


def get_entity_type_name(ent: types.TLObject) -> str:
    if isinstance(ent, types.User):
        return "user"
    if isinstance(ent, types.Channel):
        return "channel" if ent.broadcast else "group"
    if isinstance(ent, types.Chat):
        return "group"
    raise TypeError(f"Unknown entity type: {type(ent)}")


def get_entity_name(ent: types.TLObject) -> None | str:
    if isinstance(ent, types.Channel | types.Chat):
        return None if ent.title is None else cast("str", ent.title)
    if isinstance(ent, types.User):
        return ((ent.first_name or "") + " " + (ent.last_name or "")).strip()
    raise TypeError(f"Unknown entity type: {type(ent)}")


def export_entity(ent: types.TLObject) -> dict[str, Any]:
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
    result = {
        "id": dlg_filter.id,
        "title": dlg_filter.title.text,
        "peers": [],
    }
    for input_peer in dlg_filter.include_peers:
        try:
            ent = client.get_entity(input_peer)
        except ChannelPrivateError as ex:
            LOG.error(
                "Could not get data for peer %s, error is %s",
                input_peer.to_dict(),
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

    for folder in result:
        lines.extend((f"Folder: {folder['title']}", "-" * (8 + len(folder["title"]))))
        # Group peers by type
        channels = [p for p in folder["peers"] if p["type"] == "channel"]
        groups = [p for p in folder["peers"] if p["type"] == "group"]
        users = [p for p in folder["peers"] if p["type"] == "user"]

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


def main() -> None:
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

    # Output format options (required)
    output_group = parser.add_mutually_exclusive_group(required=True)
    output_group.add_argument(
        "-j",
        "--json",
        nargs="?",
        const="tgf-list.json",
        metavar="FILE",
        help="Export to JSON format (default: tgf-list.json)",
    )
    output_group.add_argument(
        "-t",
        "--text",
        nargs="?",
        const="tgf-list.txt",
        metavar="FILE",
        help="Export to text format (default: tgf-list.txt)",
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    config = get_config()
    client = TelegramClient(
        "var/tg.session",
        config["tg"]["app_id"],
        config["tg"]["app_hash"],
    )
    result = []
    with client:
        dlg_filters = client(functions.messages.GetDialogFiltersRequest())
        for dlg_filter in dlg_filters.filters:
            if isinstance(dlg_filter, types.DialogFilterDefault):
                continue
            LOG.info("Processing folder %s", dlg_filter.title.text)
            result.append(export_dialog_filter(client, dlg_filter))

    # Determine output file and format
    if args.json:
        output_file = args.json
        content = render_result(result)
        LOG.info("Writing JSON output to %s", output_file)
        # Write to file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
        LOG.info("Export completed successfully")
    elif args.text:
        output_file = args.text
        content = render_text_result(result)
        LOG.info("Writing text output to %s", output_file)
        # Write to file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
        LOG.info("Export completed successfully")


if __name__ == "__main__":
    main()
