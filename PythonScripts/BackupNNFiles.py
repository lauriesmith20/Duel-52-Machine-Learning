import numpy as np
import os

def backup_files(i):
	files = ['v11_player_one_w&b', 'v11_player_two_w&b']

	for file in files:
		with np.load('W&B/'+file+'.npz') as f:
			w1= f['w1']
			w2 = f['w2']
			b1 = f['b1']
			b2 = f['b2']
			training_count = f['training_count']
			epsilon = f['epsilon']
		
		np.savez(f'W&B/{i}g_'+file+'.npz', w1=w1, w2=w2, b1=b1, b2=b2, training_count=training_count, epsilon=epsilon)
		

