import os, sys, time
import numpy as np

audio_dir = '/data/corpora/cspan/audio/'
separated_audio_dir= '/data/corpora/cspan/audio_separated/'

#python examples/ikala/separate_ikala.py -i trump_20.wav -o ./ -m fft_1024.pkl
separate_script_path = '~/DeepConvSep/examples/ikala/separate_ikala.py'
stored_model_path = '~/DeepConvSep/fft_1024.pkl'

def make_folder(audio_file):
	containing_folder = audio_file.split('/')[-2]
	folder_name = audio_file.split('/')[-1].split('.')[0]
	new_folder_path = separated_audio_dir + containing_folder + '/' + folder_name
	os.system('mkdir ' + new_folder_path)
	return new_folder_path

def convert_mp3_to_wav(audio_file):
	print "Converting " + audio_file + " to wav..."
	r = str(np.random.randint(9999999))
	tempfile_name = 'temp_' + r + '.wav'
	os.system('ffmpeg -i ' + audio_file + ' ' + tempfile_name + ' -loglevel panic -nostats')
	return tempfile_name

def run_separation(input_audio_file, output_dir):
	print "Running source separation..."
	cmd = 'python ' + separate_script_path + ' -i ' + input_audio_file + ' -o ' + output_dir + " -m " + stored_model_path
	os.system(cmd)
	#print cmd

#/data/corpora/cspan/audio_separated/rick_santorum_3-music.mp3'
def convert_separated_files_to_mp3(output_dir):
	print "Cleaning up " + output_dir + "..."
	files = [output_dir + '/' + f for f in os.listdir(output_dir)]
	if len(files) == 2 and separated_audio_dir in files[0] and separated_audio_dir in files[1]:
		for f in files:
			mp3_filename = separated_audio_dir + output_dir.split('/')[-2] + '/' + output_dir.split('/')[-1] + '/' + output_dir.split('/')[-1] + '-' + f.replace('.wav','.mp3').split('-')[1]
			os.system('ffmpeg -i ' + f + ' ' + mp3_filename + ' -loglevel panic -nostats')
			os.system('rm ' + f)

def get_files():
	dirs = os.listdir(audio_dir)
	all_files = []
	for d in dirs:
		all_files += [audio_dir + d + '/' + f for f in os.listdir(audio_dir + d)]
	return all_files

#not_done = open('not_done.txt').read().split('\n')

if __name__ == '__main__':
	files = get_files()
	print len(files)
	start = int(sys.argv[1])
	end = int(sys.argv[2])
	for f in files[start:end]:
		ending = "/".join(f.split('.mp3')[0].split('/')[-2:])
		if True # ending in not_done: uncomment to use list of files to do
			t0 = time.time()
			output_folder = make_folder(f)
			temp_wav_file = convert_mp3_to_wav(f)
			run_separation(temp_wav_file, output_folder)
			convert_separated_files_to_mp3(output_folder)
			os.system('rm ' + temp_wav_file)
			print 'Processed ' + f + ' in ' + str(time.time()-t0) + ' seconds.'
