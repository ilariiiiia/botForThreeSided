import os
import shutil
from pathlib import Path
import json
from utils.Deck import Deck, Card, cardFromObject, cardObject, deckObject
from utils.Exceptions import BadRequest

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
        decks=decks,
        activeDeck=arg["activeDeck"]
    )


class Player:
    def __init__(self, user: discord.Member | helperUser, hand: list[str], decks: list[Deck], activeDeck: str|None):
        self.username = user.name
        self.id = user.id
        self.hand = hand if hand else []
        self.decks = decks if decks else []
        self.activeDeck = activeDeck if activeDeck else None

    @property
    def __dict__(self):
        return {
            "username": self.username,
            "id": self.id,
            "hand": self.hand,
            "decks": [deck.__dict__ for deck in self.decks],
            "activeDeck": self.activeDeck
        }

    def toJSONString(self):
        return json.dumps(self.__dict__)

    def __repr__(self):
        return f"""Player;username={self.username},id={self.id},hand={self.hand},decks={self.decks}"""

    def draw(self, n: int):
        if self.activeDeck is None:
            raise BadRequest("Active deck not chosen!")
        if n > len(self.activeDeck):
            raise BadRequest("Active deck has too little cards!")
        activeDeckIndex = -1
        for i, deck in enumerate(self.decks):
            if deck.name == self.activeDeck:
                activeDeckIndex = i
        if n > len(self.decks[activeDeckIndex].cards):
            raise BadRequest("Active deck has too little cards!")
        self.hand.extend(self.decks[activeDeckIndex].cards[0:n])
        self.decks[activeDeckIndex].cards = self.decks[activeDeckIndex].cards[n::]
        return self


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

    def isValidCardName(self, name: str) -> bool:
        return name in [c["name"] for c in self.cards]

    def findPlayer(self, playerId: str | int) -> Player:
        for player in self.getPlayers():
            if player["id"] == playerId:
                decks = []
                for deck in player["decks"]:
                    decks.append(
                        Deck(name=deck["name"])
                    )
                    decks[-1].cards = deck["cards"]
                return userFromDictionary(player, decks)
        raise PlayerNotFound(f"The player could not be found! Id sent: {playerId}")

    def findPlayerFromName(self, playerName: str) -> Player:
        for player in self.getPlayers():
            if player["userName"] == playerName:
                decks = []
                for deck in player["decks"]:
                    decks.append(
                        Deck(name=deck["name"])
                    )
                    decks[-1].cards = deck["cards"]
                return userFromDictionary(player, decks)
        raise PlayerNotFound(f"The player could not be found! Name sent: {playerName}")

    def createNewPlayer(self, newPlayer: discord.Member) -> Player:
        newPlayer = Player(newPlayer, hand=[], decks=[], activeDeck=None)
        with open(self.playersFilePath, "r") as file:
            oldData = json.load(file)
        with open(self.playersFilePath, "w") as file:
            newPlayers = oldData["players"]
            newPlayers.append(newPlayer.__dict__)
            newData = {"players": newPlayers}
            file.write(json.dumps(newData, indent=4))
        return newPlayer

    def savePlayer(self, player: Player):
        players = self.getPlayers()
        for i, p in enumerate(players):
            if p["id"] == player.id:
                players[i] = player.__dict__
        with open(self.playersFilePath, "w") as file:
            file.write(json.dumps({"players": players}, indent=4))

    def saveCards(self):
        with open(self.cardsFilePath, "w") as file:
            file.write(json.dumps({"cards": self.cards}, indent=4))

    @staticmethod
    def deleteAllData():
        shutil.rmtree("data")

    def restart(self):
        self.__init__(self.path)
