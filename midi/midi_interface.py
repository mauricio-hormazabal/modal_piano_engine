
import mido
import threading
#from mido import MidiInput

class MIDIEngineInterface:
    def __init__(self, piano_engine=None, port_name=None):
        self.piano_engine = piano_engine
        self.port_name = port_name
        self.running = False
        self.thread = None
        self.inport = None

    def _open_port(self):
        if self.port_name:
            self.inport = mido.open_input(self.port_name, callback=self._handle_midi)
        else:
            ports = mido.get_input_names()
            if not ports:
                raise RuntimeError("No se encontraron dispositivos MIDI.")
            self.inport = mido.open_input(ports[0], callback=self._handle_midi)
            
        print(f"  MIDI conectado a: {self.inport.name}")

    def _handle_midi(self, msg):
        #print(f"🎼 Recibido: {msg}") 
        if msg.type == 'note_on' and msg.velocity > 0:
            velocity = msg.velocity / 127.0
            self.piano_engine.handle_note_on(msg.note, velocity)
        elif (msg.type == 'note_off') or (msg.type == 'note_on' and msg.velocity == 0):
            self.piano_engine.handle_note_off(msg.note)
        elif msg.type == 'control_change' and msg.control == 64:
            sustain_on = msg.value >= 64
            self.piano_engine.handle_sustain(sustain_on)

    def start(self):
        self._open_port()
        self.running = True

    def stop(self):
        if self.inport:
            self.inport.close()
            print(" Puerto MIDI cerrado.")
        self.running = False
