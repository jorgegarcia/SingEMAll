import wx
import os, sys
from SEMlogic import SEMprocess

wildcard = "MIDI file (*.mid)|*.mid|"\
           "All files (*.*)|*.*"

vocalists = ['ona', 'arnau', 'lara']
languages = ['english','spanish']

class SEMApp(wx.App):
    def __init__(self, redirect=False, filename=None):
        wx.App.__init__(self, redirect, filename)
        self.fileSelected = ""
        self.frame = wx.Frame(None, wx.ID_ANY, title='Sing-EM-All GUI')
        self.frame.SetSizeWH(690, 330)

        self.panel = wx.Panel(self.frame, wx.ID_ANY)
        
        self.inputText = wx.TextCtrl(self.panel, -1,
                        "Enter your kick ass phrase to sing, here",
                       size=(300, 50), style=wx.TE_MULTILINE|wx.TE_PROCESS_ENTER)
        
        self.loadfileButton = wx.Button(self.panel, -1, "Load MIDI file", (10, 60))
        self.Bind(wx.EVT_BUTTON, self.onOpenMidiFile, self.loadfileButton)
        
        wx.StaticText(self.panel, -1, "VOCALIST", (30, 100))
        self.vocalistsList = wx.ListBox(self.panel, 60, (30, 120), (90, 50), vocalists, wx.LB_SINGLE)
        self.vocalistsList.SetSelection(0)
        self.Bind(wx.EVT_LISTBOX, self.onVocalistSelected, self.vocalistsList)
        self.vocalistLanguage = wx.StaticText(self.panel, -1, "LANGUAGE\n\nSpanish", (130, 100))
        
        self.processButton = wx.Button(self.panel, -1, "SING IT!", (100, 190))
        self.statusText = wx.StaticText(self.panel, -1, "", (100, 225))
        self.Bind(wx.EVT_BUTTON, self.onSingButton, self.processButton)
        
        png = wx.Image('assets/sem_logo.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        wx.StaticBitmap(self.panel, -1, png, (300, 0), (png.GetWidth(), png.GetHeight()))
        
        self.playResultButton = wx.Button(self.panel, -1, "PLAY Result", (60, 250))
        self.stopResultButton = wx.Button(self.panel, -1, "STOP Result", (160, 250))
        self.playResultButton.Disable()
        self.stopResultButton.Disable()
        
        self.Bind(wx.EVT_BUTTON, self.onPlayButton, self.playResultButton)
        self.Bind(wx.EVT_BUTTON, self.onStopButton, self.stopResultButton)

        self.frame.Show()

    def onVocalistSelected(self, evt):
        if(self.vocalistsList.IsSelected(0)):
            self.vocalistLanguage.SetLabel("LANGUAGE\n\nSpanish")
        if(self.vocalistsList.IsSelected(1)):
            self.vocalistLanguage.SetLabel("LANGUAGE\n\nSpanish")
        if(self.vocalistsList.IsSelected(2)):
            self.vocalistLanguage.SetLabel("LANGUAGE\n\nEnglish")


    def onOpenMidiFile(self, evt):
        dlg = wx.FileDialog(
                            self.panel, message="Choose a file",
                            defaultDir=os.getcwd(), 
                            defaultFile="",
                            wildcard=wildcard,
                            style=wx.OPEN | wx.CHANGE_DIR
                            )

        if dlg.ShowModal() == wx.ID_OK:
            self.fileSelected = dlg.GetPath()
            wx.StaticText(self.panel, -1, dlg.GetFilename(), (120, 65))

        dlg.Destroy()

    def onSingButton(self, evt):
        if (self.fileSelected == ""):
            self.statusText.SetLabel("Select a MIDI file!")
        else:
            print self.fileSelected
            self.loadfileButton.Disable()
            self.inputText.Disable()
            self.vocalistsList.Disable()
            self.processButton.Disable()
            self.playResultButton.Disable()
            self.stopResultButton.Disable()
            self.process()
        
    def process(self):
        print self.inputText.GetValue()
        print self.vocalistsList.GetStringSelection()
        
        self.statusText.SetLabel("Processing...")
        
        self.panel.Update()
        self.loadfileButton.Update()
        
        logic = SEMprocess(self.vocalistsList.GetStringSelection(), self.inputText.GetValue())
        logic.processMidiFile(self.fileSelected)
        logic.processRequest()
        self.statusText.SetLabel("Ready!")
        
        self.playResultButton.Enable()
        self.stopResultButton.Enable()
        self.loadfileButton.Enable()
        self.inputText.Enable()
        self.vocalistsList.Enable()
        self.processButton.Enable()
        
    def onPlayButton(self, evt):
        self.statusText.SetLabel("Playing result...")
        self.sound = wx.Sound(str(os.path.realpath(os.path.dirname(sys.argv[0]))) + "/workfile.wav")
        self.sound.Play(wx.SOUND_ASYNC)
        
    def onStopButton(self, evt):
        self.statusText.SetLabel("")
        self.sound.Stop()
        
if __name__ == '__main__':
    app = SEMApp()
    app.MainLoop()
