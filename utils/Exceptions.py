class BadRequest(Exception):
    """
    Error raised with a bad request
    """
    pass


class NoMoreCardsException(Exception):
    """
    Error raised when there are no more cards in a player's deck's cards.
    """
    pass
