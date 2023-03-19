import json
from random import shuffle
from utils.Exceptions import BadRequest, NoMoreCardsException

cardObject = {
    "link": str,
    "name": str,
    "props": dict
}

deckObject = {
    "name": str,
    "cards": list[cardObject]
}


class Card:
    def __init__(self, link: str, name: str, props: dict):
        self.link = link
        self.name = name
        self.props = props

    def toObject(self) -> cardObject:
        return {
            "link": self.link,
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

    def toObject(self, name) -> deckObject:
        name = name if name else False
        if name:
            return {
                "name": self.name,
                "cards": [c.name for c in self.cards]
            }
        return {
            "name": self.name,
            "cards": [c.toObject() for c in self.cards]
        }

    def toJSONString(self) -> str:
        return json.dumps(self.toObject(name=False))


def cardFromObject(obj: cardObject):
    return Card(link=obj["link"], name=obj["name"], props=obj["props"])


def cardFromJSONString(s: str):
    return cardFromObject(json.loads(s))
