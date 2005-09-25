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
#               F U N C T I O N A L   D E S C R I P T I O N
#===============================================================================
"""
pySIM application

Smartcard functions for PIN, phonebook and SMS management.
"""

#===============================================================================
#                            I M P O R T S
#===============================================================================

from wxPython.wx import *
import wx
import wx.html as html_module
from traceback import print_exc

import pySIMpcsc
import pySIMphonebook
import pySIMsms
import pySIMinfo
import pySIMpin
from pySIMskin import *
from pySIMutils import *
from pySIMconstants import *
import time
import logging

#####################################################################################
#               wx Identifiers for menus and button controls                        #
#####################################################################################

ID_MENU_FILE_EXIT = wxNewId()
ID_MENU_PHONEBOOK_ADN = wxNewId()
ID_MENU_PHONEBOOK_FDN = wxNewId()
ID_MENU_SMS = wxNewId()
ID_MENU_SIM_INFO = wxNewId()
ID_MENU_SIM_PIN_CHANGE = wxNewId()
ID_MENU_SIM_PIN_ENABLE = wxNewId()
ID_MENU_SIM_PIN_DISABLE = wxNewId()
ID_MENU_SIM_BACKUP = wxNewId()
ID_MENU_SIM_RESTORE = wxNewId()
ID_MENU_HELP_HELP = wxNewId()
ID_MENU_HELP_ABOUT = wxNewId()

ID_BUTTON_CONNECT = wxNewId()
ID_BUTTON_PHONEBOOK = wxNewId()
ID_BUTTON_SMS = wxNewId()
ID_BUTTON_EXIT = wxNewId()


#####################################################################################
#                 Setup logging for the pySIM application                           #
#####################################################################################

log = None

def initaliseLogger():
    global log
    log = logging.getLogger("pySimReader")
    log.setLevel(logging.INFO)
    # Define the handler and formmatter
    myLogHandler = logging.FileHandler("pySimReader.log", "w")
    # Attach the formatter to the handler and the handler to the log
    myLogHandler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)-5s : %(message)s", "%H:%M:%S"))
    log.addHandler(myLogHandler)
    log.info("Started pySimReader: %s" % (time.asctime()))


#####################################################################################
#     This class will be the main windows for the pySIM application                 #
#####################################################################################

class pySIM(wxskinFrame):
    def __init__(self, parent, ID, title, pos, size):
        wxskinFrame.__init__(self, parent, ID, title, pos, size)
        if pySIMpcsc.PCSCImportError:
            pySIMmessage(self, "Unable to find PCSC resources on this system.\n\nPlease ensure PCSC resource manager and Microsoft Smart Card Base components have been installed.", "PCSC error")
            raise "PCSC error"
        self.SIM = pySIMpcsc.PCSCcontroller(self)
        self.createLayout()
        self.pb = None
        self.sms = None

    def createLayout(self):
        # A Statusbar in the bottom of the window
        self.statusBar = self.CreateStatusBar()
        self.createMenus()
        self.createFrames()
        #Disable some menus until we have the reader connected
        self.enableMenus(0)

    def createMenus(self):
        # Creating the menubar.
        menuBar = wxMenuBar()

        # Setting up the 'File' menu.
        self.menuFile = wxMenu()
        self.menuFile.Append(ID_MENU_FILE_EXIT, "E&xit"," Terminate this program")
        menuBar.Append(self.menuFile,"&File")

        # Setting up the 'Phonebook' menu.
        self.menuPhonebook = wxMenu()
        self.menuPhonebook.Append(ID_MENU_PHONEBOOK_ADN, "Phonebook (ADN)"," Manage your phonebook (Abbreviated Dial Numbers)")
        self.menuPhonebook.Append(ID_MENU_PHONEBOOK_FDN, "Fixed Dialing Numbers (FDN)"," Manage your Fixed Dialing Numbers")
        menuBar.Append(self.menuPhonebook,"&Phonebook")

        # Setting up the 'SMS' menu.
        self.menuMessages = wxMenu()
        self.menuMessages.Append(ID_MENU_SMS, "SMS"," Manage your SMS messages")
        menuBar.Append(self.menuMessages,"&Messages")

        # Setting up the 'SIM' menu.
        self.menuSIM = wxMenu()
        self.menuSIM.Append(ID_MENU_SIM_INFO, "SIM Information"," Information about your SIM card")
        self.menuSIM.AppendSeparator()
        self.menuSIM.Append(ID_MENU_SIM_PIN_CHANGE, "Change PIN"," Change your PIN code (CHV1)")
        self.menuSIM.Append(ID_MENU_SIM_PIN_ENABLE, "Enable PIN"," Prompt for PIN when turning on phone")
        self.menuSIM.Append(ID_MENU_SIM_PIN_DISABLE, "Disable PIN"," Remove the PIN prompt when turning on phone")
        #self.menuSIM.AppendSeparator()
        #self.menuSIM.Append(ID_MENU_SIM_BACKUP, "Backup"," Backup your SIM information")
        #self.menuSIM.Append(ID_MENU_SIM_RESTORE, "Restore"," Restore your SIM information from a previous backup")
        menuBar.Append(self.menuSIM, "&SIM")

        # Setting up the menu.
        self.menuHelp = wxMenu()
        self.menuHelp.Append(ID_MENU_HELP_HELP, "&Help"," Help documentation")
        self.menuHelp.AppendSeparator()
        self.menuHelp.Append(ID_MENU_HELP_ABOUT, "&About"," Information about this program")
        menuBar.Append(self.menuHelp,"&Help")

        # Adding the MenuBar to the Frame content.
        self.SetMenuBar(menuBar)

        #Add the menu handlers
        EVT_MENU(self, ID_MENU_FILE_EXIT, self.closeWindow)
        EVT_MENU(self, ID_MENU_PHONEBOOK_ADN, self.buttonPhonebook)
        EVT_MENU(self, ID_MENU_PHONEBOOK_FDN, self.buttonFDN)
        EVT_MENU(self, ID_MENU_SMS, self.buttonSMS)
        EVT_MENU(self, ID_MENU_SIM_INFO, self.menuSIMInfo)
        EVT_MENU(self, ID_MENU_SIM_PIN_CHANGE, self.menuChangePIN)
        EVT_MENU(self, ID_MENU_SIM_PIN_ENABLE, self.menuEnablePIN)
        EVT_MENU(self, ID_MENU_SIM_PIN_DISABLE, self.menuDisablePIN)
        EVT_MENU(self, ID_MENU_HELP_HELP, self.menuHelpHelp)
        EVT_MENU(self, ID_MENU_HELP_ABOUT, self.menuHelpAbout)

    def createFrames(self):
        # Create the layout component and add controls to it
        self.sizer1 = wxBoxSizer(wxHORIZONTAL)
        self.bConnect = wxButton(self, ID_BUTTON_CONNECT, "Connect reader")
        self.sizer1.Add(self.bConnect, 1, wxEXPAND|wxALL)

        self.sizer2 = wxBoxSizer(wxHORIZONTAL)
        self.bPhonebook = wxButton(self, ID_BUTTON_PHONEBOOK, "Phonebook")
        self.bSMS = wxButton(self, ID_BUTTON_SMS, "SMS")
        self.sizer2.Add(self.bPhonebook, 1, wxEXPAND|wxLEFT|wxRIGHT, 5)
        self.sizer2.Add(self.bSMS, 1, wxEXPAND|wxLEFT|wxRIGHT, 5)

        self.sizer3 = wxBoxSizer(wxHORIZONTAL)
        self.bExit = wxButton(self, ID_BUTTON_EXIT, "Quit")

        self.sizer3.Add(self.bExit, 1, wxEXPAND|wxALL)

        # Use sizers to set layout options
        self.sizer = wxBoxSizer(wxVERTICAL)
        self.sizer.Add(self.sizer1,1,wxEXPAND|wxLEFT|wxRIGHT|wxTOP,15)
        self.sizer.Add(self.sizer2,1,wxEXPAND|wxALL,10)
        self.sizer.Add(self.sizer3,1,wxEXPAND|wxLEFT|wxRIGHT|wxBOTTOM,15)
        self.sizer.SetMinSize((250,150))

        # Layout for frame
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)

        # Add the button handlers
        EVT_BUTTON(self, ID_BUTTON_CONNECT, self.buttonConnectReader)
        EVT_BUTTON(self, ID_BUTTON_PHONEBOOK, self.buttonPhonebook)
        EVT_BUTTON(self, ID_BUTTON_SMS, self.buttonSMS)
        EVT_BUTTON(self, ID_BUTTON_EXIT, self.closeWindow)
        EVT_CLOSE(self, self.closeWindow)

    def closeWindow(self, event):
        """Close the application"""
        if self.pb:
            self.pb.Close(true)
        if self.sms:
            self.sms.Close(true)
        self.Destroy()

    def menuHelpHelp(self, event):
        """Show help dialog"""
        dlg = wxMessageDialog(self, 'Not Yet Implimented!', 'ToDo',
                             wxOK | wxICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()


    aboutPySIM = """pySIM is a multifunctional SIM handling program.

    Phonebook:
      - Editing existing entries
      - Adding or deleting entries
      - Phonebook backup and restore
    SMS:
      - Reading SMS messages
      - SMS backup and restore


    Program Author:
      - Todd Whiteman
      - twhitema@gmail.com
      - http://twhiteman.netfirms.com/pySIM.html
"""
    aboutPySIMhtml = """<html><body>
    pySIM is a multifunctional SIM handling program.

    Phonebook:
      - Editing existing entries
      - Adding or deleting entries
      - Phonebook backup and restore
    SMS:
      - Reading SMS messages
      - SMS backup and restore


    Program Author:
      - Todd Whiteman
      - twhitema@gmail.com
      - <a href="http://twhiteman.netfirms.com/pySIM.html">pySIM Website</a>
    </body></html>
"""
    def menuHelpAbout(self, event):
        """Show about pySIM dialog"""
        dlg = wxMessageDialog(self, self.aboutPySIM, 'About pySIM',
                             wxOK | wxICON_INFORMATION)
        #~ ovr = html_module.HtmlWindow(dlg, -1, size=(400, 400))
        #~ ovr.SetPage(self.aboutPySIMhtml)
        dlg.ShowModal()
        dlg.Destroy()

    def buttonConnectReader(self, event):
        """Connect and disconnect the smartcard reader"""
        if self.SIM.getState() == SIM_STATE_DISCONNECTED:
            self.SIM.connectReader()
            if self.SIM.getState() == SIM_STATE_CONNECTED:
                self.statusBar.SetStatusText("Card reader connected.")
                self.bConnect.SetLabel("Disconnect reader")
                self.enableMenus(1)
        else:
            self.SIM.disconnectReader()
            if self.SIM.getState() == SIM_STATE_DISCONNECTED:
                self.statusBar.SetStatusText("Card reader disconnected.")
                self.bConnect.SetLabel("Connect reader")
                self.enableMenus(0)

    def buttonPhonebook(self, event):
        """Display the phonebook window"""
        self.pb = pySIMphonebook.Phonebook(self, self.SIM, pySIMphonebook.ADN_FILE_PATH)
        self.pb.showWindow()

    def buttonFDN(self, event):
        """Display the FDN phonebook window"""
        self.fdn = pySIMphonebook.Phonebook(self, self.SIM, pySIMphonebook.FDN_FILE_PATH)
        self.fdn.showWindow()
            
    def buttonSMS(self, event):
        """Display the SMS messages window"""
        self.sms = pySIMsms.SMS(self, self.SIM)
        self.sms.showWindow()

    def menuSIMInfo(self, event):
        """Display the SIM information dialog"""
        self.cp = pySIMinfo.pySIMInfo(self, self.SIM)
        self.cp.Show(1)

    def menuChangePIN(self, event):
        """Display the change PIN dialog"""
        self.cp = pySIMpin.ChangePin(self, self.SIM)
        self.cp.ShowModal()
        self.cp.Destroy()

    def menuEnablePIN(self, event):
        """Display the enable PIN dialog"""
        self.cp = pySIMpin.ChangePin(self, self.SIM)
        self.cp.ShowModal()
        self.cp.Destroy()
        self.enableMenus(1)

    def menuDisablePIN(self, event):
        """Remove the PIN verification"""
        try:
            self.SIM.gotoFile(["3F00"])
            if self.SIM.checkAndVerifyCHV1(CHV_ALWAYS):
                apdu = "A026000108%s" % ASCIIToPIN(self.SIM.chv1)
                self.SIM.sendAPDUmatchSW(apdu, SW_OK)
                self.SIM.chv1_enabled = 0
                self.SIM.chv1 = ''
                pySIMmessage(self, "PIN verification has been removed!", "PIN disable")
        except:
            print_exc()
            pySIMmessage(self, "Unable to disable your PIN!", "SIM card error")
        self.enableMenus(1)

    def enableMenus(self, val=1):
        """Enable or disable menu's and buttons"""
        self.menuPhonebook.Enable(ID_MENU_PHONEBOOK_ADN,val)
        self.menuPhonebook.Enable(ID_MENU_PHONEBOOK_FDN,0)
        if self.SIM.FDN_available:
            self.menuPhonebook.Enable(ID_MENU_PHONEBOOK_FDN,val)
        self.menuMessages.Enable(ID_MENU_SMS,val)
        self.menuSIM.Enable(ID_MENU_SIM_INFO,val)
        self.menuSIM.Enable(ID_MENU_SIM_PIN_ENABLE,0)
        self.menuSIM.Enable(ID_MENU_SIM_PIN_DISABLE,0)
        self.menuSIM.Enable(ID_MENU_SIM_PIN_CHANGE,0)
        if self.SIM.chv1_enabled:
            self.menuSIM.Enable(ID_MENU_SIM_PIN_DISABLE,val)
            self.menuSIM.Enable(ID_MENU_SIM_PIN_CHANGE,val)
        else:
            self.menuSIM.Enable(ID_MENU_SIM_PIN_ENABLE,val)
        #self.menuSIM.Enable(ID_MENU_SIM_BACKUP,val)
        #self.menuSIM.Enable(ID_MENU_SIM_RESTORE,val)
        self.bPhonebook.Enable(val)
        self.bSMS.Enable(val)

#####################################################################################
#----------------------------------------------------------------------
#####################################################################################

class pySIMApp(wxApp):
    """Class to control the WX application"""
    def OnInit(self):
        frame = pySIM(NULL, -1, "pySIM", wxPyDefaultPosition,(250,250) )
        frame.Show(true)
        # self.setTopWindow(frame)
        return true

#####################################################################################
#----------------------------------------------------------------------
#####################################################################################

if __name__ == '__main__':
    initaliseLogger()
    try:
        # create instance and start the event loop
        pySIMApp().MainLoop()
    except Exception, exc:
        #~ pass
        #~ print_exc()
	log.exception(exc)
