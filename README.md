# Discord bot for u/6ThreeSided9
***
A discord bot to play cards in your server.

Made with <3 by [me](https://github.com/ilariiiiia)

## Getting started

In order to use the bot, please run
```bat
git clone https://github.com/ilariiiiia/botForThreeSided.git
cd botForThreeSided
pip install -r requirements.txt
```
create a .env file and, inside it, put your API key like so:
```py
botToken="YOUR_TOKEN_GOES_HERE"
```
now, do `python main.py` to run the bot. Alternatively, use `python3 main.py` instead of `python main.py`.

### Commands
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