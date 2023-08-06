# pathwin

**setPath is a library for easy manipulation of the Windows environment variable Path.**

```python
import pathwin

examplePath = "C:\\example\\"

# Manipulation of system environment variables
pathwin = Path(True)

# Manipulation of user environment variables
pathwin = Path(False)

# get Path
existPath = pathwin.getPath()
# -> "C:\\example;C:\\example2"

existPathList = pathwin.getPathList()
# -> ["C:\\example", "C:\\example2"]

# Path Override
pathwin.setPath(existPath + ";" + examplePath)

# Add to top
pathwin.addPath(examplePath)

# Fourth Add to
pathwin.addPath(examplePath, 3)

# delete path
pathwin.removePath(examplePath)

```


## Installing pathwin and Supported Versions
```bash
pip install pathwin
```




