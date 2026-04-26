from silero_vad import load_silero_vad, get_speech_timestamps
from audioworks import getSilenceRemoved
import torch
import torchaudio
import soundfile
import threading
import queue
import time
import librosa
import numpy

#need to create class for new audio, i need to make method for starting new track but i wanna eep <3
class VADAudioController:
    SAMPLING_RATE = 16000 # sample rate needed for correct silero_vad work
    CHUNK_SIZE = 20 # how many seconds will VAD process in one iteration

    def __init__(self, audio_path, VAD_sensetivity = 0.5): # constructor
        self.audio_path = audio_path
        #self.audio = self.prepare_audio()
        self.VAD_model = load_silero_vad()
        self.VAD_sensetivity = VAD_sensetivity
        self.timestampsQueue = queue.Queue() #queue needed for safe communication between threads
        self.timestamps = []
        self.seconds_skipped = 0
        self.audio_length = 0
        self.audio = self.prepare_audio()
        # self._stop_event = threading.Event()

        self.seconds_processed = 0


    #prepares audio for VAD model, beware that quality will be bad and you should use something else for playing ACTUAL audio
    def prepare_audio(self):
        #loading audio and sample rate
        prepared_audio, samplerate = soundfile.read(file=self.audio_path, dtype='float32', always_2d=False)
        # making audio into MONO if its not aleready
        if prepared_audio.ndim == 2:
            prepared_audio = prepared_audio.mean(axis=1)
        # converting a NumPy array into a PyTorch tensor
        prepared_audio = torch.from_numpy(prepared_audio)
        #resampling audio if rate isnt equal to 16kHz
        if samplerate != self.SAMPLING_RATE:
            resampler = torchaudio.transforms.Resample(orig_freq=samplerate, new_freq=self.SAMPLING_RATE)
            prepared_audio = resampler(prepared_audio)
        self.audio_length = len(prepared_audio) / self.SAMPLING_RATE
        return prepared_audio

    # this runs alongside player in another thread and processes audio chunk. by. chunk!
    def VAD_processor(self):
        while self.seconds_processed < self.audio_length:
            chunk_start = self.seconds_processed
            chunk_end = min(chunk_start + self.CHUNK_SIZE, self.audio_length)
            start_sample = int(chunk_start * self.SAMPLING_RATE)
            end_sample = int(chunk_end * self.SAMPLING_RATE)
            chunk = self.audio[start_sample:end_sample]

            chunk_timestamps = get_speech_timestamps(
                audio=chunk,
                model=self.VAD_model,
                threshold=self.VAD_sensetivity,
                sampling_rate=self.SAMPLING_RATE,
                min_speech_duration_ms=250,
                min_silence_duration_ms=1000,
                return_seconds=True
            )

            for ts in chunk_timestamps:
                self.timestampsQueue.put({
                    'start': ts['start'] + chunk_start,
                    'end': ts['end'] + chunk_start
                })

            self.seconds_processed = chunk_end

    def drainTimestampQueue(self):
        while not self.timestampsQueue.empty():
            ts = self.timestampsQueue.get()

            # calculate silence gap between previous speech end and this speech start
            if self.timestamps:
                silence_gap = ts['start'] - self.timestamps[-1]['end']
                if silence_gap > 0:
                    self.seconds_skipped += silence_gap

            self.timestamps.append(ts)

    # returns TRUE if time is in silence chunk and player should skip
    def in_silence_chunk(self, time):
        # drain queue into list of timestamps
        self.drainTimestampQueue()

        # check if position falls inside any speech segment
        for ts in self.timestamps:
            if ts['start'] <= time <= ts['end']:
                return False  # it's speech, don't skip

        # if we have timestamps covering this position and it's not speech → skip
        if self.timestamps and time < self.timestamps[-1]['end']:
            return True

        return False  # not enough data yet, don't skip

    # returns timestamp of next speech chunk
    def find_next_speech (self, time):
        for ts in self.timestamps: # dont look too optimized but EEH good enough i think
            if ts['start'] > time:
                return ts['start']

        return time  # no next speech found, stay where you are!!!

    # start VAD thread!!!
    def start(self):
        # start VAD thread
        vad_thread = threading.Thread(target=self.VAD_processor, daemon=True)
        vad_thread.start()

    def downloadChoppedAudio(self, save_path, speed_modifier=1.0):
        # wait for VAD to finish processing entire audio
        while self.seconds_processed < self.audio_length:
            time.sleep(0.1)
        # draining remaining timestamps from queue
        self.drainTimestampQueue()

        if not self.timestamps:
            raise ValueError("No speech segments detected — timestamps list is empty.")

        # loading audio in original quality
        original_audio, original_samplerate = soundfile.read(self.audio_path, always_2d=True)

        # preparing chunks of audio
        speech_chunks = []
        for ts in self.timestamps:
            start_sample = int(ts['start'] * original_samplerate)
            end_sample = int(ts['end'] * original_samplerate)
            speech_chunks.append(original_audio[start_sample:end_sample, :])

        # gluing all of it together
        chopped_audio = numpy.concatenate(speech_chunks, axis=0)

        # speeding up if needed
        if speed_modifier != 1.0:
            # librosa expects (channels, samples), so transpose in and out
            audio_transposed = chopped_audio.T  # (channels, frames)
            stretched_channels = [
                librosa.effects.time_stretch(channel, rate=speed_modifier)
                for channel in audio_transposed
            ]
            chopped_audio = numpy.stack(stretched_channels).T  # back to (frames, channels)

        # saving
        soundfile.write(save_path, chopped_audio, original_samplerate)


    # def stop(self):
    #     self._stop_event.set()
    #     while not self.timestampsQueue.empty():
    #         try: self.timestampsQueue.get_nowait()
    #         except queue.Empty: break
    #     self.timestamps.clear()
    #     self.seconds_processed = 0.0