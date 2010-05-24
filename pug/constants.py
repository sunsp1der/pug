"""Constants for use with the pug system"""
from types import BooleanType, IntType, LongType, FloatType, ComplexType, \
                       StringType, UnicodeType, TupleType, ListType, DictType, \
                       NoneType

BASIC_TYPES = [BooleanType, IntType, LongType, FloatType, ComplexType, 
                       StringType, UnicodeType, TupleType, ListType, DictType, 
                       NoneType]

# defaults
PUGFRAME_DEFAULT_SIZE = 350, 400
PUGFRAME_ATTRIBUTE_PREFIX = "   "
FORMAT_FLOATS = True