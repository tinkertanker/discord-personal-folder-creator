# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Discord Personal Folder Creator is a Python command-line tool that automates the creation of private Discord channels in bulk from a CSV file. The bot creates channels under a specified category with restricted permissions (hidden from @everyone).

## Key Commands

```bash
# Set up virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the bot
python discord_channel_creator.py
```

## Architecture

The project uses a single-file architecture (`discord_channel_creator.py`) with the following flow:

1. **Configuration Loading**: Checks for `config.json` first, falls back to interactive prompts
2. **Bot Initialization**: Uses discord.py with specific intents (guilds, members)
3. **Event-Driven Execution**: All channel creation happens in the `on_ready` event
4. **Auto-disconnect**: Bot closes connection after completing all operations

## Configuration

The bot supports two configuration methods:

1. **File-based** (preferred): Create `config.json` from `config.example.json`:
   ```json
   {
     "bot_token": "YOUR_BOT_TOKEN_HERE",
     "guild_id": 123456789012345678,
     "category_name": "Private Channels",
     "csv_file": "channels.csv"
   }
   ```

2. **Interactive**: If no config.json exists, prompts for all values

## CSV Format

Channel names are read from a CSV file, one name per line. The bot:
- Strips whitespace from names
- Skips empty rows
- Discord automatically formats names (spaces → hyphens, lowercase)

## Discord Permissions

Required bot permissions:
- Manage Channels
- Manage Roles  
- Read Messages/View Channels

Created channels have these permission overwrites:
- @everyone: Cannot view
- Bot: Can view

## Rate Limiting

The bot includes a 0.5-second delay between channel creations to avoid Discord rate limits.