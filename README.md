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

Create a `.env` file in the project root (copy from `.env.sample`):

```bash
app_api_id=12345678
app_api_hash=your_api_hash_here
```

> 💡 **How to get API credentials**: Visit [my.telegram.org/apps](https://my.telegram.org/apps), log in, and create a new application.

### Usage

**Note**: One of `-j` or `-t` options is required.

```bash
# Export to JSON format (default filename: tgf-list.json)
./export.py -j

# Export to JSON with custom filename
./export.py -j my_folders.json

# Export to text format (default filename: tgf-list.txt)
./export.py -t

# Export to text with custom filename
./export.py -t my_folders.txt

# Show help
./export.py --help
```

## 📊 Output Formats

### JSON Format
When using `-j` or `--json`, the script generates a JSON structure like this:

```json
[
  {
    "id": 1,
    "title": "Work",
    "peers": [
      {
        "type": "channel",
        "id": 1234567890,
        "username": "example_channel",
        "name": "Example Channel"
      },
      {
        "type": "group",
        "id": 9876543210,
        "username": null,
        "name": "My Work Group"
      }
    ]
  }
]
```

### Text Format
When using `-t` or `--text`, the script generates a human-readable text file:

```
TELEGRAM FOLDERS EXPORT
=======================

Folder: Work
------------
Channels (1):
  • Example Channel (@example_channel) [ID: 1234567890]

Groups (1):
  • My Work Group [ID: 9876543210]

=======================
Total: 1 folders, 1 channels, 1 groups, 0 users
Generated: 2024-01-01 12:00:00 UTC
```

## 🛠️ Development

### Testing & Code Quality

```bash
# Run tests
make test          # Run pytest tests
make test-cov      # Run tests with coverage report

# Run all checks
make check         # Linting, type checking, and tests

# Individual tools
make ruff          # Linting and formatting
make mypy          # Type checking
```

### Available Commands

```bash
make init      # Initialize development environment
make check     # Run all linting, type checking, and tests
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
