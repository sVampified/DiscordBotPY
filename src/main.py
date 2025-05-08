import discord
from discord.ext import commands

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
        

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error  


bot.run(os.getenv("DISCORD_BOT_TOKEN"))
