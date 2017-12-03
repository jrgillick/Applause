import librosa, numpy as np, pickle, pandas as pd, file_loader
import alignment, applause_list

class Speech:
	def __init__(self, file_path):
		file_path = file_loader.format_file_path_for_speech_object(file_path)
		alignment_root_dir = "/data/corpora/cspan/alignments/"
		transcript_root_dir = "/data/corpora/cspan/transcripts_clean/"
		audio_root_dir = "/data/corpora/cspan/audio/"
		applause_times_root_dir = "/data/corpora/cspan/applause_times/"
		self.file_path = file_path
		self.alignment_file = alignment_root_dir + file_path + "/" + file_path.split('/')[1] + "_single_speaker.json"
		self.transcript_file = transcript_root_dir + file_path + ".txt"
		self.audio_file = audio_root_dir + file_path + ".mp3"
		self.applause_times_file = applause_times_root_dir + file_path + ".txt"
		self.load_stored_applause_predictions(file_path)
		#self.load_stored_crowd_rmse()
		self.alignment = alignment.Alignment(self.alignment_file)
		self.alignment.speech = self
		self.applause_preds_by_second = self.get_preds_by_second()
		self.applause_list = applause_list.ApplauseList(self.applause_times_file)

		self.frame_rate = 43.06640625
		self.hop_size = 512
		self.sr = 22050
		
	def load_librosa(self):
		y,sr = librosa.load(self.audio_file)
		self.y = y; self.sr = sr

	def load_librosa_voice(self):
		voice_y,voice_sr = librosa.load(self.get_voice_audio_path())
		self.voice_y = voice_y

	def load_librosa_crowd(self):
		crowd_y,crowd_sr = librosa.load(self.get_crowd_audio_path())
		self.crowd_y = crowd_y

	def get_voice_audio_path(self):
		return '/data/corpora/cspan/audio_separated/' + self.file_path + '/' + self.file_path.split('/')[1] + '-voice.mp3'

	def get_crowd_audio_path(self):
		return '/data/corpora/cspan/audio_separated/' + self.file_path + '/' + self.file_path.split('/')[1] + '-music.mp3'

	def load_stored_applause_predictions(self, file_path):
		preds_path = '/data/corpora/cspan/applause_levels/' + file_path + '.txt'
		try:
			with open(preds_path) as f:
				self.preds = pickle.load(f)
		except IOError:
			print "Preds file not found for %s" % (file_path)

	def load_stored_crowd_rmse(self):
		path = '/data/corpora/cspan/crowd_rmse/' + self.file_path + '.pkl'
		with open(path) as f:
			self.rmse = pickle.load(f)

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

	def get_audio_following(self, start_time, length = 1):
		return(self.y[int(start_time*self.sr):int((start_time + length)*sr)])

	def get_rmse_at_times(self, start_time, end_time):
		return self.rmse[0][int(start_time*self.frame_rate):int(end_time*self.frame_rate)]

