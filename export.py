#!/usr/bin/env python3
import json
import logging
from pprint import pprint  # pylint: disable=unused-import # noqa: F401
from typing import Any, cast

import yaml
from telethon import functions, types
from telethon.errors.rpcerrorlist import ChannelPrivateError
from telethon.sync import TelegramClient


def get_config() -> dict[str, Any]:
    with open("var/config.yml", encoding="utf-8") as inp:
        return cast(dict[str, Any], yaml.safe_load(inp))


LOG = logging.getLogger(__name__)


def get_entity_type_name(ent: types.TLObject) -> str:
    if isinstance(ent, types.User):
        return "user"
    if isinstance(ent, types.Channel | types.Chat):
        if ent.broadcast:
            return "channel"
        return "group"
    raise TypeError("Unknown entity type: {}".format(type(ent)))


def get_entity_name(ent: types.TLObject) -> None | str:
    if isinstance(ent, types.Channel | types.Chat):
        if ent.title is None:
            return None
        return cast(str, ent.title)
    if isinstance(ent, types.User):
        return ((ent.first_name or "") + " " + (ent.last_name or "")).strip()
    raise TypeError("Unknown entity type: {}".format(type(ent)))


def export_entity(ent: types.TLObject) -> dict[str, Any]:
    return {
        "type": get_entity_type_name(ent),
        "id": ent.id,
        "username": ent.username,
        "name": get_entity_name(ent),
    }


def export_dialog_filter(
    client: TelegramClient, dlg_filter: types.DialogFilter
) -> dict[str, Any]:
    result = {
        "id": dlg_filter.id,
        "title": dlg_filter.title,
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
        for dlg_filter in dlg_filters:
            if isinstance(dlg_filter, types.DialogFilterDefault):
                continue
            LOG.info("Processing folder %s", dlg_filter.title)
            result.append(export_dialog_filter(client, dlg_filter))
    print(render_result(result))


if __name__ == "__main__":
    main()
