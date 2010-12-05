# This file makes sure adds pig and pug to the search path
    
try:
    import sys
    # special code just for Pig_Demo version
    import os.path
    path = os.path.split(os.path.split(__file__)[0])[0]
    sys.path.append(path)
except:
    pass#