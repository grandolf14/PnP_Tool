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
from Models import CustomDate, custDateTime

from UI_Browser import Resultbox
from UI_DataEdit import EventEditWindow, NPCEditWindow, SessionEditWindow, FightPrep
from UI_DataViews import FightView, ViewNpc, ViewDraftboard, Browser, SessionView
from UI_Utility import CustTextBrowser, DialogRandomNPC, DialogEditItem

class MyWindow(QMainWindow):
    """Manages the main window and all sublayouts

    """
    windowMode = "EditMode"  # EditMode or SessionMode
    searchMode = False  # currently searching fulltext or not
    sessionSearchFilter = {}  # Session filter specifications
    NPCSearchFilter = {}  # NPC filter specification
    eventSearchFilter = {}  # Event filter specification

    TabAdded=pyqtSignal()
    campaignSelected=pyqtSignal()


    def __init__(self):
        """initializes the mainWindow

        """

        super().__init__()
        AppData.mainWin=self

        #region signals
        self.TabAdded.connect(self.addTab)

        #endregion


        self.timer = QTimer()

        self.checkBase()

        if not self.checkCampaign(UserData.path):
            self.load_Campaign_Filedialog(exitOnFail=True)

        self.setWindowTitle(UserData.path.split("/")[-1].rstrip(".db"))
        self.mainWin_stWid = QStackedWidget()
        self.setCentralWidget(self.mainWin_stWid)

        # region Management
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
        startSession.triggered.connect(self.btn_switch_windowMode)
        sessionMenu.addAction(startSession)

        tabMenu = self.menu_Bar.addMenu("&Tabs")

        addDraftbook=QAction("Open new draftbook view", self)
        addDraftbook.triggered.connect(lambda: AppData.setCurrInfo(Flag="Draftbook",origin= self.man_cen_tabWid.currentWidget()))
        addDraftbook.triggered.connect(self.addTab)
        tabMenu.addAction(addDraftbook)

        addBrowser = QAction("Open new browser view",self)
        addBrowser.triggered.connect(lambda: AppData.setCurrInfo(Flag="Browser",origin= self.man_cen_tabWid.currentWidget()))
        addBrowser.triggered.connect(self.addTab)
        tabMenu.addAction(addBrowser)

        self.man_main_Wid = QWidget()
        self.man_main_layVB = QVBoxLayout()
        self.man_main_Wid.setLayout(self.man_main_layVB)
        self.mainWin_stWid.addWidget(self.man_main_Wid)

        self.man_cen_tabWid = QTabWidget()
        self.man_cen_tabWid.setTabsClosable(True)
        self.man_cen_tabWid.tabCloseRequested.connect(self.checkTabClose)
        self.man_main_layVB.addWidget(self.man_cen_tabWid)

        # region standard tabs
        self.loadTabLayout()
        # endregion

        self.ses_Main_wid= SessionView()
        self.mainWin_stWid.addWidget(self.ses_Main_wid)

        # endregion
        self.showMaximized()

        # creates a new Campaign if the last opened Campaign does not exist
        if dh.ApplicationValues.newFlag:
            dialog = QDialog()
            dialogLay = QVBoxLayout()
            dialog.setLayout(dialogLay)

            dialogLay.addWidget(
                QLabel("The campaign used in last program execution couldn't be found, please choose alternative:"))

            buttonlay = QHBoxLayout()

            open = QPushButton("Open other campaign")
            open.clicked.connect(dialog.accept)
            open.clicked.connect(lambda x: self.load_Campaign_Filedialog(exitOnFail=True))
            buttonlay.addWidget(open)

            new = QPushButton("Create new campaign")
            new.clicked.connect(dialog.accept)
            new.clicked.connect(lambda x: self.new_Campaign(exitOnFail=True))
            buttonlay.addWidget(new)

            dialogLay.addLayout(buttonlay)

            if not dialog.exec_():
                date = custDateTime.now().strftime("%Y-%m-%d_%H-%M")
                path = f'./Libraries/Campaign/NewCampaign_{date}.db'
                msg = QMessageBox()
                msg.setText(f"new Campaign was saved under: \n {path}")
                msg.exec_()

                shutil.copy(UserData.path, path)
                Models.ApplicationValues.save()
                UserData.path = path
                self.reload_Campaign()

    def closeAllTabs(self)->None:
        """closes AllTabs and saves all SessionValues"""
        for index in reversed(range(self.man_cen_tabWid.count())):
            widget = self.man_cen_tabWid.widget(index)
            self.checkTabClose(widget, remove=False, allowCancel=False)
        return


    def loadTabLayout(self)->None:
        """opens tabs in style defined by Userdata.campaignAppLayout and updates UserData.campaignAppLayout with current
        widget ids. AppData.setCurrInfo transfers the new tab specifics to the receiver of the tabAdded signal.

        :return: None
        """
        appLayout=UserData.campaignAppLayout.copy()
        UserData.campaignAppLayout={}
        for key in appLayout.keys():
            AppData.setCurrInfo()
            ID = appLayout[key]["id"]
            Flag = appLayout[key]["type"]
            Data = appLayout[key]["data"]
            origin=appLayout[key]["origin"]

            if origin is not None:
                try:
                    index=list(appLayout.keys()).index(origin)
                    widget=self.man_cen_tabWid.widget(index)
                    origin=widget
                except:
                    origin=None

            AppData.setCurrInfo(ID,Flag,Data,origin)
            self.TabAdded.emit()

            widget=self.man_cen_tabWid.currentWidget()
            if type(widget)== EventEditWindow or type(widget)== SessionEditWindow   or type(widget)== NPCEditWindow:
                widget.setExit(lambda: AppData.mainWin.closeTab(widget))


        for origin in [appLayout[key]["origin"] for key in appLayout.keys()]:
            if origin is not None and origin in appLayout.keys():
                index=list(appLayout.keys()).index(origin)
                widget=self.man_cen_tabWid.widget(index)
        return


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
            requestedTab=self.man_cen_tabWid.widget(widget)

        widClass = type(requestedTab)
        if widClass == EventEditWindow or widClass == SessionEditWindow or widClass == NPCEditWindow:
            dial = QDialog()
            dialLay = QVBoxLayout()
            dial.setLayout(dialLay)
            dialLay.addWidget(QLabel("Changes are not saved. Pleases select an option:"))

            save = QPushButton("Save changes")
            save.clicked.connect(lambda: requestedTab.apply(requestedTab.id))
            save.clicked.connect(dial.close)
            dialLay.addWidget(save)

            abort = QPushButton("Abort changes")
            abort.clicked.connect(lambda: requestedTab.cancel(requestedTab.id))
            abort.clicked.connect(dial.close)
            dialLay.addWidget(abort)

            if allowCancel:
                cancel = QPushButton("Cancel")
                cancel.clicked.connect(dial.close)
                dialLay.addWidget(cancel)

            dial.exec_()
        else:
            self.closeTab(requestedTab, remove=remove)


    def closeTab(self, widget, remove=True)->None:
        """closes a tab and if the tab has a caller defined and the caller exists switches to caller tab. Caller is the
            tab, from which the closed tab was opened.

            :param widget: pyqt5 widget, the tab that should be closed
            :param remove: bool, optional, if True the widget will be removed from central tab control
                                    [UserData.campaignAppLayout], not removed widgets will be saved for next campaign open
            :return: None
        """
        requestedTab = widget

        if hasattr(requestedTab,"caller") and self.man_cen_tabWid.indexOf(requestedTab.caller)!=-1:
            if type(requestedTab.caller)==ViewDraftboard:
                requestedTab.caller.man_Draftboard.updateScene()

            self.man_cen_tabWid.setCurrentWidget(requestedTab.caller)
        else:
            self.man_cen_tabWid.setCurrentIndex(0)

        self.man_cen_tabWid.removeTab(self.man_cen_tabWid.indexOf(widget))
        if remove:
            UserData.campaignAppLayout.pop(id(requestedTab))

    def addTab(self)->None:
        """function called by the TabAdded signal of MyWindow. Adds a new tab with the specifics of AppData:
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

        new=False
        if ID==None:
            new=True

        if Flag=="Browser":
            widget=Browser()

        elif Flag=="Draftbook":
            widget=ViewDraftboard(self)

        elif Flag=="Individuals":
            widget=NPCEditWindow(id=ID, new=new, notes=notes)

        elif Flag=="Events":
            widget=EventEditWindow(id=ID, new=new, notes=notes)

        elif Flag== "Sessions":
            widget= SessionEditWindow(id=ID, new=new, notes=notes)

        widget.caller = caller

        callerID=None
        if caller is not None:
            callerID=str(id(caller))

        UserData.campaignAppLayout[id(widget)] = {"type": Flag, "data": notes, "id": ID, "origin": callerID}

        self.man_cen_tabWid.addTab(widget, "Neu")
        self.man_cen_tabWid.setCurrentWidget(widget)

    # region Buttons

    # region window unspecific Buttons

    def btn_autoUpdate(self):

        try:
            os.remove("./Libraries/ProgrammData/NewCampaign.db")
            url = "https://github.com/grandolf14/PnP_Tool/raw/refs/heads/main/Libraries_default/ProgrammData/NewCampaign.db"
            urllib.request.urlretrieve(url, "./Libraries/ProgrammData/NewCampaign.db")

        except:
            msg = QMessageBox()
            msg.setText("Automatic download failed, use manual download instead.")
            if msg.exec():
                self.btn_manualUpdate()
            sys.exit()

        return

    def btn_manualUpdate(self):
        msg = QMessageBox()
        msg.setText(
            "<html> Please visit <a href=https://github.com/grandolf14/PnP_Tool/raw/refs/heads/main/Libraries_default/ProgrammData/NewCampaign.db> gitHub </a> to download the latest NewCampaign.db database and replace your current NewCampaign.db database with the dowloaded database. \n"
            "If you are not using the latest app version, please select the matching database manually from <a href=https://github.com/grandolf14/PnP_Tool/blob/main/Libraries_default/ProgrammData >here</a>.</hmtl>")

        msg.exec()
        sys.exit()

    def btn_switch_windowMode(self) -> None:
        """switches between the session and the management interface of the application and updates the session interface

        :return: ->None
        """
        if self.windowMode == "SessionMode":
            self.menu_Bar.show()
            self.windowMode = "EditMode"
            self.mainWin_stWid.setCurrentWidget(self.man_main_Wid)

        else:
            self.windowMode = "SessionMode"
            self.menu_Bar.hide()
            sessionActive = ex.searchFactory("1", 'Sessions', attributes=["current_Session"])
            if len(sessionActive) > 0:
                id = sessionActive[0][0]
                self.ses_Main_wid.btn_openPlot()
            else:
                messagbox = QMessageBox()
                messagbox.setText("pls make active Session first")
                messagbox.exec_()
                return

            self.ses_Main_wid.temp_streamSave = self.streamDecode(id)
            self.ses_Main_wid.stream_Res.resultUpdate(self.ses_Main_wid.temp_streamSave)
            self.ses_Main_wid.load_SceneRes()
            self.mainWin_stWid.setCurrentWidget(self.ses_Main_wid)

            session_NPC = ex.searchFactory("1", 'Session_Individual_jnt', attributes=['current_Session'],
                                           output="Individuals.individual_ID,indiv_fName,family_Name", shortOut=True)

            self.ses_Main_wid.sesNPC_Res.resultUpdate(session_NPC)
    # endregion

    # region other
    def checkBase(self):
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
            manDownl.clicked.connect(self.btn_manualUpdate)
            BtnLay.addWidget(manDownl)

            autoDownl = QPushButton("Automatic Download")
            autoDownl.clicked.connect(msg.close)
            autoDownl.clicked.connect(self.btn_autoUpdate)
            BtnLay.addWidget(autoDownl)

            cancel = QPushButton("Cancel")
            cancel.clicked.connect(msg.close)
            cancel.clicked.connect(sys.exit)
            BtnLay.addWidget(cancel)

            lay.addLayout(BtnLay)

            msg.exec()

    def checkCampaign(self, path, exitOnFail=False):
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

    def reload_Campaign(self):
        """reloads all contents of selected campaign and setting

        :return: ->None"""

        self.closeAllTabs()
        Models.ApplicationValues.load()

        UserData.Settingpath = ex.getFactory(1, "DB_Properties", path=UserData.path, dictOut=True)[
            "setting_Path"]
        self.setWindowTitle(UserData.path.split("/")[-1].rstrip(".db"))

        UserData.campaignAppLayout=json.loads(ex.getFactory(1, "LastSessionData", path=UserData.path, dictOut=True)["campaignAppLayout"])

        self.loadTabLayout()
        self.campaignSelected.emit()
        return

    def new_Campaign(self, exitOnFail=False):
        """creates a new campaign


        :param exitOnFail: Bool, optional, specifies if the system should exit, if any step is aborted to prevent unwanted data manipulation
        :return: ->None
        """
        copyFrom = './Libraries/ProgrammData/NewCampaign.db'
        dialog = QFileDialog()
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setDirectory('./Library/Campaign')
        dialog.setNameFilter("Databases (*.db)")
        if dialog.exec_():
            copyTo = dialog.selectedFiles()[0]
            shutil.copy(copyFrom, copyTo)
            Models.ApplicationValues.save()
            UserData.path = copyTo
            self.reload_Campaign()
        else:
            if exitOnFail:
                sys.exit()

    def copy_Campaign_Filedialog(self):
        """creates a new campaign importing the content of another campaign database

        :return: ->None
        """
        dialog = QFileDialog()
        dialog.setWindowTitle("select database to copy files")
        dialog.setDirectory('./Library/Campaign')
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
            dialog2.setDirectory('./Library/Campaign')
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
                self.reload_Campaign()

        return

    def load_Campaign_Filedialog(self, exitOnFail=False):
        """opens a filedialog to choose current Campaign.


        :param exitOnFail: Bool, optional, specifies if the system should exit on abortion to prevent unwanted data manipulation
        :return: ->None
        """

        dialog = QFileDialog()
        dialog.setWindowTitle("open Campaign Database")
        dialog.setDirectory('./Library/Campaign')
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter("Databases (*.db)")
        if dialog.exec_():
            selectedFile = dialog.selectedFiles()[0]

            if self.checkCampaign(path=selectedFile, exitOnFail=exitOnFail):
                Models.ApplicationValues.save()
                UserData.path = dialog.selectedFiles()[0]
                self.reload_Campaign()
        else:
            if exitOnFail:
                sys.exit()
        return

    def load_Setting_Filedialog(self):
        """opens a filedialog to choose the Setting for current Campaign.

        :return: ->None
        """
        dialog = QFileDialog()
        dialog.setWindowTitle("open Setting Database")
        dialog.setDirectory('./Library/Campaign')
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter("Databases (*.db)")
        if dialog.exec_():
            if ex.checkLibrary(dialog.selectedFiles()[0], True):
                dialog2 = QMessageBox()
                dialog2.setText('select Valid Database')
                dialog2.exec_()
                self.load_Setting_Filedialog()
                return

            UserData.Settingpath = dialog.selectedFiles()[0]

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

    def streamDecode(self, id):
        """decodes the database save texts to listed values

        :param id: int,
        :return: list, decoded items
        """
        values = ex.getFactory(id, 'Sessions', dictOut=True)['session_stream']
        if values != None and values != "":
            values = values.split("§€§")
            listedValues = [tuple(x.split("%€%")) for x in values]
            return listedValues
        else:
            return []

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
    # endregion

    def closeEvent(self, event)->None:
        """saves all applicationValues on MyWindow close by exiting.

        :return: None
        """
        self.closeAllTabs()
        Models.ApplicationValues.save()
        super().closeEvent(event)

    # TODO implement searchdialog and fastcreate
    # region searchdialog
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

        clearLayout(self.searchDialog_Result_lay)

        for instance in ex.searchFactory(self.searchDialog_lineEdit.text(), searchIn, shortOut=True):
            button = QPushButton(str(instance))
            button.clicked.connect(lambda: self.btn_searchDialog_choose(instance))
            self.searchDialog_Result_lay.addWidget(button)

    # endregion

def clearLayout(layout):
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
            clearLayout(layoutToRemove)
