__version__ = "0.1.0"

import random
import sys


def move_msg(Move):
    if Move == "r":
        Msg = "ROCK"
    elif Move == "p":
        Msg = "PAPER"
    elif Move == "s":
        Msg = "SCISSORS"
    return Msg


print("ROCK, PAPER, SCISSORS")

# Init variables to keep track of the number of wins, losses, and ties.
wins = 0
losses = 0
ties = 0

# Main game loop
while True:
    print("%s Wins, %s Losses, %s Ties" % (wins, losses, ties))

    # Player plays
    while True:
        print("Enter your move: (r)ock (p)aper (s)cissors or (q)uit")
        playerMove = input()
        if playerMove == "q":
            print("Bye!")
            sys.exit()  # Quit the program.
        if playerMove in ["r", "p", "s"]:
            break  # Break out of the player input loop.
        print("Type one of r, p, s, or q.")

    # Computer plays
    computerMoves = ["r", "p", "s"]
    computerMove = computerMoves[random.randint(0, 2)]

    print(move_msg(playerMove) + " versus... " + move_msg(computerMove))

    # Display and record the win/loss/tie:
    if playerMove == computerMove:
        print("It is a tie!")
        ties = ties + 1
    elif playerMove == "r" and computerMove == "s":
        print("You win!")
        wins = wins + 1
    elif playerMove == "p" and computerMove == "r":
        print("You win!")
        wins = wins + 1
    elif playerMove == "s" and computerMove == "p":
        print("You win!")
        wins = wins + 1
    elif playerMove == "r" and computerMove == "p":
        print("You lose!")
        losses = losses + 1
    elif playerMove == "p" and computerMove == "s":
        print("You lose!")
        losses = losses + 1
    elif playerMove == "s" and computerMove == "r":
        print("You lose!")
        losses = losses + 1
