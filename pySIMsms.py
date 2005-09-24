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
from wxPython.lib.mixins.listctrl import wxColumnSorterMixin
from pySIMconstants import *
from pySIMutils import *
from pySIMskin import *
from traceback import print_exc
from binascii import hexlify, unhexlify
import time, calendar

ID_LISTCTRL = wxNewId()
ID_MENU_FILE_EXPORT = wxNewId()
ID_MENU_FILE_IMPORT = wxNewId()
ID_MENU_FILE_EXIT = wxNewId()
ID_BUTTON_OK = wxNewId()
ID_BUTTON_OVERWRITE = wxNewId()
ID_BUTTON_COPY = wxNewId()
ID_BUTTON_SKIP = wxNewId()
ID_BUTTON_CANCEL = wxNewId()
ID_CHECKBOX_APPLY_ALL = wxNewId()

SMS_FILE_PATH = ["3F00", "7F10", "6F3C"]

COL_STATUS  = 0
COL_DATE    = 1
COL_FROM    = 2
COL_MESSAGE = 3
COL_SMS     = 4

STATUS_READ     = 0
STATUS_UNREAD   = 1
STATUS_DELETED  = 2

class SMS(wxskinFrame, wxColumnSorterMixin):
    def __init__(self, master, SIMcontrol):
        self.parent = master
        self.SIM = SIMcontrol
        wxskinFrame.__init__(self, self.parent, -1, "SMS Messages", wxPyDefaultPosition, (500, 400))
        self.numberRecords = 0
        self.itemDataMap = {}
        self.phonebookMap = {}
        self.createMenus()
        self.createWidgets()
        self.createPhonebookMap()

    def createMenus(self):
        # Creating the menubar.
        menuBar = wxMenuBar()

        # Setting up the menu.
        filemenu = wxMenu()
        filemenu.Append(ID_MENU_FILE_EXPORT, "Export..."," Export your SMS messages to file")
        filemenu.Append(ID_MENU_FILE_IMPORT, "Import..."," Import your SMS messages from file")
        filemenu.AppendSeparator()
        filemenu.Append(ID_MENU_FILE_EXIT, "Close"," Close this window")
        # Adding the "filemenu" to the MenuBar
        menuBar.Append(filemenu,"&File")

        # Adding the MenuBar to the Frame content.
        self.SetMenuBar(menuBar)

        #Add the menu handlers
        EVT_MENU(self, ID_MENU_FILE_EXPORT, self.doExport)
        EVT_MENU(self, ID_MENU_FILE_IMPORT, self.doImport)
        EVT_MENU(self, ID_MENU_FILE_EXIT, self.closeWindow)

    def createWidgets(self):
        self.listCtrl = wxskinListCtrl(self, ID_LISTCTRL, style=wxLC_REPORT|wxSUNKEN_BORDER|wxLC_SINGLE_SEL|wxLC_VRULES|wxLC_HRULES)
        self.listCtrl.InsertColumn(COL_STATUS, "Status")
        self.listCtrl.InsertColumn(COL_DATE, "Date")
        self.listCtrl.InsertColumn(COL_FROM, "From")
        self.listCtrl.InsertColumn(COL_MESSAGE, "Message")

        wxColumnSorterMixin.__init__(self, 4)

        self.currentItem = 0

        EVT_SIZE(self, self.OnSize)
        EVT_LIST_ITEM_SELECTED(self, ID_LISTCTRL, self.OnItemSelected)
        EVT_LIST_ITEM_ACTIVATED(self, ID_LISTCTRL, self.OnItemActivated)
        EVT_RIGHT_DOWN(self.listCtrl, self.OnRightDown)
        EVT_LEFT_DCLICK(self.listCtrl, self.OnPopupEdit)
        EVT_CLOSE(self, self.closeWindow)

        # for wxMSW and wxGTK respectively
        EVT_COMMAND_RIGHT_CLICK(self.listCtrl, ID_LISTCTRL, self.OnRightClick)
        EVT_RIGHT_UP(self.listCtrl, self.OnRightClick)

    def createPhonebookMap(self):
        pb = self.SIM.phonebook
        for i in pb.keys():
            self.phonebookMap[pb[i][1]] = pb[i][0]

    def showWindow(self):
        self.parent.Show(0)
        self.Show(1)
        self.read()
        self.UpdateView()

    def closeWindow(self, event):
        self.Show(0)
        self.parent.Show(1)
        self.Destroy()

    def UpdateView(self):
        self.listCtrl.DeleteAllItems()
        # Add our sms messages to the listbox
        i = 0
        for k in self.itemDataMap.keys():
            sms = self.itemDataMap[k][4]
            self.listCtrl.InsertStringItem(i, sms.status)
            self.listCtrl.SetStringItem(i, COL_DATE, sms.timestamp)
            self.listCtrl.SetStringItem(i, COL_FROM, self.getNameFromPhonebook(sms.number))
            self.listCtrl.SetStringItem(i, COL_MESSAGE, sms.message)
            self.listCtrl.SetItemData(i, k)
            i += 1

        self.SortListItems(1, true)
        self.listCtrl.SetColumnWidth(COL_STATUS,    65)
        self.listCtrl.SetColumnWidth(COL_DATE,      150)
        self.listCtrl.SetColumnWidth(COL_FROM,      120)
        self.listCtrl.SetColumnWidth(COL_MESSAGE,   850)
 
        self.SetTitle("(%d/%d) sms messages" % (len(self.itemDataMap), self.numberRecords))

    def doExport(self, event):
        dlg = wxFileDialog(self, "Save to file:", ".", "", "Text (*.txt)|*.txt", wxSAVE|wxOVERWRITE_PROMPT)
        if dlg.ShowModal() == wxID_OK:
            i = dlg.GetFilterIndex()
            if i == 0: # Text format
                try:
                    f = open(dlg.GetPath(), "w")
                    f.write("# Date, From, SerivceCenter, Message\n")
                    for i in self.itemDataMap.keys():
                        entry = self.itemDataMap[i]
                        f.write('%s,%s,%s,%s\n' % (entry[1], entry[2], entry[4].smsc, entry[3]))
                    f.close()
                    pySIMmessage(self, "SMS export to file was successful\n\nFilename: %s" % dlg.GetPath(), "Export OK")
                except:
                    pySIMmessage(self, "Unable to save your SMS messages to file: %s" % dlg.GetPath(), "Export error")
                    #print_exc()

        dlg.Destroy()

    def getNameFromPhonebook(self, number):
        if not number:
            return ''
        if self.phonebookMap.has_key(number):
            return "%s (%s)" % (self.phonebookMap[number], number)
        num = number
        if num[0] == '+':
            num = num[1:]
        if num[0] == '0':
            num = num[1:]
        for i in self.phonebookMap.keys():
            n = i
            if i[0] == '+':
                n = i[1:]
            if n[0] == '0':
                n = n[1:]
            pos = num.find(n)
            if pos >= 0:
                return "%s (%s)" % (self.phonebookMap[i], number)
        return number

    def doImport(self, event):
        dlg = wxFileDialog(self, "Open file:", ".", "", "Text (*.txt)|*.txt", wxOPEN)
        if dlg.ShowModal() == wxID_OK:

            # Create a list of sms name entries
            oldSMSList = {}
            newSMSList = {}
            for i in self.itemDataMap.keys():
                oldSMSList[self.itemDataMap[i][0]] = (i, self.itemDataMap[i][3])

            self.SIM.gotoFile(SMS_FILE_PATH)

            i = dlg.GetFilterIndex()
            if i == 0:
                # Text format
                f = open(dlg.GetPath(), "r")
                line_count = 0
                for line in f.readlines():
                    # Ex. 30 Jan 2003 (9:15am),+612944842,+61101,Hi there folks
                    line_count += 1
                    if line[0] == '#': # Ignore comments
                        continue
                    sf = line.split(",", 3)
                    if len(sf) == 4:
                        sms = SMSmessage()
                        sms.smsToData(sf[0], sf[1], sf[2], sf[3].rstrip())
                        newSMSList[sf[0]] = (0, sms)
                    else:
                        dlgError = wxskinMessageDialog(self, "Import file is an unknown format.\n\nLine %d: %s\n\nContinue with the next line in import file?" % (line_count, line),
                                              'Import file error', wxYES_NO | wxICON_INFORMATION)
                        ret = dlgError.ShowModal()
                        dlgError.Destroy()
                        if ret == wxID_YES:
                            continue
                        else:
                            break

            import_count = [0,0,0,0,0,0]
            dlgGuage = wxskinProgressDialog("Import file to SMS folder", "Importing %d SMS messages" % len(newSMSList), len(newSMSList) + 1, self, wxPD_CAN_ABORT | wxPD_APP_MODAL)
            for date in newSMSList.keys():
                import_type = 1
                import_count[0] += 1
                sms = newSMSList[date][1]
                if not dlgGuage.Update(import_count[0]):
                    break
                if oldSMSList.has_key(date) and oldSMSList[date][1].number == sms.number:
                    # Find out what they want to do (copy, overwrite, skip)
                    importDlg = ImportDialog(self.parent, date, number)
                    ret = importDlg.ShowModal()
                    funct = importDlg.getFunction()
                    importDlg.Destroy()

                    if ret == wxID_OK:
                        if funct == ID_BUTTON_OVERWRITE:
                            pos = oldSMSList[date][0]
                            import_type = 2
                        elif funct == ID_BUTTON_COPY:
                            pos = self.findFreePosition()
                            import_type = 3
                        else:
                            import_count[4] += 1
                            continue
                    else:
                        break
                else:
                    import_type = 1
                    pos = self.findFreePosition()
                if pos <=0:
                    pySIMmessage(self, "Cannot save SMS: %s (%s)\n\nNo free positions left on SIM card." % (date, number), "Import error - no space left on SIM")
                    break

                try:
                    self.writeSMSEntry(pos, sms)
                    self.itemDataMap[pos] = (sms.status, date, sms.number, sms.message, sms)
                    import_count[import_type] += 1
                    i += 1
                except:
                    import_count[5] += 1
                    pySIMmessage(self, "Unable to save: %s (%s)" % (date, number), "SIM card error")

            dlgGuage.Destroy()
            pySIMmessage(self, "%d file import entries\n\n%d new entries\n%d overwritten entries\n%d copied entries\n%d entries skipped" % (import_count[0], import_count[1], import_count[2], import_count[3], import_count[4]), "File import OK")
            self.UpdateView()
        dlg.Destroy()

    def read(self):
        try:
            self.SIM.gotoFile(SMS_FILE_PATH)
            # Send the get response command, to find out record length
            data, sw = self.SIM.sendAPDUmatchSW("A0C000000F", SW_OK)
            self.recordLength  = int(data[28:30], 16) # Should be 0xB0 (176)
            self.numberRecords = int(data[4:8], 16) / self.recordLength
        except:
            pySIMmessage(self, "Unable to access your SMS folder on your SIM card.", "SIM card error")
            return

        if not self.SIM.checkAndVerifyCHV1(CHV_READ, data):
            return

        apdu = "A0B2%s04" + IntToHex(self.recordLength)
        dlg = wxskinProgressDialog("SMS", "Reading your SMS messages", self.numberRecords + 1, self, wxPD_CAN_ABORT | wxPD_APP_MODAL)
        try:
            for i in range(1, self.numberRecords + 1):
                if not dlg.Update(i):
                    break
                data, sw = self.SIM.sendAPDUmatchSW(apdu % IntToHex(i), SW_OK)
                # See if SMS record is used
                status = int(data[0:2], 16)
                if status & 1 or data[2:4] != 'FF':
                    try:
                        sms = SMSmessage()
                        sms.smsFromData(data)
                        self.itemDataMap[i] = (sms.status, sms.timestamp, sms.number, sms.message, sms)
                    except:
                        print i
                        print data
                        print_exc()
                        #pass
        except:
            # Finished with the guage
            print_exc()
            pySIMmessage(self, "Unable to read your SMS messages on your SIM card.", "SIM card error")
        dlg.Destroy()

    def findFreePosition(self):
        k = self.itemDataMap.keys()
        i = 1
        while i <= self.numberRecords:
            if i not in k:
                return i
            i += 1
        return 0

    # Used by the wxColumnSorterMixin, see wxPython/lib/mixins/listctrl.py
    def GetListCtrl(self):
        return self.listCtrl

    # Catch where we are right clicking
    def OnRightDown(self, event):
        self.x = event.GetX()
        self.y = event.GetY()
        event.Skip()

    def getColumnText(self, index, col):
        item = self.listCtrl.GetItem(index, col)
        return item.GetText()

    def OnItemSelected(self, event):
        self.currentItem = event.m_itemIndex

    def OnItemActivated(self, event):
        self.currentItem = event.m_itemIndex

    def OnSize(self, event):
        w,h = self.GetClientSizeTuple()
        self.listCtrl.SetDimensions(0, 0, w, h)

    def OnRightClick(self, event):
        tsubPopupID1 = 10
        tsubPopupID2 = 11
        tsubPopupID3 = 12
        submenu = wxMenu()
        submenu.Append(tsubPopupID1, "Read")
        submenu.Append(tsubPopupID2, "Unread")
        submenu.Append(tsubPopupID3, "Deleted")

        EVT_MENU(self, tsubPopupID1, self.OnPopupMarkRead)
        EVT_MENU(self, tsubPopupID2, self.OnPopupMarkUnread)
        EVT_MENU(self, tsubPopupID3, self.OnPopupMarkDeleted)

        menu = wxMenu()
        tPopupID0 = wxNewId()
        tPopupID1 = wxNewId()
        tPopupID2 = wxNewId()
        tPopupID3 = wxNewId()
        tPopupID4 = wxNewId()
        tPopupID5 = wxNewId()
        menu.AppendMenu(tPopupID1, "Mark as", submenu)
        menu.AppendSeparator()
        menu.Append(tPopupID2, "Edit")
        menu.Append(tPopupID0, "New")
        menu.Append(tPopupID1, "Copy")
        menu.AppendSeparator()
        menu.Append(tPopupID3, "Delete")
        menu.Append(tPopupID4, "Delete All")

        EVT_MENU(self, tPopupID2, self.OnPopupEdit)
        EVT_MENU(self, tPopupID0, self.OnPopupNew)
        EVT_MENU(self, tPopupID1, self.OnPopupCopy)
        EVT_MENU(self, tPopupID3, self.OnPopupDelete)
        EVT_MENU(self, tPopupID4, self.OnPopupDeleteAll)
        self.PopupMenu(menu, wxPoint(self.x, self.y))
        menu.Destroy()
        event.Skip()

    updateRecordPDU = "A0DC%s04%s%s"

    def writeSMSEntry(self, pos, sms=None):
        if not sms:    # Erase record
            data = "00" + "FF" * (self.recordLength - 1)
        else:
            if not sms.rawMessage:
                pySIMmessage(self, "Unable to save: %s (%s)" % (sms.number, sms.timestamp), "SIM card error")
                return
            data = sms.rawMessage + "F" * ((self.recordLength << 1) - len(sms.rawMessage))
        pdu = self.updateRecordPDU % (IntToHex(pos), IntToHex(self.recordLength), data)
        self.SIM.sendAPDUmatchSW(pdu, SW_OK)

    def OnPopupMarkRead(self, event):
        self.changeStatusTo(STATUS_READ)

    def OnPopupMarkUnread(self, event):
        self.changeStatusTo(STATUS_UNREAD)

    def OnPopupMarkDeleted(self, event):
        self.changeStatusTo(STATUS_DELETED)

    def changeStatusTo(self, newStatus):
        key = self.listCtrl.GetItemData(self.currentItem)
        sms = self.itemDataMap[key][COL_SMS]
        sms.changeStatus(newStatus)
        try:
            self.SIM.gotoFile(SMS_FILE_PATH)
            self.writeSMSEntry(key, sms)
            self.itemDataMap[key] = (sms.status, sms.timestamp, sms.number, sms.message, sms)
            self.UpdateView()
        except:
            print_exc()
            pySIMmessage(self, "Unable to modify: %s (%s)" % (self.itemDataMap[key][0], self.itemDataMap[key][1]), "SIM card error")

    def OnPopupNew(self, event):
        p = SMSEditEntry(self, SMSmessage())
        if p.ShowModal() == wxID_OK:
            sms = p.getSMS()
            pos = self.findFreePosition()
            if pos:
                try:
                    self.SIM.gotoFile(SMS_FILE_PATH)
                    if not self.SIM.checkAndVerifyCHV1(CHV_UPDATE):
                        raise "Access conditions not met."
                    self.writeSMSEntry(pos, sms)
                    self.itemDataMap[pos] = (sms.status, sms.timestamp, sms.number, sms.message, sms)
                    self.UpdateView()
                except:
                    pySIMmessage(self, "Unable to save SMS message.", "SIM card error")
            else:
                pySIMmessage(self, "Cannot save: %s (%s)\n\nNo free positions left on SIM card." % (name, number), "SIM card error")
        p.Destroy()


    def OnPopupCopy(self, event):
        pos = self.listCtrl.GetItemData(self.currentItem)
        sms = self.itemDataMap[pos][COL_SMS]
        p = SMSEditEntry(self, sms.clone())
        if p.ShowModal() == wxID_OK:
            sms = p.getSMS()
            pos = self.findFreePosition()
            if pos:
                try:
                    self.SIM.gotoFile(SMS_FILE_PATH)
                    if not self.SIM.checkAndVerifyCHV1(CHV_UPDATE):
                        raise "Access conditions not met."
                    self.writeSMSEntry(pos, sms)
                    self.itemDataMap[pos] = (sms.status, sms.timestamp, sms.number, sms.message, sms)
                    self.UpdateView()
                except:
                    pySIMmessage(self, "Unable to save SMS message.", "SIM card error")
            else:
                pySIMmessage(self, "Cannot save: %s (%s)\n\nNo free positions left on SIM card." % (name, number), "SIM card error")
        p.Destroy()


    def OnPopupEdit(self, event):
        pos = self.listCtrl.GetItemData(self.currentItem)
        sms = self.itemDataMap[pos][COL_SMS]
        p = SMSEditEntry(self, sms)
        if p.ShowModal() == wxID_OK:
            sms = p.getSMS()
            try:
                self.SIM.gotoFile(SMS_FILE_PATH)
                if not self.SIM.checkAndVerifyCHV1(CHV_UPDATE):
                    raise "Access conditions not met."
                self.writeSMSEntry(pos, sms)
                self.itemDataMap[pos] = (sms.status, sms.timestamp, sms.number, sms.message, sms)
                self.UpdateView()
            except:
                pySIMmessage(self, "Unable to save SMS message.", "SIM card error")
        p.Destroy()

    def OnPopupDelete(self, event):
        key = self.listCtrl.GetItemData(self.currentItem)
        try:
            self.SIM.gotoFile(SMS_FILE_PATH)
            self.writeSMSEntry(key)
            del self.itemDataMap[key]
            self.UpdateView()
        except:
            print_exc()
            pySIMmessage(self, "Unable to delete: %s (%s)" % (self.itemDataMap[key][0], self.itemDataMap[key][1]), "SIM card error")

    delete_confirm_text = "This will delete all your phonebook entries!!\n\nAre you sure you want to delete them all?\n"
    def OnPopupDeleteAll(self, event):
        dlg = wxskinMessageDialog(self, self.delete_confirm_text,
                              'Confirm Deletion', wxYES_NO | wxICON_INFORMATION)
        ret = dlg.ShowModal()
        dlg.Destroy()
        if ret == wxID_YES:

            dlg = wxskinProgressDialog("Phonebook deletion", "Deleting your %d phonebook entries" % len(self.itemDataMap), len(self.itemDataMap) + 1, self, wxPD_CAN_ABORT | wxPD_APP_MODAL)
            try:
                self.SIM.gotoFile(SMS_FILE_PATH)
                i = 1
                for key in self.itemDataMap.keys()[:]:   # Make a copy of key table!!
                    if not dlg.Update(i):
                        break
                    self.writeSMSEntry(key)
                    del self.itemDataMap[key]
                    i += 1
            except:
                print_exc()
                pySIMmessage(self, "Unable to delete all phonebook entries!", "SIM card error")

            dlg.Destroy()
            self.UpdateView()

    # Override the column sorting function. We need to compare 'a' and 'A' as equal
    def GetColumnSorter(self):
        return self.pySIMColumnSorter

    def pySIMColumnSorter(self, key1, key2):
        # These fields are dates that we wish to sort
        col = self._col
        ascending = self._colSortFlag[col]
        if col == COL_DATE:
            item1 = calendar.timegm(self.itemDataMap[key1][COL_SMS].timetuple)
            item2 = calendar.timegm(self.itemDataMap[key2][COL_SMS].timetuple)
        else:
            item1 = self.itemDataMap[key1][col].lower()
            item2 = self.itemDataMap[key2][col].lower()

        cmpVal = cmp(item1, item2)

        # If the items are equal then pick something else to make the sort value unique
        if cmpVal == 0:
            cmpVal = apply(cmp, self.GetSecondarySortValues(col, key1, key2))

        if ascending:
            return cmpVal
        else:
            return -cmpVal

class SMSEditEntry(wxskinDialog):
    def __init__(self, parent, sms):
        wxskinDialog.__init__(self, parent, -1, "SMS edit")
        self.SetAutoLayout(true)
        self.sms = sms

        # Main window resizer object
        sizer = wxBoxSizer(wxVERTICAL)
        sizer = wxFlexGridSizer(4,1)

        self.smsLabel = wxStaticText(self, -1, "Message Text (%d / 160)" % len(sms.message))
        sizer.Add(self.smsLabel, 1, wxALIGN_CENTER | wxALL, 5)
        smsTextId = wxNewId()
        self.smsText = wxTextCtrl(self, smsTextId, sms.message, size=(300,100), style=wxTE_MULTILINE | wxTE_LINEWRAP, validator = pySIMvalidator(None, None, 160))
        sizer.Add(self.smsText, 1, wxALIGN_CENTER | wxALL, 5)

        hsizer = wxFlexGridSizer(2,3)
        label = wxStaticText(self, -1, "Date: ")
        hsizer.Add(label, 1, wxALL, 5)
        label = wxStaticText(self, -1, "From: ")
        hsizer.Add(label, 1, wxALL, 5)
        label = wxStaticText(self, -1, "Status: ")
        hsizer.Add(label, 1, wxALL, 5)

        text = wxTextCtrl(self, -1, self.sms.timestamp, style=wxTE_READONLY)
        hsizer.Add(text, 1, wxALL, 5)
        self.numberCtrl = wxTextCtrl(self, -1, self.sms.number, validator = pySIMvalidator("+*#pw0123456789", None, 20))
        hsizer.Add(self.numberCtrl, 1, wxALL, 5)

        choiceList = ['Read', 'Unread', 'Deleted']
        self.ch = wxChoice(self, -1, (80, 50), choices = choiceList)
        for i in range(len(choiceList)):
            if sms.status == choiceList[i]:
                self.ch.SetSelection(i)
                break

        hsizer.Add(self.ch, 1, wxALL, 5)
        sizer.Add(hsizer, 1, wxALL, 5)

        buttons = wxBoxSizer(wxHORIZONTAL)
        buttons.Add(wxButton(self, ID_BUTTON_OK, "Save"), 1, wxALIGN_LEFT | wxALL, 20)
        buttons.Add(wxButton(self, wxID_CANCEL, "Cancel"), 1, wxALIGN_RIGHT | wxALL, 20)
        sizer.Add(buttons, 1, wxALIGN_CENTER | wxALL, 5)

        EVT_BUTTON(self, ID_BUTTON_OK, self.onOK)
        EVT_TEXT(self.smsText, smsTextId, self.smsTextChange)

        self.SetAutoLayout(1);
        self.SetSizer(sizer)
        sizer.Fit(self)
        self.Layout()

    def smsTextChange(self, event):
        self.smsLabel.SetLabel("Message Text (%d / 160)" % len(self.smsText.GetValue()))

    def getSMS(self):
        return self.sms

    def onOK(self, event):
        if self.Validate() and self.TransferDataFromWindow():
            for i in self.smsText.GetValue().lower():
                if (((i < "a") or (i > "z")) and ((i < "%") or (i > "?"))):
                    if not dic_GSM_3_38.has_key(i):
                        pySIMmessage(self, "Invalid SMS message. Cannot have character: %s" % i, "SIM card error")
                        return
            self.sms.smsToData(self.sms.timestamp, self.numberCtrl.GetValue(), self.sms.smsc, self.smsText.GetValue())
            if self.ch.GetSelection() >= 0:
                self.sms.changeStatus(self.ch.GetSelection())
            self.EndModal(wxID_OK)

class ImportDialog(wxskinDialog):
    def __init__(self, parent, date, number):
        wxskinDialog.__init__(self, parent, -1, "SMS import")
        self.SetAutoLayout(true)
        self.function = 0

        # Main window resizer object
        border = wxBoxSizer(wxVERTICAL)

        label = wxStaticText(self, -1, "SMS from '%s' on '%s' already exists in SMS folder.\n\nDo you want to overwrite exisiting, duplicate or skip!?" % (number, date))
        border.Add(label, 1, wxALL, 10)

        buttons = wxBoxSizer(wxHORIZONTAL)
        buttons.Add(wxButton(self, ID_BUTTON_OVERWRITE, "Overwrite"), 1, wxALIGN_LEFT | wxALL, 20)
        buttons.Add(wxButton(self, ID_BUTTON_COPY, "Duplicate"), 1, wxALIGN_RIGHT | wxALL, 20)
        buttons.Add(wxButton(self, ID_BUTTON_SKIP, "Skip"), 1, wxALIGN_RIGHT | wxALL, 20)
        buttons.Add(wxButton(self, wxID_CANCEL, "Cancel"), 1, wxALIGN_RIGHT | wxALL, 20)
        border.Add(buttons, 1, wxALL)

        self.applyAll = wxCheckBox(self, ID_CHECKBOX_APPLY_ALL,   "  Apply to all", wxPoint(65, 40), wxSize(150, 20), wxNO_BORDER)
        border.Add(self.applyAll, 1, wxALIGN_CENTER | wxALL)

        EVT_BUTTON(self, ID_BUTTON_OVERWRITE, self.onOverwrite)
        EVT_BUTTON(self, ID_BUTTON_COPY, self.onDuplicate)
        EVT_BUTTON(self, ID_BUTTON_SKIP, self.onSkip)
        #EVT_CHECKBOX(self, ID_CHECKBOX_APPLY_ALL, self.EvtCheckBox)

        self.SetAutoLayout(1);
        self.SetSizer(border)
        border.Fit(self)
        self.Layout()

    def onOverwrite(self, event):
        self.function = ID_BUTTON_OVERWRITE
        self.EndModal(wxID_OK)

    def onDuplicate(self, event):
        self.function = ID_BUTTON_COPY
        self.EndModal(wxID_OK)

    def onSkip(self, event):
        self.function = ID_BUTTON_SKIP
        self.EndModal(wxID_OK)

    def getFunction(self):
        return self.function

class SMSmessage:
    # SMS Deliver and SMS Submit
    # 0107911614910900F5040B911614836816F1 0000 2050107034146B
    # 4C    FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    def __init__(self):
        self.status = 'Read'
        self.smsc = ''
        self.number = ''
        self.timestamp = ''
        self.timetuple = [0,0,0,0,0,0,0,0,0]
        self.message = ''

        self.mti  = 0
        self.mms  = 0
        self.sri  = 0
        self.udhi = 0
        self.rp   = 1
        self.pid  = 0
        self.dcs  = 0
        self.udl  = 0
        
        self.rawMessage = ''

    def clone(self):
        s = SMSmessage()
        s.smsToData(self.timestamp, self.number, self.smsc, self.message)
        s.rawMessage = self.rawMessage
        s.status = self.status
        return s

    def setStatus(self, val):
        if not (val & 0x1):
            self.status = "Deleted"
        elif not (val & 0x4):
            if not (val & 0x2):
                self.status = "Read"
            else:
                self.status = "Unread"
        elif (val & 0x7) == 0x7:
            self.status = "To be sent"
        else:
            self.status = "Unknown"

    def changeStatus(self, val=STATUS_READ):
        if val == STATUS_DELETED:
            i = 0
        elif val == STATUS_UNREAD:
            i = 0x3
        else:
            i = 0x1

        self.setStatus(i)
        if self.rawMessage:
            self.rawMessage = "0%d%s" % (i, self.rawMessage[2:])

    def smsFromData(self, data):
        self.rawMessage = data

        self.setStatus(int(data[0:2], 16))

        i = int(data[2:4], 16) << 1
        self.smsc = GSMPhoneNumberToString(data[4:4+i], replaceTonNPI=1)
        data = data[4+i:]

        val = int(data[0:2], 16)
        self.mti  = (val >> 6) & 3
        self.mms  = (val >> 5) & 1
        self.sri  = (val >> 4) & 1
        self.udhi = (val >> 3) & 1
        self.rp   = (val >> 2) & 1
        data = data[2:]

        i = int(data[:2], 16)
        j = 4 + i + (i % 2)
        self.number = GSMPhoneNumberToString(data[2:j], replaceTonNPI=1)
        data = data[j:]

        self.pid  = int(data[:2], 16)
        self.dcs  = int(data[2:4], 16)

        self.timestamp = self.convertTimestamp(data[4:18])

        self.udl  = int(data[18:20], 16) # it's meaning is dependant upon dcs value
        if ((self.dcs >> 2) & 3) == 0: # 7-bit, Default alphabet
            i = ((self.udl * 7) / 8) << 1
            if (self.udl * 7) % 8:
                i += 2
            self.message = self.convertGSM7bitToAscii(data[20:20 + i])
        elif ((self.dcs >> 2) & 3) == 1: # 8-bit data, binary
            self.message = "ERROR: Don't understand 8-bit binary messages"
        elif ((self.dcs >> 2) & 3) == 2: # 16-bit, UCS2 oh hell!  :)
            self.message = "ERROR: Don't understand 16-bit UCS2 messages"
        else:
            self.message = "ERROR: Don't understand this message format"

    def smsToData(self, date, number, smsc, message):
        # 0107911614910900F504 0B911614836816F1 0000 2050107034146B

        # add message type, sms-c details and reply path indicator
        self.timestamp = date
        self.number = number
        self.smsc = smsc
        self.message = message
        
        smsc = StringToGSMPhoneNumber(smsc)
        i = len(smsc) >> 1
        if i > 0:
            data = "01%s%s04" % (padFrontOfString(hex(i)[2:], 2), smsc)
        else:
            data = "010004"

        # add originating address
        if number[0] == '+':
            i = len(number) - 1
        else:
            i = len(number)
        number = StringToGSMPhoneNumber(number)
        data += "%s%s" % (padFrontOfString(hex(i)[2:], 2), number)

        # add PID, DCS
        data += "%s%s" % (padFrontOfString(hex(self.pid)[2:],2), padFrontOfString(hex(self.dcs)[2:],2))

        # add timestamp
        data += self.convertDateToTimestamp(date)

        # add UDL
        data += padFrontOfString(hex(len(message))[2:],2)

        # add the message (encoded in 7-bit GSM)
        self.rawMessage = data + self.convertAsciiToGSM7bit(message)

    def convertGSM7bitToAscii(self, data):
        i = 0
        mask = 0x7F
        last = 0
        res = []
        for c in unhexlify(data):
            # baaaaaaa ccbbbbbb dddccccc eeeedddd fffffeee ggggggff hhhhhhhg 0iiiiiii
            # 0aaaaaaa 0bbbbbbb 0ccccccc 0ddddddd 0eeeeeee 0fffffff 0ggggggg 0hhhhhhh 0iiiiiii
            val = ((ord(c) & mask) << i) + (last >> (8-i))
            res.append(chr(val))

            i += 1
            mask >>= 1
            last = ord(c)
            if i % 7 == 0:
                res.append(chr(last >> 1))
                i = 0
                mask = 0x7F
                last = 0
        return GSM3_38ToASCII(''.join(res))

    def convertAsciiToGSM7bit(self, data):
        i = 0
        l = 0
        mask = 0x0
        data = ASCIIToGSM3_38(data)
        res = []

        while l < len(data):
            # 0aaaaaaa 0bbbbbbb 0ccccccc 0ddddddd 0eeeeeee 0fffffff 0ggggggg 0hhhhhhh 0iiiiiii
            # baaaaaaa ccbbbbbb dddccccc eeeedddd fffffeee ggggggff hhhhhhhg 0iiiiiii
            c = ord(data[l])
            if i:
                res[-1] = chr(ord(res[-1]) + ((c & mask) << (8 - i)))
            if i != 7:
                res.append(chr(c >> i))

            i += 1
            mask = (mask << 1) + 1
            if i % 8 == 0:
                i = 0
                mask = 0x0
            l += 1

        return hexlify(''.join(res))

    def convertTimestamp(self, ts):
        # 2050107034146B
        self.timetuple = [0,0,0,0,0,0,0,0,0]

        self.timetuple[0] = int(ts[0]) + int(ts[1]) * 10
        if self.timetuple[0] >= 80:
            # Convert to previous century, hopefully no one uses this after 2079 ;)
            self.timetuple[0] += 1900
        else:
            # Convert to current century
            self.timetuple[0] += 2000

        #~ print ts
        self.timetuple[1] = int(ts[2]) + int(ts[3]) * 10
        self.timetuple[2] = int(ts[4]) + int(ts[5]) * 10
        self.timetuple[3] = int(ts[6]) + int(ts[7]) * 10
        self.timetuple[4] = int(ts[8]) + int(ts[9]) * 10
        self.timetuple[5] = int(ts[10]) + int(ts[11]) * 10
        self.timetuple[6] = calendar.weekday(self.timetuple[0], self.timetuple[1], self.timetuple[2])

        return time.asctime(self.timetuple)


    def convertDateToTimestamp(self, date):
        # Mon May 01 07:43:41 2002
        if not date:
            self.timetuple = time.localtime()
        else:
            self.timetuple = strptime(date)

        ts = ''
        for i in range(0, 6):
            s = ("%2d" % (self.timetuple[i])).replace(' ', '0')[-2:]
            ts += "%s%s" % (s[1], s[0])

        return ts + '00'

abbrevMonthNames = { "Jan":'01', "Feb":'02', "Mar":'03', "Apr":'04', "May":'05', "Jun":'06', "Jul":'07', "Aug":'08', "Sep":'09', "Oct":'10', "Nov":'11', "Dec":'12' }

def strptime(date):
    """Convert the date string into a 9 tuple"""
    df = [0,0,0,0,0,0,0,0,0]
    sp  = date.split(' ')
    spt = sp[3].split(':')

    df[0] = int(sp[4])      # Year
    if abbrevMonthNames.has_key(sp[1]):
        df[1] = int(abbrevMonthNames[sp[1]])
    else:
        df[1] = 1           # Month
    df[2] = int(sp[2])      # Day
    df[3] = int(spt[0])     # Hour
    df[4] = int(spt[1])     # Minute
    df[5] = int(spt[2])     # Second
    df[6] = calendar.weekday(df[0], df[1], df[2])

    return df
