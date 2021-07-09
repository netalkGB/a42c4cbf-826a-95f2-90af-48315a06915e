import pretty_midi
import subprocess
import time
import mido
import os
import sounddevice as sd
import wave
import numpy as np

PLAYER_PATH = "C:\\Program Files (x86)\\TMIDI Player\\TMIDI.EXE"

ports = mido.get_output_names()
print(str(ports))
midi_device_name = 'MOTU M Series MIDI Out'
midi_device_index = ports.index(list(filter(lambda v: midi_device_name in v, ports))[0])
print('index: '  + str(midi_device_index))

sound_devices = sd.query_devices()
print(sound_devices)
sd.default.samplerate = 44100
sd.default.channels = 2
sd.default.device = [16,16]#input:output
print(sound_devices[16])
# チャンネルマッピング
# in 3・4を指定
input_selector = [2, 3]
# out 1・2を指定(聴かないので指定する意味はない)
output_selector = [0, 1]

asio_in = sd.AsioSettings(channel_selectors = input_selector)
asio_out = sd.AsioSettings(channel_selectors = output_selector)
sd.default.extra_settings = (asio_in,asio_out)

midi_data = pretty_midi.PrettyMIDI('MIRROR.mid')

duration_seconds = midi_data.get_end_time()
# duration_seconds = 10
additional_seconds = 1
duration = duration_seconds + additional_seconds
recdata = sd.rec(int(duration * sd.default.samplerate))
process = subprocess.Popen(PLAYER_PATH + ' ' + os.path.abspath("MIRROR.MID"))
sd.wait()
process.kill()

# ノートオフしないで終わってもノートオフする
with mido.open_output(ports[midi_device_index]) as outport:
    # PANIC
    for ch in range(16):
        outport.send(mido.Message('note_off', channel=ch))
    # GS Reset
    sysex_gs_reset = [0x41, 0x10, 0x42, 0x12, 0x40, 0x00, 0x7F, 0x00, 0x41]
    outport.send(mido.Message('sysex', data=sysex_gs_reset))    


wave_filename = "MIRROR.mid" + ".wav"
# 正規化
data = recdata / recdata.max() * np.iinfo(np.int16).max
# float -> int
data = data.astype(np.int16)
# ファイル保存
with wave.open(wave_filename, mode='wb') as wb:
    wb.setnchannels(2)  # ステレオ
    wb.setsampwidth(2)  # 2byte(16bit)
    wb.setframerate(44100)
    wb.writeframes(data.tobytes())  # バイト配列に変換


