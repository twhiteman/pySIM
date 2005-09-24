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

backgroundColour = wxColour(230, 230, 255)

################################################################################
#                           pySIM skin helper classes                          #
################################################################################

class wxskinFrame(wxFrame):
    def __init__(self, parent, ID=-1, title="Frame", pos=wxPyDefaultPosition, size=wxPyDefaultSize):
        wxFrame.__init__(self, parent, ID, title, pos, size)
        self.SetBackgroundColour(backgroundColour)
        icon = wxIcon('pySIM.ico', wxBITMAP_TYPE_ICO)
        self.SetIcon(icon)

class wxskinPanel(wxPanel):
    def __init__(self, parent, ID=-1, pos=wxPyDefaultPosition, size=wxPyDefaultSize, style=wxTAB_TRAVERSAL, name="panel"):
        wxPanel.__init__(self, parent, ID, pos, size, style, name)
        self.SetBackgroundColour(backgroundColour)

class wxskinDialog(wxDialog):
    def __init__(self, parent, id=-1, title="Dialog", pos=wxPyDefaultPosition, size=wxPyDefaultSize, style=wxDEFAULT_DIALOG_STYLE):
        wxDialog.__init__(self, parent, id, title)
        self.SetBackgroundColour(backgroundColour)

class wxskinStaticText(wxStaticText):
    def __init__(self, parent, id, text):
        wxStaticText.__init__(self, parent, id, text)
        self.SetBackgroundColour(backgroundColour)

class wxskinListCtrl(wxListCtrl):
    def __init__(self, parent, ID=-1, pos=wxPyDefaultPosition, size=wxPyDefaultSize, style=wxLC_ICON):
        wxListCtrl.__init__(self, parent, ID, pos, size, style)
        self.SetBackgroundColour(backgroundColour)

class wxskinProgressDialog(wxProgressDialog):
    def __init__(self, title, message, maximum=100, parent=NULL, style=wxPD_AUTO_HIDE|wxPD_APP_MODAL):
        wxProgressDialog.__init__(self, title, message, maximum, parent, style)
        self.SetBackgroundColour(backgroundColour)

class wxskinMessageDialog(wxMessageDialog):
    def __init__(self, parent, messageString, titleString="pySIM", style=wxOK | wxICON_INFORMATION, pos=wxPyDefaultPosition):
        wxMessageDialog.__init__(self, parent, messageString, titleString, style, pos)
        self.SetBackgroundColour(backgroundColour)

class wxskinTextEntryDialog(wxTextEntryDialog):
    def __init__(self, parent, messageString, titleString="pySIM", defaultValue='', style=wxOK|wxCANCEL|wxCENTRE, pos=wxPyDefaultPosition):
        wxTextEntryDialog.__init__(self, parent, messageString, titleString, defaultValue, style, pos)
        self.SetBackgroundColour(backgroundColour)


################################################################################
#                           pySIM dialog helper classes                        #
################################################################################

class pySIMmessage(wxskinMessageDialog):
    def __init__(self, parent, messageString, titleString="pySIM", style=wxOK | wxICON_INFORMATION):
        wxskinMessageDialog.__init__(self, parent, messageString, titleString, style)
        self.ShowModal() 
        self.Destroy()

class pySIMenterText(wxskinTextEntryDialog):
    def __init__(self, parent, messageString, titleString="pySIM", defaultValue=''):
        wxskinTextEntryDialog.__init__(self, parent, messageString, titleString, defaultValue)
        ret = self.ShowModal()
        val = self.GetValue()
        self.Destroy()
        return (ret, val)

################################################################################
#                           pySIM other helper classes                         #
################################################################################

class pySIMvalidator(wxPyValidator):
    def __init__(self, charmap=None, minlength=None, maxlength=None):
        wxPyValidator.__init__(self)
        self.charmap = charmap
        self.minlength = minlength
        self.maxlength = maxlength
        EVT_CHAR(self, self.OnChar)

    def Clone(self):
        return pySIMvalidator(self.charmap, self.minlength, self.maxlength)

    def Validate(self, win):
        tc = self.GetWindow()
        val = tc.GetValue()
        if self.charmap:
            for x in val:
                if x not in self.charmap:
                    return false
        if self.minlength:
            if len(val) < self.minlength:
                return false
        if self.maxlength:
            if len(val) > self.maxlength:
                return false
        return true

    def TransferToWindow(self):
        return true # Prevent wxDialog from complaining.


    def TransferFromWindow(self):
        return true # Prevent wxDialog from complaining.

    def OnChar(self, event):
        key = event.KeyCode()
        if key < WXK_SPACE or key == WXK_DELETE or key > 255:
            event.Skip()
            return
        if not self.charmap or chr(key) in self.charmap:
            val = self.GetWindow().GetValue()
            if not self.maxlength or len(val) < self.maxlength:
                event.Skip()
                return

        if not wxValidator_IsSilent():
            wxBell()

        # Returning without calling even.Skip eats the event before it
        # gets to the text control
        return
