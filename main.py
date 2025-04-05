import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import json
import datetime

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
LOG_CHANNEL_ID = os.getenv('LOG_CHANNEL_ID')

PREFIX = '!!'
bot = commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all())

team_members = {}
orders = {}
start_time = datetime.datetime.now() # We'll store the time the bot starts

def load_team_data():
    try:
        with open('staff.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        print("Error decoding staff.json. Starting with an empty team.")
        return {}

def save_team_data():
    with open('staff.json', 'w') as f:
        json.dump(team_members, f, indent=4)

async def send_log_message(embed):
    log_channel = bot.get_channel(int(LOG_CHANNEL_ID))
    if log_channel:
        await log_channel.send(embed=embed)
    else:
        print(f"Error: Log channel not found with ID {LOG_CHANNEL_ID}")

@bot.event
async def on_ready():
    global team_members
    global start_time # Make sure we can update the global variable
    team_members = load_team_data()
    start_time = datetime.datetime.now() # Set the start time when the bot is ready
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Creative Vivo Designs"))

@bot.command()
@commands.has_permissions(manage_guild=True)
async def register(ctx, member: discord.Member, *, role: str):
    global team_members
    user_id = member.id
    team_members[user_id] = role
    save_team_data() # Now we save to the file!
    await ctx.send(f"Registered {member.mention} as a {role}!", delete_after=5)

    log_embed = discord.Embed(title="[ Team Member Registered ]", color=discord.Color.green(), timestamp=datetime.datetime.now())
    log_embed.add_field(name="Administrator", value=ctx.author.mention, inline=False)
    log_embed.add_field(name="Registered Member", value=member.mention, inline=False)
    log_embed.add_field(name="Assigned Role", value=role, inline=False)
    await send_log_message(log_embed)

@bot.command()
@commands.has_permissions(manage_guild=True)
async def unregister(ctx, member: discord.Member):
    global team_members
    user_id = member.id
    if user_id in team_members:
        role = team_members.pop(user_id)
        save_team_data() # And we save here too!
        await ctx.send(f"Unregistered {member.mention} who was a {role}.", delete_after=5)

        log_embed = discord.Embed(title="[ Team Member Unregistered ]", color=discord.Color.orange(), timestamp=datetime.datetime.now())
        log_embed.add_field(name="Administrator", value=ctx.author.mention, inline=False)
        log_embed.add_field(name="Unregistered Member", value=member.mention, inline=False)
        log_embed.add_field(name="Previous Role", value=role, inline=False)
        await send_log_message(log_embed)
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

@bot.command()
@commands.has_permissions(manage_guild=True)
async def addorder(ctx, id: str, order_type: str, description: str, deadline: str = None):
    if id in orders:
        await ctx.send(f"Order with ID {id} already exists!", delete_after=5)
        return
    orders[id] = {"status": "New", "type": order_type, "description": description, "deadline": deadline}
    await ctx.send(f"Order {id} added with type: {order_type} and status: New. Deadline: {deadline if deadline else 'None'}", delete_after=5)

    log_embed = discord.Embed(title="[ New Order Added ]", color=discord.Color.blue(), timestamp=datetime.datetime.now())
    log_embed.add_field(name="Administrator", value=ctx.author.mention, inline=False)
    log_embed.add_field(name="Order ID", value=id, inline=False)
    log_embed.add_field(name="Type", value=order_type, inline=True)
    log_embed.add_field(name="Description", value=description, inline=False)
    if deadline:
        log_embed.add_field(name="Deadline", value=deadline, inline=True)
    await send_log_message(log_embed)

@bot.command()
@commands.has_permissions(manage_guild=True)
async def orderstatus(ctx, id: str, *, status: str):
    if id not in orders:
        await ctx.send(f"Order with ID {id} not found!", delete_after=5)
        return
    old_status = orders[id].get("status", "Unknown")
    orders[id]["status"] = status
    await ctx.send(f"Status of order {id} updated to: {status}", delete_after=5)

    log_embed = discord.Embed(title="[ Order Status Updated ]", color=discord.Color.teal(), timestamp=datetime.datetime.now())
    log_embed.add_field(name="Administrator", value=ctx.author.mention, inline=False)
    log_embed.add_field(name="Order ID", value=id, inline=False)
    log_embed.add_field(name="Old Status", value=old_status, inline=True)
    log_embed.add_field(name="New Status", value=status, inline=True)
    await send_log_message(log_embed)

@bot.command()
@commands.has_permissions(manage_guild=True)
async def assignorder(ctx, id: str, member: discord.Member):
    if id not in orders:
        await ctx.send(f"Order with ID {id} not found!", delete_after=5)
        return
    orders[id]["assigned_to"] = member.id
    await ctx.send(f"Order {id} has been assigned to {member.mention}!", delete_after=5)

    log_embed = discord.Embed(title="[ Order Assigned ]", color=discord.Color.gold(), timestamp=datetime.datetime.now())
    log_embed.add_field(name="Administrator", value=ctx.author.mention, inline=False)
    log_embed.add_field(name="Order ID", value=id, inline=False)
    log_embed.add_field(name="Assigned To", value=member.mention, inline=False)
    await send_log_message(log_embed)

@bot.command()
async def checkorder(ctx, id: str):
    if id not in orders:
        await ctx.send(f"Order with ID {id} not found!", delete_after=5)
        return
    order = orders[id]
    embed = discord.Embed(title=f"Order ID: {id}", color=discord.Color.blue())
    embed.add_field(name="Status", value=order.get('status', 'Unknown'), inline=False)
    embed.add_field(name="Type", value=order.get('type', 'Not specified'), inline=True)
    embed.add_field(name="Description", value=order.get('description', 'Not specified'), inline=False)
    if "assigned_to" in order:
        assigned_member_id = order["assigned_to"]
        assigned_member = bot.get_user(assigned_member_id)
        if assigned_member:
            embed.add_field(name="Assigned To", value=assigned_member.name, inline=True)
            if assigned_member_id in team_members:
                embed.add_field(name="Role", value=team_members[assigned_member_id], inline=True)
            else:
                embed.add_field(name="Role", value="Not Registered", inline=True)
        else:
            embed.add_field(name="Assigned To", value="Unknown member", inline=True)
    if "deadline" in order and order["deadline"]:
        embed.add_field(name="Deadline", value=order["deadline"], inline=False)
    if "notes" in order and order["notes"]:
        notes_text = "\n".join([f"- {n}" for n in order["notes"]])
        embed.add_field(name="Notes", value=notes_text, inline=False)
    await ctx.send(embed=embed, delete_after=10)

@bot.command()
@commands.has_permissions(manage_guild=True)
async def finishorder(ctx, id: str):
    if id not in orders:
        await ctx.send(f"Order with ID {id} not found!", delete_after=5)
        return
    orders[id]["status"] = "Completed"
    await ctx.send(f"Order {id} has been marked as completed!", delete_after=5)

    log_embed = discord.Embed(title="[ Order Completed ]", color=discord.Color.green(), timestamp=datetime.datetime.now())
    log_embed.add_field(name="Administrator", value=ctx.author.mention, inline=False)
    log_embed.add_field(name="Order ID", value=id, inline=False)
    await send_log_message(log_embed)

@bot.command()
async def whoisworking(ctx):
    working_assignments = {}
    for order_id, order_info in orders.items():
        if "assigned_to" in order_info and order_info.get("status") != "Completed":
            user_id = order_info["assigned_to"]
            member = bot.get_user(user_id)
            if member:
                if member.name not in working_assignments:
                    working_assignments[member.name] = []
                working_assignments[member.name].append(order_id)

    if not working_assignments:
        await ctx.send("Looks like everyone's taking a break! No one is assigned to incomplete orders right now.")
        return

    embed = discord.Embed(title="Current Order Assignments", color=discord.Color.green())
    for worker, assigned_orders in working_assignments.items():
        embed.add_field(name=worker, value=", ".join(assigned_orders), inline=False)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_guild=True)
async def addnote(ctx, id: str, *, note: str):
    if id not in orders:
        await ctx.send(f"Order with ID {id} not found!", delete_after=5)
        return
    if "notes" not in orders[id]:
        orders[id]["notes"] = []
    orders[id]["notes"].append(note)
    await ctx.send(f"Note added to order {id}!", delete_after=5)

    log_embed = discord.Embed(title="[ Note Added to Order ]", color=discord.Color.yellow(), timestamp=datetime.datetime.now())
    log_embed.add_field(name="Administrator", value=ctx.author.mention, inline=False)
    log_embed.add_field(name="Order ID", value=id, inline=False)
    log_embed.add_field(name="Note", value=note, inline=False)
    await send_log_message(log_embed)

@bot.command()
@commands.has_permissions(manage_guild=True)
async def announcement(ctx, channel_id: int, *, message):
    green_arrow = "<a:greenarrow:1357796907006558208>"
    announcement_text = f"@everyone\n\n{green_arrow}{green_arrow} **Announcement**\n\n{green_arrow} {message}"

    channel = bot.get_channel(channel_id)
    if channel:
        await channel.send(announcement_text)
        await ctx.message.delete(delay=2)
    else:
        await ctx.send(f"Error: Channel with ID {channel_id} not found.", delete_after=5)

    log_embed = discord.Embed(title="[ Announcement Sent ]", color=discord.Color.purple(), timestamp=datetime.datetime.now())
    log_embed.add_field(name="Administrator", value=ctx.author.mention, inline=False)
    log_embed.add_field(name="Channel ID", value=channel_id, inline=False)
    log_embed.add_field(name="Message", value=message, inline=False)
    await send_log_message(log_embed)

@bot.command()
async def say(ctx, *, message):
    await ctx.send(message)
    await ctx.message.delete(delay=1) # Moved the delete command here

@bot.command()
async def shoutout(ctx, member: discord.Member, *, message: str):
    """Give a shoutout to a team member!"""
    await ctx.send(f"Hey {member.mention}! {ctx.author.name} wanted to give you a shoutout: {message}")
    await ctx.message.delete(delay=1) # Delete the command message

@bot.command()
async def mypage(ctx):
    """See your own team profile."""
    user_id = ctx.author.id
    if user_id in team_members:
        role = team_members[user_id]
        await ctx.send(f"Hey {ctx.author.name}! Your registered role is: {role}")
    else:
        await ctx.send(f"Hey {ctx.author.name}! You are not currently registered as a team member. Use `!!register` (if you have permission) to join!")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    """Clear a certain amount of messages. Requires Manage Messages permission."""
    await ctx.channel.purge(limit=amount + 1)  # +1 to delete the command message too
    await ctx.send(f"Cleared {amount} messages!", delete_after=3)

@bot.command()
async def serverinfo(ctx):
    """Get information about the current server."""
    embed = discord.Embed(title=ctx.guild.name, color=discord.Color.blue())
    embed.add_field(name="Owner", value=ctx.guild.owner.name, inline=False)
    embed.add_field(name="Member Count", value=ctx.guild.member_count, inline=False)
    embed.add_field(name="Created At", value=ctx.guild.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def poll(ctx, question: str, *options):
    """Create a simple poll with reactions."""
    if len(options) < 2 or len(options) > 10:
        await ctx.send("You need to provide between 2 and 10 options for the poll.")
        return

    embed = discord.Embed(title=f"Poll: {question}", color=discord.Color.green())
    reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    option_list = ""
    for i, option in enumerate(options):
        option_list += f"{reactions[i]} {option}\n"
    embed.description = option_list
    poll_message = await ctx.send(embed=embed)
    for i in range(len(options)):
        await poll_message.add_reaction(reactions[i])
    await ctx.message.delete(delay=1) # Let's keep the delete for the poll command too

@bot.command()
async def commands(ctx):
    help_embed = discord.Embed(title="Bot Commands", color=discord.Color.blurple())
    help_embed.add_field(name="!!team", value="Shows the list of registered team members.", inline=False)
    help_embed.add_field(name="!!checkorder <id>", value="Checks the details and status of a specific order.", inline=False)
    help_embed.add_field(name="!!finishorder <id>", value="Marks an order as completed. **Requires Manage Server permission.**", inline=False)
    help_embed.add_field(name="!!whoisworking", value="Shows who is currently assigned to incomplete orders.", inline=False)
    help_embed.add_field(name="!!addnote <order_id> <note>", value="Adds a note to a specific order. **Requires Manage Server permission.**", inline=False)
    help_embed.add_field(name="!!shoutout <member> <message>", value="Give a shoutout to a team member!", inline=False)
    help_embed.add_field(name="!!mypage", value="See your own team profile.", inline=False)
    help_embed.add_field(name="!!clear <amount>", value="Clear a certain amount of messages. **Requires Manage Messages permission.**", inline=False)
    help_embed.add_field(name="!!serverinfo", value="Get information about the current server.", inline=False)
    help_embed.add_field(name="!!poll <question> <option1> <option2> ...", value="Create a simple poll with reactions.", inline=False)
    help_embed.add_field(name="!!say <message>", value="Makes the bot say the message and deletes your command.", inline=False)
    help_embed.add_field(name="!!register <member> <role>", value="Registers a member as part of the team. **Requires Manage Server permission.**", inline=False)
    help_embed.add_field(name="!!unregister <member>", value="Unregisters a member from the team. **Requires Manage Server permission.**", inline=False)
    help_embed.add_field(name="!!addorder <id> <order_type> <description> [deadline]", value="Adds a new order to the system. You can optionally add a deadline (e.g., 2025-04-15). **Requires Manage Server permission.**", inline=False)
    help_embed.add_field(name="!!orderstatus <id> <status>", value="Updates the status of an existing order. **Requires Manage Server permission.**", inline=False)
    help_embed.add_field(name="!!assignorder <id> <member>", value="Assigns an order to a specific team member. **Requires Manage Server permission.**", inline=False)
    help_embed.add_field(name="!!announcement <channel_id> <message>", value="Sends an announcement to a specific channel. **Requires Manage Server permission.**", inline=False)
    help_embed.add_field(name="!!commands", value="Shows this list of commands.", inline=False)
    help_embed.add_field(name="!!uptime", value="Shows how long the bot has been online.", inline=False)
    await ctx.send(embed=help_embed)

@bot.command()
async def uptime(ctx):
    """Shows how long the bot has been online."""
    now = datetime.datetime.now()
    uptime = now - start_time
    hours, remainder = divmod(int(uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    await ctx.send(f"Bot has been online for: {days} days, {hours} hours, {minutes} minutes, and {seconds} seconds!")

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

bot.run(TOKEN)
