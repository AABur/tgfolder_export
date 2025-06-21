#!/usr/bin/env python3
import argparse
import json
import logging
import os
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
        return None if ent.title is None else cast(str, ent.title)
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
    return json.dumps(result, indent=2, ensure_ascii=False)


def main() -> None:
    try:
        __version__ = version("tgfolder_export")
    except Exception:
        __version__ = "unknown"

    parser = argparse.ArgumentParser(
        description="Export Telegram folder contents as JSON"
    )
    parser.add_argument(
        "--version", action="version", version=f"tgfolder_export {__version__}"
    )
    parser.parse_args()

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
    print(render_result(result))


if __name__ == "__main__":
    main()
