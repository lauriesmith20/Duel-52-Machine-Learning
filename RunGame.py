from Classes import *
from GameClass import *
from Powers import *
from Exceptions import *
from Functions import *
from NNClass import *
from BackupNNFiles import *
import time
import matplotlib.pyplot as plt 
import os
root = os.path.dirname(os.path.abspath('RunGame.py'))

master_display = False
slow_pace = False
Powers.display = False

def run_game(num):
	
	neural_net_player_one = NeuralNet(f'{root}/W&B/v12_player_one_w&b.npz', original_epsilon=0.3, train_mode=True)
	
	neural_net_player_two = NeuralNet(f'{root}/W&B/v12_player_two_w&b.npz', original_epsilon=0.5, train_mode=True)
	
	player_one = Player(neural_net_player_one,'Player One', 0, display=master_display)
	player_two = Player(neural_net_player_two,'Player Two', 1, display=master_display)
	
	Lane.lanes = []
	lane_one = Lane(1)
	lane_two = Lane(2)
	lane_three = Lane(3)
	
	playing_deck = Deck()
	playing_deck.shuffle()
	playing_deck.cut(10)
	
	game = Game(player_one, player_two, Lane.lanes, playing_deck, display=master_display, starting=num)
	
	game.deal_base_cards()
	game.deal_hand()

	while not game.won:
		game.start_round()
		
		if not game.endgame:
			game.active_player.pick_up_card(game.deck)
			game.update_endgame_status()
	
		while game.actions_remaining > 0:
			try:
				
				game.store_all_traits()
				
				if game.active_player.nn.old:
					gamestate = game.old_define_current_gamestate()
				else:
					gamestate = game.define_current_gamestate()

				_,_,premove_score = game.active_player.nn.evaluate_gamestate(gamestate)

				moves = game.collect_possible_moves()

				chosen_move, postmove_score = game.pick_move(moves)
				
				game.active_player.nn.preloss_input = gamestate	
				game.active_player.nn.preloss_score = premove_score			

				gameover = game.execute_and_train(chosen_move, gamestate, premove_score, postmove_score)

				if slow_pace:
					time.sleep(1)
				
				if gameover:
					break

				
			except NoActionsAvailableError:
				print('No Further Actions Available')
				game.actions_remaining = 0
		
		game.end_round()
		
		if slow_pace:
			time.sleep(2)
		
	game.display_winner()
	
	for net in [neural_net_player_one, neural_net_player_two]:

		if net.train_mode:
		
			net.training_count += 1
			net.update_epsilon()
			net.save_nn()	
	return

xs = [0]
y_one = [0]
y_two = [0]
games = 8500
for i in range(games):
	print(f'Game {i+1}')
	try:
		run_game(i%2)
		xs.append(i+1)
		y_one.append(Game.player_one_win_count)
		y_two.append(Game.player_two_win_count)
	except KeyboardInterrupt:
		break
	except KeyboardInterrupt:
		print('ERROR '*20)
	

fig, ax = plt.subplots()
plt.ylim(0, len(xs)-1)
plt.plot(xs, y_one, figure=fig, label='P1')
plt.plot(xs, y_two, figure=fig, color='r', label='P2')
plt.legend()
plt.show()
print('\n',Game.player_one_win_count, Game.player_two_win_count)
plt.close()
