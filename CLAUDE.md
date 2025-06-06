# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Discord Personal Folder Creator is a Python command-line tool that automates the creation of private Discord channels in bulk from a CSV file. The bot creates channels under a specified category with restricted permissions (hidden from @everyone).

**Key Features:**
- Auto-detects CSV format (simple channel names vs. channels with user invites)
- Supports bulk channel creation with optional user-specific permissions
- Updates existing channels by adding new users instead of skipping
- Includes member export functionality to get Discord user IDs
- Organized file structure with input/output directories

## Key Commands

```bash
# Set up virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the channel creator bot
python discord_channel_creator.py

# Export server members to CSV
python export_members.py
```

## Architecture

The project contains two main scripts:

### discord_channel_creator.py
- **Configuration Loading**: Checks for `config.json` first, falls back to interactive prompts
- **CSV Format Detection**: Automatically detects single-column (basic) or multi-column (with user invites) format
- **Bot Initialization**: Uses discord.py with specific intents (guilds, members)
- **Event-Driven Execution**: All channel creation happens in the `on_ready` event
- **User Resolution**: Supports Discord IDs, usernames, and legacy username#discriminator format
- **Existing Channel Handling**: Updates permissions for existing channels when users are specified
- **Auto-disconnect**: Bot closes connection after completing all operations

### export_members.py
- Exports all server members to CSV format
- Excludes bots by default (configurable)
- Outputs to timestamped files in the `output/` directory
- Includes user IDs, usernames, display names, roles, and join dates

## Configuration

The bot supports two configuration methods:

1. **File-based** (preferred): Create `config.json` from `config.example.json`:
   ```json
   {
     "bot_token": "YOUR_BOT_TOKEN_HERE",
     "guild_id": 123456789012345678,
     "category_name": "Private Channels",
     "csv_file": "input/sample.csv",
     "output_file": "discord_members.csv",
     "skip_bots": true
   }
   ```

2. **Interactive**: If no config.json exists, prompts for all values

## CSV Formats

The bot auto-detects two CSV formats:

### Simple Format (Channel Names Only)
```csv
channel-name-1
channel-name-2
channel-name-3
```

### Advanced Format (With User Invites)
```csv
channel-name-1,user_id1,username2
channel-name-2,123456789012345678,exampleuser
channel-name-3,johndoe,janedoe
```

**User Identifiers Support:**
- Discord User IDs (recommended): `123456789012345678`
- Usernames: `exampleuser`, `johndoe`
- Legacy format: `username#1234`

The bot:
- Strips whitespace from names
- Skips empty rows
- Discord automatically formats names (spaces → hyphens, lowercase)
- Resolves user identifiers and sets appropriate permissions
- For existing channels: adds specified users instead of skipping

## Discord Permissions

Required bot permissions:
- Manage Channels
- Manage Roles  
- Read Messages/View Channels

Created channels have these permission overwrites:
- @everyone: Cannot view
- Bot: Can view
- Invited users (when using advanced CSV format): Can view, read, and send messages

## File Organization

```
input/           # Place CSV files here
├── sample.csv   # Example channel list
└── .gitkeep

output/          # Generated files (gitignored except .gitkeep)
├── discord_members_YYYYMMDD_HHMMSS.csv
└── .gitkeep

config.json      # Bot configuration (create from config.example.json)
```

## Rate Limiting

The bot includes a 0.5-second delay between channel creations to avoid Discord rate limits.

## Development Notes

- All output files are gitignored to prevent accidental commits of user data
- The bot uses Server Members Intent to resolve usernames to user objects
- CSV files should be placed in the `input/` directory
- Export functionality saves timestamped files to avoid overwrites