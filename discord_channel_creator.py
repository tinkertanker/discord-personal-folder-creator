#!/usr/bin/env python3
import discord
from discord.ext import commands
import csv
import asyncio
import os
import sys
import json

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

def print_setup_instructions():
    print("\n=== Discord Bot Setup Instructions ===\n")
    print("1. Go to https://discord.com/developers/applications")
    print("2. Click 'New Application' and give it a name")
    print("3. Go to the 'Bot' section in the left sidebar")
    print("4. Click 'Add Bot' if you haven't already")
    print("5. Under 'Token', click 'Copy' to copy your bot token")
    print("6. Under 'Privileged Gateway Intents', enable:")
    print("   - SERVER MEMBERS INTENT")
    print("   - MESSAGE CONTENT INTENT (if needed)")
    print("\n7. Go to 'OAuth2' > 'URL Generator' in the left sidebar")
    print("8. Under 'Scopes', select 'bot'")
    print("9. Under 'Bot Permissions', select:")
    print("   - Manage Channels")
    print("   - Manage Roles")
    print("   - Read Messages/View Channels")
    print("10. Copy the generated URL and open it in your browser")
    print("11. Select your server and authorize the bot")
    print("\n=== Configuration ===\n")

def get_user_input():
    token = input("Enter your bot token: ").strip()
    guild_id = input("Enter your server (guild) ID: ").strip()
    category_name = input("Enter the category name where channels will be created: ").strip()
    csv_file = input("Enter the path to your CSV file: ").strip()
    
    return token, int(guild_id), category_name, csv_file

def read_channels_data(csv_file):
    """
    Read CSV file and automatically detect format:
    - Single column: channel_name (creates private channels with no specific invites)
    - Multiple columns: channel_name,user1,user2,... (creates channels and invites users)
    
    User identifiers can be Discord IDs, usernames, or username#discriminator
    """
    channels_data = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row_num, row in enumerate(reader, 1):
                if not row or not row[0].strip():  # Skip empty rows
                    continue
                
                channel_name = row[0].strip()
                # Get user identifiers from remaining columns
                user_identifiers = [user.strip() for user in row[1:] if user.strip()]
                
                channels_data.append({
                    'name': channel_name,
                    'users': user_identifiers,
                    'row': row_num
                })
                
    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)
    
    return channels_data

async def resolve_user(guild, identifier):
    """
    Resolve a user identifier to a Discord Member object.
    Supports: user ID, username, username#discriminator
    """
    # Try as user ID first
    if identifier.isdigit():
        member = guild.get_member(int(identifier))
        if member:
            return member
    
    # Try as username (with or without discriminator)
    if '#' in identifier:
        # Legacy username#discriminator format
        username, discriminator = identifier.rsplit('#', 1)
        member = discord.utils.get(guild.members, name=username, discriminator=discriminator)
    else:
        # Modern username format or display name
        member = discord.utils.get(guild.members, name=identifier)
        if not member:
            # Also try display name
            member = discord.utils.get(guild.members, display_name=identifier)
    
    return member

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
    
    # Find or create category
    category = discord.utils.get(guild.categories, name=config['category_name'])
    
    if not category:
        print(f"Creating new category: {config['category_name']}")
        try:
            category = await guild.create_category(config['category_name'])
        except discord.Forbidden:
            print("Error: Bot doesn't have permission to create categories")
            await bot.close()
            return
        except Exception as e:
            print(f"Error creating category: {e}")
            await bot.close()
            return
    else:
        print(f"Found existing category: {config['category_name']}")
    
    # Read channels and user data
    channels_data = read_channels_data(config['csv_file'])
    print(f"\nProcessing {len(channels_data)} channels...")
    
    # Detect CSV format
    has_invites = any(channel_info['users'] for channel_info in channels_data)
    if has_invites:
        print("Detected CSV with user invites - creating channels with specific user access")
    else:
        print("Detected simple CSV format - creating private channels")
    
    created = 0
    skipped = 0
    warnings = []
    
    for channel_info in channels_data:
        name = channel_info['name']
        user_identifiers = channel_info['users']
        row_num = channel_info['row']
        
        # Check if channel already exists in this category
        existing_channel = discord.utils.get(category.channels, name=name)
        
        if existing_channel:
            print(f"  Skipping '{name}' - already exists")
            skipped += 1
            continue
        
        try:
            # Start with base permissions (hidden from everyone)
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True)
            }
            
            # Add user permissions if specified
            resolved_users = []
            if user_identifiers:
                for identifier in user_identifiers:
                    member = await resolve_user(guild, identifier)
                    if member:
                        overwrites[member] = discord.PermissionOverwrite(
                            read_messages=True,
                            send_messages=True,
                            view_channel=True
                        )
                        resolved_users.append(f"{member.name} ({member.id})")
                    else:
                        warnings.append(f"Row {row_num}: Could not find user '{identifier}' for channel '{name}'")
            
            # Create the channel
            channel = await category.create_text_channel(
                name=name,
                overwrites=overwrites
            )
            
            if resolved_users:
                print(f"  Created private channel: {channel.name} - Invited: {', '.join(resolved_users)}")
            else:
                print(f"  Created private channel: {channel.name}")
            
            created += 1
            
            # Small delay to avoid rate limits
            await asyncio.sleep(0.5)
            
        except discord.Forbidden:
            print(f"  Error: No permission to create channel '{name}'")
        except discord.HTTPException as e:
            print(f"  Error creating channel '{name}': {e}")
        except Exception as e:
            print(f"  Unexpected error creating channel '{name}': {e}")
    
    print(f"\nComplete! Created {created} channels, skipped {skipped} existing channels.")
    
    # Print warnings if any
    if warnings:
        print(f"\n⚠️  Warnings ({len(warnings)}):")
        for warning in warnings:
            print(f"  - {warning}")
    
    # Disconnect bot after completion
    await bot.close()

def load_config():
    # Check for config.json first
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            return json.load(f)
    return None

def main():
    # Try to load config from file first
    file_config = load_config()
    
    if file_config:
        print("Using configuration from config.json")
        token = file_config['bot_token']
        guild_id = file_config['guild_id']
        category_name = file_config['category_name']
        csv_file = file_config['csv_file']
    else:
        print_setup_instructions()
        # Get user input
        token, guild_id, category_name, csv_file = get_user_input()
    
    # Store configuration globally
    global config
    config = {
        'guild_id': guild_id,
        'category_name': category_name,
        'csv_file': csv_file
    }
    
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