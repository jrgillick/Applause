import sys, os, librosa, pickle

sys.path.insert(0, '../core')

import alignment, speech, applause_list, file_loader, text_features,re

import librosa, numpy as np
from tqdm import tqdm

all_files = file_loader.get_non_duplicate_file_endings()


if __name__ == '__main__':
	start_index = int(sys.argv[1])
	end_index = int(sys.argv[2])

	print "Loading speeches %d to %d" % (start_index, end_index)
	speeches = [speech.Speech(f) for f in tqdm(all_files[start_index:end_index])]
	print

	for i in tqdm(range(len(speeches))):
		print "Processing speech %d of %d" % (i, len(speeches))
		speech = speeches[i]
		crowd_audio_path = speech.get_crowd_audio_path()
		crowd_rmse_path = '/'.join(crowd_audio_path.split('/')[0:-1]).replace('audio_separated','crowd_rmse') + '.pkl'
		if not os.path.exists(crowd_rmse_path):
			print crowd_rmse_path
			crowd_y,sr = librosa.load(crowd_audio_path)
			with open(crowd_rmse_path,'wb') as f:
				pickle.dump(librosa.feature.rmse(crowd_y), f)
