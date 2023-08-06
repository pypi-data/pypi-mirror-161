# commons

## Build guide

### Make sure you have upgraded version of pip

Windows

```
py -m pip install --upgrade pip
```

Linux/MAC OS

```
python3 -m pip install --upgrade pip
```

### Make sure your build tool is up to date

Windows

```
py -m pip install --upgrade build
```

Linux/MAC OS

```
python3 -m pip install --upgrade build
```

### Create the build

Windows

```
py -m build
```

Linux/MAC OS

```
python3 -m build
```

### Uploading the distribution archives

Windows

```
py -m pip install --upgrade twine
```

Linux/MAC OS

```
python3 -m pip install --upgrade twine
```

Once installed, run Twine to upload all of the archives under dist:

Windows

```
py -m twine upload --repository testpypi dist/*
```

Linux/MAC OS

```
python3 -m twine upload --repository testpypi dist/*
```

### References

https://packaging.python.org/tutorials/packaging-projects/