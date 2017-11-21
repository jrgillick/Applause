# Run Gentle App first to start HTTP server

import os
import sys

audio_filenames = open('audio_file_names.txt').read().split('\n')

try:
    if sys.argv[1] == "rev":
        audio_filenames.reverse()
except:
    None

for audio_filename in audio_filenames:
    json_filename = audio_filename.replace(".mp3",".json")
    path = "/data/corpora/ted/forced_alignments/" + json_filename

    if not os.path.exists(path):
        print path

        remote_audio_dir = "/data/corpora/ted/audio"
        remote_transcript_dir = "/data/corpora/ted/transcripts_clean/"
        remote_json_dir = "/data/corpora/ted/forced_alignments/"

        # Copy over audio file
        audio_scp_cmd = "cp " + remote_audio_dir + audio_filename + " " + "temp_audio.mp3"
        os.system(audio_scp_cmd)
        #print(audio_scp_cmd)

        # Copy over transcript file
        transcript_filename = audio_filename.replace(".mp3",".html")
        transcript_scp_cmd = "cp " + remote_transcript_dir + transcript_filename + " " + "temp_transcript.html"
        os.system(transcript_scp_cmd)
        #print(transcript_scp_cmd)

        # Clean transcript and store in text file
        t = open("temp_transcript.html").read()
        lines = t.split('\n')
        text_lines = [l.split('\t')[1] for l in lines[0:-1]]
        text = ' '.join(text_lines)
        text = text.replace("(Laughter)","").replace("(Applause)","")

        with open("temp_text.txt", "wb") as f:
            f.write(text)

        # Run forced alignment and store in json file
        json_filename = audio_filename.replace(".mp3",".json")
        alignment_cmd = "curl -X POST -F 'audio=@temp_audio.mp3' -F 'transcript=<temp_text.txt' 'http://localhost:32776/transcriptions?async=false' > /data/corpora/ted/forced_alignments/" + json_filename
        os.system(alignment_cmd)

        # Remove temp files
        os.system("rm temp_audio.mp3")
        os.system("rm temp_transcript.html")
        os.system("rm temp_text.txt")

    else:
        print "Skipping: " + path

