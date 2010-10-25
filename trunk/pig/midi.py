"""midi.py

Parse midi events in a way that's useful for making visualizers or other 
reactive systems.

Mostly from:
midi.py -- MIDI classes and parser in Python
Placed into the public domain in December 2001 by Will Ware
"""
import types
import exceptions

def getVariableLengthNumber(str):
    sum = 0
    i = 0
    while 1:
        x = ord(str[i])
        i = i + 1
        sum = (sum << 7) + (x & 0x7F)
        if not (x & 0x80):
            return sum, str[i:]
        
class midi_track():
    runningStatus = None
    def __init__(self):
        self.channel = {}

class EnumException(exceptions.Exception):
    pass

class Enumeration:
    def __init__(self, enumList):
        lookup = { }
        reverseLookup = { }
        i = 0
        uniqueNames = [ ]
        uniqueValues = [ ]
        for x in enumList:
            if type(x) == types.TupleType:
                x, i = x
            if type(x) != types.StringType:
                raise EnumException, "enum name is not a string: " + x
            if type(i) != types.IntType:
                raise EnumException, "enum value is not an integer: " + i
            if x in uniqueNames:
                raise EnumException, "enum name is not unique: " + x
            if i in uniqueValues:
                raise EnumException, "enum value is not unique for " + x
            uniqueNames.append(x)
            uniqueValues.append(i)
            lookup[x] = i
            reverseLookup[i] = x
            i = i + 1
        self.lookup = lookup
        self.reverseLookup = reverseLookup
    def __add__(self, other):
        lst = [ ]
        for k in self.lookup.keys():
            lst.append((k, self.lookup[k]))
        for k in other.lookup.keys():
            lst.append((k, other.lookup[k]))
        return Enumeration(lst)
    def hasattr(self, attr):
        return self.lookup.has_key(attr)
    def has_value(self, attr):
        return self.reverseLookup.has_key(attr)
    def __getattr__(self, attr):
        if not self.lookup.has_key(attr):
            raise AttributeError
        return self.lookup[attr]
    def whatis(self, value):
        return self.reverseLookup[value]    

channelVoiceMessages = Enumeration([("NOTE_OFF", 0x80),
                                    ("NOTE_ON", 0x90),
                                    ("POLYPHONIC_KEY_PRESSURE", 0xA0),
                                    ("CONTROLLER_CHANGE", 0xB0),
                                    ("PROGRAM_CHANGE", 0xC0),
                                    ("CHANNEL_KEY_PRESSURE", 0xD0),
                                    ("PITCH_BEND", 0xE0)])

channelModeMessages = Enumeration([("ALL_SOUND_OFF", 0x78),
                                   ("RESET_ALL_CONTROLLERS", 0x79),
                                   ("LOCAL_CONTROL", 0x7A),
                                   ("ALL_NOTES_OFF", 0x7B),
                                   ("OMNI_MODE_OFF", 0x7C),
                                   ("OMNI_MODE_ON", 0x7D),
                                   ("MONO_MODE_ON", 0x7E),
                                   ("POLY_MODE_ON", 0x7F)])

metaEvents = Enumeration([("SEQUENCE_NUMBER", 0x00),
                          ("TEXT_EVENT", 0x01),
                          ("COPYRIGHT_NOTICE", 0x02),
                          ("SEQUENCE_TRACK_NAME", 0x03),
                          ("INSTRUMENT_NAME", 0x04),
                          ("LYRIC", 0x05),
                          ("MARKER", 0x06),
                          ("CUE_POINT", 0x07),
                          ("MIDI_CHANNEL_PREFIX", 0x20),
                          ("MIDI_PORT", 0x21),
                          ("END_OF_TRACK", 0x2F),
                          ("SET_TEMPO", 0x51),
                          ("SMTPE_OFFSET", 0x54),
                          ("TIME_SIGNATURE", 0x58),
                          ("KEY_SIGNATURE", 0x59),
                          ("SEQUENCER_SPECIFIC_META_EVENT", 0x7F)])

def parse_event(self, status, lsb, msb):
    def read(self, time, str):
        global runningStatus
        self.time = time
        # do we need to use running status?
        if not (ord(str[0]) & 0x80):
            str = runningStatus + str
        runningStatus = x = str[0]
        x = ord(x)
        y = x & 0xF0
        z = ord(str[1])

        if channelVoiceMessages.has_value(y):
            self.channel = (x & 0x0F) + 1
            self.type = channelVoiceMessages.whatis(y)
            if (self.type == "PROGRAM_CHANGE" or
                self.type == "CHANNEL_KEY_PRESSURE"):
                self.data = z
                return str[2:]
            else:
                self.pitch = z
                self.velocity = ord(str[2])
                channel = self.track.channels[self.channel - 1]
                if (self.type == "NOTE_OFF" or
                    (self.velocity == 0 and self.type == "NOTE_ON")):
                    channel.noteOff(self.pitch, self.time)
                elif self.type == "NOTE_ON":
                    channel.noteOn(self.pitch, self.time, self.velocity)
                return str[3:]

        elif y == 0xB0 and channelModeMessages.has_value(z):
            self.channel = (x & 0x0F) + 1
            self.type = channelModeMessages.whatis(z)
            if self.type == "LOCAL_CONTROL":
                self.data = (ord(str[2]) == 0x7F)
            elif self.type == "MONO_MODE_ON":
                self.data = ord(str[2])
            return str[3:]

        elif x == 0xF0 or x == 0xF7:
            self.type = {0xF0: "F0_SYSEX_EVENT",
                         0xF7: "F7_SYSEX_EVENT"}[x]
            length, str = getVariableLengthNumber(str[1:])
            self.data = str[:length]
            return str[length:]

        elif x == 0xFF:
            if not metaEvents.has_value(z):
                print "Unknown meta event: FF %02X" % z
            self.type = metaEvents.whatis(z)
            length, str = getVariableLengthNumber(str[2:])
            self.data = str[:length]
            return str[length:]