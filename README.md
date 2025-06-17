# Telegram Folder Channels List Exporter

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> A modern fork of [lorien/tgfolder_export](https://github.com/lorien/tgfolder_export) with fixed runtime errors and migrated to modern Python tooling ([uv](https://docs.astral.sh/uv/)).

Export lists of channels and groups from your Telegram folders without downloading messages. Perfect for backing up your folder organization or analyzing your channel subscriptions.

## ✨ Features

- 🚀 **Fast & Modern**: Built with [uv](https://docs.astral.sh/uv/) for blazing-fast dependency management
- 📁 **Folder Export**: Export all channels and groups from your Telegram folders
- 🔒 **Privacy-First**: Only exports metadata (names, IDs, usernames) - no messages
- 📄 **JSON Output**: Clean, structured JSON format for easy processing
- 🛠️ **Developer-Friendly**: Full type hints, linting, and modern Python practices

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager
- Telegram API credentials ([get them here](https://my.telegram.org/apps))

### Installation

```bash
git clone https://github.com/AABur/tgfolder_export.git
cd tgfolder_export
make init
source .venv/bin/activate
```

### Configuration

Create a `var/config.yml` file with your Telegram API credentials:

```yaml
tg:
  app_id: 12345678        # Your Telegram app ID
  app_hash: "your_hash"   # Your Telegram app hash
```

> 💡 **How to get API credentials**: Visit [my.telegram.org/apps](https://my.telegram.org/apps), log in, and create a new application.

### Usage

```bash
# Export all folders to JSON
./export.py > export.json

# Or with custom output
./export.py > my_telegram_folders.json
```

## 📊 Output Format

The script generates a JSON structure like this:

```json
{
  "Work": {
    "channels": [
      {
        "type": "channel",
        "id": 1234567890,
        "username": "example_channel",
        "name": "Example Channel"
      }
    ],
    "groups": [
      {
        "type": "group",
        "id": 9876543210,
        "username": null,
        "name": "My Work Group"
      }
    ]
  }
}
```

## 🛠️ Development

### Code Quality

```bash
# Run all checks
make check

# Individual tools
make ruff      # Linting and formatting
make mypy      # Type checking
```

### Available Commands

```bash
make init      # Initialize development environment
make check     # Run all linting and type checks
make build     # Build the package
make clean     # Clean up generated files
```

## 📚 What are Telegram Folders?

Telegram folders help organize your chats into categories. Learn more: [Telegram Blog - Folders](https://telegram.org/blog/folders)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 🙏 Acknowledgments

- Original project by [lorien](https://github.com/lorien/tgfolder_export)
- Built with [Telethon](https://github.com/LonamiWebs/Telethon) library

## License

MIT
