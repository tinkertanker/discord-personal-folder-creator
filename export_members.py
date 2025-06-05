#!/usr/bin/env python3
import discord
from discord.ext import commands
import csv
import os
import sys
import json
from datetime import datetime

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

def load_config():
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            return json.load(f)
    return None

@bot.event
async def on_ready():
    print(f'\nBot connected as {bot.user}')
    
    # Get configuration from globals
    guild = bot.get_guild(config['guild_id'])
    if not guild:
        print(f"Error: Could not find guild with ID {config['guild_id']}")
        await bot.close()
        return
    
    print(f"Connected to server: {guild.name}")
    print(f"Total members: {guild.member_count}")
    
    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)
    
    # Export filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = config.get('output_file', f'discord_members_{timestamp}.csv')
    output_file = os.path.join('output', filename)
    
    # Collect member data
    members_data = []
    
    print("\nExporting member data...")
    for member in guild.members:
        # Skip bots if configured
        if config.get('skip_bots', True) and member.bot:
            continue
            
        member_info = {
            'id': member.id,
            'username': member.name,
            'display_name': member.display_name,
            'discriminator': member.discriminator,
            'joined_at': member.joined_at.strftime("%Y-%m-%d %H:%M:%S") if member.joined_at else 'Unknown',
            'created_at': member.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            'is_bot': member.bot,
            'top_role': member.top_role.name if member.top_role else 'None',
            'status': str(member.status),
            'nickname': member.nick if member.nick else ''
        }
        
        members_data.append(member_info)
    
    # Write to CSV
    if members_data:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'username', 'display_name', 'discriminator', 'nickname', 
                         'joined_at', 'created_at', 'is_bot', 'top_role', 'status']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for member in members_data:
                writer.writerow(member)
        
        print(f"\nExported {len(members_data)} members to {output_file}")
    else:
        print("\nNo members to export.")
    
    # Disconnect bot after completion
    await bot.close()

def main():
    # Load config
    file_config = load_config()
    
    if not file_config:
        print("Error: No config.json found. Please create one from config.example.json")
        sys.exit(1)
    
    print("Using configuration from config.json")
    token = file_config['bot_token']
    
    # Store configuration globally
    global config
    config = file_config
    
    # Run the bot
    try:
        bot.run(token)
    except discord.LoginFailure:
        print("\nError: Invalid bot token. Please check your token and try again.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError running bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()