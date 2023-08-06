from time import sleep
from tkinter import *
import threading
import psutil
import json
import os
from importlib.machinery import SourceFileLoader


HeightDefault = 48
WidthDefault = 96


class DiskInfoDefault():
    @staticmethod
    def info():
        return psutil.disk_usage('/')


class CPUInfoDefault():
    @staticmethod
    def info():
        return psutil.cpu_percent(interval=1)


class MEMInfoDefault():
    @staticmethod
    def info():
        return psutil.virtual_memory().percent


class StyleDefault():
    @staticmethod
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


ItemsDefault = [
    ["CPU", CPUInfoDefault, "{:<3}: {:<5}%"],
    ["MEM", MEMInfoDefault, "{:<3}: {:<5}%"],
]


def ModuleLoader(name, module):
    if isinstance(module, str):
        return {
            'py': SourceFileLoader(name, module).load_module(),
        }[module.split('.')[-1]]
    else:
        return module


def V1Constructor(item):
    return [
        item[0],
        None,
        item[2],
        ModuleLoader(item[0], item[1]),
    ]


def V2Constructor(item):
    return {
        "header": item[0],
        "content": None,
        "format": item[2],
        "module": ModuleLoader(item[0], item[1]),
    }


def V1ReadInfo(items):
    for item in items:
        item[1] = item[-1].info()


def V2ReadInfo(items):
    for item in items:
        item['content'] = item['module'].info()


def V1Info(items):
    return '\n'.join([item[2].format(item[0], item[1])
                      for item in items])


def V2Info(items):
    return '\n'.join([item['format'].format(
        item['header'], item['content']) for item in items])


ItemsVersionMethod = {
    'v1': {
        'constructor': V1Constructor,
        'info': V1Info,
        'read': V1ReadInfo,
    },
    'v2': {
        'constructor': V2Constructor,
        'info': V2Info,
        'read': V2ReadInfo,
    },
}


def config():
    userConfigPath = os.path.join(os.environ["HOME"], ".fstats", "config.json")
    if os.path.exists(userConfigPath):
        with open(userConfigPath, 'rb') as f:
            return True, json.load(f)
    else:
        return False, None


_user, _config = config()


def get(keys, dft, conf=_config):
    if not _user:
        return dft
    if len(keys) <= 0:
        return dft
    key = keys[0]
    if key in conf.keys():
        if len(keys) == 1:
            return conf[key]
        else:
            return get(keys[1:], dft, conf[key])
    else:
        return dft


def winCreate():
    win = Tk()
    win.title('fstats')
    win.configure(bg='white')
    win.overrideredirect(True)
    global mouseMenu
    mouseMenu = None

    width = win.winfo_screenwidth()
    heigth = win.winfo_screenheight()

    win.attributes('-type', 'black')
    win.attributes('-zoomed', False)
    win.attributes('-alpha', '0.8')
    win.attributes('-topmost', True)

    userWidth = get(['width'], WidthDefault)
    userHeight = get(['height'], HeightDefault)
    win.geometry('{}x{}+{}+{}'.format(userWidth, userHeight,
                 width - userWidth - 50, heigth - userHeight - 50))
    win.resizable(width=0, height=0)

    def DestroyMenu():
        global mouseMenu
        if isinstance(mouseMenu, Menu):
            mouseMenu.destroy()

    def StartMove(event):
        DestroyMenu()
        win.x = event.x
        win.y = event.y

    def StopMove(event):
        win.x = None
        win.y = None

    def OnMotion(event):
        deltax = event.x - win.x
        deltay = event.y - win.y
        x = win.winfo_x() + deltax
        y = win.winfo_y() + deltay
        win.geometry("+%s+%s" % (x, y))

    win.bind("<ButtonPress-1>", StartMove)
    win.bind("<ButtonRelease-1>", StopMove)
    win.bind("<B1-Motion>", OnMotion)

    def destroy():
        win.destroy()

    def popupmenu(event):
        DestroyMenu()
        global mouseMenu
        mouseMenu = Menu(win)
        mouseMenu.add_command(label='退出', command=destroy)
        mouseMenu.add_command(label='取消', command=mouseMenu.destroy)
        mouseMenu.post(event.x_root, event.y_root)

    win.bind("<ButtonPress-3>", popupmenu)

    return win


def intervalProcess(win):
    textvariable = StringVar()

    label = Label(win, justify='left', anchor='center', bg='white', fg='black', cursor='fleur',
                  font=('Monospace', 10),
                  width=win.winfo_screenwidth(), height=win.winfo_screenheight(),
                  textvariable=textvariable)
    label.pack(padx=0, pady=0)

    def refresh(textvariable):
        style = get(["style"], StyleDefault)
        items = get(["items"], ItemsDefault)
        versionMethod = ItemsVersionMethod[get(["version"], 'v1')]

        style = ModuleLoader('style', style)
        infoItems = [versionMethod['constructor'](item) for item in items]

        while True:
            versionMethod['read'](infoItems)
            style.style(infoItems, label)
            info = versionMethod['info'](infoItems)
            textvariable.set(info)

    thread = threading.Thread(target=refresh, args=(textvariable,))
    thread.daemon = True
    thread.start()


def main():
    win = winCreate()
    intervalProcess(win)
    win.mainloop()


if __name__ == '__main__':
    main()
