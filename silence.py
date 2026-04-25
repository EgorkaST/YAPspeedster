import torch
import torchaudio
import soundfile as sf
from silero_vad import load_silero_vad, read_audio, get_speech_timestamps

SAMPLING_RATE = 16000

def GetSpeechTimestamps(
        file_path,
        in_seconds = False
):

    # Load model
    model = load_silero_vad()

    # Load audio
    audio, sr = sf.read(file=file_path, dtype='float32', always_2d=False)



    #preparing audio for VAD model

    # making audio into MONO if its not aleready
    if audio.ndim == 2:
        audio = audio.mean(axis=1)
    preparedAudio = torch.from_numpy(audio)
    if sr != SAMPLING_RATE:
        resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=SAMPLING_RATE)
        preparedAudio = resampler(preparedAudio)

    # Detect speech
    speechTimestamps = get_speech_timestamps(
        preparedAudio, model,
        sampling_rate=SAMPLING_RATE,
        threshold=0.5,
        min_speech_duration_ms=250,
        min_silence_duration_ms=100,
        return_seconds = in_seconds,
    )

    return speechTimestamps



# speechTimestamps = GetSpeechTimestamps('input.mp3')
# print(f"Обнаружено {len(speechTimestamps)} моментов речи")
# for speechTimestamp in speechTimestamps:
#     print(f"начало: {speechTimestamp['start'] / SAMPLING_RATE}")