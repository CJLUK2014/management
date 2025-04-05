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
async def announcement(ctx, channel_id: int, *, message):
    """Sends an announcement to a specific channel and deletes the command."""
    green_arrow = "<a:greenarrow:1357796907006558208>"
    announcement_text = f"@everyone\n\n{green_arrow}{green_arrow} **Announcement**\n\n{green_arrow} {message}"

    channel = bot.get_channel(channel_id)
    if channel:
        await channel.send(announcement_text)
        await ctx.message.delete(delay=2)
    else:
        await ctx.send(f"Error: Channel with ID {channel_id} not found.", delete_after=5)

    log_channel = bot.get_channel(int(LOG_CHANNEL_ID))
    if log_channel:
        log_embed = discord.Embed(title="[ Command has been Used ]", color=discord.Color.purple())
        log_embed.add_field(name="- !announcement Has been used.", value=f"- The person was {ctx.author.mention}", inline=False)
        log_embed.add_field(name="Details:", value=f"- Announced in channel ID: {channel_id}\n- Message: {message}", inline=False)
        await log_channel.send(embed=log_embed)
    else:
        print(f"Error: Log channel not found with ID {LOG_CHANNEL_ID}")

@bot.command()
async def say(ctx, *, message):
    """Makes the bot say whatever you want and deletes the command."""
    await ctx.send(message)
    await ctx.message.delete(delay=1)

@bot.command()
@commands.has_permissions(manage_guild=True)
async def unregister(ctx, member: discord.Member):
    """Unregisters a member from the team."""
    user_id = member.id
    if user_id in team_members:
        role = team_members.pop(user_id)
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
async def commands(ctx):
    """Shows a list of available commands and their required permissions."""
    help_embed = discord.Embed(title="Bot Commands", color=discord.Color.blurple())
    help_embed.add_field(name="!!team", value="Shows the list of registered team members.", inline=False)
    help_embed.add_field(name="!!checkorder <id>", value="Checks the details and status of a specific order.", inline=False)
    help_embed.add_field(name="!!say <message>", value="Makes the bot say the message and deletes your command.", inline=False)
    help_embed.add_field(name="!!register <member> <role>", value="Registers a member as part of the team. **Requires Manage Server permission.**", inline=False)
    help_embed.add_field(name="!!addorder <id> <details>", value="Adds a new order to the system. **Requires Manage Server permission.**", inline=False)
    help_embed.add_field(name="!!orderstatus <id> <status>", value="Updates the status of an existing order. **Requires Manage Server permission.**", inline=False)
    help_embed.add_field(name="!!assignorder <id> <member>", value="Assigns an order to a specific team member. **Requires Manage Server permission.**", inline=False)
    help_embed.add_field(name="!!announcement <channel_id> <message>", value="Sends an announcement to a specific channel. **Requires Manage Server permission.**", inline=False)
    help_embed.add_field(name="!!unregister <member>", value="Unregisters a member from the team. **Requires Manage Server permission.**", inline=False)
    help_embed.add_field(name="!!commands", value="Shows this list of commands.", inline=False)
    await ctx.send(embed=help_embed)

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

# Make sure the bot runs with the token from the environment
if TOKEN:
    bot.run(TOKEN)
else:
    print("Error: BOT_TOKEN environment variable not set!")
