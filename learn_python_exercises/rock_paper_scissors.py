#!/usr/bin/python3

import random

def compRPC():
	randMove = (random.randrange(1, 4, 1))
	if randMove == 1:
		computerMove = "Rock"
	elif randMove == 2:
		computerMove = "Paper"
	elif randMove == 3:
		computerMove = "Scissors"
	return(computerMove)

while True:
	humanMove = str(input("Rock, Paper, or Scissors? "))
	humanMove = humanMove.capitalize()
	computerMove = compRPC()
	
	if humanMove != "Rock" and humanMove != "Paper" and humanMove != "Scissors":
		print("Please enter a valid move")

	elif computerMove == "Rock" and humanMove == "Paper":
		print("You played " + humanMove + " and I played " + computerMove)
		print("You won!")
		playAgain = str(input("Would you like to play again?(Y/N) "))
		playAgain = playAgain.capitalize()
		if playAgain == "N":
			break

	elif computerMove == "Paper" and humanMove == "Scissors":
		print("You played " + humanMove + " and I played " + computerMove)
		print("You won!")
		playAgain = str(input("Would you like to play again?(Y/N) "))
		playAgain = playAgain.capitalize()
		if playAgain == "N":
			break

	elif computerMove == "Scissors" and humanMove == "Rock":
		print("You played " + humanMove + " and I played " + computerMove)
		print("You won!")
		playAgain = str(input("Would you like to play again?(Y/N) "))
		playAgain = playAgain.capitalize()
		if playAgain == "N":
			break

	elif computerMove == humanMove:
		print("You played " + humanMove + " and I played " + computerMove)
		print("It's a draw!")
		playAgain = str(input("Would you like to play again?(Y/N) "))
		playAgain = playAgain.capitalize()
		if playAgain == "N":
			break

	else:
		print("You played " + humanMove + " and I played " + computerMove)
		print("I Win!")
		playAgain = str(input("Would you like to play again?(Y/N) "))
		playAgain = playAgain.capitalize()
		if playAgain == "N":
			break

