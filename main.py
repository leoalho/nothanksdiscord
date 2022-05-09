import discord
from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle
import random

client = commands.Bot(command_prefix="!") #Defines the prefix for the bot commands
DiscordComponents(client)

client = commands.Bot(command_prefix="!")
DiscordComponents(client)

ADMIN = "Lepanderus"
players = []
current_player = 0
tokens_on_card = 0
deck = random.sample(range(3, 36), 30)
playing = False


async def printGameState():
    global players
    global current_player
    global tokens_on_card
    global deck
    global playing
    global channel

    if len(deck) == 0:
        await gameEnded()
        return
    elif players[current_player].tokens == 0:
        await channel.send("It is " + str(players[
                                          current_player].name.display_name) + "'s turn. He/she has not got any "
                                                                               "tokens left, so he/she takes the card")
        players[current_player].add_card(deck.pop(0))
        players[current_player].tokens += tokens_on_card
        tokens_on_card = 0

    await channel.send(
        f"\n{len(deck):2} card(s) remaining. Current card: {deck[0]:2}. It has {tokens_on_card:2} token(s) on it.")
    for player in players:
        kortit = ""
        if len(player.cards) == 0:
            kortit = kortit + "None "
        else:
            player.cards.sort()
            for card in player.cards:
                kortit = kortit + str(card) + ", "
        await channel.send(player.name.display_name + ": Number of tokens: " + str(
            player.tokens) + ", cards owned: " + kortit + "Points: " + str(player.score_cards()))
    await channel.send("It is " + str(players[current_player].name.display_name) + "'s turn. Choose your action")
    await channel.send(
        components=[[
            Button(label="PASS", custom_id="button1", style=ButtonStyle.blue),
            Button(label="TAKE", custom_id="button2", style=ButtonStyle.green)
        ]]
        )


async def gameEnded():
    global players
    global current_player
    global tokens_on_card
    global deck
    global playing
    global channel

    await channel.send("All cards have been taken. The game ended")
    await channel.send("The results:")
    scores = {}
    for player in players:
        scores[player.name.display_name] = player.score_total()

    sort_scores = sorted(scores.items(), key=lambda x: x[1])
    for key, value in sort_scores:
        await channel.send(f"{key:10}: {value}")
    await channel.send("You can start a new game with the '!nothanks' command")
    players = []
    current_player = 0
    tokens_on_card = 0
    deck = random.sample(range(3, 36), 26)
    playing = False


@client.event
async def on_button_click(interaction):
    global playing
    global players
    global current_player
    global tokens_on_card
    global deck
    if interaction.user == players[current_player].name:
        if interaction.custom_id == "button1":
            await interaction.respond(content=interaction.user.display_name + " passes and places a token", ephemeral=False)
            players[current_player].tokens -= 1
            tokens_on_card += 1
            current_player = (current_player + 1) % len(players)

        if interaction.custom_id == "button2":
            await interaction.respond(content=interaction.user.display_name + " takes the card", ephemeral=False)
            players[current_player].add_card(deck.pop(0))
            players[current_player].tokens += tokens_on_card
            tokens_on_card = 0
        await printGameState()

    else:
        await interaction.respond(content=interaction.user.display_name + ", it is not your turn!", ephemeral=False)


@client.command()
async def nothanks(ctx, *args: discord.Member):
    global playing
    global players
    global current_player
    global channel
    channel = ctx.channel
    if playing:
        await ctx.send("A game is already going on, please finish it before starting a new one!")
    else:
        playing = True
        players = []
        for a in args:
            players.append(Player(a))
        random.shuffle(players)
        await ctx.send("Welcome to play a game of nothanks")
        await printGameState()


@client.command()
async def STOP(ctx):
    global playing
    if ctx.author.display_name == ADMIN:
        await gameEnded()


class Player:
    name: discord.Member
    tokens: int
    cards: list

    def __init__(self, name: discord.Member) -> None:
        self.name = name
        self.cards = []
        self.tokens = 11

    def reset(self, tokens: int) -> None:
        self.tokens = tokens
        self.cards = []

    def score_cards(self) -> int:
        summa = 0
        reversecards = self.cards.copy()
        if len(reversecards) == 0:
            return summa

        reversecards.sort()
        reversecards.reverse()

        for n in range(len(reversecards) - 1):
            if reversecards[n] != reversecards[n + 1] + 1:
                summa = summa + reversecards[n]
        summa = summa + reversecards[-1]

        return summa

    def add_card(self, card: int) -> None:
        self.cards.append(card)
        self.cards.sort()

    def score_total(self) -> int:
        return self.score_cards() - self.tokens


client.run("") #Your key here
