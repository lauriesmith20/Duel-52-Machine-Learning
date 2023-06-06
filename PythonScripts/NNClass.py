import numpy as np
import os
import random
from Exceptions import *

class NeuralNet (object):
	
	def __init__(self, filename, input_size=622, hidden_size=350, output_size=1, decay=0.9, learning_rate=0.05, original_epsilon=0.8, noisy_cutoff=21000, preloss_input=None, train_mode=True, noisy_choices=True, old=False):
		
		self.input_size = input_size
		self.filename = filename
		self.train_mode = train_mode
		self.original_epsilon = original_epsilon
		self.noisy_choices = noisy_choices
		self.noisy_cutoff = noisy_cutoff
		self.old = old
		
		self.decay = decay
		self.learning_rate = learning_rate
		
		if os.path.isfile(filename):
			print('loaded setup')
			self.load_nn()
		else:
			print('random setup')
			self.training_count = 0
			self.epsilon = original_epsilon
			self.random_initialisation(input_size, hidden_size, output_size)

		self.total_grad_w2 = np.zeros_like(self.w2)
		self.total_grad_b2 = np.zeros_like(self.b2)
		self.total_grad_w1 = np.zeros_like(self.w1)
		self.total_grad_b1 = np.zeros_like(self.b1)
	
	def forward(self, inputs):
		z1 = np.dot(inputs, self.w1) + self.b1
		a1 = np.maximum(0,z1)
		
		z2 = np.dot(a1, self.w2) + self.b2
		output = self.sigmoid(z2)
		
		return a1, z1, output
		
		
	def backward(self, inputs):
		
		a1, z1, output = self.forward(inputs)
		
		#Defining Partial Derivatives
		doutput_dz2 = self.d_sigmoid(output)
		dz2_dw2 = a1
		dz2_da1 = self.w2
		da1_dz1 = self.d_relu(z1)
		dz1_dw1 = inputs 
		
		#Calculating Grads
		grad_w2 = dz2_dw2.T * doutput_dz2
		
		grad_b2 = doutput_dz2		
		
		grad_w1 = np.outer(dz1_dw1,(da1_dz1.T * (dz2_da1 * doutput_dz2)))
		
		grad_b1 = da1_dz1 * (dz2_da1 * doutput_dz2).T
		
		#Applying Decay Parameter
		self.total_grad_w1 = self.decay * self.total_grad_w1
		self.total_grad_b1 = self.decay * self.total_grad_b1
		self.total_grad_w2 = self.decay * self.total_grad_w2
		self.total_grad_b2 = self.decay * self.total_grad_b2
		
		#Collecting Running Sum
		self.total_grad_w1 += grad_w1
		self.total_grad_b1 += grad_b1
		self.total_grad_w2 += grad_w2
		self.total_grad_b2 += grad_b2
		
		return 
		
	def train(self, prestate, prestate_score, poststate_score):
		
		if self.train_mode:
			self.backward(prestate)
			
			delta_scalar = self.learning_rate * (poststate_score - prestate_score)
			
			delta_w1 = delta_scalar * self.total_grad_w1
			delta_b1 = delta_scalar * self.total_grad_b1
			delta_w2 = delta_scalar * self.total_grad_w2
			delta_b2 = delta_scalar * self.total_grad_b2
			
			self.w1 += delta_w1
			self.b1 += delta_b1
			self.w2 += delta_w2
			self.b2 += delta_b2
			
		else:
			pass
		
	def update_epsilon(self):
		self.epsilon= self.original_epsilon* ((1+np.exp((10*self.training_count/self.noisy_cutoff)-5))**-1)
		
	def sigmoid(self, x):
		return 1/(1+np.exp(-x))
	
	def d_sigmoid(self, s):
		diff = s * (1-s)
		return diff
	
	def d_relu(self, x):
		return np.where(x>0, 1, 0)
		
	def evaluate_gamestate(self, input):
		input_2d = np.atleast_2d(input)
		output = self.forward(input_2d)
		return output
		
	def save_nn(self):
		np.savez(self.filename, w1=self.w1, w2=self.w2, b1=self.b1, b2=self.b2, training_count=self.training_count, epsilon=self.epsilon)
		
	def load_nn(self):
		with np.load(self.filename) as file:
			self.w1 = file['w1']
			self.w2 = file['w2']
			self.b1 = file['b1']
			self.b2 = file['b2']
			self.training_count = file['training_count']
			self.epsilon = file['epsilon']
	
	
	def random_initialisation(self, input_size, hidden_size, output_size):

		self.w1 = np.random.randn(input_size,hidden_size) * 0.05

		self.b1 = np.zeros((1, hidden_size))
		
		self.w2 = np.random.randn(hidden_size,output_size) * 0.08
		
		self.b2 = np.zeros((1, output_size))	
		
		
	def random_or_chosen(self):
		if self.noisy_choices:
			gate = np.random.random(1)
			if gate < self.epsilon:
				return True
		else:
			return False
			
		
	def choose_move(self, moves, scores):
		max_index = scores.argmax()
		max_move = moves[max_index]
		poststate_score = scores[max_index]
			
		return max_move, poststate_score
		
	def choose_random_move(self, moves):
		chosen_move = random.choice(moves)
		return chosen_move
		
	def old_choose_random_move(self, moves):
		new_moves=[]
		move_types = ['place_card','flip_card','flip_card','attack','attack','attack','attack']
		chosen = False
		
		while not chosen:
			chosen_move_type = random.choice(move_types)
			while chosen_move_type in move_types:
				move_types.remove(chosen_move_type)
				
			for move in moves:
				if move.function.__name__ == chosen_move_type:
					new_moves.append(move)
		
			if len(new_moves)>0:
				chosen_move = random.choice(new_moves)
				chosen=True

		return chosen_move
				

