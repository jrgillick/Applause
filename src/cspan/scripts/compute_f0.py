import os, sys, time, numpy as np

talk_audio_root = '/data/corpora/cspan/audio/'
speech_dirs = [talk_audio_root + f + '/' for f in os.listdir(talk_audio_root)]
files = []
for d in speech_dirs:
    files += [d + f for f in os.listdir(d)]
    
f0_root_dir = '/data/corpora/cspan/f0/'

def run_reaper(f):
    outfile = f.replace("/audio","/f0")
    r = str(np.random.randint(999999))
    # Create temp audio file and convert it to a mono wav file with sox
    sox_cmd = "sox %s temp_%s.wav remix 1,2" % (f, r)
    os.system(sox_cmd)
    # Compute f0 and store it in a text file
    reaper_cmd = "~/REAPER/build/reaper -i temp_%s.wav -f %s -p temp_%s.pm -a" % (r,outfile,r)
    os.system(reaper_cmd)
    cleanup_cmd = "rm temp_%s.wav temp_%s.pm" % (r,r)
    os.system(cleanup_cmd)

if __name__ == '__main__':
    start_file = int(sys.argv[1]); end_file = int(sys.argv[2])
    files=files[start_file:end_file]
    for f in files:
        t0 = time.time()
        print f.replace("/audio","/f0").replace(".mp3",".f0")
        run_reaper(f)
        print "finished %s in %s seconds" % (f, str(time.time() - t0))
