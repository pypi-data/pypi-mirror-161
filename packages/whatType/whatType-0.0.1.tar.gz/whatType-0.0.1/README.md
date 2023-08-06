# ✅ whatType
Python package to check the type of a variable or object.  

## 🚀 Usage

```python
from whatType import *

# Check for 'function' type
def test():
    pass
isFunction(test) # Returns True

# Check for 'int' type
isInt(1234) # Returns True

# Check for 'float' type
isFloat(3.1415) # Returns True

# Check for 'complex' type
isComplex(3+4j) # Returns True

# Check for 'str' type
isStr('Hello, World!') # Returns True

# Check for 'list' type
isList([1,2,3]) # Returns True

# Check for 'dict' type
isDict({"hello":"world"}) # Returns True

# Check for 'tuple' type
isTuple((1,2,3))

# Check for 'NoneType' type
isNone(None) # Returns True

# Check for 'bool' type
isBool(True) # Returns True

# Check for 'bytes' type
isBytes(b'Hello, World!') # Returns True

# Check for 'type' (class) type
class Test:
    pass
isClass(Test)
```

## 📦 Installation

Run the following to install:  

```bash
$ pip install whatType
```

## 👨‍💻 Developing isType

To install whatType, along with the tools you will need to develop and run tests, run the following in your virtualenv:  

```bash
$ pip install -e .[dev]
```

## 🚦 Development Progress

Unstable Development  