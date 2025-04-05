import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import json # We need this to work with JSON files

load_dotenv()

# Get the bot token and log channel ID from environment variables
TOKEN = os.getenv('BOT_TOKEN')
LOG_CHANNEL_ID = os.getenv('LOG_CHANNEL_ID')

PREFIX = '!!'
bot = commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all())

TEAM_FILE = 'team_members.json' # Name of the file to save team data

team_members = {}
orders = {}

# --- Functions to load and save team data ---
def load_team_data():
    try:
        with open(TEAM_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_team_data():
    with open(TEAM_FILE, 'w') as f:
        json.dump(team_members, f, indent=4) # indent makes the file easier to read

@bot.event
async def on_ready():
    global team_members # We need to tell Python we're using the global team_members variable
    team_members = load_team_data() # Load the team data when the bot starts
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Creative Vivo Designs"))

@bot.command()
@commands.has_permissions(manage_guild=True)
async def register(ctx, member: discord.Member, *, role: str):
    global team_members
    user_id = member.id
    team_members[user_id] = role
    save_team_data() # Save the updated team data
    await ctx.send(f"Registered {member.mention} as a {role}!", delete_after=5)

    log_channel = bot.get_channel(int(LOG_CHANNEL_ID))
    if log_channel:
        log_embed = discord.Embed(title="[ Command has been used ]", color=discord.Color.green())
        log_embed.add_field(name="- !register has been used!", value=f"- The administrator was {ctx.author.mention}", inline=False)
        log_embed.add_field(name="Details:", value=f"- Registered member: {member.mention}\n- Assigned role: {role}", inline=False)
        await log_channel.send(embed=log_embed)
    else:
        print(f"Error: Log channel not found with ID {LOG_CHANNEL_ID}")

@bot.command()
@commands.has_permissions(manage_guild=True)
async def unregister(ctx, member: discord.Member):
    global team_members
    user_id = member.id
    if user_id in team_members:
        role = team_members.pop(user_id)
        save_team_data() # Save the updated team data
        await ctx.send(f"Unregistered {member.mention} who was a {role}.", delete_after=5)

        log_channel = bot.get_channel(int(LOG_CHANNEL_ID))
        if log_channel:
            log_embed = discord.Embed(title="[ Command has been Used ]", color=discord.Color.orange())
            log_embed.add_field(name="- !unregister has been used!", value=f"- The administrator was {ctx.author.mention}", inline=False)
            log_embed.add_field(name="Details:", value=f"- Unregistered member: {member.mention}\n- Previous role: {role}", inline=False)
            await log_channel.send(embed=log_embed)
        else:
            print(f"Error: Log channel not found with ID {LOG_CHANNEL_ID}")
    else:
        await ctx.send(f"{member.mention} is not currently registered.", delete_after=5)

@bot.command()
async def team(ctx):
    global team_members
    if not team_members:
        await ctx.send("No team members have been registered yet.")
        return
    team_list = "Here's the team:\n"
    for user_id, role in team_members.items():
        member = bot.get_user(user_id)
        if member:
            team_list += f"- {member.name}: {role}\n"
    await ctx.send(team_list)

# ... (rest of your code for addorder, orderstatus, assignorder, checkorder, announcement, say, commands) ...

# Load environment variables
load_dotenv()

# Get the bot token and log channel ID from environment variables
TOKEN = os.getenv('BOT_TOKEN')
LOG_CHANNEL_ID = os.getenv('LOG_CHANNEL_ID')

# Make sure the bot runs with the token from the environment
if TOKEN:
    bot.run(TOKEN)
else:
    print("Error: BOT_TOKEN environment variable not set!")
