# Telegram Folder Channels List Exporter

The program exports list of channels and groups for each Telegram folder. It does
not export messages.

What is chat folders: https://telegram.org/blog/folders

## Config file

Create "var/config.yml" file with a following content

```
tg:
  app_id: ...
  app_hash: ...
```

## Installation and usage

```bash
git clone https://github.com/AABur/tgfolder_export
cd tgfolder_export
# Install uv if not already installed: https://docs.astral.sh/uv/
make init
source .venv/bin/activate
# create config file, see above
./export.py > export.json
```
