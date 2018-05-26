import numpy as np, math
from tqdm import tqdm
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
from sklearn.metrics import precision_recall_fscore_support
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
from sklearn import linear_model
from sklearn import cross_validation
from sklearn.grid_search import GridSearchCV


#### Logistic Regressions

def train_cv_logistic_regression(X,y,penalty='l2'):
	logreg=linear_model.LogisticRegression(penalty=penalty)
	clf = GridSearchCV(logreg, {'C':(0.001, .01, .1, 1, 3, 4, 5)}, cv=3)
	clf.fit(X, y)
	return clf

def train_cv_logistic_regression_faster(X,y,penalty='l2'):
	logreg=linear_model.LogisticRegression(penalty=penalty)
	clf = GridSearchCV(logreg, {'C':(0.01, 0.1, 3)}, cv=3)
	clf.fit(X, y)
	return clf

def train_logistic_regression(X,y,C=0.1,penalty='l2'):
	logreg=linear_model.LogisticRegression(penalty=penalty,C=C)
	#clf = GridSearchCV(logreg, {'C':(0.001, .1, 3)}, cv=3)
	clf = logreg
	clf.fit(X, y)
	return clf

def evaluate_model(model, X, y, model_type='sklearn',verbose=True):
	total_true = []; total_pred = []
	y_true = y
	if model_type == 'sklearn':
		y_pred = model.predict(X)
	else:
		y_pred = list(model.predict_classes(X).reshape((len(X,))))
	for i in range(len(y_true)):        
		total_true.append(y_true[i])
		total_pred.append(y_pred[i])

	total_correct = np.sum(np.array(total_true) == np.array(total_pred))
	acc=float(total_correct) / len(total_true)
	std=math.sqrt( (acc * (1-acc)) / len(total_true) )
	precision, recall, f1, support = [l[1] for l in precision_recall_fscore_support(y_true, y_pred)]
	#print "Accuracy: %.3f +/- %.3f (%s/%s)" % (acc, 1.96*std, total_correct, len(total_true))
	if verbose:
		print "Accuracy: %.3f +/- %.3f (%s/%s) | Precision: %.3f | Recall: %.3f | F1: %.3f" % (acc, 1.96*std, total_correct, len(total_true), precision, recall, f1)
	#return (acc, precision, recall, f1)
	return y_true, y_pred
	#return total_correct, len(y)


#### Neural Models

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
	model.add(Dropout(dropout,input_shape=(None, input_dim)))
	for i in range(len(layer_sizes)):
		return_sequences = False if i == len(layer_sizes) - 1 else True
		if bidirectional:
			model.add(Bidirectional(LSTM(layer_sizes[i], return_sequences=return_sequences, dropout=dropout),input_shape=(None, input_dim)))
		else:
			model.add(LSTM(layer_sizes[i],input_shape=(None,input_dim),return_sequences=return_sequences,dropout=dropout))
		if batch_norm: model.add(keras.layers.BatchNormalization())
		model.add(Activation("relu"))

	model.add(Dense(10))
	model.add(Activation("relu"))
	model.add(Dense(1))
	model.add(Activation('sigmoid'))
	optimizer = keras.optimizers.Adam()
	model.compile(optimizer=optimizer,loss=loss,metrics=metrics)
	return model

def initialize_conv_model(input_dim, layer_sizes, dropout = 0.5, loss = 'binary_crossentropy', metrics = ['accuracy'], batch_norm = True):
	model = Sequential()
	model.add(Dropout(dropout,input_shape=(3,input_dim)))
	for i in range(len(layer_sizes)):
		model.add(Conv1D(layer_sizes[i],3,padding='same',input_shape=(3, input_dim)))
		model.add(keras.layers.BatchNormalization())
		model.add(Activation('relu'))
		model.add(MaxPooling1D(pool_size=3))

	#model.add(Flatten())
	#model.add(Dense(50))
	#model.add(Dropout(dropout))
	model.add(LSTM(25,input_shape=(None,313),return_sequences=False,dropout=0.8))
	model.add(Dense(1))
	model.add(Activation('sigmoid'))
	optimizer = keras.optimizers.Adam()
	model.compile(optimizer=optimizer,loss=loss,metrics=metrics)
	return model

#def format_lstm_input(sequence_list,input_size,lstm_length=5):
#	formatted_list = []
#	formatted_labels = []
#	for i in tqdm(range(lstm_length-1,len(sequence_list))):
#		if len(formatted_list) == 0:
#			formatted_list = [sequence_list[i-lstm_length+1:i+1].reshape((1,lstm_length,input_size))]
#		else:
#			formatted_list.append(sequence_list[i-lstm_length+1:i+1].reshape((1,lstm_length,input_size)))

def format_lstm_input(sequence_list,labels,input_size,lstm_length=5):
	formatted_list = []
	formatted_labels = []
	for i, sequence in enumerate(sequence_list):
		for j in tqdm(range(lstm_length-1,len(sequence))):
			formatted_list.append(sequence[j-lstm_length+1:j+1].reshape(1,lstm_length,input_size))
			formatted_labels.append(labels[i][j])
	return formatted_list, formatted_labels
	#return np.vstack(formatted_list)

def format_multiple_phrase_input(sequence_list,labels,phrase_count=5):
	formatted_list = []
	formatted_labels = []
	for i, sequence in enumerate(sequence_list):
		for j in tqdm(range(phrase_count-1,len(sequence))):
			formatted_list.append(sequence[j-phrase_count+1:j+1].reshape(-1))
			formatted_labels.append(labels[i][j])
	return formatted_list, formatted_labels

def format_balanced_multiple_phrase_input(sequence_list,labels,phrase_count=5):
	formatted_list = []
	formatted_labels = []
	for i, sequence in enumerate(sequence_list):
		all_positive_indices = np.where(np.array(labels[i]) == 1)[0]
		all_positive_indices = [index for index in all_positive_indices if index >=phrase_count - 1]
		all_negative_indices = np.where(np.array(labels[i]) == 0)[0]
		all_negative_indices = [index for index in all_negative_indices if index >=phrase_count - 1]
		n_labels_to_use = min(len(all_positive_indices),len(all_negative_indices))
		if n_labels_to_use > 0:
			selected_positive_indices = sorted(np.random.choice(all_positive_indices,n_labels_to_use,replace=False))
			selected_negative_indices = sorted(np.random.choice(all_negative_indices,n_labels_to_use,replace=False))
			for j in range(n_labels_to_use):
				positive_index = selected_positive_indices[j]
				negative_index = selected_negative_indices[j]
				formatted_list.append(sequence[positive_index-phrase_count+1:positive_index+1].reshape(-1))
				formatted_labels.append(labels[i][positive_index])
				formatted_list.append(sequence[negative_index-phrase_count+1:negative_index+1].reshape(-1))
				formatted_labels.append(labels[i][negative_index])
		else:
			5
			#print "Empty..." + str(i)
	return formatted_list, formatted_labels

def format_balanced_multiple_phrase_input_with_deltas(sequence_list,labels,phrase_count=5):
	formatted_list = []
	formatted_labels = []
	for i, sequence in enumerate(sequence_list):
		all_positive_indices = np.where(np.array(labels[i]) == 1)[0]
		all_positive_indices = [index for index in all_positive_indices if index >=phrase_count - 1]
		all_negative_indices = np.where(np.array(labels[i]) == 0)[0]
		all_negative_indices = [index for index in all_negative_indices if index >=phrase_count - 1]
		n_labels_to_use = min(len(all_positive_indices),len(all_negative_indices))
		if n_labels_to_use > 0:
			selected_positive_indices = sorted(np.random.choice(all_positive_indices,n_labels_to_use,replace=False))
			selected_negative_indices = sorted(np.random.choice(all_negative_indices,n_labels_to_use,replace=False))
			for j in range(n_labels_to_use):
				positive_l = []
				negative_l = []
				positive_index = selected_positive_indices[j]
				negative_index = selected_negative_indices[j]
				for k in range(phrase_count):
					positive_l_initial = list(sequence[positive_index-k])
					positive_l_minus_1 = list(sequence[positive_index-k-1])
					positive_delta_1 = list(np.array(positive_l_minus_1) - np.array(positive_l_initial))
					positive_l += positive_l_initial; positive_l += positive_delta_1
					negative_l_initial = list(sequence[negative_index-k])
					negative_l_minus_1 = list(sequence[negative_index-k-1])
					negative_delta_1 = list(np.array(negative_l_minus_1) - np.array(negative_l_initial))
					negative_l += negative_l_initial; negative_l += negative_delta_1
				formatted_list.append(np.array(positive_l)); formatted_list.append(np.array(negative_l))
				formatted_labels.append(labels[i][positive_index]); formatted_labels.append(labels[i][negative_index])
		else:
			5
			#print "Empty..." + str(i)
	return formatted_list, formatted_labels

def format_multiple_phrase_input_with_deltas(sequence_list,labels,phrase_count=5):
	formatted_list = []
	formatted_labels = []
	for i, sequence in enumerate(sequence_list):
		for j in tqdm(range(phrase_count-1,len(sequence))):
			l = []
			for k in range(phrase_count):
				l_initial = list(sequence[j-k])
				l_minus_1 = list(sequence[j-k-1])
				delta_1 = list(np.array(l_minus_1) - np.array(l_initial))
				l += l_initial; l+= delta_1
			formatted_list.append(np.array(l))
			formatted_labels.append(labels[i][j])
	return formatted_list, formatted_labels

"""
def format_multiple_phrase_input_with_deltas(sequence_list,labels,phrase_count=5):
	formatted_list = []
	formatted_labels = []
	for i, sequence in enumerate(sequence_list):
		for j in tqdm(range(phrase_count-1,len(sequence))):
			l_initial = sequence[j]
			l_minus_1 = sequence[j-1]
			l_minus_2 = sequence[j-2]
			delta_1 = list(np.array(l_minus_1) - np.array(l_initial))
			delta_2 = list(np.array(l_minus_2) - np.array(l_minus_1))
			formatted_list.append(np.hstack([l_initial,l_minus_1,l_minus_2,delta_1,delta_2]))
			formatted_labels.append(labels[i][j])
	return formatted_list, formatted_labels
"""


def balance(X,y):
	X,y = shuffle(X,y)
	positive_indices = [i for i,lab in enumerate(y) if lab == 1]
	negative_indices = [i for i,lab in enumerate(y) if lab == 0]
	negative_indices = negative_indices[0:len(positive_indices)]
	X = [x for i,x in enumerate(X) if i in positive_indices or i in negative_indices]
	y = [x for i,x in enumerate(y) if i in positive_indices or i in negative_indices]
	return (X,y)
