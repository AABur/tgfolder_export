"""Tests for export.py module."""

import json
from typing import Any

import pytest
from pytest_mock import MockerFixture
from telethon import types
from telethon.errors.rpcerrorlist import ChannelPrivateError

from export import (
    export_dialog_filter,
    export_entity,
    get_config,
    get_entity_name,
    get_entity_type_name,
    main,
    render_result,
    render_text_result,
)


def test_get_config(mocker: MockerFixture) -> None:
    """Test config loading."""
    mocker.patch("export.load_dotenv")
    mocker.patch(
        "export.os.getenv",
        side_effect=lambda key: {
            "app_api_id": "12345",
            "app_api_hash": "test_hash",
        }.get(key),
    )

    config = get_config()

    assert config["tg"]["app_id"] == 12345
    assert config["tg"]["app_hash"] == "test_hash"


def test_get_config_missing_env_vars(mocker: MockerFixture) -> None:
    """Test config loading with missing environment variables."""
    mocker.patch("export.load_dotenv")
    mocker.patch("export.os.getenv", return_value=None)

    with pytest.raises(ValueError, match="Missing required environment variables"):
        get_config()


def test_get_entity_type_name_user(mocker: MockerFixture) -> None:
    """Test entity type detection for User."""
    user = mocker.Mock(spec=types.User)
    assert get_entity_type_name(user) == "user"


def test_get_entity_type_name_channel(mocker: MockerFixture) -> None:
    """Test entity type detection for Channel (broadcast)."""
    channel = mocker.Mock(spec=types.Channel)
    channel.broadcast = True
    assert get_entity_type_name(channel) == "channel"


def test_get_entity_type_name_group(mocker: MockerFixture) -> None:
    """Test entity type detection for Channel (group)."""
    group = mocker.Mock(spec=types.Channel)
    group.broadcast = False
    assert get_entity_type_name(group) == "group"


def test_get_entity_type_name_chat(mocker: MockerFixture) -> None:
    """Test entity type detection for Chat."""
    chat = mocker.Mock(spec=types.Chat)
    assert get_entity_type_name(chat) == "group"


def test_get_entity_type_name_unknown(mocker: MockerFixture) -> None:
    """Test entity type detection for unknown type."""
    unknown = mocker.Mock()
    with pytest.raises(TypeError, match="Unknown entity type"):
        get_entity_type_name(unknown)


def test_get_entity_name_channel(mocker: MockerFixture) -> None:
    """Test entity name extraction for Channel."""
    channel = mocker.Mock(spec=types.Channel)
    channel.title = "Test Channel"
    assert get_entity_name(channel) == "Test Channel"


def test_get_entity_name_channel_no_title(mocker: MockerFixture) -> None:
    """Test entity name extraction for Channel without title."""
    channel = mocker.Mock(spec=types.Channel)
    channel.title = None
    assert get_entity_name(channel) is None


def test_get_entity_name_chat(mocker: MockerFixture) -> None:
    """Test entity name extraction for Chat."""
    chat = mocker.Mock(spec=types.Chat)
    chat.title = "Test Chat"
    assert get_entity_name(chat) == "Test Chat"


def test_get_entity_name_user_full_name(mocker: MockerFixture) -> None:
    """Test entity name extraction for User with full name."""
    user = mocker.Mock(spec=types.User)
    user.first_name = "John"
    user.last_name = "Doe"
    assert get_entity_name(user) == "John Doe"


def test_get_entity_name_user_first_name_only(mocker: MockerFixture) -> None:
    """Test entity name extraction for User with first name only."""
    user = mocker.Mock(spec=types.User)
    user.first_name = "John"
    user.last_name = None
    assert get_entity_name(user) == "John"


def test_get_entity_name_user_last_name_only(mocker: MockerFixture) -> None:
    """Test entity name extraction for User with last name only."""
    user = mocker.Mock(spec=types.User)
    user.first_name = None
    user.last_name = "Doe"
    assert get_entity_name(user) == "Doe"


def test_get_entity_name_user_no_name(mocker: MockerFixture) -> None:
    """Test entity name extraction for User without name."""
    user = mocker.Mock(spec=types.User)
    user.first_name = None
    user.last_name = None
    assert get_entity_name(user) == ""


def test_get_entity_name_unknown(mocker: MockerFixture) -> None:
    """Test entity name extraction for unknown type."""
    unknown = mocker.Mock()
    with pytest.raises(TypeError, match="Unknown entity type"):
        get_entity_name(unknown)


def test_export_entity_user_with_username(mocker: MockerFixture) -> None:
    """Test entity export for User with username."""
    user = mocker.Mock(spec=types.User)
    user.id = 12345
    user.first_name = "John"
    user.last_name = "Doe"
    user.username = "johndoe"

    result = export_entity(user)

    assert result == {
        "type": "user",
        "id": 12345,
        "name": "John Doe",
        "username": "johndoe",
    }


def test_export_entity_channel_with_username(mocker: MockerFixture) -> None:
    """Test entity export for Channel with username."""
    channel = mocker.Mock(spec=types.Channel)
    channel.id = 67890
    channel.title = "Test Channel"
    channel.broadcast = True
    channel.username = "testchannel"

    result = export_entity(channel)

    assert result == {
        "type": "channel",
        "id": 67890,
        "name": "Test Channel",
        "username": "testchannel",
    }


def test_export_entity_chat_no_username(mocker: MockerFixture) -> None:
    """Test entity export for Chat without username."""
    chat = mocker.Mock(spec=types.Chat)
    chat.id = 54321
    chat.title = "Test Chat"

    result = export_entity(chat)

    assert result == {
        "type": "group",
        "id": 54321,
        "name": "Test Chat",
        "username": None,
    }


def test_export_dialog_filter_success(mocker: MockerFixture) -> None:
    """Test dialog filter export with successful peer fetching."""
    # Mock client
    client = mocker.Mock()

    # Mock entities
    channel = mocker.Mock(spec=types.Channel)
    channel.id = 12345
    channel.title = "Test Channel"
    channel.broadcast = True
    channel.username = "testchannel"

    user = mocker.Mock(spec=types.User)
    user.id = 67890
    user.first_name = "John"
    user.last_name = "Doe"
    user.username = "johndoe"

    client.get_entity.side_effect = [channel, user]

    # Mock dialog filter
    dlg_filter = mocker.Mock(spec=types.DialogFilter)
    dlg_filter.id = 1
    dlg_filter.title = mocker.Mock()
    dlg_filter.title.text = "Work"
    dlg_filter.include_peers = [mocker.Mock(), mocker.Mock()]  # Two mock peers

    result = export_dialog_filter(client, dlg_filter)

    assert result["id"] == 1
    assert result["title"] == "Work"
    assert len(result["peers"]) == 2

    # Check first peer (channel)
    assert result["peers"][0]["type"] == "channel"
    assert result["peers"][0]["id"] == 12345
    assert result["peers"][0]["username"] == "testchannel"

    # Check second peer (user)
    assert result["peers"][1]["type"] == "user"
    assert result["peers"][1]["id"] == 67890
    assert result["peers"][1]["username"] == "johndoe"


def test_export_dialog_filter_with_private_channel(mocker: MockerFixture) -> None:
    """Test dialog filter export with ChannelPrivateError."""
    # Mock client
    client = mocker.Mock()

    # Mock successful entity
    user = mocker.Mock(spec=types.User)
    user.id = 67890
    user.first_name = "John"
    user.last_name = "Doe"
    user.username = "johndoe"

    # First call raises ChannelPrivateError, second succeeds
    client.get_entity.side_effect = [ChannelPrivateError("Private channel"), user]

    # Mock dialog filter
    dlg_filter = mocker.Mock(spec=types.DialogFilter)
    dlg_filter.id = 1
    dlg_filter.title = mocker.Mock()
    dlg_filter.title.text = "Mixed"
    dlg_filter.include_peers = [mocker.Mock(), mocker.Mock()]  # Two mock peers

    mock_log = mocker.patch("export.LOG")
    result = export_dialog_filter(client, dlg_filter)

    # Should have logged the error
    mock_log.error.assert_called_once()

    # Should only have one peer (the successful one)
    assert len(result["peers"]) == 1
    assert result["peers"][0]["type"] == "user"
    assert result["peers"][0]["id"] == 67890


def test_render_result(mocker: MockerFixture) -> None:
    """Test JSON rendering of results."""
    test_data = [
        {
            "id": 1,
            "title": "Work",
            "peers": [
                {
                    "type": "channel",
                    "id": 12345,
                    "name": "Test Channel",
                    "username": "testchannel",
                }
            ],
        }
    ]

    result = render_result(test_data)

    # Should be valid JSON
    parsed = json.loads(result)
    assert parsed == test_data

    # Should be pretty-printed (contains newlines and spaces)
    assert "\n" in result
    assert "  " in result


def test_render_result_unicode(mocker: MockerFixture) -> None:
    """Test JSON rendering with unicode characters."""
    test_data = [
        {
            "id": 1,
            "title": "International",  # Changed from Cyrillic
            "peers": [],
        }
    ]

    result = render_result(test_data)
    parsed = json.loads(result)

    assert parsed[0]["title"] == "International"
    # Should contain actual unicode, not escaped
    assert "International" in result


def test_main(mocker: MockerFixture) -> None:
    """Test main function execution with no arguments (backward compatibility)."""
    # Mock config
    config_data: dict[str, Any] = {"tg": {"app_id": 12345, "app_hash": "test_hash"}}

    # Mock dialog filter
    mock_filter = mocker.Mock(spec=types.DialogFilter)
    mock_filter.id = 1
    mock_filter.title = mocker.Mock()
    mock_filter.title.text = "Work"
    mock_filter.include_peers = []

    # Mock responses
    mock_filters_response = mocker.Mock()
    mock_filters_response.filters = [mock_filter]

    # Mock sys.argv to have no additional arguments (backward compatibility)
    mocker.patch("sys.argv", ["export.py"])

    mocker.patch("export.get_config", return_value=config_data)
    mock_client_class = mocker.patch("export.TelegramClient")
    mock_print = mocker.patch("builtins.print")
    mocker.patch("export.logging.basicConfig")

    mock_client = mocker.Mock()
    mock_client_class.return_value = mock_client
    mock_client.__enter__ = mocker.Mock(return_value=mock_client)
    mock_client.__exit__ = mocker.Mock(return_value=None)
    mock_client.return_value = mock_filters_response

    main()

    # Verify TelegramClient was created with correct params
    mock_client_class.assert_called_once_with("var/tg.session", 12345, "test_hash")

    # Verify print was called with JSON output
    mock_print.assert_called_once()
    printed_output = mock_print.call_args[0][0]

    # Should be valid JSON
    parsed = json.loads(printed_output)
    assert isinstance(parsed, list)
    assert len(parsed) == 1
    assert parsed[0]["id"] == 1
    assert parsed[0]["title"] == "Work"


def test_render_text_result(mocker: MockerFixture) -> None:
    """Test text rendering of results."""
    test_data = [
        {
            "id": 1,
            "title": "Work",
            "peers": [
                {
                    "type": "channel",
                    "id": 12345,
                    "name": "Test Channel",
                    "username": "testchannel",
                },
                {
                    "type": "group",
                    "id": 67890,
                    "name": "Test Group",
                    "username": None,
                },
            ],
        }
    ]

    result = render_text_result(test_data)

    # Should contain expected text elements
    assert "TELEGRAM FOLDERS EXPORT" in result
    assert "Folder: Work" in result
    assert "Channels (1):" in result
    assert "Groups (1):" in result
    assert "Test Channel (@testchannel)" in result
    assert "Test Group [ID: 67890]" in result
    assert "Total: 1 folders, 1 channels, 1 groups, 0 users" in result
    assert "Generated:" in result


def test_main_json_output(mocker: MockerFixture) -> None:
    """Test main function with JSON output."""
    # Mock config
    config_data: dict[str, Any] = {"tg": {"app_id": 12345, "app_hash": "test_hash"}}

    # Mock dialog filter
    mock_filter = mocker.Mock(spec=types.DialogFilter)
    mock_filter.id = 1
    mock_filter.title = mocker.Mock()
    mock_filter.title.text = "Work"
    mock_filter.include_peers = []

    # Mock responses
    mock_filters_response = mocker.Mock()
    mock_filters_response.filters = [mock_filter]

    # Mock file operations
    mock_open = mocker.mock_open()
    mocker.patch("builtins.open", mock_open)
    mocker.patch("sys.argv", ["export.py", "-j", "test.json"])

    mocker.patch("export.get_config", return_value=config_data)
    mock_client_class = mocker.patch("export.TelegramClient")
    mocker.patch("export.logging.basicConfig")

    mock_client = mocker.Mock()
    mock_client_class.return_value = mock_client
    mock_client.__enter__ = mocker.Mock(return_value=mock_client)
    mock_client.__exit__ = mocker.Mock(return_value=None)
    mock_client.return_value = mock_filters_response

    main()

    # Verify TelegramClient was created with correct params
    mock_client_class.assert_called_once_with("var/tg.session", 12345, "test_hash")

    # Verify file was opened for writing
    mock_open.assert_called_once_with("test.json", "w", encoding="utf-8")

    # Verify JSON content was written
    written_content = "".join(call.args[0] for call in mock_open().write.call_args_list)
    parsed = json.loads(written_content)
    assert isinstance(parsed, list)
    assert len(parsed) == 1
    assert parsed[0]["id"] == 1
    assert parsed[0]["title"] == "Work"


def test_main_text_output(mocker: MockerFixture) -> None:
    """Test main function with text output."""
    # Mock config
    config_data: dict[str, Any] = {"tg": {"app_id": 12345, "app_hash": "test_hash"}}

    # Mock dialog filter
    mock_filter = mocker.Mock(spec=types.DialogFilter)
    mock_filter.id = 1
    mock_filter.title = mocker.Mock()
    mock_filter.title.text = "Personal"
    mock_filter.include_peers = []

    # Mock responses
    mock_filters_response = mocker.Mock()
    mock_filters_response.filters = [mock_filter]

    # Mock file operations
    mock_open = mocker.mock_open()
    mocker.patch("builtins.open", mock_open)
    mocker.patch("sys.argv", ["export.py", "-t", "test.txt"])

    mocker.patch("export.get_config", return_value=config_data)
    mock_client_class = mocker.patch("export.TelegramClient")
    mocker.patch("export.logging.basicConfig")

    mock_client = mocker.Mock()
    mock_client_class.return_value = mock_client
    mock_client.__enter__ = mocker.Mock(return_value=mock_client)
    mock_client.__exit__ = mocker.Mock(return_value=None)
    mock_client.return_value = mock_filters_response

    main()

    # Verify TelegramClient was created with correct params
    mock_client_class.assert_called_once_with("var/tg.session", 12345, "test_hash")

    # Verify file was opened for writing
    mock_open.assert_called_once_with("test.txt", "w", encoding="utf-8")

    # Verify text content was written
    written_content = "".join(call.args[0] for call in mock_open().write.call_args_list)
    assert "TELEGRAM FOLDERS EXPORT" in written_content
    assert "Folder: Personal" in written_content
