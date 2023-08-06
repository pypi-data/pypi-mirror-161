"""Implementation of perl charnames functions"""

__author__ = """Joe Cool"""
___email__ = 'snoopyjc@gmail.com'
__version__ = '0.980'

import perllib
import unicodedata
import re
perllib.init_package('charnames')

def string_vianame(name):
    """This is a runtime equivalent to \\N{...}. name can be any expression that evaluates to a name accepted by \\N{...}"""
    if not name:
        return None
    if (_m := re.match(r'^U\+([0-9a-fA-F]+)$', name)):
        ordinal = int(_m.group(1), 16)
        return chr(ordinal)
    try:
        return unicodedata.lookup(name)
    except Exception:
        return None

charnames.string_vianame = string_vianame

def vianame(name):
    """This is similar to string_vianame. The main difference is that under most circumstances, vianame returns an ordinal code point, whereas string_vianame returns a string."""
    if not name:
        return None
    if (_m := re.match(r'^U\+([0-9a-fA-F]+)$', name)):
        return int(_m.group(1), 16)
    try:
        return ord(unicodedata.lookup(name))
    except Exception:
        return None

charnames.vianame = vianame

_extra_table = {0: 'NULL', 1: 'START OF HEADING', 2: 'START OF TEXT', 3: 'END OF TEXT', 4: 'END OF TRANSMISSION', 5: 'ENQUIRY', 6: 'ACKNOWLEDGE', 7: 'ALERT', 8: 'BACKSPACE', 9: 'CHARACTER TABULATION', 10: 'LINE FEED', 11: 'LINE TABULATION', 12: 'FORM FEED', 13: 'CARRIAGE RETURN', 14: 'SHIFT OUT', 15: 'SHIFT IN', 16: 'DATA LINK ESCAPE', 17: 'DEVICE CONTROL ONE', 18: 'DEVICE CONTROL TWO', 19: 'DEVICE CONTROL THREE', 20: 'DEVICE CONTROL FOUR', 21: 'NEGATIVE ACKNOWLEDGE', 22: 'SYNCHRONOUS IDLE', 23: 'END OF TRANSMISSION BLOCK', 24: 'CANCEL', 25: 'END OF MEDIUM', 26: 'SUBSTITUTE', 27: 'ESCAPE', 28: 'INFORMATION SEPARATOR FOUR', 29: 'INFORMATION SEPARATOR THREE', 30: 'INFORMATION SEPARATOR TWO', 31: 'INFORMATION SEPARATOR ONE', 127: 'DELETE', 128: 'PADDING CHARACTER', 129: 'HIGH OCTET PRESET', 130: 'BREAK PERMITTED HERE', 131: 'NO BREAK HERE', 132: 'INDEX', 133: 'NEXT LINE', 134: 'START OF SELECTED AREA', 135: 'END OF SELECTED AREA', 136: 'CHARACTER TABULATION SET', 137: 'CHARACTER TABULATION WITH JUSTIFICATION', 138: 'LINE TABULATION SET', 139: 'PARTIAL LINE FORWARD', 140: 'PARTIAL LINE BACKWARD', 141: 'REVERSE LINE FEED', 142: 'SINGLE SHIFT TWO', 143: 'SINGLE SHIFT THREE', 144: 'DEVICE CONTROL STRING', 145: 'PRIVATE USE ONE', 146: 'PRIVATE USE TWO', 147: 'SET TRANSMIT STATE', 148: 'CANCEL CHARACTER', 149: 'MESSAGE WAITING', 150: 'START OF GUARDED AREA', 151: 'END OF GUARDED AREA', 152: 'START OF STRING', 153: 'SINGLE GRAPHIC CHARACTER INTRODUCER', 154: 'SINGLE CHARACTER INTRODUCER', 155: 'CONTROL SEQUENCE INTRODUCER', 156: 'STRING TERMINATOR', 157: 'OPERATING SYSTEM COMMAND', 158: 'PRIVACY MESSAGE', 159: 'APPLICATION PROGRAM COMMAND', }

def viacode(code):
    """Returns the full name of the character indicated by the numeric code."""
    if code is None:
        return None
    try:
        if isinstance(code, str):
            if code[0:2] == 'U+' or code[0:2] == '0x':
                code = int(code[2:], 16)
            elif code[0:1] == '0' or re.search('[A-Fa-f]', code):
                code = int(code, 16)
        return unicodedata.name(chr(int(code)))
    except Exception:
        # Fix for https://bugs.python.org/issue46947:
        try:
            return _extra_table[int(code)]
        except Exception:
            pass
        return None

charnames.viacode = viacode


