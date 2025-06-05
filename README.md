# Discord Personal Folder Creator

A command-line tool to bulk create private Discord channels under a specified category from a CSV file.

## Features

- Creates multiple private text channels from a CSV list
- Organizes channels under a specified category
- Provides clear setup instructions for Discord Developer Portal
- Skips existing channels to avoid duplicates
- Sets channels as private (hidden from @everyone role)

## Prerequisites

- Python 3.8 or higher
- A Discord account with server management permissions

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
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

1. Run the script:
```bash
python discord_channel_creator.py
```

2. Follow the on-screen instructions to:
   - Create a Discord application and bot
   - Get your bot token
   - Add the bot to your server
   - Configure necessary permissions

3. When prompted, provide:
   - Bot token
   - Server (Guild) ID
   - Category name for the channels
   - Path to your CSV file

## CSV Format

Create a CSV file with channel names, one per line, and place it in the `input/` directory:

```csv
channel-name-1
channel-name-2
channel-name-3
```

See `input/sample.csv` for an example. Update your `config.json` to point to your CSV file:
```json
"csv_file": "input/your-channels.csv"
```

## How It Works

1. The bot connects to your Discord server
2. Creates or finds the specified category
3. Reads channel names from the CSV file
4. Creates private text channels with restricted permissions
5. Skips any channels that already exist

## Permissions

The bot requires:
- Manage Channels
- Manage Roles
- Read Messages/View Channels

Created channels are private by default (only visible to administrators and the bot).

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