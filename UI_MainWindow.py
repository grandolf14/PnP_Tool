import os
import sys
import shutil
import urllib.request

from datetime import datetime, timedelta

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QMainWindow, QLabel, QWidget, QPushButton, QHBoxLayout, QGridLayout, QLineEdit, QMessageBox, \
    QVBoxLayout, QAction, QStackedWidget, QFileDialog, QTabWidget, QTextEdit, QScrollArea, QDialog, QComboBox, \
    QDialogButtonBox, QFrame, QCheckBox


import DB_Access as ex
import Models as dh

from AppVar import UserData, AppData
from Models import CustomDate

from UI_Browser import Resultbox
from UI_DataEdit import EventEditWindow, NPCEditWindow, SessionEditWindow, FightPrep
from UI_DataViews import FightView, ViewNpc, ViewDraftboard, Browser
from UI_Utility import CustTextBrowser, DialogRandomNPC, DialogEditItem

class MyWindow(QMainWindow):
    """Manages the main window and all sublayouts

    """
    windowMode = "EditMode"  # EditMode or SessionMode
    searchMode = False  # currently searching fulltext or not
    sessionSearchFilter = {}  # Session filter specifications
    NPCSearchFilter = {}  # NPC filter specification
    eventSearchFilter = {}  # Event filter specification

    ses_dateChange = pyqtSignal()
    ses_timeChange = pyqtSignal()

    TabAdded=pyqtSignal()


    def __init__(self):
        """initializes the mainWindow

        """

        super().__init__()

        self.TabAdded.connect(self.addTab)

        self.timer = QTimer()

        # check if the base campaigns version matches the applications version
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
        addDraftbook.triggered.connect(lambda: AppData.setCurrInfo(None,"Draftbook",None))
        addDraftbook.triggered.connect(self.addTab)
        tabMenu.addAction(addDraftbook)

        addBrowser = QAction("Open new browser view",self)
        addBrowser.triggered.connect(lambda: AppData.setCurrInfo(None, "Browser", None))
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
        self.man_Draftboard=ViewDraftboard(win=self)
        self.man_cen_tabWid.addTab(self.man_Draftboard,"Draftboard")

        self.man_Browser=Browser()
        self.man_cen_tabWid.addTab(self.man_Browser, "Browser")
        # endregion

        # region Session
        self.ses_Main_wid = QWidget()
        self.ses_main_layHB = QHBoxLayout()
        self.ses_Main_wid.setLayout(self.ses_main_layHB)
        self.mainWin_stWid.addWidget(self.ses_Main_wid)

        self.ses_side_layVB = QVBoxLayout()
        self.ses_main_layHB.addLayout(self.ses_side_layVB, stretch=15)

        self.ses_cen_stWid = QStackedWidget()
        self.ses_main_layHB.addWidget(self.ses_cen_stWid, stretch=70)

        self.ses_side_stream = QVBoxLayout()
        self.ses_main_layHB.addLayout(self.ses_side_stream, stretch=15)

        ses_side_btn_leaveSes = QPushButton("leave Session")
        ses_side_btn_leaveSes.clicked.connect(self.btn_switch_windowMode)
        self.ses_side_layVB.addWidget(ses_side_btn_leaveSes)

        # region timeWidget_sidebar
        self.ses_side_Time_wid = QWidget()
        self.ses_side_Time_layVB = QVBoxLayout()
        self.ses_side_Time_wid.setLayout(self.ses_side_Time_layVB)
        self.ses_side_layVB.addWidget(self.ses_side_Time_wid)

        ses_side_Time_layHB = QHBoxLayout()
        self.ses_side_Time_layVB.addLayout(ses_side_Time_layHB)

        ses_side_Time_layHB.addWidget(QLabel("Ort:"), alignment=Qt.Alignment(4))

        self.ses_side_Time_Location_lEdit = QLineEdit()
        self.ses_side_Time_Location_lEdit.setText("%s" % (UserData.location[0]))
        self.ses_side_Time_Location_lEdit.textEdited.connect(self.linEditChanged_ses_location)
        ses_side_Time_layHB.addWidget(self.ses_side_Time_Location_lEdit, alignment=Qt.Alignment(4))

        ses_side_Time_layHB0 = QHBoxLayout()
        self.ses_side_Time_layVB.addLayout(ses_side_Time_layHB0)

        self.ses_side_Time_Date_label = QLabel("Tag: %s" % (UserData.today))
        self.ses_dateChange.connect(lambda: self.ses_side_Time_Date_label.setText("Tag: %s" % (UserData.today)))
        ses_side_Time_layHB0.addWidget(self.ses_side_Time_Date_label, alignment=Qt.Alignment(4))

        ses_side_Time_layHB1 = QHBoxLayout()
        self.ses_side_Time_layVB.addLayout(ses_side_Time_layHB1)

        plus7DateButton = QPushButton("++")
        plus7DateButton.clicked.connect(lambda: self.btn_ses_date(7))
        ses_side_Time_layHB1.addWidget(plus7DateButton)

        plusDateBtn = QPushButton("+")
        plusDateBtn.clicked.connect(lambda: self.btn_ses_date(1))
        ses_side_Time_layHB1.addWidget(plusDateBtn)

        minusDateButton = QPushButton("-")
        minusDateButton.clicked.connect(lambda: self.btn_ses_date(-1))
        ses_side_Time_layHB1.addWidget(minusDateButton)

        ses_side_Time_layHB2 = QHBoxLayout()
        self.ses_side_Time_layVB.addLayout(ses_side_Time_layHB2)

        self.weather_Time = QLabel("Uhrzeit %s" % (UserData.now.strftime("%H Uhr")))
        self.ses_timeChange.connect(
            lambda: self.weather_Time.setText("Uhrzeit %s" % (UserData.now.strftime("%H Uhr"))))
        ses_side_Time_layHB2.addWidget(self.weather_Time, alignment=Qt.Alignment(4))

        ses_side_Time_layHB3 = QHBoxLayout()
        self.ses_side_Time_layVB.addLayout(ses_side_Time_layHB3)

        plus6TimeBtn = QPushButton("++")
        plus6TimeBtn.clicked.connect(lambda: self.btn_ses_time(6))
        ses_side_Time_layHB3.addWidget(plus6TimeBtn)

        plusTimeBtn = QPushButton("+")
        plusTimeBtn.clicked.connect(lambda: self.btn_ses_time(1))
        ses_side_Time_layHB3.addWidget(plusTimeBtn)

        minusTimeBtn = QPushButton("-")
        minusTimeBtn.clicked.connect(lambda: self.btn_ses_time(-1))
        ses_side_Time_layHB3.addWidget(minusTimeBtn)

        self.ses_side_Time_weatherCurrent = QLabel("%s" % (UserData.weather))
        self.ses_side_Time_layVB.addWidget(self.ses_side_Time_weatherCurrent, alignment=Qt.Alignment(5))

        self.ses_side_Time_weatherNext = QLabel("Morgiges Wetter:\n%s" % (UserData.weatherNext))
        self.ses_side_Time_layVB.addWidget(self.ses_side_Time_weatherNext, alignment=Qt.Alignment(5))

        ses_side_Time_weatherNext_btn = QPushButton("Wetterwandel")
        ses_side_Time_weatherNext_btn.clicked.connect(self.btn_ses_weatherNext)
        self.ses_side_Time_layVB.addWidget((ses_side_Time_weatherNext_btn))

        # endregion_sidebar

        # region NPC_sidebar
        self.ses_side_NPC_tabWid = QTabWidget()
        self.ses_side_layVB.addWidget(self.ses_side_NPC_tabWid)

        self.ses_side_sesNPC_wid = QWidget()
        self.ses_side_searchNPC_wid = QWidget()

        self.ses_side_NPC_tabWid.addTab(self.ses_side_sesNPC_wid, "Session NPCs")
        self.ses_side_NPC_tabWid.addTab(self.ses_side_searchNPC_wid, "search")

        self.ses_side_sesNPC_layVB = QVBoxLayout()
        self.ses_side_sesNPC_wid.setLayout(self.ses_side_sesNPC_layVB)

        button = QPushButton('random Char')
        button.clicked.connect(self.btn_ses_randomChar)
        self.ses_side_layVB.addWidget(button)

        button = QPushButton('neuer Kampf')
        button.clicked.connect(self.btn_ses_newFight)
        self.ses_side_layVB.addWidget(button)

        button = QPushButton('open Plot')
        button.clicked.connect(self.btn_ses_openPlot)
        self.ses_side_layVB.addWidget(button)

        # region session NPC Tab

        self.ses_sesNPC = Resultbox()
        self.ses_sesNPC.setPref(standardbutton=self.load_ses_NpcInfo, standardButtonVerticalAlignment=False, col=1)
        self.ses_sesNPC.resultUpdate([])
        self.ses_side_sesNPC_layVB.addWidget(self.ses_sesNPC)
        # endregion

        # region search NPC Tab

        self.ses_side_searchNPC_layVB = QVBoxLayout()
        self.ses_side_searchNPC_wid.setLayout(self.ses_side_searchNPC_layVB)

        searchNPC_Layout_HBox = QHBoxLayout()
        self.ses_side_searchNPC_layVB.addLayout(searchNPC_Layout_HBox)

        self.ses_side_searchNPC_wid_LineEdit = QLineEdit()
        self.ses_side_searchNPC_wid_LineEdit.textEdited.connect(self.linEditChanged_ses_searchNPC)
        searchNPC_Layout_HBox.addWidget(self.ses_side_searchNPC_wid_LineEdit, alignment=Qt.Alignment(0))

        Button = QPushButton("search Fulltext is off")
        if self.searchMode:
            Button.setText("search Fulltext is on")
        Button.clicked.connect(self.btn_switch_searchMode)
        searchNPC_Layout_HBox.addWidget(Button)

        self.searchNPCRes = Resultbox()
        self.searchNPCRes.setPref(standardbutton=self.load_ses_NpcInfo, standardButtonVerticalAlignment=False, col=1)
        self.searchNPCRes.resultUpdate(ex.searchFactory("", 'Individuals', shortOut=True, searchFulltext=True))
        self.ses_side_searchNPC_layVB.addWidget(self.searchNPCRes)

        self.linEditChanged_ses_searchNPC()
        # endregion

        self.ses_cen_stWid_currentInstance = None
        self.ses_cen_stWid_lastInstance = None
        self.ses_cen_stWid_LastWid = None
        # endregion

        # region StreamSidebar
        self.temp_streamSave = []

        self.ses_scenes = Resultbox()
        self.ses_scenes.setPref(standardbutton=self.btn_ses_openScene, col=1)
        self.ses_timeChange.connect(self.load_ses_ScenePicker)
        self.ses_side_stream.addWidget(self.ses_scenes, stretch=50)

        self.ses_streamResult = Resultbox()
        self.ses_streamResult.setPref(reloadBottom=True, paintLight=[0], paintItemFrame=True, ignoreIndex=[None], col=1)
        self.ses_streamResult.setSource([x[1] for x in self.temp_streamSave if len(self.temp_streamsave) > 0])
        self.ses_streamResult.resultUpdate()

        self.ses_stream_textEdit = QTextEdit()

        button = QPushButton("submit text")
        button.clicked.connect(self.btn_ses_submitStream)

        self.ses_side_stream.addWidget(self.ses_streamResult, stretch=50)
        self.ses_side_stream.addWidget(self.ses_stream_textEdit, stretch=10)
        self.ses_side_stream.addWidget(button)
        # endregion

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
                date = datetime.now().strftime("%Y-%m-%d_%H-%M")
                path = f'./Libraries/Campaign/NewCampaign_{date}.db'
                msg = QMessageBox()
                msg.setText(f"new Campaign was saved under: \n {path}")
                msg.exec_()

                shutil.copy(UserData.path, path)
                UserData.path = path
                self.reload_Campaign()


    #ToDo Doc
    def checkTabClose(self,index):
        requestedTab = self.man_cen_tabWid.widget(index)

        widClass = type(requestedTab)
        if widClass == EventEditWindow or widClass == SessionEditWindow or widClass == NPCEditWindow:
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
            dialLay.addWidget(cancel)

            dial.exec_()
        else:
            self.closeTab(index)

    #ToDo Doc
    def closeTab(self, index):

        if index =="Current":
            requestedTab=self.man_cen_tabWid.currentWidget()
            index=self.man_cen_tabWid.currentIndex()
        else:
            requestedTab = self.man_cen_tabWid.widget(index)

        if hasattr(requestedTab,"caller") and self.man_cen_tabWid.indexOf(requestedTab.caller)!=-1:
            if type(requestedTab.caller)==ViewDraftboard:
                requestedTab.caller.man_Draftboard.updateScene()

            self.man_cen_tabWid.setCurrentWidget(requestedTab.caller)
        else:
            self.man_cen_tabWid.setCurrentIndex(0)

        self.man_cen_tabWid.removeTab(index)

    #ToDo Doc
    def addTab(self):
        ID=AppData.current_ID
        Flag=AppData.current_Flag
        notes= AppData.current_Data

        new=False
        if ID==None:
            new=True

        caller=self.man_cen_tabWid.currentWidget()

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

    #ToDO update
    def btn_switch_searchMode(self):
        """switches the fulltext search mode and calls for new search and resultbox updates

        :return: ->None
        """
        if self.searchMode:
            self.sender().setText("search Fulltext is off")
            self.searchMode = False
        else:
            self.sender().setText("search Fulltext is on")
            self.searchMode = True

        self.linEditChanged_ses_searchNPC()

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
                self.btn_ses_openPlot()
            else:
                messagbox = QMessageBox()
                messagbox.setText("pls make active Session first")
                messagbox.exec_()
                return

            self.temp_streamSave = self.streamDecode(id)
            self.ses_streamResult.resultUpdate(self.temp_streamSave)
            self.load_ses_ScenePicker()
            self.mainWin_stWid.setCurrentWidget(self.ses_Main_wid)

            session_NPC = ex.searchFactory("1", 'Session_Individual_jnt', attributes=['current_Session'],
                                           output="Individuals.individual_ID,indiv_fName,family_Name", shortOut=True)

            self.ses_sesNPC.resultUpdate(session_NPC)

    # endregion

    # region Session Buttons
    def btn_ses_time(self, Value):
        """adds or substracts hours from the current time and updates the today display

        :param Value: int, time in hours
        :return: ->None
        """
        oldDate = UserData.now.date()
        if Value > 0:
            UserData.now = UserData.now + timedelta(hours=Value)
            if oldDate != UserData.now.date():
                self.btn_ses_date(1)
                return
        else:
            UserData.now = UserData.now - timedelta(hours=1)
            if oldDate != UserData.now.date():
                self.btn_ses_date(-1)
                return

        self.ses_timeChange.emit()
        return

    def btn_ses_date(self, Value):
        """adds or subtracts days to current time and updates the today display

        :param Value: int, time in days
        :return: ->None
        """
        if Value > 0:
            days = "d" + str(Value)
            UserData.today = UserData.today + days
        else:
            UserData.today = UserData.today - "d1"
        self.ses_timeChange.emit()
        self.ses_dateChange.emit()

    def btn_ses_weatherNext(self):
        """calculates the weather for today and tomorrow based on database tables

        :return: ->None
        """
        weather = UserData.weather
        UserData.weather = UserData.weatherNext

        UserData.weatherNext = UserData.weatherNext.next()
        self.ses_side_Time_weatherCurrent.setText("%s" % (UserData.weather))
        self.ses_side_Time_weatherNext.setText("Morgiges Wetter:\n%s" % (UserData.weatherNext))

        date = str(UserData.today)
        hour = UserData.now.strftime("%H Uhr")
        location = UserData.location[0]
        self.temp_streamSave.append(
            (date + " " + hour + " " + location + " " + str(weather), str(UserData.weather)))
        self.ses_streamResult.resultUpdate(self.temp_streamSave)

        streamSave = self.temp_streamSave.copy()

        text = self.streamEncode()

        id = ex.searchFactory("1", 'Sessions', attributes=["current_Session"], searchFulltext=True)[0][0]
        ex.updateFactory(id, [text], 'Sessions', ['session_stream'])

    def btn_ses_startFight(self, fighter=None):
        """starts a prepared fight as FightView in self.ses_cen_stWid

        :param fighter: list of dicts|None, optional, dicts matching the FightView.createFighter requirements
        """
        fightWin = QWidget()
        fightWin_Lay = QVBoxLayout()
        fightWin.setLayout(fightWin_Lay)

        fightCenWid = FightView(fighter)
        fightWin_Lay.addWidget(fightCenWid)

        self.ses_cen_stWid.addWidget(fightWin)
        self.ses_cen_stWid.setCurrentWidget(fightWin)

        if self.ses_cen_stWid.count() > 1:
            self.ses_cen_stWid.layout().takeAt(0)

    def btn_ses_newFight(self):
        """ initializes a FightPrep Widget in self.ses_cen_stWid"""
        fightWin = QWidget()
        fightWin_Lay = QVBoxLayout()
        fightWin.setLayout(fightWin_Lay)

        prepFight = FightPrep()
        fightWin_Lay.addWidget(prepFight)

        button = QPushButton("Kampf beginnen")
        button.clicked.connect(lambda: self.btn_ses_startFight(prepFight.fighter))
        fightWin_Lay.addWidget(button)

        self.ses_cen_stWid.addWidget(fightWin)
        self.ses_cen_stWid.setCurrentWidget(fightWin)

        if self.ses_cen_stWid.count() > 1:
            self.ses_cen_stWid.layout().takeAt(0)

    def btn_ses_openPlot(self, id=False):
        """opens the plot of the active session in central session Widget and displays linked events and NPC's

        :return: ->None
        """
        if id is False:
            current_Session = ex.searchFactory("1", library='Sessions', attributes=['current_Session'])[0]
        else:
            current_Session = ex.searchFactory(id, library='Sessions', attributes=['session_ID'])[0]

        plotWin = QWidget()
        plotWin_Lay = QVBoxLayout()
        plotWin.setLayout(plotWin_Lay)

        title = QLabel(current_Session[1])
        plotWin_Lay.addWidget(title)

        text = CustTextBrowser()
        text.setText(current_Session[2])
        text.setReadOnly(True)
        plotWin_Lay.addWidget(text)

        scenes = ex.searchFactory(str(current_Session[0]), "Events", attributes=["fKey_session_ID"],
                                  OrderBy="Events.event_Date",
                                  output="Events.event_ID,Events.event_Title, Events.event_Date,Events.event_Location,Events.event_short_desc")

        scene_Resultbox = Resultbox()
        scene_Resultbox.setPref(standardbutton=self.btn_ses_openScene, col=4)
        scene_Resultbox.resultUpdate(scenes)
        plotWin_Lay.addWidget(scene_Resultbox)

        session_NPC = ex.searchFactory("1", 'Session_Individual_jnt', attributes=['current_Session'],
                                       output="Individuals.individual_ID,indiv_fName,family_Name", shortOut=True)

        self.ses_sesNPC.resultUpdate(session_NPC)

        self.ses_cen_stWid.addWidget(plotWin)
        self.ses_cen_stWid.setCurrentWidget(plotWin)

        if self.ses_cen_stWid.count() > 1:
            self.ses_cen_stWid.layout().takeAt(0)

    def btn_ses_scene_enter(self) -> None:
        """Updates the sessions time and date if it differs from the scenes time and date and emits the corresponding signal

        """
        id = self.sender().page
        raw_date = ex.getFactory(id, "Events", output="event_Date")[0]
        raw_date = raw_date.split(" ")
        raw_date[-1] = raw_date[-1].split(":")[0]
        date = raw_date[2] + "." + raw_date[1] + "." + raw_date[0]
        time = raw_date[3]

        if UserData.today != CustomDate(date):
            UserData.today = CustomDate(date)
            UserData.now = UserData.now.replace(hour=int(time))
            self.ses_dateChange.emit()
            self.ses_timeChange.emit()

        elif UserData.now.strftime("%H") != time:
            UserData.now = UserData.now.replace(hour=int(time))
            self.ses_timeChange.emit()
        return

    def btn_ses_openScene(self, id=False):
        """opens a scene in central session Widget and displays linked NPC's

        :return: ->None
        """

        if id is False:
            id = self.sender().page

        scene = ex.getFactory(id, "Events",
                              output="event_Title,event_Date,event_Location,event_short_desc,event_long_desc",
                              dictOut=True)

        layout = QGridLayout()
        scene_scroll = QScrollArea()
        scene_scroll.setLayout(layout)

        title = QLabel(scene["event_Title"])
        layout.addWidget(title, 0, 0)

        if scene["event_Date"]:
            date = QLabel(scene["event_Date"])
            button = QPushButton("Enter Scene")
            button.page = id
            button.setCheckable(True)
            if id == self.ses_lastScene[0]:
                button.setChecked(True)
                button.setText("Scene Active")
            button.clicked.connect(self.btn_ses_scene_enter)

            self.ses_timeChange.connect(
                lambda: button.setChecked(True) if self.ses_lastScene[0] == button.page else button.setChecked(False))
            self.ses_timeChange.connect(
                lambda: button.setText("Scene Active") if self.ses_lastScene[0] == button.page else button.setText(
                    "Enter Scene"))

            layout.addWidget(button, 0, 3)
        else:
            date = QLabel("no date assigned")
        layout.addWidget(date, 0, 2)

        if scene["event_Location"]:
            location = QLabel(scene["event_Location"])
        else:
            location = QLabel(scene["no Location assigned"])
        layout.addWidget(location, 0, 1)

        shortDesc = CustTextBrowser()
        shortDesc.setText(scene["event_short_desc"])
        layout.addWidget(shortDesc, 1, 0, 1, 4)

        longDesc = CustTextBrowser()
        longDesc.setText(scene["event_long_desc"])
        layout.addWidget(longDesc, 2, 0, 1, 4)

        scene_NPC = ex.searchFactory(str(id), 'Event_Individuals_jnt',
                                     attributes=['Event_Individuals_jnt.fKey_event_ID'], shortOut=True)
        self.ses_sesNPC.resultUpdate(scene_NPC)

        fighterList = []
        if id:
            fighterList = ex.searchFactory(str(id), "Event_Fighter_jnt",
                                           innerJoin="LEFT JOIN Fighter ON Event_Fighter_jnt.fKey_Fighter_ID=Fighter.Fighter_ID",
                                           attributes=["fKey_Event_ID"], dictOut=True)
        if fighterList != []:

            for contestant in fighterList:
                contestant["name"] = contestant["Fighter_Name"]
                contestant["life"] = contestant["Fighter_HP"]
                contestant["ini"] = contestant["Fighter_Initiative"]
                contestant["mana"] = contestant["Fighter_Mana"]
                contestant["karma"] = contestant["Fighter_Karma"]
                contestant["weapon"] = contestant["Fighter_Weapon"]

            button = QPushButton("Kampf beginnen")
            button.clicked.connect(lambda: self.btn_ses_startFight(fighterList))
            layout.addWidget(button)

        self.ses_cen_stWid.addWidget(scene_scroll)
        self.ses_cen_stWid.setCurrentWidget(scene_scroll)

        if self.ses_cen_stWid.count() > 1:
            self.ses_cen_stWid.layout().takeAt(0)

    def btn_ses_randomChar(self):
        """opens a dialog to create a new (random) NPC, on success links the new NPC to the session

        :return:
        """
        dialog = DialogRandomNPC(exitfunc=lambda: None)
        if dialog.exec_():
            self.linEditChanged_ses_searchNPC()
            sessionNPC = ex.searchFactory('1', 'Session_Individual_jnt', attributes=["current_Session"], shortOut=True,
                                          output='Individuals.individual_ID,indiv_fName,family_Name')

            self.ses_sesNPC.resultUpdate(sessionNPC)

    def btn_ses_submitStream(self):
        """adds a new note to the session and display's it

        :return: ->None
        """
        text = self.ses_stream_textEdit.toPlainText().strip("\n")
        date = str(UserData.today)
        hour = UserData.now.strftime("%H Uhr")
        weather = str(UserData.weather)
        location = UserData.location[0]
        if text != "":
            self.temp_streamSave.append((date + " " + hour + " " + location + " " + weather, text))
            self.ses_stream_textEdit.clear()
            self.ses_streamResult.resultUpdate(self.temp_streamSave)

            text = self.streamEncode()
            id = ex.searchFactory("1", 'Sessions', attributes=["current_Session"])[0][0]
            ex.updateFactory(id, [text], 'Sessions', ['session_stream'])
        return

    # endregion

    # region lineedit signals
    def linEditChanged_ses_location(self):
        """saves the current location

        :return: ->None
        """
        UserData.location = [self.ses_side_Time_Location_lEdit.text()]

    def linEditChanged_ses_searchNPC(self):
        """updates the search result after changing search text

        :return: ->None
        """
        charakters = ex.searchFactory(self.ses_side_searchNPC_wid_LineEdit.text(), "Individuals", shortOut=True,
                                      searchFulltext=self.searchMode)
        self.searchNPCRes.resultUpdate(charakters)
        return
    # endregion

    # region other
    def openEditWindow(self, obj, dialog, collection):
        """opens an Edit window for the linked event, session or NPC at current tab

        :param obj: Datalabel, the linked label
        :param dialog: QDialog, the sender of the event
        :param collection: list, selected attributes of the item
        :return: ->None
        """
        dialog.close()
        text = ""
        for item in collection:
            if item.checkState():
                text += item.text()
                text += ":"
        text = text.rstrip(":")
        ex.updateFactory(obj.labelData["note_ID"], [text], "Notes", ["note_Content"])

        listeLybraries = {"Sessions": SessionEditWindow, "Events": EventEditWindow, "Individuals": NPCEditWindow}
        widget = listeLybraries[obj.linked[0]]
        widget = widget(id=obj.linked[1])
        widget.caller =self.man_cen_tabWid.currentWidget()

        self.man_cen_tabWid.addTab(widget, obj.linked[0])
        self.man_cen_tabWid.setCurrentWidget(widget)
        index = self.man_cen_tabWid.indexOf(widget)
        widget.setExit(lambda: self.closeTab(index))


    def init_Draftboard_GraphicScene(self):
        """Replaces self.man_Draftboard_menu_selDB with new widget and initializes new Draftboard selection

        :return: ->None
        """
        self.man_Draftboard_menu_selDB = QComboBox()

        draftboards = ex.searchFactory("", "Draftbooks", output="draftbook_Title,draftbook_ID")
        for board in draftboards:
            self.man_Draftboard_menu_selDB.addItem(*board)

        self.man_Draftboard_menu_selDB.currentIndexChanged.connect(self.man_Draftboard.updateScene)
        self.man_Draftboard_sidebar.addWidget(self.man_Draftboard_menu_selDB, 0, 1, 1, 2)
        self.man_Draftboard.updateScene(window=self)
        return

    def reload_Campaign(self):
        """reloads all contents of selected campaign and setting

        :return: ->None"""
        UserData.Settingpath = ex.getFactory(1, "DB_Properties", path=UserData.path, dictOut=True)[
            "setting_Path"]
        self.setWindowTitle(UserData.path.split("/")[-1].rstrip(".db"))
        self.init_Draftboard_GraphicScene()
        self.linEditChanged_man_searchNPC()
        self.linEditChanged_man_searchSession()
        self.linEditChanged_man_searchEvent()
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

            # checks for invalid databaseVersion
            if not ex.checkLibrary(selectedFile):
                dialog2 = QMessageBox()
                dialog2.setText(
                    'The selected database version does not match the application version. Should the database'
                    'version be updated?')
                dialog2.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
                if dialog2.exec_() == 16384:
                    ex.updateLibraryVersion(selectedFile)
                else:
                    if exitOnFail:
                        sys.exit()
                    return

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

    # ToDo Doc
    def load_ses_ScenePicker(self):
        id = ex.searchFactory("1", 'Sessions', output="session_ID", attributes=["current_Session"])[0][0]
        scenes = ex.searchFactory(str(id), "Events", output="Events.event_ID,Events.event_Date, Events.event_Title ",
                                  attributes=["fKey_Session_ID"], OrderBy="Events.event_Date")
        passive_scenes = []
        active_scenes = []
        lastDate = None
        for scene in scenes:
            date = scene[1].split(" ")
            time = date[-1].split(":")[0]
            date = date[2] + "." + date[1] + "." + date[0]
            scene = [x for x in scene]
            scene[1] = date
            if date != lastDate:
                scene.insert(2, date)
                lastDate = date

            if CustomDate(date) > UserData.today:
                active_scenes.append(scene)
            elif CustomDate(date) == UserData.today and int(time) > int(UserData.now.strftime("%H")):
                active_scenes.append(scene)
            else:
                passive_scenes.append(scene)

        lightIndex = []
        final_scenes = active_scenes
        if len(passive_scenes) != 0:
            self.ses_lastScene = passive_scenes.pop(-1)
            if len(self.ses_lastScene) == 3:
                self.ses_lastScene.insert(2, self.ses_lastScene[1])
            lightIndex = [*range(len(active_scenes) + 1, (len(active_scenes) + 1) + (len(passive_scenes)))]
            final_scenes = [self.ses_lastScene] + active_scenes + passive_scenes
        self.ses_scenes.setPref(standardbutton=self.btn_ses_openScene, col=1, ignoreIndex=[0, 1],
                                paintItemLight=lightIndex)
        self.ses_scenes.resultUpdate(final_scenes)
        return

    def load_ses_NpcInfo(self, custId=False):
        """opens a viewNPC Widget in central session widget

        :param custId: int, id for not button caused function call
        :return:
        """

        if custId == False:
            id = self.sender().page
        else:
            id = custId

        NPCWin = ViewNpc(id, self.load_ses_NpcInfo)
        self.ses_cen_stWid.addWidget(NPCWin)
        self.ses_cen_stWid.setCurrentWidget(NPCWin)
        if self.ses_cen_stWid.count() > 1:
            self.ses_cen_stWid.layout().takeAt(0)

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

    def streamEncode(self):
        """encodes the session stream for database insertion

        :return: str, encoded text
        """
        streamSave = self.temp_streamSave.copy()
        text = ""
        for set in streamSave:
            text += set[0] + "%€%" + set[1] + "§€§"
        text = text.rstrip("§€§")
        return text

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
