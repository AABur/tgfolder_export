# Telegram Folder Channels List Exporter

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> A modern fork of [lorien/tgfolder_export](https://github.com/lorien/tgfolder_export) with fixed runtime errors and migrated to modern Python tooling ([uv](https://docs.astral.sh/uv/)).

Export lists of channels and groups from your Telegram folders without downloading messages. Perfect for backing up your folder organization or analyzing your channel subscriptions.

## ✨ Features

- 🚀 **Fast & Modern**: Built with [uv](https://docs.astral.sh/uv/) for blazing-fast dependency management
- 📦 **Zero-Setup**: Inline script metadata (PEP 723) allows direct execution with `uv run`
- 📁 **Folder Export**: Export all channels and groups from your Telegram folders
- 🔒 **Privacy-First**: Only exports metadata (names, IDs, usernames) - no messages
- 📄 **Multiple Formats**: JSON and human-readable text output formats
- 📊 **Progress Tracking**: Real-time progress bar for large exports
- 🔧 **Configurable**: Environment-based logging and configuration
- 🛡️ **Robust Error Handling**: Graceful handling of private channels and API errors
- 🛠️ **Developer-Friendly**: Full type hints, linting, and modern Python practices

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager
- Telegram API credentials ([get them here](https://my.telegram.org/apps))

### Installation

#### Option 1: Traditional Setup
```bash
git clone https://github.com/AABur/tgfolder_export.git
cd tgfolder_export
make init
source .venv/bin/activate
```

#### Option 2: Direct Script Execution (Recommended)
The script includes inline metadata for uv, allowing direct execution without setup:
```bash
git clone https://github.com/AABur/tgfolder_export.git
cd tgfolder_export
# uv will automatically install Python 3.11+ and dependencies
uv run export.py -j
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
# Using uv (recommended - handles dependencies automatically)
uv run export.py -j                    # JSON format (default: tgf-list.json)
uv run export.py -j my_folders.json    # JSON with custom filename
uv run export.py -t                    # Text format (default: tgf-list.txt) 
uv run export.py -t my_folders.txt     # Text with custom filename
uv run export.py --help               # Show help

# Traditional execution (requires activated virtual environment)
./export.py -j
./export.py -t my_folders.txt
./export.py --help
```

### Session Management

On first run, you'll be prompted to authenticate with Telegram:
- Enter your phone number
- Enter the verification code sent to your Telegram app
- If you have 2FA enabled, enter your password

**Session Storage**: Authentication is saved in `.tempts/tg.session` (hidden directory, auto-created)

**Session Expiry**: Sessions expire after 7 days. When expired, you'll be prompted to re-authenticate.

**Clear Session**: Force clear saved session to re-authenticate:
```bash
uv run export.py --clear-session
./export.py --clear-session
```

### Environment Variables

You can customize the behavior using environment variables:

```bash
# Set logging level (DEBUG, INFO, WARNING, ERROR)
export LOG_LEVEL=DEBUG
uv run export.py -j
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
make lint          # Linting and formatting
make mypy          # Type checking
```

### Available Commands

```bash
make init      # Initialize development environment
make check     # Run all linting, type checking, and tests
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
