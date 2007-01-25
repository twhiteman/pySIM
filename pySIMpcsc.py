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
from pySIMskin import *
from pySIMutils import *
from traceback import print_exc
from binascii import hexlify, unhexlify

try:
    PCSCImportError = 0
    import PCSCHandle
except ImportError:
    PCSCImportError = 1
    import traceback
    traceback.print_exc()

ID_LISTBOX = wx.NewId() 
ID_BUTTON_OK = wx.NewId() 
ID_BUTTON_CANCEL = wx.NewId() 

class PCSCcontroller(wxskinDialog):
    def __init__(self, parent):
        self.parent = parent
        wxskinDialog.__init__(self, parent, -1, "Select card reader",
                          wx.DefaultPosition, wx.DefaultSize, wx.DEFAULT_DIALOG_STYLE)
        self.state = SIM_STATE_DISCONNECTED
        self.readerName = ""
        self.chv1_enabled = 0
        self.chv1_tries_left = 0
        self.chv1 = ""
        self.chv2_enabled = 0
        self.chv2_tries_left = 0
        self.chv2 = ""
        self.FDN_available = 0
        self.phonebook = {}
        if PCSCImportError:
            self.pcsc = None
        else:
            self.pcsc = PCSCHandle.PCSCHandle()
        self.createLayout()
        # Don't show the select reader dialog yet
        self.Show(0)

    def createLayout(self):
        self.listbox = wx.ListBox(self, ID_LISTBOX, wx.DefaultPosition, wx.DefaultSize, [],
                                 wx.LB_SINGLE | wx.LB_SORT, wx.DefaultValidator)
        self.listbox.typedText = ""

	try:
		s = self.pcsc.listAllReaders()
	except:
		print_exc()
        for i in s.split("\t"):
            if i:
                self.listbox.Append(i)

        self.bOK = wx.Button(self, ID_BUTTON_OK, "OK")
        self.bCancel = wx.Button(self, ID_BUTTON_CANCEL, "Cancel")

        self.sizer1 = wx.BoxSizer(wx.VERTICAL)
        self.sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer2.Add(self.bOK, 1, wx.EXPAND|wx.ALL,10)
        self.sizer2.Add(self.bCancel, 1, wx.EXPAND|wx.ALL,10)
        self.sizer1.Add(self.listbox, 1, wx.EXPAND|wx.ALL,20)
        self.sizer1.Add(self.sizer2)
        self.SetSizer(self.sizer1)
        self.SetAutoLayout(1)
        self.sizer1.Fit(self)

        wx.EVT_LISTBOX_DCLICK(self, ID_LISTBOX, self.selectNewReaderOK)
        wx.EVT_BUTTON(self, ID_BUTTON_OK, self.selectNewReaderOK)
        wx.EVT_BUTTON(self, ID_BUTTON_CANCEL, self.selectNewReaderCancel)

    def getState(self):
        return self.state

    def getReaderName(self):
        return self.readerName

    def connectReader(self):
        if not self.getReaderName():
            self.selectNewReader()
        if self.getReaderName():
            res = self.pcsc.openSession(self.getReaderName(), SCARD_PROTOCOL_T0)
            if res == 0:
                self.state = SIM_STATE_CONNECTED
                self.gatherInfo()
            else:
                #~ print "Blah blah"
                dlg = wx.MessageDialog(self, 'Unable to connect to reader: %s' % self.getReaderName(), 'Reader error', 
                                     wx.OK | wx.ICON_INFORMATION) 
                dlg.ShowModal() 
                dlg.Destroy()
                self.readerName = ""

    def disconnectReader(self):
        if self.pcsc.closeSession() == 0:
            self.state = SIM_STATE_DISCONNECTED
        self.readerName = ""
        self.chv1 = ""
        self.phonebook = {}

    def selectNewReader(self):
        self.ShowModal()

    def selectNewReaderOK(self, *args):
        self.readerName = self.listbox.GetStringSelection()
        self.closeDialog()

    def selectNewReaderCancel(self, *args):
        self.closeDialog()

    def sendAPDU(self, command):
        """sendAPDU(pdu)
        
            command : string of hexadecimal characters (ex. "A0A40000023F00")
            result  : tuple(data, sw), where
                      data : string (in hex) of returned data (ex. "074F4EFFFF")
                      sw   : string (in hex) of status word (ex. "9000")
        """

        data = self.pcsc.sendAPDU(command)
        #print "In:  " + command
        #print "Out: " + data
        if len(data) > 4:
            return data[:-4], data[-4:]
        else:
            return '', data

    def sendAPDUmatchSW(self, command, matchSW):
        """sendAPDUmatchSW(pdu)
        
            command : string of hexadecimal characters (ex. "A0A40000023F00")
            matchSW : string of 4 hexadecimal characters (ex. "9000")
            result  : tuple(data, sw), where
                      data : string (in hex) of returned data (ex. "074F4EFFFF")
                      sw   : string (in hex) of status word (ex. "9000")
        """
        
        data, sw = self.sendAPDU(command)
        if sw != matchSW:
            raise RuntimeError("Status words do not match. Result: %s, Expected: %s" % (sw, matchSW))
        return data, sw

    def gatherInfo(self):
        try:
            self.gotoFile(["3F00"])
            data, sw = self.sendAPDUmatchSW("A0F200000D", SW_OK)
            l = 0x0D + int(data[24:26], 16)
            data, sw = self.sendAPDUmatchSW("A0F20000%s" % IntToHex(l), SW_OK)
            s = unhexlify(data)

            # Check whether CHV1 is enabled
            self.chv1_enabled = 1
            if ord(s[13]) & 0x80:
                self.chv1_enabled = 0

            # Get number of CHV1 attempts left (0 means blocked, oh crap!)
            self.chv1_tries_left = ord(s[18]) & 0x0F

            # 0000000C3F000100000000030A93070A0400838A838A00
            if len(s) >= 22:
                # Get number of CHV2 attempts left (0 means blocked, oh crap!)
                self.chv2_enabled = 1
                self.chv2_tries_left = ord(s[20]) & 0x0F
                
            # See if the FDN file exists
            try:
                self.SIM.gotoFile(["3F00", "7F10", "6F3B"])
                self.FDN_available = 1
            except:
                pass
        except:
            print_exc()
            pySIMmessage(self, "Unable to gather information about your card.", "SIM card error")

    def gotoFile(self, dirList):
        for i in dirList:
            data, sw = self.sendAPDU("A0A4000002%s" % i)
            if sw[0:2] != SW_FOLDER_SELECTED_OK[0:2]:
                raise RuntimeError("Cannot select file/folder %s" % i)

    def checkAndVerifyCHV1(self, checktype=CHV_UPDATE, data=None):
        if not self.chv1_enabled:
            # No PIN set on this card
            return 1
        if self.chv1:
            # Must have verified successfully already
            return 1

        # Issue the status command if we don't already have the data
        if not data:
            data, sw = self.sendAPDUmatchSW("A0C000000F", SW_OK)

        # Check if CHV1 is needed for this function (read / write)
        # 000007DF3F000100 00 444401071302
        if checktype == CHV_ALWAYS:
            val = 1
        elif checktype & CHV_UPDATE:
            val = int(data[17], 16)
        else: # Must be checking for read access
            val = int(data[16], 16)

        if val == 0: # means we don't need chv1, always access is set
            return 1
        elif val == 1: # means chv1 is needed, try and verify it
            # Have not verified yet, try now, ask for the PIN number
            dlg = wxskinTextEntryDialog(self, 'Enter your PIN (4 to 8 digits) :', 'PIN verification', '', style=wx.TE_PASSWORD|wx.OK|wx.CANCEL)
            ret = dlg.ShowModal()
            self.chv1 = dlg.GetValue()
            dlg.Destroy()

            if ret == wx.ID_OK:
                ok = True
                for i in self.chv1:
                    if i not in "0123456789":
                        ok = False
                if len(self.chv1) < 4 or len(self.chv1) > 8:
                    ok = False

                if not ok:
                    pySIMmessage(self, "Invalid PIN! Must be 4 to 8 digits long\n\nDigits are these characters: 0123456789", "SIM card error")
                    return 0
                try:
                    self.sendAPDUmatchSW("A020000108%s" % ASCIIToPIN(self.chv1), SW_OK)
                    return 1
                except:
                    self.chv1 = ''
                    pySIMmessage(self, "Incorrect PIN!", "SIM card error")
                    print_exc()

        # Must need CHV2 or ADM access, foo-ey!
        return 0

    def closeDialog(self):
        self.Show(0)
