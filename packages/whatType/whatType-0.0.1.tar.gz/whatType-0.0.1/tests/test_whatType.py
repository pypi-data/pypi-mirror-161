from whatType import *

def test_isFunction():
    def test():
        pass
    assert isFunction(test) == True

def test_isInt():
    assert isInt(1234) == True

def test_isFloat():
    assert isFloat(3.1415) == True

def test_isComplex():
    assert isComplex(3+4j) == True

def test_isStr():
    assert isStr("Hello, World!") == True

def test_isList():
    assert isList([1,2,3]) == True

def test_isDict():
    assert isDict({"hello":"world"}) == True

def test_isTuple():
    assert isTuple((1,2,3)) == True

def test_isNone():
    assert isNone(None) == True

def test_isBool():
    assert isBool(True) == True

def test_isBytes():
    assert isBytes(b'Hello, World!') == True

def test_isClass():
    class Test:
        pass
    assert isClass(Test) == True