import sys, os, librosa, pickle

sys.path.insert(0, '../core')

import alignment, speech, applause_list, file_loader, text_features,re

import librosa, numpy as np
from tqdm import tqdm

all_files = file_loader.get_non_duplicate_file_endings()

def add_to_hash(h,d):
	for k in d.keys():
		h[k] = d[k]
	return h

#### Methods for computing audio features

def get_pitch_tracking(audio, sr):
	r = str(np.random.randint(999999))
	librosa.output.write_wav('temp_%s.wav' % (r) ,audio,sr)
	reaper_cmd = "~/REAPER/build/reaper -i temp_%s.wav -f temp_%s.f0 -p temp_%s.pm -a" % (r,r,r)
	os.system(reaper_cmd)
	txt = open('temp_%s.f0' %(r)).read()
	txt = txt.split('\n')[7:][0:-1]
	split_lines = [l.split(' ') for l in txt]
	cleanup_cmd = "rm temp_%s.wav temp_%s.f0 temp_%s.pm" %(r,r,r)
	os.system(cleanup_cmd)
	return split_lines

def compute_audio_pitch_features(audio,sr):
	pitch_list = np.array([p[2] for p in get_pitch_tracking(audio,sr)]).astype(np.float32)
	mean_pitch = np.mean(pitch_list)
	max_pitch = np.max(pitch_list)
	min_pitch = np.min(pitch_list)
	range_pitch = max_pitch - min_pitch
	std_pitch = np.std(pitch_list)
	internal_silence = np.sum(pitch_list == -1) / float(len(pitch_list))
	return {'mean_pitch': mean_pitch, 'max_pitch': max_pitch, 'min_pitch': min_pitch, 'range_pitch': range_pitch, 'std_pitch': std_pitch, 'internal_silence': internal_silence}

def compute_audio_energy_features(audio,sr):
	rmse = librosa.feature.rmse(audio,frame_length=1024)
	mean_energy = np.mean(rmse)
	min_energy = np.min(rmse)
	max_energy = np.max(rmse)
	range_energy = max_energy - min_energy
	std_energy = np.std(rmse)
	return {'mean_energy': mean_energy, 'min_energy': min_energy, 'max_energy': max_energy, 'range_energy': range_energy, 'std_energy': std_energy}

def compute_audio_features(audio, sr):
	tries = 0
	feats = None
	while tries < 10 and feats is None:
		try:
			feats = add_to_hash(compute_audio_pitch_features(audio,sr),compute_audio_energy_features(audio,sr))
		except:
			tries += 1
			feats = None
	return feats

####

def get_audio_features_by_phrase(s):
	phrase_times = s.alignment.get_phrase_times()
	feats_list = []
	for p in tqdm(phrase_times):
		start, end = p[0], p[1]
		while end - start < 0.4:
			start -= 0.2; end += 0.2
		y = s.y[int(start*s.sr):int(end*s.sr)]
		feats_list.append(compute_audio_features(y, s.sr))
	return feats_list

#if __name__ == '__main__':
#	start_index = int(sys.argv[1])
#	end_index = int(sys.argv[2])

	#print "Loading speeches %d to %d" % (start_index, end_index)
	#all_files = file_loader.get_non_duplicate_file_endings()[start_index:end_index]
	#speeches = []
	#for f in tqdm(all_files):
	#	try:
	#		speeches.append(speech.Speech(f) )
	#	except:
	#		print f
	#speeches = [s for s in speeches if s.alignment.alignments is not None]

	#for i in tqdm(range(len(speeches))):
	#	print "Processing speech %d of %d" % (i, len(speeches))
	#	speech = speeches[i]
	#	if os.path.exists(speech.alignment_file):
	#		speech.load_librosa()
	#		output_path = speech.audio_file.replace('/audio/','/phrase_audio_features/').replace('.mp3','.pkl')
	#		if not os.path.exists(output_path):
	#			print output_path
	#			features = get_audio_features_by_phrase(speech)
	#			with open(output_path,'wb') as f:
	#				pickle.dump(features, f)

"""
	paths = open('/home/jrgillick/Applause/missing_phrase_audio_paths.txt').read().split('\n')[0:-1][start_index:end_index]
	for p in paths:
		suffix = p.split('/')[-1].split('.')[0]
		print suffix
		s = speech.Speech(suffix)
		if os.path.exists(s.alignment_file):
			s.load_librosa()
			output_path = s.audio_file.replace('/audio/','/phrase_audio_features/').replace('.mp3','.pkl')
			if not os.path.exists(output_path):
				print output_path
				features = get_audio_features_by_phrase(s)
				with open(output_path,'wb') as f:
					pickle.dump(features, f)

"""

import jeb_speech

jeb = jeb_speech.Speech('jeb')
jeb.load_librosa()
output_path = '/home/jrgillick/jeb_audio_features.pkl'
print output_path
features = get_audio_features_by_phrase(jeb)
with open(output_path,'wb') as f:
	pickle.dump(features, f)
