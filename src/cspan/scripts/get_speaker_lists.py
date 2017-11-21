import os

transcripts_dir = '/data/corpora/cspan/transcripts/'
speaker_lists_dir = '/data/corpora/cspan/speaker_lists/'

folders = os.listdir(transcripts_dir)

def get_speaker_list_from_folder(folder):
    transcript_files = os.listdir(transcripts_dir + folder)
    speaker_list_file_name = speaker_lists_dir + folder + '.txt'
    print speaker_list_file_name
    speaker_list = []
    for transcript_file in transcript_files:
        # Create folder to store the alignment files
        transcript_file_name = transcripts_dir+folder+"/" + transcript_file
        lines = open(transcript_file_name).read().split('\n')[2:]
        for line in lines:
            if '\t' in line:
                timestamp,speaker,text = line.split('\t')
                speaker_list.append(speaker)
    speaker_list = list(set(speaker_list))
    with open(speaker_list_file_name,'wb') as f:
        for s in speaker_list:
            f.write(s + '\n')

for folder in folders:
    get_speaker_list_from_folder(folder)
