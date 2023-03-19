import json
from random import shuffle
from utils.Exceptions import BadRequest, NoMoreCardsException


def cardFromObject(obj):
    return Card(image=obj["image"], name=obj["name"], props=obj["props"])


def cardFromJSONString(s: str):
    return cardFromObject(json.loads(s))


class Card:
    def __init__(self, image, name: str, props: dict):
        self.image = image
        self.name = name
        self.properties = props

    def toObject(self):
        return {
            "image": self.image,
            "name": self.name,
            "props": self.properties
        }

    def toJSONString(self):
        return json.dumps(self.toObject())


class Deck:
    def __init__(self, name):
        self.cards: list[Card] = []
        self.name = name

    def shuffle(self) -> None:
        shuffle(self.cards)

    def draw(self, num) -> list[Card]:
        try:
            num = int(num)
        except Exception:
            raise BadRequest
        if len(self.cards) > num:
            return self.cards[0:num]
        raise NoMoreCardsException("Attempted to draw cards from a deck with no cards")

    def removeCard(self, card: Card) -> None:
        self.cards.remove(card)
