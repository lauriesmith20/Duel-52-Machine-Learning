import numpy as np
import random
import time
from Classes import *
from Functions import *

deck_values = ['2','3','4','5','6','7','8','9','10','J','Q','K','A' ]
deck_suits = ['H','D','S','C']
starting_hand_count = 5
number_of_lanes = 3
turns_per_go = 3
pile_exhausted = False
actions = {0:'placed a card', 1:'flipped a card',2:'attacked a card', 3:'attacked and killed a card'}

deck = create_deck(deck_values, deck_suits)

playing_deck = deck[10:]

player_one = Player(0, 'Player One')
player_two = Player(1, 'Player Two')
active_player = player_one
	
lane_one = Lane(1)
lane_two = Lane(2)
lane_three = Lane(3)
lanes = [lane_one, lane_two, lane_three]

#Start The Game

deal_base_cards(lanes, playing_deck)

for i in range(starting_hand_count):
	player_one.pick_up_card(playing_deck)
	player_two.pick_up_card(playing_deck)

turn_counter = 0
winner_declared = False

while not winner_declared:
	
	turn_counter = display_counter(active_player, turn_counter)
	reset_cooldowns()
	#time.sleep(1)
	
	if not pile_exhausted:
		active_player.pick_up_card(playing_deck)
		if len(playing_deck) == 0:
			pile_exhausted = True
			activate_base_cards()
	
	turns_remaining = turns_per_go
	if turn_counter == 1 and active_player==player_one:
		turns_remaining -= 1
	
	while turns_remaining > 0:
		try:
			take_turn(lanes)
			turns_remaining -= 1
			
		except PermissionError:
			print('No possible moves')
			turns_remaining=0
			
		show_board()
		#time.sleep(0.7)
	
	active_player = change_active_player()
	
	
	if turn_counter == 500:
		winner_declared=True
	

