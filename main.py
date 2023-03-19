import os

import discord
from discord.ext import commands
from discord.ext.commands.context import Context  # for typing only
from dotenv import load_dotenv

from utils.db import Database, PlayerNotFound
# utilities
from utils.log import Logger
from utils.Exceptions import BadRequest

load_dotenv()
APIToken = os.getenv("botToken")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

logger = Logger(__file__)
db = Database(__file__)


async def handlePlayerExists(ctx: Context) -> bool:
    try:
        db.findPlayer(ctx.message.author.id)
        return True
    except PlayerNotFound:
        embed = discord.Embed(
            title='Uh Oh! An error occurred!',
            description='Player not found! Creating a new player... If this happened through a command, please re-run '
                        'it.',
            color=0xff0000)
        await ctx.send(embed=embed)
        db.createNewPlayer(ctx.message.author)
        return True


@bot.event
async def on_ready():
    logger.log("bot ready!")
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
    await handlePlayerExists(ctx)
    player = db.findPlayer(ctx.message.author.id)
    embed = discord.Embed(title='Found you!', description='', color=0x79e4ff)
    for name in player.objectify().keys():
        embed.add_field(name=name, value=player.objectify()[name], inline=False)
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
async def showAllCards(ctx: Context):
    logger.log("showAllCards opened")
    embed = discord.Embed(title="All available cards!", color=0x79e4ff)
    for c in db.getCards():
        embed.add_field(name=c["name"], value=c["props"], inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def saveMe(ctx: Context):
    logger.log("saveMe opened")
    db.savePlayer(db.findPlayer(ctx.message.author.id))
    embed = discord.Embed(title="Saved!", color=0x79e4ff)
    await ctx.send(embed=embed)


@bot.command()
async def saveCards(ctx: Context):
    logger.log("saveCards opened")
    db.saveCards()
    embed = discord.Embed(title="Saved!", color=0x79e4ff)
    await ctx.send(embed=embed)


@bot.command()
async def addCardToDeck(ctx: Context, deckName: str, cardName: str):
    logger.log("addCardToDeck opened")
    if not db.isValidCardName(cardName):
        embed = discord.Embed(title='Add card to deck', description="Such card doesn't exist. Please use "
                                                                    "/showAllCards to see all of them", color=0xff0000)
        await ctx.send(embed=embed)
        raise BadRequest("There isn't a card called like that. Please use /showAllCards to see all of them.")
    player = db.findPlayer(ctx.message.author.id)
    deckIndex = -1
    for i in range(len(player.decks)):
        if player.decks[i].name == deckName:
            deckIndex = i
    if deckIndex == -1:
        raise BadRequest("There is no deck called like that!")
    player.decks[deckIndex].cards.append(db.getCardFromName(cardName))
    db.savePlayer(player)
    embed = discord.Embed(title="Card added!", color=0x79e4ff)
    await ctx.send(embed=embed)


@bot.command()
async def rm(ctx: Context):
    logger.log("rm opened")
    await deleteAllData(ctx)


@bot.command()
async def deleteAllData(ctx: Context):
    logger.log("deleteAllData opened")
    db.deleteAllData()
    await ctx.send("Done!")


@bot.command()
async def restart(ctx: Context):
    logger.log("restart opened")
    db.restart()
    await ctx.send("Restarted!")


@bot.command()
async def ping(ctx):
    logger.log("ping opened")
    await ctx.send('pong')


if __name__ == "__main__":
    bot.run(APIToken)
