import pretty_midi
import subprocess
import mido
import os
import sounddevice as sd
import wave
import numpy as np
import sys

PLAYER_PATH = "C:\\Program Files (x86)\\TMIDI Player\\TMIDI.EXE"
REC_AUDIO_DEVICE_IDX = 16
PLAYBACK_AUDIO_DEVICE_IDX = 16
MIDI_DEVICE_IDX = 2
REC_SAMPLE_RATE = 44100
REC_CHANNELS = 2
INPUT_CHANNEL_LEFT = 2
INPUT_CHANNEL_RIGHT = 3
OUTPUT_CHANNEL_LEFT = 0
OUTPUT_CHANNEL_RIGHT = 1

MIDI_FILENAME = "MIRROR.mid"

PADDING_REC_TIME = 2

midi_abspath = os.path.abspath(MIDI_FILENAME)

ports = mido.get_output_names()
sound_devices = sd.query_devices()


if len(sys.argv) >= 2 and sys.argv[1] == 'get' and sys.argv[2] == 'devices':
    print(str(ports))
    print(sound_devices)
    sys.exit()

sd.default.samplerate = REC_SAMPLE_RATE
sd.default.channels = REC_CHANNELS
sd.default.device = [REC_AUDIO_DEVICE_IDX, PLAYBACK_AUDIO_DEVICE_IDX] #input:output
print(sound_devices[REC_AUDIO_DEVICE_IDX])
print(ports[MIDI_DEVICE_IDX])
# チャンネルマッピング
input_selector = [INPUT_CHANNEL_LEFT, INPUT_CHANNEL_RIGHT]
# out 1・2を指定(聴かないので指定する意味はない)
output_selector = [OUTPUT_CHANNEL_LEFT, OUTPUT_CHANNEL_RIGHT]
asio_in = sd.AsioSettings(channel_selectors = input_selector)
asio_out = sd.AsioSettings(channel_selectors = output_selector)
sd.default.extra_settings = (asio_in,asio_out)

midi_data = pretty_midi.PrettyMIDI(midi_abspath)

duration_seconds = midi_data.get_end_time()

rec_time_seconds = duration_seconds + PADDING_REC_TIME

process = subprocess.Popen(PLAYER_PATH + ' ' + midi_abspath)
recdata = sd.rec(int(rec_time_seconds * REC_SAMPLE_RATE))
sd.wait()
process.kill()

# 鳴りっぱなしの音を止める
with mido.open_output(ports[MIDI_DEVICE_IDX]) as outport:
    # 念のため全チャンネルノートオフ
    for ch in range(16):
        outport.send(mido.Message('note_off', channel=ch))
    # GS Reset（リバーブ対策）
    sysex_gs_reset = [0x41, 0x10, 0x42, 0x12, 0x40, 0x00, 0x7F, 0x00, 0x41]
    outport.send(mido.Message('sysex', data=sysex_gs_reset))    

wave_filename = "record" + os.sep + os.path.basename(midi_abspath) + ".wav"
# 正規化
data = recdata / recdata.max() * np.iinfo(np.int16).max
# float -> int
data = data.astype(np.int16)
# ファイル保存
with wave.open(wave_filename, mode='wb') as wb:
    wb.setnchannels(REC_CHANNELS)  # ステレオ
    quantifying_byte_number = 2 # 16bit
    wb.setsampwidth(quantifying_byte_number)  # 2byte(16bit)
    wb.setframerate(REC_SAMPLE_RATE)
    wb.writeframes(data.tobytes())  # バイト配列に変換


