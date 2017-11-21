import os

movs_dir = '/data/corpora/cspan/movs/'
audio_dir = '/data/corpora/cspan/audio/'

folders = os.listdir(movs_dir)

def convert_folder(folder):
    mov_files = os.listdir(movs_dir + folder)
    for mov_file in mov_files:
        mov_file_name = movs_dir + folder + "/" + mov_file
        audio_file_name = audio_dir + folder + "/" + mov_file.replace(".mp4",".mp3")
        os.system("ffmpeg -i " + mov_file_name + " " + audio_file_name)

for folder in folders:
    convert_folder(folder)
