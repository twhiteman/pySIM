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

from wxPython.wx import *
from wxPython.xrc import *
from pySIMconstants import *
from pySIMutils import *
from pySIMskin import *
from traceback import print_exc
from binascii import hexlify, unhexlify

ID_BUTTON_CHANGE_PIN = wxNewId()

class topPanel(wxskinPanel):
    def __init__(self, parent, SIMcontrol, id=-1):
        wxskinPanel.__init__(self, parent, id, style=wxSIMPLE_BORDER)
        self.parent = parent
        self.SIM = SIMcontrol
        self.createWidgets()

    def createWidgets(self):
        sizer = wxBoxSizer(wxVERTICAL)

        # Serial number: i.e. 8961080000000522829
        self.SIM.gotoFile(["3F00", "2FE2"])
        data, sw = self.SIM.sendAPDUmatchSW("A0B000000A", SW_OK)
        s = swapNibbles(removePadding(data))
        label = wxskinStaticText(self, -1, "Serial number:")
        text = wxTextCtrl(self, -1, s, style=wxTE_READONLY)
        fgs = wxBoxSizer(wxHORIZONTAL)
        fgs.Add(label, 1, wxALIGN_LEFT | wxLEFT, 10)
        fgs.Add(text, 1, wxALIGN_RIGHT | wxRIGHT, 10)
        sizer.Add(fgs, 1, wxALL, 5)

        # IMSI: i.e. 505084000052282
        self.SIM.gotoFile(["3F00", "7F20", "6F07"])
        self.SIM.checkAndVerifyCHV1(CHV_READ)
        data, sw = self.SIM.sendAPDUmatchSW("A0B0000009", SW_OK)
        s = swapNibbles(removePadding(data[2:]))[1:]
        label = wxskinStaticText(self, -1, "IMSI number:")
        text= wxTextCtrl(self, -1, s, style=wxTE_READONLY)
        fgs = wxBoxSizer(wxHORIZONTAL)
        fgs.Add(label, 1, wxALIGN_LEFT | wxLEFT, 10)
        fgs.Add(text, 1, wxALIGN_RIGHT | wxRIGHT, 10)
        sizer.Add(fgs, 1, wxALL, 5)

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
        text = wxTextCtrl(self, -1, s, style=wxTE_READONLY)
        fgs = wxBoxSizer(wxHORIZONTAL)
        fgs.Add(label, 1, wxALIGN_LEFT | wxLEFT, 10)
        fgs.Add(text, 1, wxALIGN_RIGHT | wxRIGHT, 10)
        sizer.Add(fgs, 1, wxALL, 5)

        self.SetSizer(sizer)
        self.SetAutoLayout(1) 
        sizer.Fit(self)
        sizer.Layout() 

class bottomPanel(wxskinPanel):
    def __init__(self, parent, SIMcontrol, id=-1):
        wxskinPanel.__init__(self, parent, id, style=wxSIMPLE_BORDER)
        self.parent = parent
        self.SIM = SIMcontrol
        self.createWidgets()

    def createWidgets(self):
        sizer = wxGridSizer(3,3,5,5)

        self.SIM.gatherInfo()
        sizer.Add(0,10, 1, wxLEFT, 10) # Spacer
        sizer.Add(wxskinStaticText(self, -1, "Activated"), 1, wxLEFT | wxRIGHT, 10)
        sizer.Add(wxskinStaticText(self, -1, "Tries left"), 1, wxRIGHT, 10)

        sizer.Add(wxskinStaticText(self, -1, "PIN1"), 1, wxLEFT, 10)
        if self.SIM.chv1_enabled:
            sizer.Add(wxTextCtrl(self, -1, "Yes", style=wxTE_READONLY), 1, wxRIGHT, 10)
        else:
            sizer.Add(wxTextCtrl(self, -1, "No", style=wxTE_READONLY), 1, wxRIGHT, 10)
        sizer.Add(wxTextCtrl(self, -1, "%d" % self.SIM.chv1_tries_left, style=wxTE_READONLY), 1, wxRIGHT, 10)

        sizer.Add(wxskinStaticText(self, -1, "PIN2"), 1, wxLEFT, 10)
        if self.SIM.chv2_enabled:
            sizer.Add(wxTextCtrl(self, -1, "Yes", style=wxTE_READONLY), 1, wxRIGHT, 10)
        else:
            sizer.Add(wxTextCtrl(self, -1, "No", style=wxTE_READONLY), 1, wxRIGHT, 10)
        sizer.Add(wxTextCtrl(self, -1, "%d" % self.SIM.chv2_tries_left, style=wxTE_READONLY), 1, wxRIGHT, 10)

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
        sizer = wxBoxSizer(wxVERTICAL) 

        sizer.Add(topPanel(self, self.SIM), 1, wxALL|wxEXPAND, 5)
        sizer.Add(bottomPanel(self, self.SIM), 1, wxALL|wxEXPAND, 5)
        #buttons = wxBoxSizer(wxHORIZONTAL)
        #buttons.Add(wxButton(self, ID_BUTTON_CHANGE_PIN, "Okay"), 1, wxALIGN_LEFT | wxALL, 20)
        #buttons.Add(wxButton(self, wxID_CANCEL, "Cancel"), 1, wxALIGN_RIGHT | wxALL, 20)
        #sizer.Add(buttons, 1, wxALL)

        self.SetSizer(sizer) 
        self.SetAutoLayout(1) 
        sizer.Fit(self)
        self.Layout()

        EVT_CLOSE(self, self.closeWindow)

    def closeWindow(self, event):
        self.Destroy()
