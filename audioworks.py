import ffmpeg
from silence import GetSpeechTimestamps
import ffmpeg
import os
import tempfile

def getSilenceRemoved(
    input_path,
    save_path,
    speech_timestamps=[],
    speed_multiplier=1,
):
    if speech_timestamps == []:
        speech_timestamps = GetSpeechTimestamps(file_path=input_path, in_seconds=True)

    temp_files = []

    try:
        # save each segment as a temp file
        for i, ts in enumerate(speech_timestamps):
            temp_path = f'temp_segment_{i}.wav'
            temp_files.append(temp_path)

            stream = (
                ffmpeg
                .input(input_path)
                .filter('atrim', start=ts['start'], end=ts['end'])
                .filter('asetpts', 'PTS-STARTPTS')
            )
            if speed_multiplier != 1:
                stream = stream.filter('atempo', speed_multiplier)

            stream.output(temp_path).overwrite_output().run(quiet=True)

        # write a list file for ffmpeg concat
        list_path = 'temp_list.txt'
        with open(list_path, 'w') as f:
            for temp_path in temp_files:
                f.write(f"file '{os.path.abspath(temp_path)}'\n")

        # concatenate all temp files
        (
            ffmpeg
            .input(list_path, format='concat', safe=0)
            .output(save_path)
            .overwrite_output()
            .run(quiet=True)
        )

    finally:
        # clean up temp files
        for temp_path in temp_files:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        if os.path.exists(list_path):
            os.remove(list_path)

getSilenceRemoved(
    input_path = 'gaigulian.wav',
    save_path = 'sped-up.wav',
    speed_multiplier = 2,
)