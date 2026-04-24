import torch
import torchaudio
import soundfile as sf

SAMPLING_RATE = 16000

# Load model
model, utils = torch.hub.load(
    repo_or_dir='snakers4/silero-vad',
    model='silero_vad',
    force_reload=False
)
(get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils

# Load audio
audio, sr = sf.read('gaigulian.wav', dtype='float32', always_2d=False)
if audio.ndim == 2:
    audio = audio.mean(axis=1)  # stereo → mono

wav = torch.from_numpy(audio)
if sr != SAMPLING_RATE:
    resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=SAMPLING_RATE)
    wav = resampler(wav)

# Detect speech
speech_timestamps = get_speech_timestamps(
    wav, model,
    sampling_rate=SAMPLING_RATE,
    threshold=0.5,
    min_speech_duration_ms=250,
    min_silence_duration_ms=100,
)

# Extract segments
speech_only = collect_chunks(speech_timestamps, wav)

# Save with soundfile instead of torchaudio
sf.write('output_no_silence.wav', speech_only.numpy(), SAMPLING_RATE)
print(f"Done! {len(speech_timestamps)} speech segment(s) kept.")