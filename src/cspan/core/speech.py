import librosa, numpy as np, pickle, pandas as pd

class Speech:
	def __init__(self, file_path):
		alignment_root_dir = "/data/corpora/cspan/alignments/"
		transcript_root_dir = "/data/corpora/cspan/transcripts_clean/"
		audio_root_dir = "/data/corpora/cspan/audio/"
		applause_times_root_dir = "/data/corpora/cspan/applause_times/"
		self.alignment_file = alignment_root_dir + file_path + "/" + file_path.split('/')[1] + ".json"
		self.transcript_file = transcript_root_dir + file_path + ".txt"
		self.audio_file = audio_root_dir + file_path + ".mp3"
		self.applause_times_file = applause_times_root_dir + file_path + ".txt"
		self.load_stored_applause_predictions(file_path)
		
	def load_librosa(self):
		y,sr = librosa.load(self.audio_file)
		self.y = y; self.sr = sr

	def load_stored_applause_predictions(self, file_path):
		preds_path = '/data/corpora/cspan/applause_levels/' + file_path + '.txt'
		try:
			with open(preds_path) as f:
				self.preds = pickle.load(f)
		except IOError:
			print "Preds file not found"

	def get_number_of_seconds(self, frame_rate = 43.064598):
		return int(len(self.preds) / frame_rate)

	def get_preds_by_second(self, frame_rate = 43.064598):
		preds_by_second = []
		for i in range(self.get_number_of_seconds()):
			frames = int(i*frame_rate), int((i+1)*frame_rate)
			preds_by_second.append(np.mean(self.preds[frames[0]:frames[1]]))
		return preds_by_second

	def get_audio_region(self,instance):
		return(y[instance[0]:instance[1]])
