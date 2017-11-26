import os

root_audio_dir = '/data/corpora/cspan/audio/'

def get_non_duplicate_file_endings():
	paths = open('/data/corpora/cspan/keeper_speeches.txt').read().split('\n')[0:-1]
	return [p.split('/')[-1].split('.')[0] for p in paths]

def get_all_file_endings():
	dirs = os.listdir(root_audio_dir)
	all_file_endings = []
	for d in dirs:
		all_file_endings += [root_audio_dir + d + '/' + f for f in os.listdir(root_audio_dir + d)]
	return [f.split('.mp3')[0].split('/')[-1] for f in all_file_endings]

def get_speaker_name(file_ending):
	return '_'.join(file_ending.split('_')[0:-1])

def format_file_path_for_speech_object(file_ending):
	return get_speaker_name(file_ending) + '/' + file_ending
	
