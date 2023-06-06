import random
from Exceptions import *

class Powers (object):
	endgame = False
	ace_flip = False
	display = False
	
	def __init__(self):
		pass
			
	def activate_two(player, deck):
		if not Powers.endgame and len(deck.container)>0:
			#player.show_hand()
			player.pick_up_card(deck)
			#player.show_hand()
			player.discard_from_hand()
			#player.show_hand()
			power_display('Picked up & discarded')
		else:
			pass
			
	def activate_three(card):
		card.health = 1
		card.flip()
			
	def activate_five(player, lane):
		for card in lane.container[player.index]:
			if not card.flipped and card.location != 'base':
				card.flip()
		
		message = f'Flipped all cards in Lane {lane.number}'
		power_display(message)
			
	def activate_six(player, lane):
		enemy_index = abs(player.index-1)
		for card in lane.container[enemy_index]:
			if card.value != '9':
				card.frozen = True
		power_display(f'Froze lane {lane.number}')
		
	def activate_seven(player, lanes):
		for lane in lanes:
			for card in lane.container[player.index]:
				card.heal()
		power_display('Healed all cards')
		
	def activate_eight(attacker, eight):
		if attacker.value != '9':
			attacker.attacked(eight, eight_retaliation = True)
			
	def activate_jack(jack):
		jack.health += 1
		
	def activate_queen(player, queen, lanes):
		moveable_cards = []
		for lane in lanes:
			if lane != queen.lane:
				for card in lane.container[player.index]:
					if card.location != 'base':
						moveable_cards.append(card)
					
		if len(moveable_cards) == 0:
			raise NoCardsForQueenToMoveError
			
		card_to_move = random.choice(moveable_cards)
		Powers.move_card_with_queen(player, queen, card_to_move)

	def move_card_with_queen(player, queen, card):
		card.lane.container[player.index].remove(card)
		queen.lane.container[player.index].append(card)

		card.lane = queen.lane
		

		if card.flipped:
			power_display(f'{card.value+card.suit} moved to Lane {queen.lane.number}')
			
		else:
			power_display(f'{card.hidden} moved to Lane {queen.lane.number}')					
			
	def activate_king(player, lane):
		for card in lane.container[player.index]:
			if card.value != 'K':
				card.activate_flip_power()
		
	def activate_ace(card):
		card.double_attack = True
		Powers.ace_flip = True
		power_display('Extra turn')
	
def power_display(string):
	if Powers.display:
		print(string)
