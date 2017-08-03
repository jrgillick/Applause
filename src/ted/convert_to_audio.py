from subprocess import call
import os
import sys

if __name__ == '__main__':
	video_dir = sys.argv[1]
	audio_dir = sys.argv[2]

	video_files = os.listdir(video_dir)
	for video_file in video_files:
		vid_file = video_dir + video_file
		audio_file = audio_dir + video_file.replace('.mp4','.mp3')
		cmd = "sudo ffmpeg -i " + vid_file + " " + audio_file
		print cmd
		os.system(cmd)
