import json
from random import shuffle
from utils.Exceptions import BadRequest, NoMoreCardsException

cardObject = {
    "image": str,
    "name": str,
    "props": dict
}

deckObject = {
    "name": str,
    "cards": list[cardObject]
}


class Card:
    def __init__(self, image: str, name: str, props: dict):
        self.image = image
        self.name = name
        self.props = props

    def toObject(self) -> cardObject:
        return {
            "image": self.image,
            "name": self.name,
            "props": self.props
        }

    def toJSONString(self) -> str:
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

    def toObject(self) -> deckObject:
        return {
            "name": self.name,
            "cards": [c.toObject() for c in self.cards]
        }

    def toJSONString(self) -> str:
        return json.dumps(self.toObject())


def cardFromObject(obj: cardObject):
    return Card(image=obj["image"], name=obj["name"], props=obj["props"])


def cardFromJSONString(s: str):
    return cardFromObject(json.loads(s))


def deckFromObject(obj: deckObject) -> Deck:
    newDeck = Deck(name=obj.name)
    newDeck.cards = [cardFromObject(c) for c in obj.cards]
    return newDeck
