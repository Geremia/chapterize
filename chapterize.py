#!/usr/bin/python3

# Concatenate audio files and add chapter markers.

import glob, os, tqdm, sys

if len(sys.argv) != 3:
    print("Usage example: " + sys.argv[0] + " concatenated.mp4 '*.mp3'")
    exit()

cattedAudio = sys.argv[1]
inputAudio = sys.argv[2]

inputAudioFiles=glob.glob(inputAudio)
inputAudioFiles.sort()

starttimes=[]
time = 0 #cummulative start time (nanoseconds)
for i in tqdm.tqdm(inputAudioFiles):
    time += float(os.popen('sox ' + i + ' -n stat |& head -2 | tail -1 | grep -o "[0-9.]\+"').read().strip())*1e9
    starttimes.append([i, str(int(time))])

metadata = os.popen('ffmpeg -i ' + inputAudioFiles[0] + ' -f ffmetadata -v quiet -').read()

# https://ffmpeg.org/ffmpeg-formats.html#Metadata-1
# "If the timebase is missing then start/end times are assumed to be in ð»ð®ð»ð¼ðð²ð°ð¼ð»ð±ð."
# "chapter start and end times in form âSTART=numâ, âEND=numâ, where num is a ð½ð¼ðð¶ðð¶ðð² ð¶ð»ðð²ð´ð²ð¿."
start=''
for i in starttimes:
    metadata += '''[CHAPTER]
START=''' + start + '''
END=''' + i[1] + '''
title=''' + i[0] + '\n'
    start = i[1]

tmpmeta = os.popen('mktemp').read().strip()
metafile = open(tmpmeta, 'w')
print(metadata, file=metafile)
metafile.close()

barSeparatedFilenames = ''
for i in inputAudioFiles:
    barSeparatedFilenames += i+'|'

os.system('ffmpeg -i "concat:' + barSeparatedFilenames[:-1]  + '" -i ' + tmpmeta + ' -map_metadata 1 -codec copy ' + cattedAudio)
os.system('rm -fr ' + tmpmeta)
