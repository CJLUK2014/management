import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

# Get the bot token and log channel ID from environment variables
TOKEN = os.getenv('BOT_TOKEN')
LOG_CHANNEL_ID = os.getenv('LOG_CHANNEL_ID')

PREFIX = '!!'
bot = commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all())

team_members = {}
orders = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Creative Vivo Designs"))

@bot.command()
@commands.has_permissions(manage_guild=True)
async def register(ctx, member: discord.Member, *, role: str):
    user_id = member.id
    team_members[user_id] = role
    await ctx.send(f"Registered {member.mention} as a {role}!", delete_after=5)

    log_channel = bot.get_channel(int(LOG_CHANNEL_ID)) # Make sure LOG_CHANNEL_ID is treated as a number
    if log_channel:
        log_embed = discord.Embed(title="[ Command has been used ]", color=discord.Color.green())
        log_embed.add_field(name="- !register has been used!", value=f"- The administrator was {ctx.author.mention}", inline=False)
        log_embed.add_field(name="Details:", value=f"- Registered member: {member.mention}\n- Assigned role: {role}", inline=False)
        await log_channel.send(embed=log_embed)
    else:
        print(f"Error: Log channel not found with ID {LOG_CHANNEL_ID}")

@bot.command()
async def team(ctx):
    if not team_members:
        await ctx.send("No team members have been registered yet.")
        return
    team_list = "Here's the team:\n"
    for user_id, role in team_members.items():
        member = bot.get_user(user_id)
        if member:
            team_list += f"- {member.name}: {role}\n"
    await ctx.send(team_list)

@bot.command()
@commands.has_permissions(manage_guild=True)
async def addorder(ctx, id: str, *, details: str):
    if id in orders:
        await ctx.send(f"Order with ID {id} already exists!", delete_after=5)
        return
    order_info = {"status": "New"}
    details_parts = details.split(" Type: ", 1)
    if len(details_parts) == 2:
        order_info["type"] = details_parts[0]
        description_part = details_parts[1].split(" Description: ", 1)
        if len(description_part) == 2:
            order_info["description"] = description_part[1]
        else:
            order_info["description"] = details_parts[1]
    else:
        order_info["description"] = details

    orders[id] = order_info
    await ctx.send(f"Order {id} added with status: New", delete_after=5)

    log_channel = bot.get_channel(int(LOG_CHANNEL_ID)) # Make sure LOG_CHANNEL_ID is treated as a number
    if log_channel:
        log_embed = discord.Embed(title="[ Command has been Used ]", color=discord.Color.blue())
        log_embed.add_field(name="- !addorder Has been used.", value=f"- The person was {ctx.author.mention}", inline=False)
        log_embed.add_field(name="Details:", value=f"- Order ID: {id}\n- Type: {order_info.get('type', 'Not specified')}\n- Description: {order_info.get('description', 'Not specified')}", inline=False)
        await log_channel.send(embed=log_embed)
    else:
        print(f"Error: Log channel not found with ID {LOG_CHANNEL_ID}")

@bot.command()
@commands.has_permissions(manage_guild=True)
async def orderstatus(ctx, id: str, *, status: str):
    if id not in orders:
        await ctx.send(f"Order with ID {id} not found!", delete_after=5)
        return
    orders[id]["status"] = status
    await ctx.send(f"Status of order {id} updated to: {status}", delete_after=5)
    # Add logging for !orderstatus here if you want!

@bot.command()
@commands.has_permissions(manage_guild=True)
async def assignorder(ctx, id: str, member: discord.Member):
    if id not in orders:
        await ctx.send(f"Order with ID {id} not found!", delete_after=5)
        return
    orders[id]["assigned_to"] = member.id
    await ctx.send(f"Order {id} has been assigned to {member.mention}!", delete_after=5)

    log_channel = bot.get_channel(int(LOG_CHANNEL_ID)) # Make sure LOG_CHANNEL_ID is treated as a number
    if log_channel:
        log_embed = discord.Embed(title="[ Command has been Used ]", color=discord.Color.gold())
        log_embed.add_field(name="- !assignorder Has been used.", value=f"- The person was {ctx.author.mention}", inline=False)
        log_embed.add_field(name="Details:", value=f"- Order ID: {id}\n- Assigned to: {member.mention}", inline=False)
        await log_channel.send(embed=log_embed)
    else:
        print(f"Error: Log channel not found with ID {LOG_CHANNEL_ID}")

@bot.command()
async def checkorder(ctx, id: str):
    if id not in orders:
        await ctx.send(f"Order with ID {id} not found!", delete_after=5)
        return
    order = orders[id]
    details = f"Order ID: {id}\nStatus: {order.get('status', 'Unknown')}\n"
    if "type" in order:
        details += f"Type: {order['type']}\n"
    if "description" in order:
        details += f"Description: {order['description']}\n"
    if "assigned_to" in order:
        assigned_member = bot.get_user(order["assigned_to"])
        if assigned_member:
            details += f"Assigned to: {assigned_member.name}\n"
        else:
            details += "Assigned to: Unknown member\n"
    await ctx.send(details, delete_after=10)

@bot.command()
@commands.has_permissions(manage_guild=True)
async def announcement(ctx, *, message):
    green_arrow = "<a:greenarrow:1357796907006558208>"
    announcement_text = f"@everyone\n\n{green_arrow}{green_arrow} **Announcement**\n\n{green_arrow} {message}"
    await ctx.send(announcement_text, delete_after=5)
    await ctx.message.delete(delay=1)

@bot.command()
async def say(ctx, *, message):
    """Makes the bot say whatever you want and deletes the command."""
    await ctx.send(message)
    await ctx.message.delete(delay=1)

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
