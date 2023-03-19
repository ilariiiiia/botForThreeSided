import os
import shutil
from pathlib import Path
import json
from utils.Deck import Deck, Card, cardFromObject, cardObject, deckObject

import discord

playerObject = {
    "username": str,
    "id": int,
    "hand": list[str],
    "deck": list[deckObject]
}


class PlayerNotFound(Exception):
    """
    Error raised when the player is not found
    """
    pass


class helperUser:
    def __init__(self, name, userID):
        self.name = name
        self.id = userID


def userFromDictionary(arg: dict, decks: list[Deck]):
    return Player(
        user=helperUser(arg["username"], arg["id"]),
        hand=arg["hand"],
        decks=decks
    )


class Player:
    def __init__(self, user: discord.Member | helperUser, hand: list[Card], decks: list[Deck]):
        self.username = user.name
        self.id = user.id
        self.hand = hand if hand else []
        self.decks = decks if decks else []
        self.activeDeck = None

    def objectify(self) -> dict:
        return {
            "username": self.username,
            "id": self.id,
            "hand": self.hand,
            "decks": [deck.toObject(name=True) for deck in self.decks]
        }

    def toJSONString(self):
        return json.dumps(self.objectify())

    def __repr__(self):
        return f"""Player;username={self.username},id={self.id},hand={self.hand},decks={self.decks}"""


class Database:
    def __init__(self, path: str):
        self.path = path
        self.root = os.path.dirname(os.path.abspath(path))
        self.playersFolderPath = Path(f"{self.root}/data")
        self.cardsFolderPath = Path(f"{self.root}/assets/cards")
        self.playersFilePath = self.playersFolderPath / "players.json"
        self.cardsFilePath = self.cardsFolderPath / "cards.json"
        self.cards = self.getCards()

        # initialize an empty database, in case it doesn't exist
        def initializeDB():
            with open(self.playersFilePath, "w") as playersFile:
                playersFile.write('{"players":[]}')

        self.createFileIfNotExists(
            folderPath=self.playersFolderPath, filePath=self.playersFilePath, initFunction=initializeDB
        )

        # read cards
        def initializeCards():
            with open(self.cardsFilePath, "w") as cardsFile:
                cardsFile.write('{"cards":[]}')

        self.createFileIfNotExists(
            folderPath=self.cardsFolderPath, filePath=self.cardsFilePath, initFunction=initializeCards
        )

    @staticmethod
    def createFileIfNotExists(folderPath, filePath, initFunction):
        if not filePath.exists():
            try:
                initFunction()
            except FileNotFoundError:  # Directory does not exist
                os.mkdir(folderPath)
                initFunction()

    def getPlayers(self) -> list[playerObject]:
        with open(self.playersFilePath, "r") as file:
            return json.load(file)["players"]

    def getCards(self) -> list[cardObject]:
        with open(self.cardsFilePath, "r") as file:
            return json.load(file)["cards"]

    def getCardFromName(self, name: str) -> Card:
        for card in self.getCards():
            if card["name"] == name:
                return cardFromObject(card)

    def findPlayer(self, playerId: str | int) -> Player:
        for player in self.getPlayers():
            if player["id"] == playerId:
                decks = []
                for deck in player["decks"]:
                    decks.append(
                        Deck(name=deck["name"])
                    )
                    decks[-1].cards = [self.getCardFromName(c) for c in deck["cards"]]
                return userFromDictionary(player, decks)
        raise PlayerNotFound(f"The player could not be found! Id sent: {playerId}")

    def createNewPlayer(self, newPlayer: discord.Member) -> Player:
        newPlayer = Player(newPlayer, hand=[], decks=[])
        with open(self.playersFilePath, "r") as file:
            oldData = json.load(file)
        with open(self.playersFilePath, "w") as file:
            newPlayers = oldData["players"]
            newPlayers.append(newPlayer.objectify())
            newData = {"players": newPlayers}
            file.write(json.dumps(newData, indent=4))
        return newPlayer

    def savePlayer(self, player: Player):
        players = self.getPlayers()
        for i, p in enumerate(players):
            if p["id"] == player.id:
                players[i] = player.objectify()
        with open(self.playersFilePath, "w") as file:
            file.write(json.dumps({"players": players}, indent=4))

    def saveCards(self):
        with open(self.playersFilePath, "w") as file:
            file.write(json.dumps(self.cards, indent=4))

    @staticmethod
    def deleteAllData():
        shutil.rmtree("data")

    def restart(self):
        self.__init__(self.path)
