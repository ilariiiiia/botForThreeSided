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

    def toJSONString(self) -> str:
        return json.dumps(self.__dict__)


class Deck:
    def __init__(self, name):
        self.cards: list[str] = []
        self.name = name

    def shuffle(self) -> None:
        shuffle(self.cards)

    def draw(self, num) -> list[str]:
        try:
            num = int(num)
        except Exception:
            raise BadRequest
        if len(self.cards) > num:
            return self.cards[0:num]
        raise NoMoreCardsException("Attempted to draw cards from a deck with no cards")

    def removeCard(self, card: str | Card) -> None:
        if type(card) == Card:
            card = card.name
        self.cards.remove(card)

    def toJSONString(self) -> str:
        return json.dumps(self.__dict__)


def cardFromObject(obj: cardObject):
    return Card(link=obj["link"], name=obj["name"], props=obj["props"])


def cardFromJSONString(s: str):
    return cardFromObject(json.loads(s))
