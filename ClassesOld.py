class Player:

	This is a big test for GitHub to see if I can upload any changes.
	
	def __init__(self, index, name):
		self.hand = []
		self.index = index
		self.name = name
	
	def pick_up_card(self, deck):
		new_card = deck.pop()
		new_card.location = 'hand'
		self.hand.append(new_card)
		
	def show_hand(self):
		hand_values = []
		for i in self.hand:
			hand_values.append(i.value+i.suit)
		print(hand_values)
		
	def place_card(self, lane, card_index):
		card = self.hand.pop(card_index)
		lane.add_card(card, self)
		
	def flip_card(self, lane, card_index):
		try:
			card_to_flip = lane.container[self.index][card_index]
			
			card_to_flip.flip()
			
		except IndexError:
			print("There are not this many cards in the lane")
			raise IndexError
		except AssertionError:
			print("This card has already been flipped")
			raise PermissionError
		except PermissionError:
			print("This card cannot be flipped")
			raise PermissionError
		except:
			raise KeyError
	
	def attack(self, lane_index, friendly_card, enemy_card):
		killed_a_card = False
		friendly_card.cooldown=True
		if enemy_card.health > 0:
			enemy_card.health -= 1
		elif enemy_card.health == 0:
			enemy_card.destroy(lane_index)
			killed_a_card = True
		return killed_a_card
			
			
class Card:
	blank = 'X'
	card_instances = []
	
	def __init__(self, value, suit, location, lane=None, health=1, flipped=False, cooldown=False):
		self.value = value
		self.suit = suit
		self.location = location
		self.flipped = flipped
		self.health = health
		self.cooldown = cooldown
		self.lane = lane
		
		Card.card_instances.append(self)
		
	def flip(self):
		if not self.flipped and self.location != 'base':
			self.flipped = True
		elif self.flipped:
			raise AssertionError
		else: 
			raise PermissionError
		
	def destroy(self, lane_index):
		remove_all_instances(self, lane_index)
		
class Lane:
	def __init__(self, lane_number):
		self.number = lane_number
		self.container = [[],[]]
		
	def add_base_cards(self, deck):
		new_card = deck.pop()
		new_card_two = deck.pop()
		self.container[0].append(new_card)
		self.container[1].append(new_card_two)
		new_card.location = 'base'
		new_card.lane = self.number
		new_card_two.location = 'base'
		new_card_two.lane = self.number
		
	def add_card(self, card, active_player):
		card.location = 'field'
		card.lane = self.number
		self.container[active_player.index].append(card)
		
	def show(self):
		visual_container = [[],[]]
		for count, side in enumerate(self.container):
			for x in side:
				if x.flipped:
					visual_container[count].append(f'{x.value}{x.suit}{x.health}')
				
				else:
					visual_container[count].append(f'{x.blank}{x.health}')
						
		print(visual_container)
		
		
