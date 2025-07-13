
import mido
import time
import threading

# Callback que el motor de síntesis debe implementar:
# def handle_note_on(midi_note, velocity)
# def handle_note_off(midi_note)
# def handle_sustain(is_pressed)

class MIDIEngineInterface:
    def __init__(self, piano_engine, port_name=None):
        self.piano_engine = piano_engine
        self.port_name = port_name
        self.running = False
        self.sustain = False


    def start(self):
        self.running = True
        input_names = mido.get_input_names()
        if self.port_name is None and input_names:
            self.port_name = input_names[0]
        try: 
            self.inport = mido.open_input(self.port_name)
            print(f"[MIDI] Listening on '{self.port_name}'...")        
            threading.Thread(target=self._loop, daemon=True).start()
        except Exception as e:
            print(f"[MIDI] Hubo un error al intentar abrir un puerto MIDI: {e}")

    def stop(self):
        self.running = False
        self.inport.close()

    def _loop(self):
        for msg in self.inport:
            if not self.running:
                break
            self._handle_message(msg)

    def _handle_message(self, msg):
        if msg.type == 'note_on' and msg.velocity > 0:
            self.piano_engine.handle_note_on(msg.note, msg.velocity / 127.0)
        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            self.piano_engine.handle_note_off(msg.note)
        elif msg.type == 'control_change' and msg.control == 64:  # Sustain pedal
            self.sustain = msg.value >= 64
            self.piano_engine.handle_sustain(self.sustain) #
