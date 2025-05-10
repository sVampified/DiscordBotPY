import discord
from discord import Embed, Color
from discord.ext import commands
from datetime import datetime


from dotenv import load_dotenv
import os

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="", intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.event
async def on_message_delete(message):
    await message.author.send(f"You have successfully deleted your message: ```{message.content}```")


@bot.event
async def on_message_edit(before_message, after_message):

    if after_message.author.bot:
        return

    await bot.process_commands(after_message)

    await before_message.channel.send(f"{before_message.author.mention} just edited a message!")
    await before_message.channel.send(f"Before it was edited, the message content was ```{before_message.content}```")
    await before_message.channel.send(f"Now it is ```{after_message.content}```")


@bot.command()
async def ping(ctx, arg):
    if arg.isdigit():
        await ctx.send(f"<@{arg}>")
    else:
        await ctx.send("Please provide a correct USER ID")


@bot.command()
async def academic(ctx, arg):
    if arg.lower() == "calendar":
        await ctx.send("https://seattlecentral.edu/about/calendar/current-academic-calendar")


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
    guild = bot.get_guild(1242670627370962964)


    #TODO - FIX THE FEATURE, is specified user a member of the guild or not.
    if user_id:
        user_target = await bot.fetch_user(user_id)

        if guild.get_member(user_id) is not None:
            in_server = True

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
async def commands(ctx):
    await ctx.send("```\nping\nacademic calendar\ntalk to\nmember count\nwhoami\n```")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error  


bot.run(os.getenv("DISCORD_BOT_TOKEN"))
