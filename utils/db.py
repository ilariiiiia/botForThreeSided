from random import shuffle
import os
from pathlib import Path
import json
from typing import List

import discord


class NoMoreCardsException(Exception):
    """
    Error raised when there are no more cards in a player's deck's cards.
    """
    pass


class BadRequest(Exception):
    """
    Error raised with a bad request
    """
    pass


class PlayerNotFound(Exception):
    """
    Error raised when the player is not found
    """
    pass


class helperUser:
    def __init__(self, name, userID):
        self.name = name
        self.id = userID


class Card:
    def __init__(self, image, name: str, props: dict):
        self.image = image
        self.name = name
        self.properties = props


class Deck:
    def __init__(self, name):
        self.cards: list[Card] = []
        self.name = name

    def shuffle(self) -> None:
        shuffle(self.cards)

    def draw(self, num) -> list[Card]:
        try:
            num = int(num)
        except Exception as e:
            raise BadRequest
        if len(self.cards) > num:
            return self.cards[0:num]
        raise NoMoreCardsException("Attempted to draw cards from a deck with no cards")

    def removeCard(self, card: Card) -> None:
        self.cards.remove(card)


def userFromDictionary(arg: dict):
    return Player(user=helperUser(arg["username"], arg["id"]), cards=arg["cards"], decks=arg["decks"])


class Player:
    def __init__(self, user: discord.Member | helperUser, cards: list[Card], decks: list[Deck]):
        self.username = user.name
        self.id = user.id
        self.cards = cards if cards else []
        self.hand = []
        self.decks = decks if decks else []

    def objectify(self) -> dict:
        return {
            "username": self.username,
            "id": self.id,
            "cards": [card.__str__() for card in self.cards],
            "decks": [deck.__str__() for deck in self.decks]
        }

    def toJSONString(self):
        return json.dumps(self.objectify())

    def __repr__(self):
        return f"""
Player.
username = {self.username}
id = {self.id}
cards = {self.cards}
decks = {self.decks}
"""


class Database:
    def __init__(self, path: str):
        self.root = os.path.dirname(os.path.abspath(path))
        self.folderPath = Path(f"{self.root}/data")
        self.filePath = self.folderPath / "players.json"

        def rewriteDB():
            with open(self.filePath, "w") as file:
                file.write('{"players":[]}')

        if not self.filePath.exists():
            try:
                rewriteDB()
            except FileNotFoundError:  # Directory does not exist
                os.mkdir(self.folderPath)
                rewriteDB()

    def getPlayers(self) -> dict:
        with open(self.filePath, "r") as file:
            return json.load(file)["players"]

    def findPlayer(self, playerId: str | int) -> Player:
        for player in self.getPlayers():
            if player["id"] == playerId:
                return userFromDictionary(player)
        raise PlayerNotFound(f"The player could not be found! Id sent: {playerId}")

    def createNewPlayer(self, newPlayer: discord.Member) -> None:
        newPlayer = Player(newPlayer, cards=[], decks=[])
        with open(self.filePath, "r") as file:
            oldData = json.load(file)
        with open(self.filePath, "w") as file:
            newPlayers = oldData["players"]
            newPlayers.append(newPlayer.objectify())
            newData = {"players": newPlayers}
            file.write(json.dumps(newData, indent=4))
