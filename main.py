import pretty_midi
import mido
import time
import math
import threading

class ThreadPrint(threading.Thread):
    def __init__(self, msg):
        super().__init__()
        self.msg = msg

    def run(self):
        print(self.msg)

# midi_data = pretty_midi.PrettyMIDI('MIRROR.mid')

# duration_seconds = midi_data.get_end_time()

# print(math.ceil(duration_seconds))

ports = mido.get_output_names()
with mido.open_output(ports[0]) as outport:
    for msg in mido.MidiFile('MIRROR.mid'):
        time.sleep(msg.time)
        if not msg.is_meta:
            # thread_1 = ThreadPrint(msg)
            # thread_1.start()
            outport.send(msg) 


