import ffmpeg
import os

def getSilenceRemoved(
    input_path,
    save_path,
    speech_timestamps=[],
    speed_multiplier=1,
):
    temp_files = []
    list_path = 'temp_list.txt'

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
        with open(list_path, 'w') as f:
            for temp_path in temp_files:
                abs_path = os.path.abspath(temp_path).replace('\\', '/')
                f.write(f"file '{abs_path}'\n")

        # concatenate all temp files
        (
            ffmpeg
            .input(list_path, format='concat', safe=0)
            .output(save_path)
            .overwrite_output()
            .run()
        )

    finally:
        # clean up temp files
        for temp_path in temp_files:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        if os.path.exists(list_path):
            os.remove(list_path)