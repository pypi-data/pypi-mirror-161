"""
isType
https://github.com/xhelphin/whatType

Python package to check the type of a variable or object.
"""


def isFunction(inp):
    """
    Returns True if the supplied argument is a function, else returns False.
    """
    if type(inp) == type(isFunction):
        return True
    return False

def isInt(inp):
    """
    Returns True if the supplied argument is an integer, else returns False.
    """
    if type(inp) == type(1234):
        return True
    return False

def isFloat(inp):
    """
    Returns True if the supplied argument is a float, else returns False.
    """
    if type(inp) == type(3.1415):
        return True
    return False

def isComplex(inp):
    """
    Returns True if the supplied argument is a complex, else returns False.
    """
    if type(inp) == type(3+4j):
        return True
    return False

def isStr(inp):
    """
    Returns True if the supplied argument is a string, else returns False.
    """
    if type(inp) == type("Hello, World!"):
        return True
    return False

def isList(inp):
    """
    Returns True if the supplied argument is a list, else returns False.
    """
    if type(inp) == type([1,2,3]):
        return True
    return False

def isDict(inp):
    """
    Returns True if the supplied argument is a dictionary, else returns False.
    """
    if type(inp) == type({"hello":"world"}):
        return True
    return False

def isTuple(inp):
    """
    Returns True if the supplied argument is a tuple, else returns False.
    """
    if type(inp) == type((1,2,3)):
        return True
    return False

def isNone(inp):
    """
    Returns True if the supplied argument is a NoneType, else returns False.
    """
    if type(inp) == type(None):
        return True
    return False

def isBool(inp):
    """
    Returns True if the supplied argument is a Boolean, else returns False.
    """
    if type(inp) == type(True):
        return True
    return False

def isBytes(inp):
    """
    Returns True if the supplied argument is a byte stream, else returns False.
    """
    if type(inp) == type(b'Hello, World!'):
        return True
    return False

def isClass(inp):
    """
    Returns True if the supplied argument is a class, else returns False."""
    class Test:
        pass
    if type(inp) == type(Test):
        return True
    return False