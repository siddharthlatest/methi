import wx
import threading
import os
from subprocess import Popen
from time import sleep
import platform

import Common

TRAY_TOOLTIP = 'Appbin'
TRAY_ICON = '1.ico'


def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.AppendItem(item)
    return item


class TaskBarIcon(wx.TaskBarIcon):
    def __init__(self, stateQ, iconQ):
        super(TaskBarIcon, self).__init__()
        self.set_icon(TRAY_ICON)
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.launchClient)
        self.stateQ = stateQ
        self.iconQ = iconQ

    def CreatePopupMenu(self):
        menu = wx.Menu()
        create_menu_item(menu, 'Appbin', self.launchClient)
        create_menu_item(menu, 'Open Logs', self.openLogs)
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def set_icon(self, path):
        icon = wx.IconFromBitmap(wx.Bitmap(path))
        self.SetIcon(icon, TRAY_TOOLTIP)

    def on_left_down(self, event):
        pass
        #print 'Tray icon was left-clicked.'

    def launchClient(self, event):
		if platform.system()=='Linux':
			Popen("./appbin")
		else:
			Popen("appbin.bat")

    def openLogs(self, event):
        if platform.system()=='Linux':
            Popen(["nano", "../data/daemon_logs.log"])
        else:
            Popen(["notepad.exe", "../data/daemon_logs.log"])

    def on_hello(self, event):
        print 'Hello, world!'

    def on_exit(self, event):
        self.stateQ.put("-1")
        self.iconQ.put("exit")
        sleep(10)
        os._exit(0)
        wx.CallAfter(self.Destroy)


def iconPoller(tb, iconQ):
    while True:
        icon = iconQ.get()
        if icon == "exit":
            return
        tb.set_icon(icon)

def startGUI(iconQ, stateQ):
    app = wx.PySimpleApp()
    tb = TaskBarIcon(stateQ, iconQ)
    t = threading.Thread(target=iconPoller, args=(tb, iconQ))
    t.start()
    app.MainLoop()