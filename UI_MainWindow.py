import os
import sys
import shutil
import urllib.request
import json

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QMainWindow, QLabel, QWidget, QPushButton, QHBoxLayout, QGridLayout, QLineEdit, QMessageBox, \
    QVBoxLayout, QAction, QStackedWidget, QFileDialog, QTabWidget, QTextEdit, QScrollArea, QDialog, QComboBox, \
    QDialogButtonBox, QFrame, QCheckBox


import DB_Access as ex
import Models
import Models as dh

from AppVar import UserData, AppData
from Models import CustomDate, custDateTime, ApplicationValues

from UI_DataEdit import EventEditWindow, NPCEditWindow, SessionEditWindow, FightPrep
from UI_DataViews import FightView, ViewNpc, ViewDraftboard, Browser, SessionView
from UI_Utility import CustTextBrowser, DialogRandomNPC, DialogEditItem, Resultbox

class MyWindow(QMainWindow):
    """Manages the main window and all sublayouts

    """
    windowMode = "EditMode"  # EditMode or SessionMode

    tabAdded=pyqtSignal()
    dataChanged=pyqtSignal()


    def __init__(self):
        """initializes the mainWindow

        """

        super().__init__()
        AppData.mainWin=self
        self.timer = QTimer()

        #region signals
        self.tabAdded.connect(self.addTab)
        #endregion

        self.Mode_Stacked = QStackedWidget()
        self.setCentralWidget(self.Mode_Stacked)

        # region Menu_bar
        self.menu_Bar = self.menuBar()
        campaignMenu = self.menu_Bar.addMenu("&Campaign")

        openCampaign = QAction("Open Campaign", self)
        openCampaign.triggered.connect(self.load_Campaign_Filedialog)
        campaignMenu.addAction(openCampaign)

        newCampaign = QAction("New Campaign", self)
        newCampaign.triggered.connect(self.new_Campaign)
        campaignMenu.addAction(newCampaign)

        copyCampaign = QAction("New Campaign from", self)
        copyCampaign.triggered.connect(self.copy_Campaign_Filedialog)
        campaignMenu.addAction(copyCampaign)

        chooseSetting = QAction("Choose Setting", self)
        chooseSetting.triggered.connect(self.load_Setting_Filedialog)
        campaignMenu.addAction(chooseSetting)

        sessionMenu = self.menu_Bar.addMenu("&Session")

        startSession = QAction("start Session", self)
        startSession.triggered.connect(self.enterSession)
        sessionMenu.addAction(startSession)

        tabMenu = self.menu_Bar.addMenu("&Tabs")

        addDraftbook=QAction("Open new draftbook view", self)
        addDraftbook.triggered.connect(lambda: AppData.setCurrInfo(Flag="Draftbook",origin= self.man_Tab.currentWidget()))
        addDraftbook.triggered.connect(self.addTab)
        tabMenu.addAction(addDraftbook)

        addBrowser = QAction("Open new browser view",self)
        addBrowser.triggered.connect(lambda: AppData.setCurrInfo(Flag="Browser",origin= self.man_Tab.currentWidget()))
        addBrowser.triggered.connect(self.addTab)
        tabMenu.addAction(addBrowser)

        #endregion

        # region tabs
        self.man_Tab = QTabWidget()
        self.man_Tab.setTabsClosable(True)
        self.man_Tab.tabCloseRequested.connect(self.checkTabClose)
        self.Mode_Stacked.addWidget(self.man_Tab)
        # endregion

        # region check database compatibility
        self.checkBase()

        if not ApplicationValues.loadAppData():
            self.missingCampaign()

        if not self.checkCampaign(UserData.path):
            self.load_Campaign_Filedialog(exitOnFail=True)
        else:
            self.loadCampaign()
        # endregion

        self.setWindowTitle(UserData.path.split("/")[-1].rstrip(".db"))

        self.showMaximized()

    def checkBase(self)->None:
        """checks the NewCampaign Database for matching the applications database requirement and allows the user to
            select the download method on not matching database"""
        if not ex.checkLibrary(path="./Libraries/ProgrammData/NewCampaign.db"):
            msg = QDialog()
            lay = QVBoxLayout()
            msg.setLayout(lay)

            lbl = QLabel(
                "Current application database version does not match application version. Please select update method")
            lay.addWidget(lbl)

            BtnLay = QHBoxLayout()

            manDownl = QPushButton("Manual Download")
            manDownl.clicked.connect(msg.close)
            manDownl.clicked.connect(self.manualUpdateBase)
            BtnLay.addWidget(manDownl)

            autoDownl = QPushButton("Automatic Download")
            autoDownl.clicked.connect(msg.close)
            autoDownl.clicked.connect(self.autoUpdateBase)
            BtnLay.addWidget(autoDownl)

            cancel = QPushButton("Cancel")
            cancel.clicked.connect(msg.close)
            cancel.clicked.connect(sys.exit)
            BtnLay.addWidget(cancel)

            lay.addLayout(BtnLay)

            msg.exec()

    def autoUpdateBase(self)->None:
        """tries to automatically download the current version of newCampaign via gitHub and calls for manual download if failed"""
        try:
            os.remove("./Libraries/ProgrammData/NewCampaign.db")
            url = "https://github.com/grandolf14/PnP_Tool/raw/refs/heads/main/Libraries_default/ProgrammData/NewCampaign.db"
            urllib.request.urlretrieve(url, "./Libraries/ProgrammData/NewCampaign.db")

        except:
            msg = QMessageBox()
            msg.setText("Automatic download failed, use manual download instead.")
            if msg.exec():
                self.manualUpdateBase()
            sys.exit()


    def manualUpdateBase(self)->None:
        """Opens an info message to download the current NewCampaign version and exits application"""
        msg = QMessageBox()
        msg.setText(
            "<html> Please visit <a href=https://github.com/grandolf14/PnP_Tool/raw/refs/heads/main/Libraries_default/ProgrammData/NewCampaign.db> gitHub </a> to download the latest NewCampaign.db database and replace your current NewCampaign.db database with the dowloaded database. \n"
            "If you are not using the latest app version, please select the matching database manually from <a href=https://github.com/grandolf14/PnP_Tool/blob/main/Libraries_default/ProgrammData >here</a>.</hmtl>")

        msg.exec()
        sys.exit()

    def missingCampaign(self) -> None:
        """ Checks if the campaign opened last application execution still exists, if loads other campaign or new
        campaign on user selection"""


        dialog = QDialog()
        dialogLay = QVBoxLayout()
        dialog.setLayout(dialogLay)

        dialogLay.addWidget(
            QLabel("The campaign used in last program execution couldn't be found, please choose alternative:"))

        buttonlay = QHBoxLayout()

        open = QPushButton("Open other campaign")
        open.clicked.connect(dialog.accept)
        open.clicked.connect(lambda x: self.load_Campaign_Filedialog(exitOnFail=True, initCall=True))
        buttonlay.addWidget(open)

        new = QPushButton("Create new campaign")
        new.clicked.connect(dialog.accept)
        new.clicked.connect(lambda x: self.new_Campaign(exitOnFail=True, initCall=True))
        buttonlay.addWidget(new)

        dialogLay.addLayout(buttonlay)

        if not dialog.exec_():
            date = custDateTime.now().strftime("%Y-%m-%d_%H-%M")
            path = f'./Libraries/Campaign/NewCampaign_{date}.db'
            msg = QMessageBox()
            msg.setText(f"new Campaign was saved under: \n {path}")
            msg.exec_()

            shutil.copy(UserData.path, path)
            UserData.path = path

    def checkCampaign(self, path:str, exitOnFail:bool=False)->bool:
        """Checks the campaign database on matching required application version.

            :param path: str, the campaign path that should be checked
            :param exitOnFail: bool, optional, exits application if True and user selects that the database should'nt be upgraded

            :return: bool, True if the Library matches application requirement or it was successfully updated
            """
        if not ex.checkLibrary(path):
            dialog2 = QMessageBox()
            dialog2.setText(
                'The selected database version does not match the application version. Should the database'
                'version be updated?')
            dialog2.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
            if dialog2.exec_() == 16384:
                ex.updateLibraryVersion(path)
                return True
            else:
                if exitOnFail:
                    sys.exit()
                return False
        return True

    def new_Campaign(self, exitOnFail=False, initCall=False):
        """creates a new campaign

        :param exitOnFail: Bool, optional, specifies if the system should exit, if any step is aborted to prevent unwanted data change
        :param initCall: Bool, optional, if True prevents closeCampaign call, used only on myWindow init
        :return: ->None
        """
        copyFrom = './Libraries/ProgrammData/NewCampaign.db'
        dialog = QFileDialog()
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setDirectory(os.getcwd()+'/Libraries/Campaign')
        dialog.setNameFilter("Databases (*.db)")
        if dialog.exec_():
            copyTo = dialog.selectedFiles()[0]
            shutil.copy(copyFrom, copyTo)

            if not initCall:
                self.closeCampaign()

            UserData.path = copyTo
            self.loadCampaign()
        else:
            if exitOnFail:
                sys.exit()

    def copy_Campaign_Filedialog(self):
        """creates a new campaign importing the content of another campaign database

        :return: ->None
        """
        dialog = QFileDialog()
        dialog.setWindowTitle("select database to copy files")
        dialog.setDirectory(os.getcwd()+'./Libraries/Campaign')
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter("Databases (*.db)")
        if dialog.exec_():
            selectedFile = dialog.selectedFiles()[0]
            retVal = None
            if not ex.checkLibrary(selectedFile):
                msg = QMessageBox()
                msg.setText("Invalid database version, should the original database be updated?")
                msg.setInformativeText(
                    "If no is selected, only the new Campaign will work with current application version ")
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
                msg.setDefaultButton(QMessageBox.Yes)

                retVal = msg.exec_()

                if retVal == 16384:  # Yes
                    path = ex.updateLibraryVersion(selectedFile)
                    if type(path) == str:
                        msg = QMessageBox()
                        msg.setText("Update failed, please use the backup: " + path)
                        msg.exec_()
                        return
                elif retVal == 4194305:  # cancel
                    return

            copyFrom = dialog.selectedFiles()[0]
            dialog2 = QFileDialog()
            dialog2.setAcceptMode(QFileDialog.AcceptSave)
            dialog2.setDirectory(os.getcwd()+'./Libraries/Campaign')
            dialog2.setNameFilter("Databases (*.db)")
            if dialog2.exec_():
                copyTo = dialog2.selectedFiles()[0]
                shutil.copy(copyFrom, copyTo)
                if retVal == 65536:  # No
                    path = ex.updateLibraryVersion(copyTo)
                    if type(path) == str:
                        msg = QMessageBox()
                        msg.setText("Update failed, please use the backup: " + path)
                        return

                Models.ApplicationValues.save()
                UserData.path = copyTo
                self.loadCampaign()

        return

    def load_Campaign_Filedialog(self, exitOnFail=False, initCall=False):
        """opens a filedialog to choose current Campaign.

        :param exitOnFail: Bool, optional, specifies if the system should exit on abortion to prevent unwanted data manipulation
        :param initCall: Bool, optional, if True prevents closeCampaign call, used only on myWindow init
        :return: ->None
        """

        dialog = QFileDialog()
        dialog.setWindowTitle("open Campaign Database")
        dialog.setDirectory(os.getcwd()+'./Libraries/Campaign')
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter("Databases (*.db)")
        if dialog.exec_():
            selectedFile = dialog.selectedFiles()[0]

            if self.checkCampaign(path=selectedFile, exitOnFail=exitOnFail):
                if not initCall:
                    self.closeCampaign()
                UserData.path = dialog.selectedFiles()[0]
                self.loadCampaign()
        else:
            if exitOnFail:
                sys.exit()
        return

    def loadCampaign(self)->None:
        """loads campaign database data, updates window title and reloads all widgets and user defined application layout"""
        ApplicationValues.loadCampaignData()
        self.setWindowTitle(UserData.path.split("/")[-1].rstrip(".db"))

        self.loadTabLayout()

    def closeCampaign(self)->None:
        """saves all values of currently opened campaign and prevents opened editViews from data loss"""

        if self.Mode_Stacked.widget(1) is not None:
            self.ses_Wid.saveValues()
            self.Mode_Stacked.removeWidget(self.ses_Wid)

        ApplicationValues.save()

        self.abortMission=False

        for index in reversed(range(self.man_Tab.count())):
            widget = self.man_Tab.widget(index)
            self.checkTabClose(widget, remove=False, allowCancel=False)
            if self.abortMission:
                return


        return

    def load_Setting_Filedialog(self):
        """opens a filedialog to choose the Setting for current Campaign.

        :return: ->None
        """
        setDialog = QFileDialog()
        setDialog.setWindowTitle("open Setting Database")
        setDialog.setFileMode(QFileDialog.ExistingFile)
        setDialog.setNameFilter("Databases (*.db)")
        setDialog.setDirectory(os.getcwd()+'/Libraries/Setting/')
        if setDialog.exec_():
            if ex.checkLibrary(setDialog.selectedFiles()[0], False):
                dialog2 = QMessageBox()
                dialog2.setText('select Valid Database')
                dialog2.exec_()
                self.load_Setting_Filedialog()
                return

            UserData.Settingpath = setDialog.selectedFiles()[0]


    def loadTabLayout(self)->None:
        """opens tabs in style defined by Userdata.campaignAppLayout and updates UserData.campaignAppLayout with current
        widget ids. AppData.setCurrInfo transfers the new tab specifics to the receiver of the tabAdded signal.

        :return: None
        """
        appLayout=UserData.campaignAppLayout.copy()
        UserData.campaignAppLayout={}
        for key in appLayout.keys():

            ID = appLayout[key]["id"]
            Flag = appLayout[key]["type"]
            Data = appLayout[key]["data"]
            origin=appLayout[key]["origin"]

            if origin is not None:
                try:
                    index=list(appLayout.keys()).index(origin)
                    widget=self.man_Tab.widget(index)
                    origin=widget
                except:
                    origin=None

            AppData.setCurrInfo(ID,Flag,Data,origin)
            self.tabAdded.emit()

        return

    def addTab(self)->None:
        """function called by the tabAdded signal of MyWindow. Adds a new tab with the specifics of AppData:
                current_ID holds the id of linked dataset
                current_Flag holds the type of new opened tab
                current_Data holds further information
                current_origin holds the tab that requested the new tab open or that was visible while open was requested
                                origin will be saved as widgets caller

                switches to widget after opening the new tab

        :return: None
        """
        ID=AppData.current_ID
        Flag=AppData.current_Flag
        notes= AppData.current_Data
        caller=AppData.current_origin

        if Flag != "Browser" and Flag != "Draftbook":
            existing_tabs=UserData.campaignAppLayout
            for tab in existing_tabs:
                if existing_tabs[tab]["type"]==Flag and existing_tabs[tab]["id"]==ID:
                    self.man_Tab.setCurrentIndex(list(existing_tabs).index(tab))
                    return

        new=False
        if ID==None:
            new=True

        if Flag=="Browser":
            name = Flag
            widget=Browser()
            self.dataChanged.connect(widget.updateSearch)
            widget.dataChanged.connect(self.dataChanged.emit)

        elif Flag=="Draftbook":
            name = Flag
            widget=ViewDraftboard()
            self.dataChanged.connect(widget.Draftboard.updateScene)


        elif Flag=="Individuals":
            widget=NPCEditWindow(id=ID, new=new, notes=notes)
            widget.dataChanged.connect(self.dataChanged.emit)
            widget.widgetClosed.connect(lambda: self.closeTab(widget))

            if new:
                name= "New Character"
            else:
                fnames=[x[0]+"." for x in widget.data["indiv_fName"].split(" ")]
                fnames = " ".join(fnames)
                name = "Char : %.15s" %(fnames +" " +widget.data["family_Name"])

        elif Flag=="Events":
            widget=EventEditWindow(id=ID, new=new, notes=notes)
            widget.dataChanged.connect(self.dataChanged.emit)
            widget.widgetClosed.connect(lambda: self.closeTab(widget))

            if new:
                name= "New Event"
            else:
                name = "Event : %.15s" % widget.data["event_Title"]

        elif Flag== "Sessions":
            widget= SessionEditWindow(id=ID, new=new, notes=notes)
            widget.dataChanged.connect(self.dataChanged.emit)
            widget.widgetClosed.connect(lambda: self.closeTab(widget))
            if new:
                name= "New Session"
            else:
                name = "Session : %.15s" % widget.data["session_Name"]


        widget.caller = caller

        callerID=None
        if caller is not None:
            callerID=str(id(caller))

        UserData.campaignAppLayout[id(widget)] = {"type": Flag, "data": notes, "id": ID, "origin": callerID}

        self.man_Tab.addTab(widget, name)
        self.man_Tab.setCurrentWidget(widget)
    # region Buttons

    def checkTabClose(self, widget, remove=True, allowCancel=True)->None:
        """checks the inserted widget for unsaved data and allows user to save or abort changes if there is any before
        closing the tab.

        :param widget: pyqt5 widget, the widget that defines the tab that should be removed
        :param remove: bool, optional, if True the widget will be removed from central tab control
                                    [UserData.campaignAppLayout], not removed widgets will be saved for next campaign open
        :param allowCancel: bool, optional, in certain cases canceling the tab close leads to bugs

        :return: None
        """
        requestedTab = widget
        if type(requestedTab)==int:
            requestedTab=self.man_Tab.widget(widget)

        widClass = type(requestedTab)
        if widClass != EventEditWindow and widClass != SessionEditWindow and widClass != NPCEditWindow:
            self.closeTab(requestedTab, remove=remove)
            return

        if requestedTab.ValuesChanged is False:
            self.closeTab(requestedTab, remove=remove)
            return

        self.man_Tab.setCurrentWidget(requestedTab)
        dial = QDialog()
        dialLay = QVBoxLayout()
        dial.setLayout(dialLay)
        dialLay.addWidget(QLabel("Changes are not saved. Pleases select an option:"))

        save = QPushButton("Save changes")
        save.clicked.connect(requestedTab.apply)
        save.clicked.connect(dial.close)
        dialLay.addWidget(save)

        abort = QPushButton("Abort changes")
        abort.clicked.connect(requestedTab.cancel)
        abort.clicked.connect(dial.close)
        dialLay.addWidget(abort)

        cancel = QPushButton("Cancel")
        cancel.clicked.connect(dial.close)
        cancel.clicked.connect(self.abort)
        dialLay.addWidget(cancel)
        self.abortMission = False

        dial.exec_()


    def abort(self):
        self.abortMission=True
    # endregion
    
    def closeTab(self, widget, remove=True)->None:
        """closes a tab and if the tab has a caller defined and the caller exists switches to caller tab. Caller is the
            tab, from which the closed tab was opened.

            :param widget: pyqt5 widget, the tab that should be closed
            :param remove: bool, optional, if True the widget will be removed from central tab control
                                    [UserData.campaignAppLayout], not removed widgets will be saved for next campaign open
            :return: None
        """
        requestedTab = widget
        identifier=id(requestedTab)

        if hasattr(requestedTab,"caller") and self.man_Tab.indexOf(requestedTab.caller)!=-1:
            if type(requestedTab.caller)==ViewDraftboard:
                requestedTab.caller.Draftboard.updateScene()

            self.man_Tab.setCurrentWidget(requestedTab.caller)
        else:
            self.man_Tab.setCurrentIndex(0)

        self.man_Tab.removeTab(self.man_Tab.indexOf(widget))
        if remove:
             del UserData.campaignAppLayout[identifier]

    def enterSession(self)->None:
        """initializes new SessionView and enters the SessionView"""
        self.menu_Bar.hide()
        sessionActive = ex.searchFactory("1", 'Sessions', attributes=["current_Session"],dictOut=True)
        if len(sessionActive) == 0:
            messagbox = QMessageBox()
            messagbox.setText("pls make active Session first")
            messagbox.exec_()
            return

        id = sessionActive[0]["session_ID"]
        self.ses_Wid = SessionView(id)
        self.Mode_Stacked.addWidget(self.ses_Wid)
        self.Mode_Stacked.setCurrentWidget(self.ses_Wid)

    def leaveSession(self)->None:
        """Saves all changed sessionData in UserData and closes the SessionView"""
        self.ses_Wid.saveValues()

        self.menu_Bar.show()
        self.Mode_Stacked.setCurrentWidget(self.man_Tab)
        self.Mode_Stacked.removeWidget(self.ses_Wid)
    # region other

    def openInfoBox(self, text, delay=3000):
        """opens a dialog with a simple text-message for users

        :param text: str, text of infobox
        :param delay: int, the time the infobox should be visible
        :return: ->None
        """

        counter = 0
        textNew = ""
        for object in text.split(" "):
            counter += len(object)
            while len(object) > 20:
                textNew += object[0:20] + "-\n"
                object = object[20:len(object)]
                continue
            if counter > 20:
                counter = 0
                textNew += "\n"
                textNew += object + " "
            else:
                textNew += object + " "

        self.infoBox = QDialog()

        self.infoBox.setWindowFlags(Qt.CustomizeWindowHint)
        infoboxLay = QVBoxLayout()
        self.infoBox.setLayout(infoboxLay)
        infoboxLay.addWidget(QLabel(textNew), alignment=Qt.Alignment(4))
        self.timer2 = QTimer()
        self.timer2.timeout.connect(self.infoBox.close)
        self.timer2.start(delay)
        ph = self.geometry().height()
        pw = self.geometry().width()
        px = self.geometry().x()
        py = self.geometry().y()
        # self.infoBox.move(px+pw -dw, py + ph - dh)
        self.infoBox.setGeometry(px + pw - 250, py + ph - 130, 220, 100)
        self.infoBox.open()

    def closeEvent(self, event)->None:
        """saves all applicationValues on MyWindow close by exiting.

        :return: None
        """
        self.closeCampaign()
        if not self.abortMission:
            event.accept()
            super().closeEvent(event)
        else:
            event.ignore()



    # TODO implement searchdialog and fastcreate
    # region searchdialog

    def timer_start(self, delay=500, function=None):
        """calls a function after a specific delay

        :param delay: int, optional, milliseconds of delay
        :param function: function, optional, function to call after delay
        :return:
        """
        if not function:
            function = self.linEditChanged_man_searchNPC

        self.timer.timeout.connect(function)
        self.timer.start(delay)
    def openSearchDialog(self, text, searchIn: str, createNew=False):

        self.searchDialogResult = []
        self.searchDialog = QDialog()
        searchDialog_layout = QVBoxLayout()
        self.searchDialog.setLayout(searchDialog_layout)

        searchDialog_layout.addWidget(QLabel(text), stretch=10)

        self.searchDialog_label = QLabel("\n")
        searchDialog_layout.addWidget(self.searchDialog_label)

        self.searchDialog_lineEdit = QLineEdit()
        self.searchDialog_lineEdit.textEdited.connect(
            lambda: self.timer_start(500, lambda: self.lineEditChanged_searchDialog(searchIn)))
        searchDialog_layout.addWidget(self.searchDialog_lineEdit)

        if createNew:
            self.searchDialog_Btn_createNew = QPushButton("create New")
            self.searchDialog_Btn_createNew.clicked.connect(lambda: self.btn_fastCreate(searchIn))
            searchDialog_layout.addWidget(self.searchDialog_Btn_createNew)

        searchDialog_scroll = QScrollArea()
        searchDialog_scroll.setWidgetResizable(True)
        searchDialog_layout.addWidget(searchDialog_scroll)

        searchDialog_Result = QWidget()
        self.searchDialog_Result_lay = QVBoxLayout()
        searchDialog_Result.setLayout(self.searchDialog_Result_lay)
        searchDialog_scroll.setWidget(searchDialog_Result)

        searchDialog_button_layHB = QHBoxLayout()
        searchDialog_layout.addLayout(searchDialog_button_layHB)

        okButton = QPushButton("apply Changes")
        okButton.clicked.connect(self.searchDialog.close)
        searchDialog_button_layHB.addWidget(okButton)

        cancelButton = QPushButton("cancel")
        cancelButton.clicked.connect(self.btn_searchDialog_cancel)
        searchDialog_button_layHB.addWidget(cancelButton)

        self.lineEditChanged_searchDialog(searchIn)
        self.searchDialog.exec()
        return self.searchDialogResult

    def btn_fastCreate(self, Class):

        helpInstanceList = [None for x in range(Class.requiredVar)]
        helpInstance = Class(*helpInstanceList)

        self.fastCreateDialog = QDialog()
        self.fastCreateDialog_layout = QVBoxLayout()
        self.fastCreateDialog.setLayout(self.fastCreateDialog_layout)

        for i in range(Class.requiredVar):
            label = QLabel("%s:" % (helpInstance.__dict__[list(helpInstance.__dict__)[i]]))
            self.fastCreateDialog_layout.addWidget(label)

            lineedit = QLineEdit()
            self.fastCreateDialog_layout.addWidget(lineedit)

        layout2 = QHBoxLayout()

        button = QPushButton("create")
        button.clicked.connect(self.btn_fastcreate_create)
        layout2.addWidget(button)

        button = QPushButton("cancel")
        button.clicked.connect(self.fastCreateDialog.close)
        layout2.addWidget(button)
        self.fastCreateDialog_layout.addLayout(layout2)

        self.fastcreate_argumentList = []
        self.fastCreateDialog.exec()
        instance = Class(*self.fastcreate_argumentList)

        return instance

    def btn_fastcreate_create(self):

        getValues = []
        counter = 0

        for index in range(self.fastCreateDialog_layout.count()):
            if self.fastCreateDialog_layout.itemAt(index) is not None:
                item = self.fastCreateDialog_layout.itemAt(index).widget()
            else:
                continue
            if type(item) == QLineEdit:
                counter += 1
                if item.text() != "":
                    getValues.append(item.text())

        self.fastcreate_argumentList = getValues
        if len(getValues) < counter:
            msgBox = QMessageBox()
            msgBox.setText("Bitte alle Felder ausfüllen!")
            msgBox.exec()

        else:
            self.fastCreateDialog.close()

    def btn_searchDialog_cancel(self):
        self.searchDialogResult = []
        self.searchDialog.close()

    def btn_searchDialog_choose(self, instance):
        self.searchDialogResult = instance
        self.searchDialog_label.setText("chosen: \n" + str(instance))

    def lineEditChanged_searchDialog(self, searchIn):
        self.timer.stop()

        self.clearLayout(self.searchDialog_Result_lay)

        for instance in ex.searchFactory(self.searchDialog_lineEdit.text(), searchIn, shortOut=True):
            button = QPushButton(str(instance))
            button.clicked.connect(lambda: self.btn_searchDialog_choose(instance))
            self.searchDialog_Result_lay.addWidget(button)

    def clearLayout(self,layout):  #
        """removes all items from the layout

        :param layout: QLayout-widget
        :return: ->None
        """
        for i in reversed(range(layout.count())):
            layoutItem = layout.itemAt(i)
            if layoutItem.widget() is not None:
                widgetToRemove = layoutItem.widget()
                widgetToRemove.setParent(None)
                layout.removeWidget(widgetToRemove)
            elif layoutItem.spacerItem() is not None:
                widgetToRemove = layoutItem.spacerItem()
                layout.removeItem(widgetToRemove)
            else:
                layoutToRemove = layout.itemAt(i)
                self.clearLayout(layoutToRemove)
    # endregion



