import os

import discord
from discord.ext import commands
from discord.ext.commands.context import Context  # for typing only
from dotenv import load_dotenv

# utilities
from utils.db import Database, PlayerNotFound
from utils.Deck import Deck
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
    logger.log("handlePlayerExists called", props={
        "ctx": Logger.contextToObject(ctx)
    })
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
        return False


@bot.event
async def on_ready():
    logger.log("bot ready!")
    print(f'Logged in as {bot.user}')


@bot.event
async def on_message(message: discord.Message):
    logger.log("Message arrived!", props={
        "payload": logger.messageToObject(message)
    })
    if message.author == bot.user:
        return
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return


@bot.command()
async def whoAmI(ctx: Context):
    logger.log("whoAmI called", props={
        "ctx": Logger.contextToObject(ctx)
    })
    await handlePlayerExists(ctx)
    player = db.findPlayer(ctx.message.author.id)
    embed = discord.Embed(title='Found you!', description='', color=0x79e4ff)
    for name in player.__dict__.keys():
        embed.add_field(name=name, value=player.__dict__[name], inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def decks(ctx: Context):
    logger.log("decks called", props={
        "ctx": Logger.contextToObject(ctx)
    })
    try:
        author = db.findPlayer(ctx.message.author.id)
        embed = discord.Embed(title='Decks', description='Your current decks', color=0x79e4ff)
        for deck in author.decks:
            embed.add_field(name=f'"{deck.name}"', value=f'{len(deck.cards)} cards', inline=False)
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
async def newDeck(ctx: Context, name: str = None):
    logger.log("newDeck called", props={
        "ctx": Logger.contextToObject(ctx),
        "name": name
    })
    if not await handlePlayerExists(ctx):
        return
    player = db.findPlayer(ctx.message.author.id)
    for deck in player.decks:
        if deck.name == name:
            embed = discord.Embed(title='newDeck', description='Deck already exists! Please try another name',
                                  color=0xff0000)
            await ctx.send(embed=embed)
            raise BadRequest("Deck already exists!")
    player.decks.append(Deck(name=name))
    db.savePlayer(player)
    await decks(ctx)


@bot.command()
async def removeDeck(ctx: Context, name: str = None):
    logger.log("removeDeck called", props={
        "ctx": Logger.contextToObject(ctx),
        "name": name
    })
    if not await handlePlayerExists(ctx):
        return
    player = db.findPlayer(ctx.message.author.id)
    found = False
    for i, deck in enumerate(player.decks):
        if deck.name == name:
            player.decks.remove(deck)
            found = True
    if not found:
        embed = discord.Embed(title='removeDeck', description="Deck doesn't exist! Please try another name",
                              color=0xff0000)
        await ctx.send(embed=embed)
        raise BadRequest("Deck does not exist!")
    db.savePlayer(player)
    await decks(ctx)


@bot.command()
async def showAllCards(ctx: Context):
    logger.log("showAllCards called", props={
        "ctx": Logger.contextToObject(ctx)
    })
    embed = discord.Embed(title="All available cards!", color=0x79e4ff)
    for c in db.getCards():
        embed.add_field(name=c["name"], value=c["props"], inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def saveMe(ctx: Context):
    logger.log("saveMe called", props={
        "ctx": Logger.contextToObject(ctx)
    })
    if not await handlePlayerExists(ctx):
        return
    db.savePlayer(db.findPlayer(ctx.message.author.id))
    embed = discord.Embed(title="Saved!", color=0x79e4ff)
    await ctx.send(embed=embed)


@bot.command()
async def saveCards(ctx: Context):
    logger.log("saveCards called", props={
        "ctx": Logger.contextToObject(ctx)
    })
    db.saveCards()
    embed = discord.Embed(title="Saved!", color=0x79e4ff)
    await ctx.send(embed=embed)


@bot.command()
async def addCardToDeck(ctx: Context, cardName: str, deckName: str):
    logger.log("addCardToDeck called", props={
        "ctx": Logger.contextToObject(ctx),
        "cardName": cardName,
        "deckName": deckName
    })
    if not await handlePlayerExists(ctx):
        return
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
        embed = discord.Embed(title='Add card to deck', description="Such deck doesn't exist. Please use "
                                                                    "/whoAmI to see your decks", color=0xff0000)
        await ctx.send(embed=embed)
        raise BadRequest("There is no deck called like that!")
    player.decks[deckIndex].cards.append(cardName)
    db.savePlayer(player)
    embed = discord.Embed(title="Card added!", color=0x79e4ff)
    await ctx.send(embed=embed)


@bot.command()
async def addCardToOtherDeck(ctx: Context, cardName: str, otherName: str, deckName: str):
    logger.log("addCardToDeck called", props={
        "ctx": Logger.contextToObject(ctx),
        "cardName": cardName,
        "deckName": deckName,
    })
    if not await handlePlayerExists(ctx):
        logger.log("Access denied", props={
            "ctx": Logger.contextToObject(ctx),
            "cardName": cardName,
            "deckName": deckName,
        })
        embed = discord.Embed(
            title='Uh Oh! An error occurred!',
            description="You don't seem to have the needed permissions!",
            color=0xff0000)
        await ctx.send(embed=embed)
        return
    if not any(str(r) == "sudo-user" for r in ctx.message.author.roles):
        return
    if not db.isValidCardName(cardName):
        embed = discord.Embed(title='Add card to deck', description="Such card doesn't exist. Please use "
                                                                    "/showAllCards to see all of them", color=0xff0000)
        await ctx.send(embed=embed)
        raise BadRequest("There isn't a card called like that. Please use /showAllCards to see all of them.")
    player = db.findPlayerFromName(otherName)
    deckIndex = -1
    for i in range(len(player.decks)):
        if player.decks[i].name == deckName:
            deckIndex = i
    if deckIndex == -1:
        embed = discord.Embed(title='Add card to deck', description="Such deck doesn't exist. Please use "
                                                                    "/whoAmI to see your decks", color=0xff0000)
        await ctx.send(embed=embed)
        raise BadRequest("There is no deck called like that!")
    player.decks[deckIndex].cards.append(cardName)
    db.savePlayer(player)
    embed = discord.Embed(title="Card added!", color=0x79e4ff)
    await ctx.send(embed=embed)


@bot.command()
async def draw(ctx: Context, n: str):
    logger.log("draw called", props={
        "ctx": Logger.contextToObject(ctx),
        "n": n
    })
    if not await handlePlayerExists(ctx):
        return
    try:
        int(n)
    except ValueError:
        embed = discord.Embed(title='Draw', description="Value inputted is not a number!", color=0xff0000)
        await ctx.send(embed=embed)
        raise BadRequest("Value inputted is not a number!")
    num = int(n)
    player = db.findPlayer(ctx.message.author.id)
    db.savePlayer(player.draw(num))


@bot.command()
async def rm(ctx: Context):
    logger.log("rm called", props={
        "ctx": Logger.contextToObject(ctx)
    })
    await deleteAllData(ctx)


@bot.command()
async def deleteAllData(ctx: Context):
    logger.log("deleteAllData called", props={
        "ctx": Logger.contextToObject(ctx)
    })
    db.deleteAllData()
    await ctx.send("Done!")


@bot.command()
async def restart(ctx: Context):
    logger.log("restart called", props={
        "ctx": Logger.contextToObject(ctx)
    })
    db.restart()
    await ctx.send("Restarted!")


@bot.command()
async def ping(ctx: Context):
    logger.log("ping called", props={
        "ctx": Logger.contextToObject(ctx)
    })
    await ctx.send('pong')


if __name__ == "__main__":
    bot.run(APIToken)
