import discord
from discord import Embed, Color, app_commands
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="", intents=intents)
deleted_messages = []

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

    try:
        synced = await bot.tree.sync(guild=discord.Object(os.getenv("GUILD_ID")))
        print(f"Synced {len(synced)} commands")
    except Exception as e: 
        print(f"Error syncing commands: {e}")

@bot.tree.command(name="ping", description="Pong!", guild=discord.Object(os.getenv("GUILD_ID")))
async def replyPing(interaction:discord.Interaction):
    await interaction.response.send_message("Pong!")

@bot.tree.command(name="academic-calendar", description="Sends a link to the Seattle Central academic calendar",
                  guild=discord.Object(os.getenv("GUILD_ID")))
async def replyAcademicCalendar(interaction:discord.Interaction):
    await interaction.response.send_message("https://seattlecentral.edu/about/calendar/current-academic-calendar")


#TODO -  use a dictionary instead of a list for deleted messages as you want
# a key value pair, author : message
# so when you snipe, it shows the author who wrote that deleted message
@bot.event
async def on_message_delete(message):
    await message.author.send(f"You have successfully deleted your message: ```{message.content}```")

    deleted_messages.append(message.content)

    if len(deleted_messages) >= 4:
        deleted_messages.clear()


@bot.event
async def on_message_edit(before_message, after_message):
    if after_message.author.bot:
        return

    await bot.process_commands(after_message)

    await before_message.channel.send(f"{before_message.author.mention} just edited a message!")
    await before_message.channel.send(f"Before it was edited, the message content was ```{before_message.content}```")
    await before_message.channel.send(f"Now it is ```{after_message.content}```")


@bot.command()
async def ping(ctx, arg=None):
    if not arg:
        await ctx.send("Please provide a USER ID")
        return
    elif not arg.isdigit():
        await ctx.send("Please provide a proper USER ID")
        return
    await ctx.send(f"<@{arg}>")



@bot.command()
async def academic(ctx, arg=None):
    if not arg:
        await ctx.send("Did you mean **academic calendar**?")
    if arg.lower() == "calendar":
        await ctx.send("https://seattlecentral.edu/about/calendar/current-academic-calendar")
    else:
        await ctx.send("Did you mean **academic calendar**?")


@bot.command()
async def talk(ctx, arg, user_ID, *, msg):
    if arg.lower() == "to":
        if user_ID:
            try:
                sendUser = await bot.fetch_user(int(user_ID))
                await sendUser.send(f"{msg}")
                await ctx.send("Message sent successfully!")
            except discord.NotFound:
                await ctx.send("User not found!")
            except discord.Forbidden:
                await ctx.send("I don't have permission to message this user.")
        else:
            return
    

@bot.command()
async def member(ctx, arg):
    if arg.lower() == "count":
        await ctx.send(f"Number of members: {ctx.guild.member_count}")


@bot.command()
async def whoami(ctx, user_id: int = None):
    ret_embed = None
    in_server = False
    guild = bot.get_guild(int(os.getenv("GUILD_ID")))
    member = None

    if user_id:
        user_target = await bot.fetch_user(user_id)

        try:
            member = await guild.fetch_member(user_id)
            in_server = True
        except discord.NotFound:
            in_server = False

        ret_embed = Embed(
            color=0xff5733,
            title=f"User: {user_target}",
            description=f"Their user id: {user_target.id}\nTheir join date: {user_target.created_at.strftime('%B %d, %Y')}\nIn server: {'Yes' if in_server else 'No'}",
            timestamp=datetime.now()
        )

        ret_embed.set_author(name=ctx.author, url=None, icon_url=ctx.author.avatar.url)
        ret_embed.set_thumbnail(url=user_target.avatar.url)

        await ctx.send(embed=ret_embed)
        
        return
    else:
        ret_embed = Embed(
            color=0xff5733,
            title=f"User: {ctx.author}",
            description=f"Your user id: {ctx.author.id}\n Your join date: {ctx.author.created_at.strftime("%B %d, %Y")}",
            timestamp=datetime.now()
        )

        ret_embed.set_author(name=ctx.author, url=None, icon_url=ctx.author.avatar.url)
        ret_embed.set_thumbnail(url=ctx.author.avatar.url)

        await ctx.send(embed=ret_embed)
        return

@bot.command()
async def creator(ctx):
    creator_user = await bot.fetch_user(os.getenv("CREATOR_ID"))

    ret_embed = Embed(
        color=0x8c0ce4,
        title=f"Creater of bot: {creator_user}",
        description=f"Their user id: {creator_user.id}\n Their join date: {creator_user.created_at.strftime('%B %d, %Y')}",
        timestamp=datetime.now()
    )

    ret_embed.set_author(name=ctx.author, url=None, icon_url=ctx.author.avatar.url)
    ret_embed.set_thumbnail(url=ctx.author.avatar.url)

    await ctx.send(embed=ret_embed)


#TODO - FIX creating voice channels
@bot.command()
async def create(ctx, arg, category_name, channel_name):
    if ctx.author.guild_permissions.manage_channels:
        category = discord.utils.get(ctx.author.guild.categories, name=category_name)

        if category:
            if arg.lower() == "channel":
                await ctx.guild.create_text_channel(channel_name, category=category)
                await ctx.send(f"The text channel **{channel_name}** has been created in the **{category}** channel")
            elif arg.lower() == "voicechannel":
                await ctx.guild.create_voice_channel(channel_name, category=category_name)
                await ctx.send(f"The voice channel **{channel_name}** has been created in the **{category}** channel")
        else:
            if arg.lower() == "channel":
                await ctx.guild.create_text_channel(channel_name)
                await ctx.send(f"Could not find category **{category_name}**. Created text channel **{channel_name}** without a category")
            elif arg.lower() == "voicechannel":
                await ctx.guild.create_voice_channel(channel_name)
                await ctx.send(f"Could not find category **{category_name}**. Created voice channel **{channel_name}** without a category")
    else:
        await ctx.send("You don't have permissions")


@bot.command()
async def snipe(ctx):
    for i in range(len(deleted_messages)):
        await ctx.send(deleted_messages[i])

@bot.command()
async def list(ctx, arg):
    if arg.lower() == "commands":
        await ctx.send("```\nlist commands\nping\nacademic calendar\ntalk to\nmember count\nwhoami\ncreator\ncreate voicechannel/channel```")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error  


bot.run(os.getenv("DISCORD_BOT_TOKEN"))
