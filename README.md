# Discord Personal Folder Creator

A command-line tool to bulk create private Discord channels under a specified category from a CSV file.

## Features

- Creates multiple private text channels from a CSV list
- Updates existing channels by adding new users when specified in CSV
- Organizes channels under a specified category
- Provides clear setup instructions for Discord Developer Portal
- Handles existing channels intelligently (updates permissions instead of skipping)
- Sets channels as private (hidden from @everyone role)

## Prerequisites

- Python 3.8 or higher
- A Discord account with server management permissions

## Installation

1. Clone this repository:
```bash
git clone https://github.com/tinkertanker/discord-personal-folder-creator.git
cd discord-personal-folder-creator
```

2. Set up Python virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Setup

1. Copy the example config file:
```bash
cp config.example.json config.json
```

2. Edit `config.json` with your Discord bot details:
```json
{
  "bot_token": "YOUR_BOT_TOKEN_HERE",
  "guild_id": 123456789012345678,
  "category_name": "Private Channels",
  "csv_file": "input/sample.csv"
}
```

3. Follow the on-screen instructions when you first run the script to:
   - Create a Discord application and bot
   - Get your bot token
   - Add the bot to your server
   - Configure necessary permissions

4. Run the script:
```bash
python discord_channel_creator.py
```

## CSV Formats

The script automatically detects your CSV format:

### Simple Format (Channel Names Only)
Create a CSV file with channel names, one per line:

```csv
channel-name-1
channel-name-2
channel-name-3
```

### Advanced Format (With User Invites)
Include user identifiers to automatically invite specific users:

```csv
channel-name-1,user_id1,username2
channel-name-2,123456789012345678,exampleuser
channel-name-3,johndoe,janedoe
```

**User identifiers can be:**
- **Discord User ID** (recommended): `123456789012345678`
- **Username**: `exampleuser` or `johndoe`
- **Legacy format**: `username#1234`

See `input/sample.csv` for an example. Update your `config.json` to point to your CSV file:
```json
"csv_file": "input/your-channels.csv"
```

## How It Works

1. The bot connects to your Discord server
2. Creates or finds the specified category
3. Reads channel names and optional user lists from the CSV file
4. For each channel:
   - If it doesn't exist: Creates a private text channel with restricted permissions
   - If it exists and has users specified: Adds those users to the existing channel
   - If it exists with no users specified: Skips it
5. Reports the number of channels created, updated, and skipped

## Permissions

The bot requires:
- Manage Channels
- Manage Roles
- Read Messages/View Channels

Created channels are private by default (only visible to administrators and the bot). When using the advanced CSV format with user invites, only the specified users will have access to each channel.

## Exporting Discord Members

To export a list of server members to CSV:

```bash
python export_members.py
```

This will:
- Connect to your Discord server
- Export all members (excluding bots by default) to a timestamped CSV file
- Save the file to the `output/` directory
- Include user IDs, usernames, display names, nicknames, join dates, roles, and status

## File Organization

### Input Directory
- Place your channel list CSV files in the `input/` directory
- Example: `input/sample.csv`
- Update `config.json` to point to your CSV file

### Output Directory
- All generated files are saved to the `output/` directory
- Member export CSV files: `output/discord_members_YYYYMMDD_HHMMSS.csv`
- The `output/` directory is gitignored to prevent accidental commits of user data

## Notes

- Channel names are automatically formatted (spaces become hyphens, lowercase)
- The bot disconnects automatically after creating all channels
- A small delay is added between channel creations to avoid rate limits
- Exported member data is saved with UTF-8 encoding to handle special characters