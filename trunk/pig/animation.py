from Opioid2D import ResourceManager

def get_grid_sequence_frames( image, width, height, sequence):
    """get_grid sequence_frames( sequence)->list of frames from grid image
    
sequence: A list of frame numbers and/or tuples. Numbers in the list will be
translated into their corresponding images. Tuples should be in the range form 
(start, stop, step=1) and will be translated into a range of frames. For example 
'[1,(3,6)]' will return these frames: 1, 3, 4, 5 and '[10, (17,14,-1)]' will
return these: 10, 17, 16, 15. 
"""
    frame_nums = parse_grid_sequence( sequence)
    images = ResourceManager.get_grid( image,width,height)
    frames = []
    for n in frame_nums:
        frames.append( images[n])
    return frames

def parse_grid_sequence( sequence):
    """parse_grid_sequence( sequence)->list of numbers translated from sequence
    
sequence: A list of frame numbers and/or tuples. Numbers in the list will be
unchanged. Tuples should be in the range form (start, stop, step=1) and will be 
translated into a range of numbers. For example '[1,(3,6)]' will return this:
[1, 3, 4, 5] and '[10, (17,14,-1)]' will return this: [10, 17, 16, 15]. 
"""
    parsed = []
    for entry in sequence:
        if type(entry) == tuple:
            for n in range(*entry):
                parsed.append(n)
        else:
            parsed.append(entry)
    return parsed