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
from pySIMconstants import *
from pySIMutils import *
from pySIMskin import *
from traceback import print_exc
from binascii import hexlify, unhexlify

ID_BUTTON_CHANGE_PIN = wx.NewId()

class ChangePin(wxskinDialog):
    def __init__(self, parent, SIMcontrol):
        wxskinDialog.__init__(self, parent, -1, "Change your PIN")
        self.oldpin = None
        self.newpin1 = None
        self.newpin2 = None
        self.parent = parent
        self.SIM = SIMcontrol
        self.createWidgets()

    def createWidgets(self):
        # Main window resizer object
        border = wx.BoxSizer(wx.VERTICAL)

        label = wxskinStaticText(self, -1, "Your old and new PIN must be exactly 4 digits in length.")
        border.Add(label, 1, wx.ALL, 10)

        fgs = wx.BoxSizer(wx.HORIZONTAL)
        label = wxskinStaticText(self, -1, "Current PIN: ")
        fgs.Add(label, 1, wx.ALIGN_LEFT | wx.LEFT, 10)
        if self.SIM.chv1_enabled:
            self.textCtrlOldPin = wx.TextCtrl(self, -1, '', validator = pySIMvalidator("0123456789", 4, 4), style=wx.TE_PASSWORD)
        else:
            self.textCtrlOldPin = wx.TextCtrl(self, -1, '(Not set)', style=wx.TE_READONLY)
        fgs.Add(self.textCtrlOldPin, 1, wx.ALIGN_RIGHT | wx.RIGHT, 10)
        border.Add(fgs, 1, wx.ALL)

        fgs = wx.BoxSizer(wx.HORIZONTAL)
        label = wxskinStaticText(self, -1, "New PIN: ")
        fgs.Add(label, 1, wx.ALIGN_LEFT | wx.LEFT, 10)
        self.textCtrlNewPin1 = wx.TextCtrl(self, -1, '', validator = pySIMvalidator("0123456789", 4, 4), style=wx.TE_PASSWORD)
        fgs.Add(self.textCtrlNewPin1, 1, wx.ALIGN_RIGHT | wx.RIGHT, 10)
        border.Add(fgs, 1, wx.ALL)

        fgs = wx.BoxSizer(wx.HORIZONTAL)
        label = wxskinStaticText(self, -1, "New PIN (verify): ")
        fgs.Add(label, 1, wx.ALIGN_LEFT | wx.LEFT, 10)
        self.textCtrlNewPin2 = wx.TextCtrl(self, -1, '', validator = pySIMvalidator("0123456789", 4, 4), style=wx.TE_PASSWORD)
        fgs.Add(self.textCtrlNewPin2, 1, wx.ALIGN_RIGHT | wx.RIGHT, 10)
        border.Add(fgs, 1, wx.ALL)

        buttons = wx.BoxSizer(wx.HORIZONTAL)
        buttons.Add(wx.Button(self, ID_BUTTON_CHANGE_PIN, "Okay"), 1, wx.ALIGN_LEFT | wx.ALL, 20)
        buttons.Add(wx.Button(self, wx.ID_CANCEL, "Cancel"), 1, wx.ALIGN_RIGHT | wx.ALL, 20)
        border.Add(buttons, 1, wx.ALL)

        wx.EVT_BUTTON(self, ID_BUTTON_CHANGE_PIN, self.onOK)

        self.SetAutoLayout(1);
        self.SetSizer(border)
        border.Fit(self)
        self.Layout()

    def getValues(self):
        return (self.nameCtrl.GetValue(), self.numberCtrl.GetValue())

    def onOK(self, event):
        if self.Validate() and self.TransferDataFromWindow():
            if self.textCtrlNewPin1.GetValue() != self.textCtrlNewPin2.GetValue():
                pySIMmessage(self, "New PINs do not match!", "SIM card error")
                return
            
            if not self.SIM.chv1_enabled:
                # Enable CHV 'A028000108'
                apdu = "A028000108%s" % ASCIIToPIN(self.textCtrlNewPin1.GetValue())
            else:
                # Change CHV
                apdu = "A024000110%s%s" % (ASCIIToPIN(self.textCtrlOldPin.GetValue()), ASCIIToPIN(self.textCtrlNewPin1.GetValue()))

            try:
                self.SIM.sendAPDUmatchSW(apdu, SW_OK)
                self.SIM.chv1_enabled = 1
                self.chv1 = self.textCtrlNewPin1.GetValue()
            except:
                print "apdu: %r" % (apdu, )
                print_exc()
                pySIMmessage(self, "Invalid PIN!", "SIM card error")
                return

            pySIMmessage(self, "PIN was set successfully!", "Change PIN")
            self.EndModal(wx.ID_OK)
