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

#import win32com.client
from wxPython.wx import *
from wxPython.lib.mixins.listctrl import wxColumnSorterMixin
from pySIMconstants import *
from pySIMutils import *
from pySIMskin import *
from traceback import print_exc
from binascii import hexlify, unhexlify

ID_LISTCTRL = wxNewId()
ID_MENU_FILE_READ = wxNewId()
ID_MENU_FILE_EXPORT = wxNewId()
ID_MENU_FILE_IMPORT = wxNewId()
ID_MENU_FILE_EXIT = wxNewId()
ID_BUTTON_OK = wxNewId()
ID_BUTTON_OVERWRITE = wxNewId()
ID_BUTTON_COPY = wxNewId()
ID_BUTTON_SKIP = wxNewId()
ID_BUTTON_CANCEL = wxNewId()
ID_CHECKBOX_APPLY_ALL = wxNewId()

ADN_FILE_PATH = ["3F00", "7F10", "6F3A"]
FDN_FILE_PATH = ["3F00", "7F10", "6F3B"]

class Phonebook(wxskinFrame, wxColumnSorterMixin):
    def __init__(self, master, SIMcontrol, filepath):
        self.parent = master
        self.SIM = SIMcontrol
        self.filepath = filepath
        wxskinFrame.__init__(self, self.parent, -1, "Phonebook", wxPyDefaultPosition, (500, 400))
        self.numberRecords = 0
        self.abortedRead = 0
        self.itemDataMap = {}
        self.createMenus()
        self.createWidgets()

    def createMenus(self):
        # Creating the menubar.
        menuBar = wxMenuBar()

        # Setting up the menu.
        filemenu = wxMenu()
        filemenu.Append(ID_MENU_FILE_READ, "Read"," Read your phonebook contacts from your SIM.")
        filemenu.AppendSeparator()
        filemenu.Append(ID_MENU_FILE_EXPORT, "Export..."," Export your phone contacts to file")
        filemenu.Append(ID_MENU_FILE_IMPORT, "Import..."," Import your phone contacts from file")
        filemenu.AppendSeparator()
        filemenu.Append(ID_MENU_FILE_EXIT, "Close"," Close the phonebook")
        # Adding the "filemenu" to the MenuBar
        menuBar.Append(filemenu,"&File")

        # Adding the MenuBar to the Frame content.
        self.SetMenuBar(menuBar)

        #Add the menu handlers
        EVT_MENU(self, ID_MENU_FILE_READ, self.read)
        EVT_MENU(self, ID_MENU_FILE_EXPORT, self.doExport)
        EVT_MENU(self, ID_MENU_FILE_IMPORT, self.doImport)
        EVT_MENU(self, ID_MENU_FILE_EXIT, self.closeWindow)

    def createWidgets(self):
        self.listCtrl = wxskinListCtrl(self, ID_LISTCTRL, style=wxLC_REPORT|wxSUNKEN_BORDER|wxLC_SINGLE_SEL|wxLC_VRULES|wxLC_HRULES)
        self.listCtrl.InsertColumn(0, "Name")
        self.listCtrl.InsertColumn(1, "Number")

        wxColumnSorterMixin.__init__(self, 2)

        self.currentItem = 0

        EVT_SIZE(self, self.OnSize)
        EVT_LIST_ITEM_SELECTED(self, ID_LISTCTRL, self.OnItemSelected)
        EVT_LIST_ITEM_ACTIVATED(self, ID_LISTCTRL, self.OnItemActivated)
        EVT_CLOSE(self, self.closeWindow)

        EVT_LEFT_DCLICK(self.listCtrl, self.OnPopupEdit)
        EVT_RIGHT_DOWN(self.listCtrl, self.OnRightDown)

        # for wxMSW and wxGTK respectively
        EVT_COMMAND_RIGHT_CLICK(self.listCtrl, ID_LISTCTRL, self.OnRightClick)
        EVT_RIGHT_UP(self.listCtrl, self.OnRightClick)

    def showWindow(self):
        self.parent.Show(0)
        self.Show(1)
        self.read()
        self.UpdateView()

    def closeWindow(self, event):
        self.SIM.phonebook = self.itemDataMap
        self.Show(0)
        self.parent.Show(1)
        self.Destroy()

    def doExport(self, event):
        export_count = 0
        dlg = wxFileDialog(self, "Save to file:", ".", "", "Text (*.txt)|*.txt", wxSAVE|wxOVERWRITE_PROMPT)
        if dlg.ShowModal() == wxID_OK:
            i = dlg.GetFilterIndex()
            if i == 0: # Text format
                try:
                    f = open(dlg.GetPath(), "w")
                    f.write('# "Name", Number\n')
                    for i in range(self.listCtrl.GetItemCount()):
                        f.write('"%s",%s\n' % (self.getColumnText(i,0), self.getColumnText(i,1)))
                        export_count += 1
                    f.close()
                    pySIMmessage(self, "Exported %d phonebook contacts\n\nFilename: %s" % (export_count, dlg.GetPath()), "Export OK")
                except:
                    print_exc()
                    pySIMmessage(self, "Unable to save your phonebook to file: %s" % dlg.GetPath(), "Export error")
#            elif i == 1: # Excel document
#                try:
#                    xl = win32com.client.Dispatch("Excel.Application")
#                    xl.Workbooks.Add() 
#                    xl.Cells(1,1).Value = "Name"
#                    xl.Cells(1,2).Value = "Number"
#                    for i in range(self.listCtrl.GetItemCount()):
#                        row = i + 2
#                        xl.Cells(row,1).Value = self.getColumnText(i,0)
#                        xl.Cells(row,2).Value = self.getColumnText(i,1)
#                        export_count += 1
#                    xl.ActiveWorkbook.SaveAs(dlg.GetPath())
#                    xl.ActiveWorkbook.DisplayAlerts = 0
#                    #xl.Saved = 1
#                    xl.Quit()
#                    pySIMmessage(self, "Exported %d phonebook contacts\n\nFilename: %s" % (export_count, dlg.GetPath()), "Export OK")
#                except:
#                    print_exc()
#                    pySIMmessage(self, "Unable to save your phonebook to file: %s" % dlg.GetPath(), "Export error")
        dlg.Destroy()

    def doImport(self, event):
        dlg = wxFileDialog(self, "Open file:", ".", "", "Text (*.txt)|*.txt", wxOPEN)
        if dlg.ShowModal() == wxID_OK:

            # Create a list of phonebook name entries
            oldNameList = {}
            newNameList = {}
            for i in self.itemDataMap.keys():
                oldNameList[self.itemDataMap[i][0]] = (i, self.itemDataMap[i][1])

            try:
                self.SIM.gotoFile(self.filepath)
            except:
                pySIMmessage(self, "Unable to find your SMS folder on your SIM card.", "SIM card error")
                return

            i = dlg.GetFilterIndex()
            if i == 0:
                # Text format
                f = open(dlg.GetPath(), "r")
                line_count = 0
                for line in f.readlines():
                    line_count += 1
                    if line[0] == '#': # Ignore comments
                        continue
                    # Ex. "Bradfield College",+612944842
                    pos = line.find('"')
                    rpos = line.rfind('"')
                    if rpos > pos:
                        name = line[pos+1:rpos]
                        number = line[rpos+2:].strip()
                        newNameList[name] = (0, number)
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
            apply_all = 0
            dlgGuage = wxskinProgressDialog("Import file to phonebook", "Importing %d phonebook entries" % len(newNameList), len(newNameList) + 1, self, wxPD_CAN_ABORT | wxPD_APP_MODAL)
            for namekey in newNameList.keys():
                import_type = 1
                import_count[0] += 1
                name = namekey
                number = newNameList[namekey][1]

                if len(name) > self.nameLength:
                    dlgError = wxskinMessageDialog(self, "Name '%s' is too long.\nOK to truncate to '%s'?\n\nIf you select no, then this entry will be ignored." % (name, name[:self.nameLength]),
                      'Import file error', wxYES_NO | wxICON_INFORMATION)
                    ret = dlgError.ShowModal()
                    dlgError.Destroy()
                    if ret != wxID_YES:
                        import_count[4] += 1
                        continue
                    name = name[:self.nameLength]

                if not dlgGuage.Update(import_count[0]):
                    break
                if oldNameList.has_key(name):
                    # Find out what they want to do (copy, overwrite, skip)
                    if not apply_all:
                        importDlg = ImportDialog(self.parent, name)
                        ret = importDlg.ShowModal()
                        funct = importDlg.getFunction()
                        if importDlg.applyAll.IsChecked():
                            apply_all = funct
                        importDlg.Destroy()
                    else:
                        ret = wxID_OK
                        funct = apply_all

                    if ret == wxID_OK:
                        if funct == ID_BUTTON_OVERWRITE:
                            pos = oldNameList[name][0]
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
                if not pos:
                    pySIMmessage(self, "Cannot save: %s (%s)\n\nNo free positions left on SIM card." % (name, number), "Import error - no space left on SIM")
                    break

                try:
                    if self.writePhonebookEntry(pos, name, number) == wxID_NO:
                        break
                    self.itemDataMap[pos] = (name, number)
                    import_count[import_type] += 1
                    i += 1
                except:
                    import_count[5] += 1
                    pySIMmessage(self, "Unable to save: %s (%s)" % (name, number), "SIM card error")

            dlgGuage.Destroy()
            pySIMmessage(self, "%d file import entries\n\n%d new entries\n%d overwritten entries\n%d copied entries\n%d entries skipped\n%d import errors" % (import_count[0], import_count[1], import_count[2], import_count[3], import_count[4], import_count[5]), "File import OK")
            self.UpdateView()
        dlg.Destroy()

    def read(self, *args):
        try:
            self.SIM.gotoFile(self.filepath)
            # Send the get response command, to find out record length
            data, sw = self.SIM.sendAPDUmatchSW("A0C000000F", SW_OK)
            self.recordLength  = int(data[28:30], 16) # Usually 0x20
            # Now we can work out the name length & number of records
            self.nameLength = self.recordLength - 14 # Defined GSM 11.11
            self.numberRecords = int(data[4:8], 16) / self.recordLength
        except:
            pySIMmessage(self, "Unable to find your phonebook on your SIM card.", "SIM card error")
            return

        if not self.SIM.checkAndVerifyCHV1(CHV_READ, data):
            return

        apdu = "A0B2%s04" + IntToHex(self.recordLength)
        dlg = wxskinProgressDialog("Phonebook", "Reading your phonebook entries", self.numberRecords + 1, self, wxPD_CAN_ABORT | wxPD_APP_MODAL)
        try:
            hexNameLen = self.nameLength << 1
            for i in range(1, self.numberRecords + 1):
                if not dlg.Update(i):
                    self.abortedRead = 1
                    break
                data, sw = self.SIM.sendAPDUmatchSW(apdu % IntToHex(i), SW_OK)
                # Find the end of the name
                #print data
                if data[0:2] != 'FF':
                    name = GSM3_38ToASCII(unhexlify(data[:hexNameLen]))
                    if ord(name[-1]) > 0x80:
                    	# Nokia phones add this as a group identifier. Remove it.
                    	name = name[:-1].rstrip()
                    number = ""
                    numberLen = int(data[hexNameLen:hexNameLen+2], 16)
                    if numberLen > 0 and numberLen <= (11): # Includes TON/NPI byte
                        hexNumber = data[hexNameLen+2:hexNameLen+2+(numberLen<<1)]
                        if hexNumber[:2] == '91':
                            number = "+"
                        number += GSMPhoneNumberToString(hexNumber[2:])
                    self.itemDataMap[i] = (name, number)
            self.abortedRead = 0
        except:
            # Finished with the guage
            self.abortedRead = 1
            print_exc()
            pySIMmessage(self, "Unable to read the phonebook on your SIM card.", "SIM card error")
        dlg.Destroy()

    def findFreePosition(self):
        k = self.itemDataMap.keys()
        i = 1
        while i <= self.numberRecords:
            if i not in k:
                return i
            i += 1
        return 0

    def UpdateView(self):
        self.listCtrl.DeleteAllItems()
        # Add our phonebook to the listbox
        i = 0
        for k in self.itemDataMap.keys():
            self.listCtrl.InsertStringItem(i, self.itemDataMap[k][0])
            self.listCtrl.SetStringItem(i, 1, self.itemDataMap[k][1])
            self.listCtrl.SetItemData(i, k)
            i += 1

        self.SortListItems(0, true)
        self.listCtrl.SetColumnWidth(0, 200)
        self.listCtrl.SetColumnWidth(1, 200)
 
        self.SetTitle("(%d/%d) phonebook entries" % (len(self.itemDataMap), self.numberRecords))

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
        menu = wxMenu()
        tPopupID0 = wxNewId()
        tPopupID1 = wxNewId()
        tPopupID2 = wxNewId()
        tPopupID3 = wxNewId()
        tPopupID4 = wxNewId()
        tPopupID5 = wxNewId()
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
        if len(self.itemDataMap) == 0:
            for m in menu.GetMenuItems():
                m.Enable(false)
            m = menu.FindItemById(tPopupID0)
            m.Enable(true)
            
        self.PopupMenu(menu, wxPoint(self.x, self.y))
        menu.Destroy()
        event.Skip()

    updateRecordPDU = "A0DC%s04%s%s"
    def writePhonebookEntry(self, pos, name='', number=''):
        if self.abortedRead:
            dlg = wxskinMessageDialog(self, "Did not finish reading your entire SIM card phonebook.\nAs a result, this may overwrite any exisiting phonebook contacts that have not been read yet!\n\nDo you wish to continue anyway?",
                                  'Overwrite warning', wxYES_NO | wxICON_WARNING)
            ret = dlg.ShowModal()
            dlg.Destroy()
            if ret == wxID_NO:
                return wxID_NO
            else:
                self.abortedRead = 0

        if not name:
            data = "FF" * self.recordLength
        else:
            GSMnumber = StringToGSMPhoneNumber(number)
            data = "%s%s%sFFFF" % ( padString(hexlify(ASCIIToGSM3_38(name)), self.nameLength << 1, "F"),
                                    IntToHex(len(GSMnumber) / 2),
                                    padString(GSMnumber, 22, 'F'))
        pdu = self.updateRecordPDU % (IntToHex(pos), IntToHex(self.recordLength), data)
        self.SIM.sendAPDUmatchSW(pdu, SW_OK)
        return wxID_YES

    def OnPopupNew(self, event):
        p = PhonebookEditEntry(self, '', '', 1, self.nameLength)
        if p.ShowModal() == wxID_OK:
            name, number = p.getValues()
            pos = self.findFreePosition()
            if pos:
                try:
                    self.SIM.gotoFile(self.filepath)
                    if not self.SIM.checkAndVerifyCHV1(CHV_UPDATE):
                        raise "Access conditions not met."
                    if self.writePhonebookEntry(pos, name, number) == wxID_YES:
                        self.itemDataMap[pos] = (name, number)
                        self.UpdateView()
                except:
                    pySIMmessage(self, "Unable to save: %s (%s)" % (name, number), "SIM card error")
            else:
                pySIMmessage(self, "Cannot save: %s (%s)\n\nNo free positions left on SIM card." % (name, number), "SIM card error")
        p.Destroy()

    def OnPopupCopy(self, event):
        name = self.getColumnText(self.currentItem, 0)
        number = self.getColumnText(self.currentItem, 1)
        p = PhonebookEditEntry(self, name, number, 1, self.nameLength)
        if p.ShowModal() == wxID_OK:
            name, number = p.getValues()
            pos = self.findFreePosition()
            if pos:
                try:
                    self.SIM.gotoFile(self.filepath)
                    if not self.SIM.checkAndVerifyCHV1(CHV_UPDATE):
                        raise "Access conditions not met."
                    if self.writePhonebookEntry(pos, name, number) == wxID_YES:
                        self.itemDataMap[pos] = (name, number)
                        self.UpdateView()
                except:
                    pySIMmessage(self, "Unable to save: %s (%s)" % (name, number), "SIM card error")
            else:
                pySIMmessage(self, "Cannot save: %s (%s)\n\nNo free positions left on SIM card." % (name, number), "SIM card error")
        p.Destroy()

    def OnPopupEdit(self, event):
        name = self.getColumnText(self.currentItem, 0)
        number = self.getColumnText(self.currentItem, 1)
        p = PhonebookEditEntry(self, name, number, 1, self.nameLength)
        if p.ShowModal() == wxID_OK:
            name, number = p.getValues()
            pos = self.listCtrl.GetItemData(self.currentItem)
            try:
                self.SIM.gotoFile(self.filepath)
                if not self.SIM.checkAndVerifyCHV1(CHV_UPDATE):
                    raise "Access conditions not met."
                if self.writePhonebookEntry(pos, name, number) == wxID_YES:
                    self.itemDataMap[pos] = (name, number)
                    self.UpdateView()
            except:
                pySIMmessage(self, "Unable to save: %s (%s)" % (name, number), "SIM card error")
        p.Destroy()

    def OnPopupDelete(self, event):
        key = self.listCtrl.GetItemData(self.currentItem)
        try:
            self.SIM.gotoFile(self.filepath)
            if not self.SIM.checkAndVerifyCHV1(CHV_UPDATE):
                raise "Access conditions not met."
            self.writePhonebookEntry(key)
            del self.itemDataMap[key]
            self.UpdateView()
        except:
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
                self.SIM.gotoFile(self.filepath)
                if not self.SIM.checkAndVerifyCHV1(CHV_UPDATE):
                    raise "Access conditions not met."
                i = 1
                for key in self.itemDataMap.keys()[:]:   # Make a copy of key table!!
                    if not dlg.Update(i):
                        break
                    self.writePhonebookEntry(key)
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
        col = self._col
        ascending = self._colSortFlag[col]
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

class PhonebookEditEntry(wxskinDialog):
    def __init__(self, parent, name, number, minnamelen, maxnamelen):
        wxskinDialog.__init__(self, parent, -1, "Phonebook edit entry")
        self.SetAutoLayout(true)
        self.name = None
        self.number = None
        nameTextId = wxNewId()

        # Main window resizer object
        border = wxBoxSizer(wxVERTICAL)

        label = wxStaticText(self, -1, "Enter the phonebook entry name, number and press OK.")
        border.Add(label, 1, wxALL, 10)

        #fgs = wxFlexGridSizer(2,3,5,20)
        fgs = wxBoxSizer(wxHORIZONTAL)
        label = wxStaticText(self, -1, "Name (max %d): " % maxnamelen)
        fgs.Add(label, 1, wxALIGN_LEFT | wxLEFT, 10)
        self.nameCtrl = wxTextCtrl(self, nameTextId, name, validator = pySIMvalidator(None, minnamelen, maxnamelen))
        fgs.Add(self.nameCtrl, 1, wxALIGN_RIGHT | wxRIGHT, 10)
        border.Add(fgs, 1, wxALL)

        fgs = wxBoxSizer(wxHORIZONTAL)
        label = wxStaticText(self, -1, "Number (max 20): ")
        fgs.Add(label, 1, wxALIGN_LEFT | wxLEFT, 10)
        self.numberCtrl = wxTextCtrl(self, -1, number, validator = pySIMvalidator("+*#pw0123456789", None, 20))
        fgs.Add(self.numberCtrl, 1, wxALIGN_RIGHT | wxRIGHT, 10)
        border.Add(fgs, 1, wxALL)

        buttons = wxBoxSizer(wxHORIZONTAL)
        buttons.Add(wxButton(self, ID_BUTTON_OK, "Okay"), 1, wxALIGN_LEFT | wxALL, 20)
        buttons.Add(wxButton(self, wxID_CANCEL, "Cancel"), 1, wxALIGN_RIGHT | wxALL, 20)
        border.Add(buttons, 1, wxALL)

        EVT_BUTTON(self, ID_BUTTON_OK, self.onOK)
        EVT_TEXT_ENTER(self, nameTextId, self.onOK)

        self.SetAutoLayout(1);
        self.SetSizer(border)
        border.Fit(self)
        self.Layout()

    def getValues(self):
        return (self.nameCtrl.GetValue(), self.numberCtrl.GetValue())

    def onOK(self, event):
        if self.Validate() and self.TransferDataFromWindow():
            for i in self.nameCtrl.GetValue().lower():
                if (((i < "a") or (i > "z")) and ((i < "%") or (i > "?"))):
                    if not dic_GSM_3_38.has_key(i):
                        pySIMmessage(self, "Invalid name. Cannot have character: %s" % i, "SIM card error")
                        return
            self.EndModal(wxID_OK)

class ImportDialog(wxskinDialog):
    def __init__(self, parent, name):
        wxskinDialog.__init__(self, parent, -1, "Phonebook import")
        self.SetAutoLayout(true)
        self.function = 0

        # Main window resizer object
        border = wxBoxSizer(wxVERTICAL)

        label = wxStaticText(self, -1, "Name '%s' already exists in SIM phonebook.\n\nDo you want to overwrite exisiting, duplicate or skip!?" % (name))
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
