# Copyright (C) 2005, Todd Whiteman
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

#===============================================================================
#                            I M P O R T S
#===============================================================================

import wx 
from wx.xrc import *
from pySIMconstants import *
from pySIMutils import *
from pySIMskin import *
from traceback import print_exc
from binascii import hexlify, unhexlify

ID_BUTTON_CHANGE_PIN = wx.NewId()

class topPanel(wxskinPanel):
    def __init__(self, parent, SIMcontrol, id=-1):
        wxskinPanel.__init__(self, parent, id, style=wx.SIMPLE_BORDER)
        self.parent = parent
        self.SIM = SIMcontrol
        self.createWidgets()

    def createWidgets(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Serial number: i.e. 8961080000000522829
        self.SIM.gotoFile(["3F00", "2FE2"])
        data, sw = self.SIM.sendAPDUmatchSW("A0B000000A", SW_OK)
        s = swapNibbles(removePadding(data))
        label = wxskinStaticText(self, -1, "Serial number:")
        text = wx.TextCtrl(self, -1, s, style=wx.TE_READONLY)
        fgs = wx.BoxSizer(wx.HORIZONTAL)
        fgs.Add(label, 1, wx.ALIGN_LEFT | wx.LEFT, 10)
        fgs.Add(text, 1, wx.ALIGN_RIGHT | wx.RIGHT, 10)
        sizer.Add(fgs, 1, wx.ALL, 5)

        # IMSI: i.e. 505084000052282
        self.SIM.gotoFile(["3F00", "7F20", "6F07"])
        self.SIM.checkAndVerifyCHV1(CHV_READ)
        data, sw = self.SIM.sendAPDUmatchSW("A0B0000009", SW_OK)
        s = swapNibbles(removePadding(data[2:]))[1:]
        label = wxskinStaticText(self, -1, "IMSI number:")
        text= wx.TextCtrl(self, -1, s, style=wx.TE_READONLY)
        fgs = wx.BoxSizer(wx.HORIZONTAL)
        fgs.Add(label, 1, wx.ALIGN_LEFT | wx.LEFT, 10)
        fgs.Add(text, 1, wx.ALIGN_RIGHT | wx.RIGHT, 10)
        sizer.Add(fgs, 1, wx.ALL, 5)

        # SIM Phase: i.e. 2+
        self.SIM.gotoFile(["3F00", "7F20", "6FAE"])
        data, sw = self.SIM.sendAPDUmatchSW("A0B0000001", SW_OK)
        if data == "00":
            s = 'Phase 1'
        elif data == "01":
            s = 'Phase 2'
        else:
            s = 'Phase 2+'
        label = wxskinStaticText(self, -1, "SIM phase:")
        text = wx.TextCtrl(self, -1, s, style=wx.TE_READONLY)
        fgs = wx.BoxSizer(wx.HORIZONTAL)
        fgs.Add(label, 1, wx.ALIGN_LEFT | wx.LEFT, 10)
        fgs.Add(text, 1, wx.ALIGN_RIGHT | wx.RIGHT, 10)
        sizer.Add(fgs, 1, wx.ALL, 5)

        self.SetSizer(sizer)
        self.SetAutoLayout(1) 
        sizer.Fit(self)
        sizer.Layout() 

class bottomPanel(wxskinPanel):
    def __init__(self, parent, SIMcontrol, id=-1):
        wxskinPanel.__init__(self, parent, id, style=wx.SIMPLE_BORDER)
        self.parent = parent
        self.SIM = SIMcontrol
        self.createWidgets()

    def createWidgets(self):
        sizer = wx.GridSizer(3,3,5,5)

        self.SIM.gatherInfo()
        sizer.Add(wx.Size(0,0), 10, 1, wx.LEFT, 10) # Spacer
        sizer.Add(wxskinStaticText(self, -1, "Activated"), 1, wx.LEFT | wx.RIGHT, 10)
        sizer.Add(wxskinStaticText(self, -1, "Tries left"), 1, wx.RIGHT, 10)

        sizer.Add(wxskinStaticText(self, -1, "PIN1"), 1, wx.LEFT, 10)
        if self.SIM.chv1_enabled:
            sizer.Add(wx.TextCtrl(self, -1, "Yes", style=wx.TE_READONLY), 1, wx.RIGHT, 10)
        else:
            sizer.Add(wx.TextCtrl(self, -1, "No", style=wx.TE_READONLY), 1, wx.RIGHT, 10)
        sizer.Add(wx.TextCtrl(self, -1, "%d" % self.SIM.chv1_tries_left, style=wx.TE_READONLY), 1, wx.RIGHT, 10)

        sizer.Add(wxskinStaticText(self, -1, "PIN2"), 1, wx.LEFT, 10)
        if self.SIM.chv2_enabled:
            sizer.Add(wx.TextCtrl(self, -1, "Yes", style=wx.TE_READONLY), 1, wx.RIGHT, 10)
        else:
            sizer.Add(wx.TextCtrl(self, -1, "No", style=wx.TE_READONLY), 1, wx.RIGHT, 10)
        sizer.Add(wx.TextCtrl(self, -1, "%d" % self.SIM.chv2_tries_left, style=wx.TE_READONLY), 1, wx.RIGHT, 10)

        self.SetSizer(sizer)
        self.SetAutoLayout(1) 
        sizer.Fit(self)
        sizer.Layout() 

class pySIMInfo(wxskinFrame):
    def __init__(self, parent, SIMcontrol):
        wxskinFrame.__init__(self, parent, -1, "SIM Information", size=(300,300))
        self.parent = parent
        self.SIM = SIMcontrol
        self.createWidgets()

    def createWidgets(self):
        # Main window resizer object
        sizer = wx.BoxSizer(wx.VERTICAL) 

        sizer.Add(topPanel(self, self.SIM), 1, wx.ALL|wx.EXPAND, 5)
        sizer.Add(bottomPanel(self, self.SIM), 1, wx.ALL|wx.EXPAND, 5)
        #buttons = wx.BoxSizer(wx.HORIZONTAL)
        #buttons.Add(wx.Button(self, ID_BUTTON_CHANGE_PIN, "Okay"), 1, wx.ALIGN_LEFT | wx.ALL, 20)
        #buttons.Add(wx.Button(self, wxID_CANCEL, "Cancel"), 1, wx.ALIGN_RIGHT | wx.ALL, 20)
        #sizer.Add(buttons, 1, wx.ALL)

        self.SetSizer(sizer) 
        self.SetAutoLayout(1) 
        sizer.Fit(self)
        self.Layout()

        wx.EVT_CLOSE(self, self.closeWindow)

    def closeWindow(self, event):
        self.Destroy()
