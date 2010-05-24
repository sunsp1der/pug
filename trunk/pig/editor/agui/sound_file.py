from pug import Filename

class SoundFile( Filename):
    def __init__(self, attribute, window, aguidata={}, **kw):
        aguidata['wildcards'] = "wav file (*.wav)|*.wav" 
#                   "mp3 file (*.mp3)|*.mp3|" \
#                   "midi files (*.mid)|*.mid|" \
#                   "All files (*.*)|*.*"
        aguidata['subfolder'] = "sound"
        Filename.__init__(self, attribute, window, aguidata=aguidata, **kw)