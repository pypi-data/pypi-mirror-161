A package encapsulating a few frequently used functions for faster Python programming. 

## Install
`python3 -m pip install codefast`

Or, update to latest version with:

`python3 -m pip install codefast --upgrade`


## Usage
### 1. Manipulate JSON Files
```python
import codefast as cf
# read file
json_content = jsn.read('json_file.json')
# write file
json.write(json_content, '/tmp/json_file.json)
```

### 2. Manipulate CSV Files
```python
import codefast as cf
# read file
content = cf.csv.read('somefile.csv')
# write file
cf.csv.write(content, 'somefile.csv')
```

### 3. Manipulate normal Files
```python
import codefast as cf
# read file
content = io.read('somefile.txt')
# or content = cf.file.read

# write file
io.write(content, 'somefile.txt')
```

### 4. Logging
```python
import codefast as cf
cf.info("Here we go")
cf.warn("Not good, something went wrong")
cf.error("Unexpected result")
```

### 5. Others
```python
import codefast as cf
cf.post('www.abcde.com', json={}) # encapsulate requests.post
cf.get('wwww.example.com') # encapsulate requests.get
cf.shell('ls -lt') # run system command
```

