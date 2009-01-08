"""InfoStruct.py"""

class InfoStruct():
    """InfoStruct(**kwargs)

An object used to store data... no functionality. kwargs will be assigned to
attributes on the object.
"""
    def __init__(self, **kwargs):
        for attr, data in kwargs.iteritems():
            setattr(self, attr, data)