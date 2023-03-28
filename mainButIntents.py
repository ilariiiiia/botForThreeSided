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

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

logger = Logger(__file__)
db = Database(__file__)


async def handlePlayerExists(ctx: Context) -> bool:
    try:
        db.findPlayer(ctx.message.author.id)
        logger.log("handlePlayerExists called", props={
            "interaction": Logger.contextToObject(ctx),
            "success": True
        })
        return True
    except PlayerNotFound:
        logger.log("handlePlayerExists called", props={
            "interaction": Logger.contextToObject(ctx),
            "success": False
        })
        embed = discord.Embed(
            title='Uh Oh! An error occurred!',
            description='Player not found! Creating a new player... If this happened through a command, please re-run '
                        'it.',
            color=0xff0000)
        await ctx.send(embed=embed)
        db.createNewPlayer(ctx.message.author)
        return False


@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        logger.log("Message arrived!", props={
            "payload": logger.messageToObject(message),
            "wasMe": True
        })
        return
    if message.content.startswith(bot.command_prefix):
        logger.log("Message arrived!", props={
            "payload": logger.messageToObject(message),
            "wasMe": False
        })
        await bot.process_commands(message)
        return


@bot.tree.command(name="whoami", description="Gives your stats")
async def whoAmI(ctx: Context):
    if not await handlePlayerExists(ctx):
        logger.log("whoAmI called", props={
            "interaction": Logger.contextToObject(ctx),
            "success": False
        })
        return
    player = db.findPlayer(ctx.message.author.id)
    embed = discord.Embed(title='Found you!', description='', color=0x79e4ff)
    for name in player.__dict__.keys():
        embed.add_field(name=name, value=player.__dict__[name], inline=False)
    await ctx.send(embed=embed)
    logger.log("whoAmI called", props={
        "interaction": Logger.contextToObject(ctx),
        "success": True
    })


@bot.tree.command(name="decks")
async def decks(ctx: Context):
    try:
        author = db.findPlayer(ctx.message.author.id)
        embed = discord.Embed(title='Decks', description='Your current decks', color=0x79e4ff)
        for deck in author.decks:
            embed.add_field(name=f'"{deck.name}"', value=f'{len(deck.cards)} cards', inline=False)
        if not len(author.decks):
            embed = discord.Embed(title='Decks', description='You have no decks at the moment. Please consider '
                                                             'creating one with /newDeck', color=0x79e4ff)
        await ctx.send(embed=embed)
        logger.log("decks called", props={
            "interaction": Logger.contextToObject(ctx),
            "success": True
        })
    except PlayerNotFound:
        logger.log("decks called", props={
            "interaction": Logger.contextToObject(ctx),
            "success": False
        })
        embed = discord.Embed(title='Decks', description='Player not found! Creating a new player...', color=0xff0000)
        await ctx.send(embed=embed)
        db.createNewPlayer(ctx.message.author)
        await decks(ctx)


@bot.command(name="newdeck")
async def newDeck(ctx: Context, name: str = None):
    if not await handlePlayerExists(ctx):
        logger.log("newDeck called", props={
            "interaction": Logger.contextToObject(ctx),
            "name": name,
            "success": False
        })
        return
    player = db.findPlayer(ctx.message.author.id)
    for deck in player.decks:
        if deck.name == name:
            embed = discord.Embed(title='newDeck', description='Deck already exists! Please try another name',
                                  color=0xff0000)
            await ctx.send(embed=embed)
            logger.log("newDeck called", props={
                "interaction": Logger.contextToObject(ctx),
                "name": name,
                "success": False
            })
            raise BadRequest("Deck already exists!")
    player.decks.append(Deck(name=name))
    db.savePlayer(player)
    await decks(ctx)
    logger.log("newDeck called", props={
        "interaction": Logger.contextToObject(ctx),
        "name": name,
        "success": True
    })


@bot.command(name="removedeck")
async def removeDeck(ctx: Context, name: str = None):
    if not await handlePlayerExists(ctx):
        logger.log("removeDeck called", props={
            "interaction": Logger.contextToObject(ctx),
            "name": name,
            "success": False
        })
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
        logger.log("removeDeck called", props={
            "interaction": Logger.contextToObject(ctx),
            "name": name,
            "success": False
        })
        raise BadRequest("Deck does not exist!")
    db.savePlayer(player)
    await decks(ctx)
    logger.log("removeDeck called", props={
        "interaction": Logger.contextToObject(ctx),
        "name": name,
        "success": True
    })


@bot.tree.command(name="showallcards")
async def showAllCards(ctx: Context):
    logger.log("showAllCards called", props={
        "interaction": Logger.contextToObject(ctx)
    })
    embed = discord.Embed(title="All available cards!", color=0x79e4ff)
    for c in db.getCards():
        embed.add_field(name=c["name"], value=c["props"], inline=False)
    await ctx.send(embed=embed)


@bot.command(name="addcardtodeck")
async def addCardToDeck(ctx: Context, cardName: str, deckName: str):
    if not await handlePlayerExists(ctx):
        logger.log("addCardToDeck called", props={
            "interaction": Logger.contextToObject(ctx),
            "cardName": cardName,
            "deckName": deckName,
            "success": False
        })
        return
    if not db.isValidCardName(cardName):
        embed = discord.Embed(title='Add card to deck', description="Such card doesn't exist. Please use "
                                                                    "/showAllCards to see all of them", color=0xff0000)
        await ctx.send(embed=embed)
        logger.log("addCardToDeck called", props={
            "interaction": Logger.contextToObject(ctx),
            "cardName": cardName,
            "deckName": deckName,
            "success": False
        })
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
        logger.log("addCardToDeck called", props={
            "interaction": Logger.contextToObject(ctx),
            "cardName": cardName,
            "deckName": deckName,
            "success": False
        })
        raise BadRequest("There is no deck called like that!")
    player.decks[deckIndex].cards.append(cardName)
    db.savePlayer(player)
    embed = discord.Embed(title="Card added!", color=0x79e4ff)
    await ctx.send(embed=embed)
    logger.log("addCardToDeck called", props={
        "interaction": Logger.contextToObject(ctx),
        "cardName": cardName,
        "deckName": deckName,
        "success": False
    })


@bot.command(name="addcardtootherdeck")
async def addCardToOtherDeck(ctx: Context, cardName: str, otherName: str, deckName: str):
    if not await handlePlayerExists(ctx):
        logger.log("addCardToOtherDeck called but player does not exist", props={
            "interaction": Logger.contextToObject(ctx),
            "cardName": cardName,
            "deckName": deckName,
            "success": False
        })
        return
    if not any(str(r) == "sudo-user" for r in ctx.message.author.roles):
        logger.log("addCardToOtherDeck called but user isn't sudo user", props={
            "interaction": Logger.contextToObject(ctx),
            "cardName": cardName,
            "deckName": deckName,
            "success": False
        })
        embed = discord.Embed(
            title='Uh Oh! An error occurred!',
            description="You don't seem to have the needed permissions!",
            color=0xff0000)
        await ctx.send(embed=embed)
        return
    if not db.isValidCardName(cardName):
        embed = discord.Embed(title='Add card to deck', description="Such card doesn't exist. Please use "
                                                                    "/showAllCards to see all of them", color=0xff0000)
        await ctx.send(embed=embed)
        logger.log("addCardToOtherDeck called but card is not valid card name", props={
            "interaction": Logger.contextToObject(ctx),
            "cardName": cardName,
            "deckName": deckName,
            "success": False
        })
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
        logger.log("addCardToDeck called but deck does not exist", props={
            "interaction": Logger.contextToObject(ctx),
            "cardName": cardName,
            "deckName": deckName,
            "success": False
        })
        raise BadRequest("There is no deck called like that!")
    player.decks[deckIndex].cards.append(cardName)
    db.savePlayer(player)
    embed = discord.Embed(title="Card added!", color=0x79e4ff)
    await ctx.send(embed=embed)
    logger.log("addCardToDeck called", props={
        "interaction": Logger.contextToObject(ctx),
        "cardName": cardName,
        "deckName": deckName,
        "success": True
    })


@bot.command(name="draw")
async def draw(ctx: Context, n: str):
    if not await handlePlayerExists(ctx):
        logger.log("draw called but user doesn't exist", props={
            "interaction": Logger.contextToObject(ctx),
            "n": n,
            "success": False
        })
        return
    try:
        int(n)
    except ValueError:
        embed = discord.Embed(title='Draw', description="Value inputted is not a number!", color=0xff0000)
        await ctx.send(embed=embed)
        logger.log("draw called but input isn't a number", props={
            "interaction": Logger.contextToObject(ctx),
            "n": n,
            "success": False
        })
        raise BadRequest("Value inputted is not a number!")
    num = int(n)
    player = db.findPlayer(ctx.message.author.id)
    db.savePlayer(player.draw(num))
    embed = discord.Embed(title="Card(s) drawn!", color=0x79e4ff)
    await ctx.send(embed=embed)
    logger.log("draw called", props={
        "interaction": Logger.contextToObject(ctx),
        "n": n,
        "success": True
    })


@bot.command(name="play", description="plays the card as argument")
async def play(ctx: Context, cardName: str):
    if not await handlePlayerExists(ctx):
        logger.log("draw called but player does not exist", props={
            "interaction": Logger.contextToObject(ctx),
            "cardName": cardName,
            "success": False
        })
        return
    if not db.isValidCardName(cardName):
        embed = discord.Embed(title='Play',
                              description="Card does not exist. Please try again",
                              color=0xff0000)
        await ctx.send(embed=embed)
        logger.log("draw called but card does not exist", props={
            "interaction": Logger.contextToObject(ctx),
            "cardName": cardName,
            "success": False
        })
        raise BadRequest("Card does not exist!")
    player = db.findPlayer(ctx.message.author.id)
    db.savePlayer(player.play(cardName))
    embed = discord.Embed(title="Card played!", color=0x79e4ff)
    card = db.getCardFromName(cardName)
    embed.set_image(url=card.link)
    await ctx.send(embed=embed)
    logger.log("draw called", props={
        "interaction": Logger.contextToObject(ctx),
        "cardName": cardName,
        "success": True
    })


@bot.command(name="setcurrentdeck", description="Sets current deck to the argument")
async def setCurrentDeck(ctx: Context, deckName: str):
    if not await handlePlayerExists(ctx):
        logger.log("setCurrentDeck called but player does not exist", props={
            "interaction": Logger.contextToObject(ctx),
            "deckName": deckName,
            "success": False
        })
        return
    player = db.findPlayer(ctx.message.author.id)
    if any(deck.name == deckName for deck in player.decks):
        logger.log("setCurrentDeck called", props={
            "interaction": Logger.contextToObject(ctx),
            "deckName": deckName,
            "success": True
        })
        player.activeDeck = deckName
        db.savePlayer(player)
        embed = discord.Embed(title=f"Active deck changed to {deckName}", color=0x79e4ff)
        await ctx.send(embed=embed)
        return
    logger.log("setCurrentDeck called but deck does not exist", props={
        "interaction": Logger.contextToObject(ctx),
        "deckName": deckName,
        "success": False
    })
    return


@bot.tree.command(name="rm", description="Removes all user data")
async def rm(interaction: discord.interactions.Interaction):
    db.deleteAllData()
    await interaction.response.send_message(content="Done!")
    logger.log("rm called", props={
        "interaction": Logger.contextToObject(interaction),
        "success": True
    })
    db.restart()
    logger.log("restart called", props={
        "interaction": Logger.contextToObject(interaction),
        "success": True
    })


@bot.tree.command(name="restart", description="restarts the data")
async def restart(ctx: discord.interactions.Interaction):
    db.restart()
    await ctx.response.send_message(content="Restarted!")
    logger.log("restart called", props={
        "interaction": Logger.contextToObject(ctx),
        "success": True
    })


@bot.tree.command(name="commands", description="sends all the commands available")
async def commands(interaction: discord.interactions.Interaction):
    await interaction.response.send_message(content="""
Welcome! Here is a list of my commands...
+ **whoAmI**
    + Gives an overview of your account, including name, id, hand, and decks.
+ **decks**
    + Tells you your decks and the number of cards inside them.
+ **newDeck**
    + Creates a new deck.
+ **removeDeck**
    + Removes a deck.
+ **setCurrentDeck `[deckName]`**
    + Sets the current deck to `deckName`
+ **showAllCards**
    + Shows all available cards from the shared card pool.
+ **addCardToDeck `[card]`, `[deck]`**
    + Adds a card `card` to the deck `deck`.
+ **addCardToOtherDeck** `[card]` `[name]` `[deck]`
    + Adds a card `card` to `name`'s deck `deck`
+ **draw `[n]`**
    + Draws `n` cards.
+ **rm**
    + Deletes all user data (testing only).
+ **restart**
    + restarts the bot.
+ **commands**
    + Returns a list of the bot's commands
    """, ephemeral=True)
    logger.log("commands called", props={
        "interaction": Logger.contextToObject(interaction),
        "success": True
    })

@bot.event
async def on_ready():
    logger.log("bot ready!")
    synced = await bot.tree.sync()
    print(f'Logged in as {bot.user} with {synced} commands synced')


if __name__ == "__main__":
    bot.run(APIToken)
