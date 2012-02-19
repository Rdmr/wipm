#!/usr/bin/env python

# Author : Radomir Azizov
 
import os
import wx
import wx.lib.agw.flatnotebook as fnb
from MySTC import MySTC as PyTextCtrl
from ConfigParser import ConfigParser
import serial
import wxSerialConfigDialog


class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        # config init
        #cfg_defaults = {'port' : '/dev/ttyACM0', 'baudrate' : '19200', 'pmfeatures': '.', 'main_size': '600,600'}
        self.cfg = ConfigParser()
        self.cfg_path = os.path.abspath('.') + '/cfg.ini'
        self.cfg.read(self.cfg_path)
              
        size = map(int,self.cfg.get('MAIN','size').split(','))
        wx.Frame.__init__(self, parent, title = title, size = size)
        #Init notebook
        self.notebook = fnb.FlatNotebook(self, wx.ID_ANY, agwStyle = fnb.FNB_MOUSE_MIDDLE_CLOSES_TABS | fnb.FNB_NO_TAB_FOCUS | fnb.FNB_X_ON_TAB | fnb.FNB_SMART_TABS | fnb.FNB_DROPDOWN_TABS_LIST | fnb.FNB_FF2)
        self.textControls = []
        self.NewTab()

        self.CreateRightClickOnTabMenu()
        self.notebook.SetRightClickMenu(self._rmenu)
        
        #Init docking windows
        self.CreateMenuBar()
        self.CreateStatusBar() # A StatusBar in the bottom of the window        

        self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CONTEXT_MENU, self.OnNotebookContextMenu)
        self.notebook.Bind(fnb.EVT_FLATNOTEBOOK_PAGE_CLOSED, self.OnCloseTab)

        self.Centre()
        self.Show(True)

    def OnDummy(self, event):
        pass
        
    def onPathSettings(self, event):
         dlg = wx.DirDialog(self, "Choose a directory with pmfeatures.py:")
         if dlg.ShowModal() == wx.ID_OK:
            self.cfg.set('MAIN', 'pmfeatures', dlg.GetPath())
            f = open(self.cfg_path, "w")
            self.cfg.write(f)
            f.close()
         dlg.Destroy()
       

    def CreateMenuBar(self):
        menuData = (("&File",
                     ("&New", "Create new file", self.OnNewTab),   
                     ("&Open", "Open existing file", self.OnOpen),
                     ("&Save", "Save existing file", self.OnSave),
                     ("&Save as", "Save existing file as", self.OnSaveAs),
                     ("&Quit", "Quit", self.OnExit)),
                    ("&Settings",
                     ("&Port settings", "Serial port settings", self.OnPortSettings),
                     ("&Project folder", "Folder with pmfeatures.py", self.onPathSettings)),
                    ("&Help",
                     ("&About", "About", self.OnAbout),
                     ))
    
    
        menuBar = wx.MenuBar()                                                                
        for eachMenuData in menuData:
              menuLabel = eachMenuData[0]
              menuItems = eachMenuData[1:]
              menuBar.Append(self.createMenu(menuItems), menuLabel)
        self.SetMenuBar(menuBar)
        
    def createMenu(self, menuData):
        menu = wx.Menu()
        for menuLabel, menuStatus, menuHandler in menuData:
              if menuLabel:
                  menuItem = menu.Append(-1, menuLabel, menuStatus)
                  self.Bind(wx.EVT_MENU, menuHandler, menuItem)
              else:
                  menu.AppendSeparator()              
        return menu

    def OnNotebookContextMenu(self, e):
        self.notebook.SetSelection(e.GetSelection())

    def CreateRightClickOnTabMenu(self):
        self._rmenu = wx.Menu()
        item = wx.MenuItem(self._rmenu, wx.ID_ANY,
                           "Close Tab\tCtrl+F4",
                           "Close Tab")
        self.Bind(wx.EVT_MENU, self.onDeletePage, item)
        self._rmenu.AppendItem(item)
        
    def onDeletePage(self, event):
        """
        Removes a page from the notebook
        """
        self.notebook.DeletePage(self.notebook.GetSelection())

    def OnAbout(self,e):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog(self, "GUI for IPM\nmailto: Radomir.Azizov@gmail.com\nWipm v0.8  02.2012", "About", wx.OK)
        dlg.ShowModal() # Show it
        dlg.Destroy() # finally destroy it when finished.

    def OnExit(self,e):
        self.Close(True)  # Close the frame.

        
    def OnSave(self, e):
        """ Save a file"""
        page, filename = self.textControls[self.notebook.GetSelection()]
        if filename:
            page.SaveFile(filename)
        else:
            self.OnSaveAs(e)
        
    def OnSaveAs(self, e):
        """ Save a file"""
        dlg = wx.FileDialog(self, "Choose a file", "", "", "*.py", wx.SAVE  | wx.OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            filename = os.path.join(dlg.GetDirectory(), dlg.GetFilename())
            self.notebook.GetCurrentPage().SaveFile(filename)
            self.notebook.SetPageText(self.notebook.GetSelection(), dlg.GetFilename())
            page, tmp = self.textControls[(e.GetSelection())]
            self.textControls[(e.GetSelection())] = page, filename
        dlg.Destroy()
        
    def NewTab(self, title = "Untitled", filename = None):
        tab = PyTextCtrl(self.notebook, self)
        self.textControls.append((tab, filename))
        self.notebook.AddPage(tab, title)
        self.notebook.SetSelection(len(self.textControls)-1)    
        
    def OnOpen(self, e):
        """ Open a file"""
        dlg = wx.FileDialog(self, "Choose a file", "", "", "*.py", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            dirname = dlg.GetDirectory()
            fullfilename = os.path.join(dirname, filename)
            self.NewTab(filename)
            #self.notebook.GetCurrentPage().LoadFile(fullfilename)
            for s in open(fullfilename).readlines():
                self.notebook.GetCurrentPage().loadStr(s)
        dlg.Destroy()
        
    def OnNewTab(self, e):
        self.NewTab()
        
    def OnCloseTab(self, e):
        self.textControls.pop(e.GetSelection())
        
    def OnPortSettings(self,e):
        ser = serial.Serial()
             
        dialog_serial_cfg = wxSerialConfigDialog.SerialConfigDialog(None, -1, "", show=wxSerialConfigDialog.SHOW_BAUDRATE, serial = ser)
        result = dialog_serial_cfg.ShowModal()
        dialog_serial_cfg.Destroy()
        if result == wx.ID_OK or e is not None:
                self.cfg.set('SERIAL', 'port', ser.portstr)
                self.cfg.set('SERIAL', 'baudrate', ser.baudrate)
                #self.cfg.set('SERIAL', 'bytesize', serial.bytesize)
                #self.cfg.set('SERIAL', 'parity', serial.parity)
                #self.cfg.set('SERIAL', 'stopbits', serial.stopbits)
                #self.cfg.set('SERIAL', 'rtscts', serial.rtscts)
                f = open(self.cfg_path, "w")
                self.cfg.write(f)
                f.close()

app = wx.App(False)
frame = MainWindow(None, "wipm")
app.MainLoop()

