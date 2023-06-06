from Classes import *

def check_for_endgame(deck):
	endgame_begun = False
	if deck.exhausted:
		activate_base_cards()
		endgame_begun = True
	else:
		pass
	return endgame_begun
	
			
def activate_base_cards():
	for card in Card.instances:
		if card.location == 'base':
			card.location == 'field'
			

def update_active_player(current, one, two):
	if current == one:
		new = two
	elif current == two:
		new = one
	return ne
