import os

import discord
from discord.ext import commands
from discord.ext.commands.context import Context  # for typing only
from dotenv import load_dotenv

from utils.db import Database, PlayerNotFound
# utilities
from utils.log import Logger

load_dotenv()
APIToken = os.getenv("botToken")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

logger = Logger(__file__)
db = Database(__file__)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


@bot.event
async def on_message(message):
    logger.log(message)
    if message.author == bot.user:
        return
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return


@bot.command()
async def whoAmI(ctx: Context):
    logger.log("whoAmI opened")
    try:
        db.findPlayer(ctx.message.author.id)
        embed = discord.Embed(title='Who are you?', description='I found you!', color=0x79e4ff)
        await ctx.send(embed=embed)
    except PlayerNotFound:
        embed = discord.Embed(title='Who are you?', description='Player not found! Creating a new player...',
                              color=0xff0000)
        await ctx.send(embed=embed)
        db.createNewPlayer(ctx.message.author)
        embed = discord.Embed(title='Who are you?', description='Player created!',
                              color=0x79e4ff)
        await ctx.send(embed=embed)

@bot.command()
async def decks(ctx: Context):
    logger.log("decks opened")
    try:
        author = db.findPlayer(ctx.message.author.id)
        embed = discord.Embed(title='Decks', description='Your current decks', color=0x79e4ff)
        for deck in author.decks:
            maxLvl = max(card.level for card in deck.cards)
            embed.add_field(name=f'"{deck.name}"', value=f'{len(deck.cards)} cards, max. lvl.:{maxLvl}', inline=False)
        if not len(author.decks):
            embed = discord.Embed(title='Decks', description='You have no decks at the moment. Please consider '
                                                             'creating one with /newDeck', color=0x79e4ff)
        await ctx.send(embed=embed)
    except PlayerNotFound:
        embed = discord.Embed(title='Decks', description='Player not found! Creating a new player...', color=0xff0000)
        await ctx.send(embed=embed)
        db.createNewPlayer(ctx.message.author)
        await decks(ctx)



@bot.command()
async def ping(ctx):
    logger.log("ping sent")
    await ctx.send('pong')


if __name__ == "__main__":
    bot.run(APIToken)
