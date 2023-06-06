from Exceptions import *
from Powers import *
import random
import copy
	
class Player (object):
	
	def __init__(self, nn, name, index, display=True):
		self.name = name
		self.index = index 
		self.hand = []
		self.action_options = [self.place_card, self.flip_card, self.attack]
		self.lanes_won = 0
		self.display = display
		self.nn = nn
		
		self.traits = {}
		
	def set_traits(self):
		self.traits['hand'] = copy.copy(self.hand)
		self.traits['lanes_won'] = copy.copy(self.lanes_won)
		
	def restore(self):
		self.hand = copy.copy(self.traits['hand'])
		self.lanes_won = self.traits['lanes_won']
		
	def pick_up_card(self, deck):
		new_card = deck.container.pop()
		new_card.location = 'hand'
		new_card.player = self
		self.hand.append(new_card)
		
	def discard_from_hand(self):
		discard = random.choice(self.hand)
		discard.destroy()
	
	def place_card(self, lane, card, display=False):
		card_to_place = self.hand.pop(self.hand.index(card))
		lane.add_card(self, card_to_place)
		
		if display:
			print(f'Placed a card in Lane {lane.number}')
		
	def flip_card(self, lane, card, display=False):	
		if display:
			print(f'Flipped {card.value+card.suit} in Lane {lane.number}')
		card.flip()
		
	def attack(self, lane, attacking_card, enemy_card, enemy_card_two=None, display=False):
		
		vs = attacking_card.value + attacking_card.suit
		if enemy_card.flipped:	
			enemy_card_display=enemy_card.value+enemy_card.suit
		else:
			enemy_card_display= enemy_card.hidden
			
		
		if not enemy_card_two:
			result = enemy_card.attacked(attacking_card)
			
			if display:
				print(f'{vs} {result} {enemy_card_display} in Lane {lane.number}')
			else:
				pass
		
		else:
			result_one, result_two= attacking_card.ten_attack(enemy_card, enemy_card_two)
			
			if enemy_card_two.flipped:	
				enemy_card_two_display=enemy_card_two.value+enemy_card_two.suit
			else:
				enemy_card_two_display= enemy_card_two.hidden

			if display:
				print(f'{vs} {result_one} {enemy_card_display} AND {result_two} {enemy_card_two_display} in Lane {lane.number}')
				
	def find_flippable_cards(self, lane):
		flippable_list = []
		container = lane.container[self.index]
		for card in container:
			if not card.flipped and card.location != 'base' and not card.frozen:
				flippable_list.append(card)
				
		if len(flippable_list)==0:
			raise NoFlippableCards
		return flippable_list
					
	# Only for random selection
	def identify_fighting_cards(self, lane):
		enemy_index = abs(self.index-1)
		friendly_cards=[]
		enemy_cards=[]
		jack_cards=[]
		for card in lane.container[enemy_index]:
			if card.location != 'base':
				enemy_cards.append(card)
				if card.value == 'J':
					jack_cards.append(card)
					
		if len(jack_cards)>0:
			enemy_cards=jack_cards
					
		if len(enemy_cards)==0:
			raise NoAttackableCardsError
						
		for card in lane.container[self.index]:
			if card.flipped and not card.cooldown and not card.frozen:
				friendly_cards.append(card)
				
		if len(friendly_cards)==0:
			raise NoAttackingCardsError
				
		return friendly_cards, enemy_cards
		
		
	def identify_attacking_moves(self, lane, friendlies, enemies):
		attacking_moves = []
		
		for friendly in friendlies:
			
			if friendly.value=='10':
				ten_attacks = self.identify_ten_attacks(lane,friendly,enemies)
				attacking_moves.extend(ten_attacks)
				
			else:
				for enemy in enemies:
					move = Move(self.attack,lane,friendly,enemy)
					attacking_moves.append(move)
					
		return attacking_moves

					
	def identify_ten_attacks(self, lane, friendly, enemies):
		attacking_moves=[]
		combo_moves=False
		
		for i,enemy in enumerate(enemies):
			if enemy.flipped:
				if enemy.value in ['Q','K','A']:
					continue
				elif enemy.value == '9':
					move = Move(self.attack,lane,friendly,enemy)
					attacking_moves.append(move)
					continue
					
					
			for enemy_two in enemies[i+1:]:
				if enemy_two.value in ['Q','K','A','9'] and enemy_two.flipped:
					continue
							
				combo_moves=True
				move = Move(self.attack,lane,friendly,enemy,enemy_two)
				attacking_moves.append(move)
						
			if not combo_moves:
				move = Move(self.attack,lane,friendly,enemy)
				attacking_moves.append(move)
						
		return attacking_moves
		
		
	def show_hand(self):
		hand_values=[]
		for card in self.hand:
			hand_values.append(card.value+card.suit)
			
		print(hand_values)
				
		
	
class Card (object):
	
	hidden = 'X'
	instances = []
	
	def __init__(self, value, suit, health=1, location='deck'):
		self.value = value
		self.suit = suit
		self.health = health
		self.location = location
		self.flipped = False
		self.cooldown = False
		self.frozen = False
		self.lane = None
		self.player = None
		self.deck = None
		self.dead = False
		self.double_attack = False
		Card.instances.append(self)
		self.instance_index = Card.instances.index(self)
		
		self.traits = {'player':'empty'}
	
	def set_traits(self):
		self.traits['health'] = copy.copy(self.health)
		self.traits['location'] = copy.copy(self.location)
		self.traits['flipped'] = copy.copy(self.flipped)
		self.traits['cooldown'] = copy.copy(self.cooldown)
		self.traits['frozen'] = copy.copy(self.frozen)
		self.traits['lane'] = self.lane
		self.traits['dead'] = copy.copy(self.dead)
		self.traits['double_attack'] = copy.copy(self.double_attack)

	def restore(self):
		self.health = self.traits['health']
		self.location = self.traits['location']
		self.flipped = self.traits['flipped']
		self.cooldown = self.traits['cooldown']
		self.frozen = self.traits['frozen']
		self.lane = self.traits['lane']
		self.dead = self.traits['dead']
		self.double_attack = self.traits['double_attack']
		

	def flip(self):
		if self.location != 'base' and not self.flipped:
			self.flipped = True
			self.activate_flip_power()
		elif self.flipped:
			raise AlreadyFlippedError
		elif self.location == 'base':
			raise InactiveBaseError
			
	def heal(self):
		if self.value == 'J' and self.flipped:
			self.health = 2
		else:
			self.health = 1
	
			
	def attacked(self, attacking_card, eight_retaliation = False):
		
		if attacking_card.double_attack:
			attacking_card.double_attack = False
			
		else:
			attacking_card.cooldown = True
		
		if self.value == 'J' and attacking_card.value == '9':
			self.health -= 2
		else:
			self.health -= 1
		
		if self.health >= 0:
			result = 'Attacked'
			
		elif self.health < 0:
			if self.value == '3' and not self.flipped:
				result = 'Triggered'
				Powers.activate_three(self)
			else:
				self.destroy()
				result = 'Attacked & killed'
				
		if self.value == '8' and not eight_retaliation and self.flipped:
			Powers.activate_eight(attacking_card, self)
			result += ' & self-damaged'
			
		return result
		
	def ten_attack(self, enemy_one, enemy_two):
		result_one = enemy_one.attacked(self)
		result_two = enemy_two.attacked(self)
		
		return result_one, result_two

	def destroy(self):
		if self.player:
			if self.lane:
				self.dead = True
				container = self.lane.container[self.player.index]
				while self in container:
					container.remove(self)
			if self.location == 'hand':
				self.player.hand.remove(self)
		
	def activate_flip_power(self):
		if not self.flipped:
			return
			
		if self.value == '2':
			#print(self.deck.container)
			Powers.activate_two(self.player, self.deck)
			
		elif self.value == '5':
			Powers.activate_five(self.player, self.lane)
			
		elif self.value == '6':
			Powers.activate_six(self.player, self.lane)
			
		elif self.value == '7':
			Powers.activate_seven(self.player, Lane.lanes)
			
		elif self.value == 'J':
			Powers.activate_jack(self)
			
		elif self.value == 'Q':
			try:
				Powers.activate_queen(self.player, self, Lane.lanes)
			except NoCardsForQueenToMoveError:
				pass
				
		elif self.value == 'K':
			Powers.activate_king(self.player, self.lane)
			
		elif self.value == 'A':
			Powers.activate_ace(self)

class Lane (object):
	
	lanes = []
	
	def __init__(self, number, is_won=False, winner=None):
		self.number = number
		self.index = number - 1
		self.is_won = is_won
		self.winner = winner
		
		self.container = [[],[]]
		
		Lane.lanes.append(self)
		
		self.traits = {}
		
	def set_traits(self):
		self.traits['is_won'] = copy.copy(self.is_won)
		self.traits['winner'] = copy.copy(self.winner)
		self.traits['container'] = [copy.copy(self.container[0]), copy.copy(self.container[1])]
		
	def restore(self):
		self.is_won = self.traits['is_won']
		self.winner = self.traits['winner']
		self.container = [copy.copy(self.traits['container'][0]), copy.copy(self.traits['container'][1])]
		
	def add_base_cards(self, deck_object, player_one, player_two):
		deck = deck_object.container
		for i in range(2):
			card = deck.pop()
			self.container[i].append(card)
			card.lane = self
			card.location = 'base'
			if i == 0:
				card.player = player_one
			elif i == 1:
				card.player = player_two
			
	def add_card(self, player, card):
		self.container[player.index].append(card)
		card.location = 'field'
		card.lane = self
		
	def check(self, player_one, player_two):
		if len(self.container[0]) == 0:
			self.is_won = True
			self.winner = player_two
		elif len(self.container[1]) == 0:
			self.is_won = True
			self.winner = player_one
		else:
			pass
			
	def show(self):
		visual_container = [[],[]]
		for count, side in enumerate(self.container):
			for x in side:
				if x.flipped:
					visual_container[count].append(f'{x.value}{x.suit}{x.health}')
				
				else:
					visual_container[count].append(f'{x.hidden}{x.health}')
						
		print(visual_container)
	
	
class Deck (object):
	
	def __init__(self, exhausted=False):
		self.exhausted = exhausted
		self.container = []
		self.values = ['2','3','4','5','6','7','8','9','10','J','Q','K','A' ]
		self.suits = ['H','D','S','C']
		Card.instances = []
		
		self.traits = {}
		
	def set_traits(self):
		self.traits['exhausted'] = copy.copy(self.exhausted)
		self.traits['container'] = copy.copy(self.container)
		
		
	def restore(self):
		self.exhausted = self.traits['exhausted']
		self.container = copy.copy(self.traits['container'])
		
	def shuffle(self):
		for v in self.values:
			for s in self.suits:
				card = Card(v, s)
				self.container.append(card)
				card.deck = self
				
		random.shuffle(self.container)
		
	def cut(self, cut_number):
		for i in range(cut_number):
			card = self.container.pop()
			card.destroy()
			
	def show(self):
		print_list =[]
		for card in self.container:
			print_list.append(card.value+card.suit)
		print(print_list)
	

class Counter (object):
	
	def __init__(self):
		self.round = 0
		
	def show(self):
		print(f'Round {self.round}')
		
	def update(self, player):
		if player.index == 0:
			self.round += 1
		
			
		
class Move (object):
	
	def __init__(self, function, lane, friendly_card, enemy_card=None, enemy_card_two=None):
		self.function = function
		self.lane = lane
		self.friendly_card = friendly_card
		self.enemy_card = enemy_card
		self.enemy_card_two = enemy_card_two
		
	def run_move(self, display=False):
		if self.enemy_card:
			if self.enemy_card_two:
				self.function(self.lane, self.friendly_card, self.enemy_card, self.enemy_card_two, display=display)
			else:
				self.function(self.lane, self.friendly_card, self.enemy_card, display=display)
		else:
			self.function(self.lane, self.friendly_card, display)
	
		
class Gamestate (object):
	
	def __init__(self, status, numbers, hand, lanes, unknowns):
		self.status = status
		self.original_status = status
		self.numbers = numbers
		self.original_numbers = numbers
		self.hand = hand
		self.original_hand = hand
		self.lanes_array = lanes
		self.original_lanes_array = lanes
		self.unknowns = unknowns
		self.original_unknowns = unknowns
	
	def restore_state(self):
		self.status = self.original_status
		self.numbers = self.original_numbers
		self.hand = self.original_hand
		self.lanes_array = self.original_lanes_array
		self.unknowns = self.original_unknowns
	
	def place_card(self, lane, card):
	
		self.hand[card.instance_index] = 0
		self.numbers['active_hand'] -= 1
		
		self.lanes_array[lane.index, 51+len(self.unknowns[0, lane.index])] = [1,1,0]
		self.numbers[f'active_l{lane.number}'] +=1
		
	def flip_card(self, lane, card):
		self.lanes_array[lane.index,card.instance_index] = [1,card.health,1]
		self.unknowns[0, lane.index].remove(card)
		
	def attack_card(self, lane, attacker, enemy):
		pass
	
	def build_input(self):
		input = []
		status_keys = ['won','active_l_won','non_active_l_won','endgame']
		status_inputs=[]
		for item in status_keys:
			status_inputs.append(self.status[item])
		
		numbers_keys = ['deck','active_hand','non_active_hand','active_l1','non_active_l1','active_l2','non_active_l2','active_l3','non_active_l3']
		numbers_inputs=[]
		for item in numbers_keys:
			numbers_inputs.append(self.numbers[item])
		
		
		for j in range(self.unknowns.shape[1]):
			for number, card in enumerate(self.unknowns[0,j]):
				self.lanes_array[j,52+number]= [1,card.health,0]
			
			for number, card in enumerate(self.unknowns[1,j]):
				self.lanes_array[j,62+number]= [-1,-card.health,0]			
					
		flattened_lanes = self.lanes_array.flatten()
		print(self.lanes_array)
		
		input.extend(status_inputs)
		input.extend(numbers_inputs)
		input.extend(self.hand)
		input.extend(flattened_lanes)
		

		
		
		
	
		
		
