import numpy as np

def get_lag_factors(series,p=4,min_difference=-np.inf):
	# p is the number of lags
	X = []
	y = []
	for index in range(p,len(series)):
		if np.abs(series[index] - series[index-1]) > min_difference:
			lag_features = list(series[index-p:index])
			X.append(series[index-p:index])
			y.append(series[index])
	return X,y

def get_data_and_labels(speech_list,min_difference=-np.inf):
	big_X = []; big_y = []
	for s in speech_list:
		preds_by_second = np.array(s.get_preds_by_second())
		X,y = get_lag_factors(preds_by_second,min_difference=min_difference)
		if len(big_X) == 0:
			big_X = X
			big_y = y
		else:
			big_X = np.vstack([big_X, X])
			big_y += y
	return big_X, big_y
