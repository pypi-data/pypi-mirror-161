Display SYSTEM info such as CPU/MEM on a floating window.

### Install

```
pip3 install fstats
```

### Usage

```
fstats &
```

### Config

fstats support user config, add the config file to `~/.fstats/`.

```json
{
    "width": 96,
    "height": 48,
    "style": "<HOME path>/.fstats/style.py",
    "items": [
        ["CPU", "<HOME path>/.fstats/cpu.py", "{:<3}: {:<5}%"],
        ["MEM", "<HOME path>/.fstats/mem.py", "{:<3}: {:<5}%"]
    ]
}
```

`width` & `height` descript the floating window's size.

CPU item (`cpu.py`):

```python
import psutil

def info():
    return psutil.cpu_percent(interval=1)
```

MEM item (`mem.py`):

```python
import psutil

def info():
    return psutil.virtual_memory().percent
```

Style config (`style.py`):

```python
# infoItems contains all items
#    infoItems: [item0, item1, ...]
#    item[0-n]: [name, value, format]
# label: tkinter Label 
def style(infoItems, label):
    high = False
    for item in infoItems:
        if item[0] in {'CPU', 'MEM'} and item[1] > 90:
            high = True
    if high:
        label['bg'] = 'red'
        label['fg'] = 'white'
    else:
        label['bg'] = 'white'
        label['fg'] = 'black'
```