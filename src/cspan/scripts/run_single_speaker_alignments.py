import os

transcripts_dir = '/data/corpora/cspan/transcripts/'
alignments_dir = '/data/corpora/cspan/alignments/'
speaker_lists_dir = '/data/corpora/cspan/speaker_lists/'

folders = os.listdir(transcripts_dir)

for folder in folders:
    transcript_files = os.listdir(transcripts_dir + folder)
    speaker_list = open(speaker_lists_dir + folder + '.txt').read().split('\n')
    print speaker_list

    for transcript_file in transcript_files:
        alignment_folder_name = alignments_dir + folder + '/' + transcript_file.replace('.txt','')
        alignment_file_name = alignment_folder_name + "/" + transcript_file.replace(".txt","_single_speaker.json")
        #if os.path.exists(alignment_file_name) and os.path.getsize(alignment_file_name) == 0:
        #    os.system('rm ' + alignment_file_name)
        transcript_file_name = transcripts_dir+folder+"/" + transcript_file
        audio_file_name = transcript_file_name.replace("/transcripts","/audio").replace('.txt','.mp3')
        if os.path.exists(audio_file_name) and os.path.exists(transcript_file_name) and (not os.path.exists(alignment_file_name) or os.path.getsize(alignment_file_name) == 0):
            lines = open(transcript_file_name).read().split('\n')[2:]
            full_text = ""
            for line in lines:
                if '\t' in line:
                    timestamp,speaker,text = line.split('\t')
                    if speaker in speaker_list:
                        full_text += text + '\n'
            with open('temp_txt.txt','wb') as f:
                f.write(full_text)
            alignment_cmd = "curl -X POST -F 'audio=@" + audio_file_name + "' -F 'transcript=@temp_txt.txt' 'http://localhost:32769/transcriptions?async=false' > " + alignment_file_name
            print alignment_cmd
            os.system(alignment_cmd)
            os.system('rm temp_txt.txt')
