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

backgroundColour = wx.Colour(230, 230, 255)

################################################################################
#                           pySIM skin helper classes                          #
################################################################################

class wxskinFrame(wx.Frame):
    def __init__(self, parent, ID=-1, title="Frame", pos=wx.DefaultPosition, size=wx.DefaultSize):
        wx.Frame.__init__(self, parent, ID, title, pos, size)
        self.SetBackgroundColour(backgroundColour)
        icon = wx.Icon('pySIM.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

class wxskinPanel(wx.Panel):
    def __init__(self, parent, ID=-1, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.TAB_TRAVERSAL, name="panel"):
        wx.Panel.__init__(self, parent, ID, pos, size, style, name)
        self.SetBackgroundColour(backgroundColour)

class wxskinDialog(wx.Dialog):
    def __init__(self, parent, id=-1, title="Dialog", pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE):
        wx.Dialog.__init__(self, parent, id, title)
        self.SetBackgroundColour(backgroundColour)

class wxskinStaticText(wx.StaticText):
    def __init__(self, parent, id, text):
        wx.StaticText.__init__(self, parent, id, text)
        self.SetBackgroundColour(backgroundColour)

class wxskinListCtrl(wx.ListCtrl):
    def __init__(self, parent, ID=-1, pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.LC_ICON):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        self.SetBackgroundColour(backgroundColour)

class wxskinProgressDialog(wx.ProgressDialog):
    def __init__(self, title, message, maximum=100, parent=None, style=wx.PD_AUTO_HIDE|wx.PD_APP_MODAL):
        wx.ProgressDialog.__init__(self, title, message, maximum, parent, style)
        self.SetBackgroundColour(backgroundColour)

class wxskinMessageDialog(wx.MessageDialog):
    def __init__(self, parent, messageString, titleString="pySIM", style=wx.OK | wx.ICON_INFORMATION, pos=wx.DefaultPosition):
        wx.MessageDialog.__init__(self, parent, messageString, titleString, style, pos)
        self.SetBackgroundColour(backgroundColour)

class wxskinTextEntryDialog(wx.TextEntryDialog):
    def __init__(self, parent, messageString, titleString="pySIM", defaultValue='', style=wx.OK|wx.CANCEL|wx.CENTRE, pos=wx.DefaultPosition):
        wx.TextEntryDialog.__init__(self, parent, messageString, titleString, defaultValue, style, pos)
        self.SetBackgroundColour(backgroundColour)


################################################################################
#                           pySIM dialog helper classes                        #
################################################################################

class pySIMmessage(wxskinMessageDialog):
    def __init__(self, parent, messageString, titleString="pySIM", style=wx.OK | wx.ICON_INFORMATION):
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

class pySIMvalidator(wx.PyValidator):
    def __init__(self, charmap=None, minlength=None, maxlength=None):
        wx.PyValidator.__init__(self)
        self.charmap = charmap
        self.minlength = minlength
        self.maxlength = maxlength
        wx.EVT_CHAR(self, self.OnChar)

    def Clone(self):
        return pySIMvalidator(self.charmap, self.minlength, self.maxlength)

    def Validate(self, win):
        tc = self.GetWindow()
        val = tc.GetValue()
        if self.charmap:
            for x in val:
                if x not in self.charmap:
                    return False
        if self.minlength:
            if len(val) < self.minlength:
                return False
        if self.maxlength:
            if len(val) > self.maxlength:
                return False
        return True

    def TransferToWindow(self):
        return True # Prevent wxDialog from complaining.


    def TransferFromWindow(self):
        return True # Prevent wxDialog from complaining.

    def OnChar(self, event):
        key = event.KeyCode
        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return
        if not self.charmap or chr(key) in self.charmap:
            val = self.GetWindow().GetValue()
            if not self.maxlength or len(val) < self.maxlength:
                event.Skip()
                return

        if not wx.Validator_IsSilent():
            wx.Bell()

        # Returning without calling even.Skip eats the event before it
        # gets to the text control
        return
