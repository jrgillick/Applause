from keras.models import Sequential
from keras.layers import Dense, Activation, Convolution2D, Conv1D, MaxPooling2D, MaxPooling1D, Flatten, Dropout
import keras.optimizers
from keras.models import load_model
import keras.regularizers
from keras.regularizers import l2, l1
from keras.layers import LSTM
from keras.layers import regularizers
from keras.layers import Bidirectional

from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
from sklearn import linear_model

def initialize_feed_forward_model(input_dim, layer_sizes, dropout = 0.5, loss = 'binary_crossentropy', metrics = ['accuracy'], batch_norm = True):
	model = Sequential()
	for i in range(len(layer_sizes)):
		model.add(Dense(layer_sizes[0], use_bias = True, input_dim=input_dim))		
		if batch_norm: model.add(keras.layers.BatchNormalization())
		model.add(Dropout(dropout))
		model.add(Activation("relu"))

	model.add(Dense(1))
	model.add(Activation('sigmoid'))
	optimizer = keras.optimizers.Adam()
	model.compile(optimizer=optimizer,loss=loss,metrics=metrics)
	return model  

def initialize_lstm_model(input_dim, layer_sizes, dropout = 0.5, loss = 'binary_crossentropy', metrics = ['accuracy'], batch_norm = True, bidirectional = False):
	model = Sequential()
	for i in range(len(layer_sizes)):
		return_sequences = False if i == len(layer_sizes) - 1 else True
		if bidirectional:
			model.add(Bidirectional(LSTM(layer_sizes[i], return_sequences=return_sequences, dropout=dropout),input_shape=(None, input_dim)))
		else:
			model.add(LSTM(layer_sizes[i],input_shape=(None,input_dim),return_sequences=return_sequences,dropout=dropout))
		model.add(Activation("relu"))

	model.add(Dense(1))
	model.add(Activation('sigmoid'))
	optimizer = keras.optimizers.Adam()
	model.compile(optimizer=optimizer,loss=loss,metrics=metrics)
	return model

def format_lstm_input(sequence_list,lstm_length=5):
	formatted_list = []
	for i in tqdm(range(lstm_length,len(sequence_list))):
		if len(formatted_list) == 0:
			formatted_list = [sequence_list[i-lstm_length:i].reshape((1,lstm_length,305))]
		else:
			formatted_list.append(sequence_list[i-lstm_length:i].reshape((1,lstm_length,305)))
	return np.vstack(formatted_list)
