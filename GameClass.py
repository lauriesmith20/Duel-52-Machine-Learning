from Classes import *
from Powers import *
from NNClass import *
import numpy as np
import copy
import time

class Game (object):
	player_one_win_count = 0
	player_two_win_count = 0
	
	def __init__(self, player_one, player_two, lanes, deck, round=0, won=False, endgame=False, actions_remaining=2, starting_hand=5, display=True, starting=0):

		self.player_one = player_one
		self.player_two = player_two
		
		if starting == 0:
			self.starting_player = self.player_one
			self.non_active_player = self.player_two
			
		elif starting == 1:
			self.starting_player = self.player_two
			self.non_active_player = self.player_one
		
		self.active_player = self.starting_player

		self.round = round
		self.won = won
		self.endgame = endgame
		self.actions_remaining = actions_remaining
		self.lanes = lanes
		self.deck = deck
		self.starting_hand = starting_hand
		self.winner = None
		self.display = display
		
		self.traits = {}
		
		
	def set_traits(self):
		self.traits['won'] = copy.copy(self.won)
		self.traits['endgame'] = copy.copy(self.endgame)
		self.traits['actions_remaining'] = copy.copy(self.actions_remaining)
		self.traits['winner'] = copy.copy(self.winner)
		
		
	def store_all_traits(self):
		self.set_traits()
		self.player_one.set_traits()
		self.player_two.set_traits()
		self.deck.set_traits()
		for lane in self.lanes:
			lane.set_traits()
		for card in Card.instances:
			card.set_traits()

	
	def restore(self):
		self.won = self.traits['won']
		self.endgame = self.traits['endgame']
		self.actions_remaining = self.traits['actions_remaining']
		self.winner = self.traits['winner']
		
		
	def restore_all(self):
		self.restore()
		self.player_one.restore()
		self.player_two.restore()
		self.deck.restore()
		for lane in self.lanes:
			lane.restore()
		for card in Card.instances:
			card.restore()


	def deal_base_cards(self):
		for lane in self.lanes:
			lane.add_base_cards(self.deck, self.player_one, self.player_two)
			
			
	def deal_hand(self):
		for i in range(self.starting_hand):
			self.player_one.pick_up_card(self.deck)
			self.player_two.pick_up_card(self.deck)
	
	
	def start_round(self):
		self.update_counter()
		self.display_round()
		self.reset_cooldowns()
		self.update_endgame_status()
		
		
	def update_endgame_status(self):
		if len(self.deck.container)==0:
			self.endgame = True
			Powers.endgame = True
			self.activate_base_cards()
			
			
	def monitor_flips(self):
		if Powers.ace_flip:
			self.actions_remaining += 1
			Powers.ace_flip = False
			
			
	def monitor_lanes(self):
		for lane in self.lanes:
			if not lane.is_won:
				self.award_lane(lane)
			
		if self.player_one.lanes_won == 2:
			self.won = True
			self.winner = self.player_one
			
		elif self.player_two.lanes_won == 2:
			self.won = True
			self.winner = self.player_two
		

	def award_lane(self, lane):
		if len(lane.container[self.player_one.index])==0:
			lane.is_won = True
			lane.winner = self.player_two
			self.player_two.lanes_won += 1
					
		elif len(lane.container[self.player_two.index])==0:
			lane.is_won = True
			lane.winner = self.player_one		
			self.player_one.lanes_won += 1		
			
	def activate_base_cards(self):
		for card in Card.instances:
			if card.location == 'base':
				card.location = 'field'
		
	def end_round(self):
		self.display_board()
		self.unfreeze_cards()
		self.update_active_player()
		self.actions_remaining = 3
	
	def unfreeze_cards(self):
		for lane in self.lanes:
			for card in lane.container[self.active_player.index]:
				card.frozen = False
		
	def update_active_player(self):
		if self.active_player == self.player_one:
			self.active_player = self.player_two
			self.non_active_player = self.player_one
			
		elif self.active_player == self.player_two:
			self.active_player = self.player_one
			self.non_active_player = self.player_two

			
	def update_counter(self):
		if self.active_player == self.starting_player:
			self.round += 1
			
	def display_round(self):
		if self.display:
			print(f'Round {self.round}: {self.active_player.name}')
			print('-'*15)
		
	def reset_cooldowns(self):
		for card in Card.instances:
			if card.cooldown:
				card.cooldown = False
			if card.double_attack:
				card.double_attack = False
		
	def display_board(self):
		if self.display:
			for lane in self.lanes:
				lane.show()
			print('-'*20)
			
	def collect_possible_moves(self):
		possible_moves = []
		p = self.active_player
		hand = p.hand
		for lane in self.lanes:
			
			for card in hand:
				if not lane.is_won:
					move = Move(p.place_card, lane, card)
					possible_moves.append(move)
		
			try:
				flips = p.find_flippable_cards(lane)
				for card in flips:
					move = Move(p.flip_card, lane, card)
					possible_moves.append(move)
			except NoFlippableCards:
				pass
			
			try:		
				friendlies, enemies = p.identify_fighting_cards(lane)
				attacking_moves= p.identify_attacking_moves(lane,friendlies,enemies)
				
				possible_moves.extend(attacking_moves)

			except (NoAttackingCardsError, NoAttackableCardsError):
				pass 
				
		if len(possible_moves) == 0:
			raise NoActionsAvailableError
			
		return possible_moves
	
	
	def pick_move(self, moves):
		
		random = self.active_player.nn.random_or_chosen()
		
		if random:
			move = self.active_player.nn.choose_random_move(moves)
			score = self.test_single_move(move)
			return move, score
			
		else:
			scores = np.empty((len(moves)))
		
			for i, move in enumerate(moves):
				score = self.test_single_move(move)
				if score==1:
					return move, score
				else:
					scores[i] = score
			
			max_move, poststate_score = self.active_player.nn.choose_move(moves, scores)
		
		return max_move, poststate_score
		
	def test_single_move(self, move):
		move.run_move()
		self.monitor_flips()
		self.monitor_lanes()
		
		if self.won and self.winner==self.active_player:
			score = 1
			self.restore_all()
			return score
			
		if self.active_player.nn.old:
			gamestate = self.old_define_current_gamestate()
		else:
			gamestate = self.define_current_gamestate()
			
		_,_,score = self.active_player.nn.evaluate_gamestate(gamestate)

		score = score[0,0]
		
		self.restore_all()	
		
		return score	
			
		
	def execute_and_train(self, best_move, prestate, prestate_score, poststate_score):
		
		Powers.display = self.display
		best_move.run_move(display=self.display)
		Powers.display = False
		self.monitor_flips()
		self.actions_remaining -= 1
		if self.endgame:
			self.monitor_lanes()
			
		
		if not self.won:
			self.active_player.nn.train(prestate, prestate_score, poststate_score)

			return False
		
		else:

			if self.winner==self.active_player:
				self.active_player.nn.train(prestate,prestate_score,poststate_score)
				
				self.non_active_player.nn.train(self.non_active_player.nn.preloss_input, self.non_active_player.nn.preloss_score, -1)
				
			else:
				self.active_player.nn.train(prestate,prestate_score,-5)
				
			return True
				
		
	def display_winner(self):
		if self.winner.name == 'Player One':
			Game.player_one_win_count += 1
		else:
			Game.player_two_win_count += 1
		print(f'{self.winner.name} wins!!!!\n')
		
		
	def old_define_current_gamestate(self):
		
		status = [self.active_player.lanes_won, self.non_active_player.lanes_won,
		int(self.endgame)]
		
		numbers = [
		len(self.deck.container), len(self.active_player.hand),
		len(self.non_active_player.hand),
		len(self.lanes[0].container[0]),
		len(self.lanes[0].container[1]),		
		len(self.lanes[1].container[0]),
		len(self.lanes[1].container[1]),
		len(self.lanes[2].container[0]),
		len(self.lanes[2].container[1]),
		]
		
		cards_in_hand = np.zeros((52), dtype=int)
		for hand_card in self.active_player.hand:
			cards_in_hand[hand_card.instance_index] = 1
		
		lane_input = np.zeros((3,72,3), dtype=int)
		unknowns = np.zeros((2,3), dtype=int)
		
		for index, card in enumerate(Card.instances):

			if card.lane and not card.dead:
			
				if card.player == self.active_player:
					side = 1
				else:
					side = -1
								
				lane_index = card.lane.index

				if card.flipped:
					lane_input[lane_index, index]= [side,side*card.health,side*int(card.flipped)]
					
				else:
					if card.player == self.active_player:
						unknowns[0, lane_index] += 1
						lane_input[lane_index, 51+unknowns[0, lane_index]] = [side,card.health,0]
									
					else:
						unknowns[1, lane_index] += 1
						lane_input[lane_index, 61+unknowns[1, lane_index]] = [side,side*card.health,0]
		
		flattened_lanes = lane_input.flatten()

		gamestate = []
		gamestate.extend(status)
		gamestate.extend(numbers)
		gamestate.extend(cards_in_hand)
		gamestate.extend(flattened_lanes)
		
		gamestate = np.array(gamestate)
		
		return gamestate
		
	
	def define_current_gamestate(self):
		
		status = [self.active_player.lanes_won, self.non_active_player.lanes_won,
		int(self.endgame)]
		
		cards_in_hand = np.zeros((52), dtype=int)
		for hand_card in self.active_player.hand:
			cards_in_hand[hand_card.instance_index] = 1
		
		lane_input = np.zeros((3,63,3), dtype=int)
		unknowns = np.zeros((3), dtype=int)
		
		for index, card in enumerate(Card.instances):

			if card.lane and not card.dead:
			
				if card.player == self.active_player:
					side = 1
				else:
					side = -1
								
				lane_index = card.lane.index

				if card.flipped:
					lane_input[lane_index, index]= [side,side*card.health,side*int(card.flipped)]
					
				else:
					if card.player == self.active_player:
						if card.location != 'base':
							lane_input[lane_index, index] = [side,card.health,0]
						else:
							lane_input[lane_index, 52]=[1,card.health,0]
									
					else:
						unknowns[lane_index] += 1
						lane_input[lane_index, 52+unknowns[lane_index]]= [side,side*card.health,0]
		
		flattened_lanes = lane_input.flatten()

		gamestate = []
		gamestate.extend(status)
		gamestate.extend(cards_in_hand)
		gamestate.extend(flattened_lanes)
		
		gamestate = np.array(gamestate)
		
		return gamestate
