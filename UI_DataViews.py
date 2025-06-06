from PyQt5.QtCore import Qt, pyqtSignal,QTimer
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QStackedWidget, QScrollArea, QFrame, QLabel, QHBoxLayout, \
                            QGridLayout, QComboBox, QDialogButtonBox, QDialog, QCheckBox,QLineEdit,QTextEdit, QMessageBox, \
                            QTabWidget

import DB_Access as ex

from datetime import timedelta

from AppVar import AppData, UserData
from UI_DataEdit import DraftBoard, FightPrep
from UI_Utility import FightChar, CustTextBrowser, DialogEditItem, DialogRandomNPC, Resultbox
from Models import CustomDate


class SessionView(QWidget):
    dateChanged = pyqtSignal()
    timeChanged = pyqtSignal()

    def __init__(self, id):

        self.id=id

        self.today = UserData.today
        self.now = UserData.now
        self.weather = UserData.weather
        self.weatherNext = UserData.weatherNext
        self.location = UserData.location

        super().__init__()

        mainLey = QHBoxLayout()
        self.setLayout(mainLey)

        leftLay = QVBoxLayout()
        mainLey.addLayout(leftLay, stretch=15)

        self.cenStacked = QStackedWidget()
        mainLey.addWidget(self.cenStacked, stretch=70)

        rightLay = QVBoxLayout()
        mainLey.addLayout(rightLay, stretch=15)

        leaveSes_btn = QPushButton("leave Session")
        leaveSes_btn.clicked.connect(AppData.mainWin.leaveSession)
        leftLay.addWidget(leaveSes_btn)

        # region timeWidget_sidebar
        timeWid = QWidget()  # ToDo remove widget?
        timeLay = QVBoxLayout()  # ToDO gridLayout?
        timeWid.setLayout(timeLay)
        leftLay.addWidget(timeWid)

        timeLay_h = QHBoxLayout()
        timeLay.addLayout(timeLay_h)

        timeLay_h.addWidget(QLabel("Ort:"), alignment=Qt.Alignment(4))

        self.location_LineEd = QLineEdit()
        self.location_LineEd.setText("%s" % (self.location))
        self.location_LineEd.textEdited.connect(self.update_location)
        timeLay_h.addWidget(self.location_LineEd, alignment=Qt.Alignment(4))

        timeLay_h0 = QHBoxLayout()
        timeLay.addLayout(timeLay_h0)

        date_Lbl = QLabel("Tag: %s" % (self.today))
        self.dateChanged.connect(lambda: date_Lbl.setText("Tag: %s" % (self.today)))
        timeLay_h0.addWidget(date_Lbl, alignment=Qt.Alignment(4))

        timeLay_h1 = QHBoxLayout()
        timeLay.addLayout(timeLay_h1)

        nextWeek_btn = QPushButton("++")
        nextWeek_btn.clicked.connect(lambda: self.btn_dateChange(7))
        timeLay_h1.addWidget(nextWeek_btn)

        tomorrow_btn = QPushButton("+")
        tomorrow_btn.clicked.connect(lambda: self.btn_dateChange(1))
        timeLay_h1.addWidget(tomorrow_btn)

        yesterday_btn = QPushButton("-")
        yesterday_btn.clicked.connect(lambda: self.btn_dateChange(-1))
        timeLay_h1.addWidget(yesterday_btn)

        timeLay_h2 = QHBoxLayout()
        timeLay.addLayout(timeLay_h2)

        time_Lbl = QLabel("Uhrzeit %s" % (self.now.strftime("%H Uhr")))
        self.timeChanged.connect(
            lambda: time_Lbl.setText("Uhrzeit %s" % (self.now.strftime("%H Uhr"))))
        timeLay_h2.addWidget(time_Lbl, alignment=Qt.Alignment(4))

        timeLay_h3 = QHBoxLayout()
        timeLay.addLayout(timeLay_h3)

        quarterday_btn = QPushButton("++")
        quarterday_btn.clicked.connect(lambda: self.btn_timeChange(6))
        timeLay_h3.addWidget(quarterday_btn)

        hour_btn = QPushButton("+")
        hour_btn.clicked.connect(lambda: self.btn_timeChange(1))
        timeLay_h3.addWidget(hour_btn)

        lastHour_btn = QPushButton("-")
        lastHour_btn.clicked.connect(lambda: self.btn_timeChange(-1))
        timeLay_h3.addWidget(lastHour_btn)

        self.weatherNow_Lbl = QLabel("%s" % (self.weather))
        timeLay.addWidget(self.weatherNow_Lbl, alignment=Qt.Alignment(5))

        self.weatherNext_Lbl = QLabel("Morgiges Wetter:\n%s" % (self.weatherNext))
        timeLay.addWidget(self.weatherNext_Lbl, alignment=Qt.Alignment(5))

        weatherNext_btn = QPushButton("Wetterwandel")
        weatherNext_btn.clicked.connect(self.btn_nextWeather)
        timeLay.addWidget(weatherNext_btn)

        # endregion_sidebar

        # region NPC_sidebar
        npc_Tab = QTabWidget()
        leftLay.addWidget(npc_Tab)

        # region session NPC Tab

        sesNPC_Wid = QWidget()
        npc_Tab.addTab(sesNPC_Wid, "Session NPCs")

        sesNPC_Lay = QVBoxLayout()
        sesNPC_Wid.setLayout(sesNPC_Lay)

        self.sesNPC_Res = Resultbox()
        self.sesNPC_Res.setPref(standardbutton=self.load_NPCInfo, standardButtonVerticalAlignment=False, col=1)
        self.sesNPC_Res.resultUpdate([])
        sesNPC_Lay.addWidget(self.sesNPC_Res)
        # endregion

        # region search NPC Tab
        self.searchNPC_Wid = QWidget()
        npc_Tab.addTab(self.searchNPC_Wid, "search")

        searchNPC_Lay = QVBoxLayout()
        self.searchNPC_Wid.setLayout(searchNPC_Lay)

        searchNPCBar_Lay = QHBoxLayout()
        searchNPC_Lay.addLayout(searchNPCBar_Lay)

        self.searchNPC_LineEd = QLineEdit()
        self.searchNPC_LineEd.textEdited.connect(self.update_searchNPC_Res)
        searchNPCBar_Lay.addWidget(self.searchNPC_LineEd, alignment=Qt.Alignment(0))

        self.searchMode_Btn = QPushButton("search Fulltext")
        self.searchMode_Btn.setCheckable(True)
        self.searchMode_Btn.clicked.connect(self.update_searchNPC_Res)
        searchNPCBar_Lay.addWidget(self.searchMode_Btn)

        self.searchNPC_Res = Resultbox()
        self.searchNPC_Res.setPref(standardbutton=self.load_NPCInfo, standardButtonVerticalAlignment=False, col=1)
        self.searchNPC_Res.resultUpdate(ex.searchFactory("", 'Individuals', shortOut=True, searchFulltext=True))
        searchNPC_Lay.addWidget(self.searchNPC_Res)

        self.update_searchNPC_Res()  # ToDo necessary?
        # endregion

        button = QPushButton('random Char')
        button.clicked.connect(self.btn_randChar)
        leftLay.addWidget(button)

        button = QPushButton('neuer Kampf')
        button.clicked.connect(self.btn_newFight)
        leftLay.addWidget(button)

        button = QPushButton('open Plot')
        button.clicked.connect(self.btn_openPlot)
        leftLay.addWidget(button)
        # endregion

        # region StreamSidebar
        self.temp_streamSave = []

        self.scenes_Res = Resultbox()
        self.scenes_Res.setPref(standardbutton=self.btn_openScene, col=1)
        self.timeChanged.connect(self.load_SceneRes)
        rightLay.addWidget(self.scenes_Res, stretch=50)

        self.stream_Res = Resultbox()
        self.stream_Res.setPref(reloadBottom=True, paintLight=[0], paintItemFrame=True, ignoreIndex=[None], col=1)
        self.stream_Res.setSource([x[1] for x in self.temp_streamSave if len(self.temp_streamsave) > 0])
        self.stream_Res.resultUpdate()

        self.stream_TextEd = QTextEdit()

        button = QPushButton("submit text")
        button.clicked.connect(self.btn_submitStream)

        rightLay.addWidget(self.stream_Res, stretch=50)
        rightLay.addWidget(self.stream_TextEd, stretch=10)
        rightLay.addWidget(button)
        # endregion

        self.btn_openPlot()
        self.temp_streamSave = self.streamDecode(self.id)
        self.stream_Res.resultUpdate(self.temp_streamSave)
        self.load_SceneRes()



    def saveValues(self) -> None:
        """updates UserData to match SessionView - instance Data"""
        UserData.weather = self.weather
        UserData.location = self.location
        UserData.weatherNext = self.weatherNext
        UserData.today = self.today
        UserData.now = self.now

    def streamEncode(self) -> str:  # ToDo remove
        """encodes the session stream for database insertion

        :return: str, encoded text
        """
        streamSave = self.temp_streamSave.copy()
        text = ""
        for set in streamSave:
            text += set[0] + "%€%" + set[1] + "§€§"
        text = text.rstrip("§€§")
        return text

    # region Session Buttons

    def streamDecode(self, id) -> list:  # ToDo remove
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

    def load_SceneRes(self) -> None:
        """sorts and updates the scene selection resultbox with past scenes (based on current date and time) painted
        grey and appended at end"""
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

            if CustomDate(date) > self.today:
                active_scenes.append(scene)
            elif CustomDate(date) == self.today and int(time) > int(self.now.strftime("%H")):
                active_scenes.append(scene)
            else:
                passive_scenes.append(scene)

        lightIndex = []
        final_scenes = active_scenes
        self.ses_lastScene = scenes[0]
        if len(passive_scenes) != 0:
            self.ses_lastScene = passive_scenes.pop(-1)
            if len(self.ses_lastScene) == 3:
                self.ses_lastScene.insert(2, self.ses_lastScene[1])
            lightIndex = [*range(len(active_scenes) + 1, (len(active_scenes) + 1) + (len(passive_scenes)))]
            final_scenes = [self.ses_lastScene] + active_scenes + passive_scenes
        self.scenes_Res.setPref(standardbutton=self.btn_openScene, col=1, ignoreIndex=[0, 1],
                                paintItemLight=lightIndex)
        self.scenes_Res.resultUpdate(final_scenes)

    def load_NPCInfo(self, custId=False) -> None:
        """opens a viewNPC Widget in central session widget

        :param custId: int, id for not button caused function call
        :return:
        """

        if custId == False:
            id = self.sender().page
        else:
            id = custId

        NPCWin = ViewNpc(id, self.load_NPCInfo)
        self.cenStacked.addWidget(NPCWin)
        self.cenStacked.setCurrentWidget(NPCWin)
        if self.cenStacked.count() > 1:
            self.cenStacked.layout().takeAt(0)

    def update_location(self) -> None:
        """saves the current location

        :return: None
        """
        self.location = self.location_LineEd.text()

    def update_searchNPC_Res(self) -> None:
        """updates the search result after changing search text

        :return: None
        """
        charakters = ex.searchFactory(self.searchNPC_LineEd.text(), "Individuals", shortOut=True,
                                      searchFulltext=self.searchMode_Btn.isChecked())
        self.searchNPC_Res.resultUpdate(charakters)

    def btn_timeChange(self, Value) -> None:
        """adds or substracts hours from the current time and updates the today display

        :param Value: int, time in hours
        :return: ->None
        """
        oldDate = self.now.date()
        if Value > 0:
            self.now = self.now + timedelta(hours=Value)
            if oldDate != self.now.date():
                self.btn_dateChange(1)
                return
        else:
            self.now = self.now - timedelta(hours=1)
            if oldDate != self.now.date():
                self.btn_dateChange(-1)
                return

        self.timeChanged.emit()
        return

    def btn_dateChange(self, Value) -> None:
        """adds or subtracts days to current time and updates the today display

        :param Value: int, time in days
        :return: ->None
        """
        if Value > 0:
            days = "d" + str(Value)
            self.today = self.today + days
        else:
            self.today = self.today - "d1"
        self.timeChanged.emit()
        self.dateChanged.emit()

    def btn_nextWeather(self) -> None:
        """calculates the weather for today and tomorrow based on database tables

        :return: ->None
        """
        weather = self.weather
        self.weather = self.weatherNext

        self.weatherNext = self.weatherNext.next()
        self.weatherNow_Lbl.setText("%s" % (self.weather))
        self.weatherNext_Lbl.setText("Morgiges Wetter:\n%s" % (self.weatherNext))

        date = str(self.today)
        hour = self.now.strftime("%H Uhr")
        location = self.location[0]
        self.temp_streamSave.append(
            (date + " " + hour + " " + location + " " + str(weather), str(self.weather)))
        self.stream_Res.resultUpdate(self.temp_streamSave)

        text = self.streamEncode()

        id = ex.searchFactory("1", 'Sessions', attributes=["current_Session"], searchFulltext=True)[0][0]
        ex.updateFactory(id, [text], 'Sessions', ['session_stream'])

    def btn_startFight(self, fighter=None) -> None:
        """starts a prepared fight as FightView in self.cenStacked

        :param fighter: list of dicts|None, optional, dicts matching the FightView.createFighter requirements
        """
        fightWin = QWidget()
        fightWin_Lay = QVBoxLayout()
        fightWin.setLayout(fightWin_Lay)

        fightCenWid = FightView(fighter)
        fightWin_Lay.addWidget(fightCenWid)

        self.cenStacked.addWidget(fightWin)
        self.cenStacked.setCurrentWidget(fightWin)

        if self.cenStacked.count() > 1:
            self.cenStacked.layout().takeAt(0)

    def btn_newFight(self) -> None:
        """ initializes a FightPrep Widget in self.cenStacked"""
        fightWin = QWidget()
        fightWin_Lay = QVBoxLayout()
        fightWin.setLayout(fightWin_Lay)

        prepFight = FightPrep()
        fightWin_Lay.addWidget(prepFight)

        button = QPushButton("Kampf beginnen")
        button.clicked.connect(lambda: self.btn_startFight(prepFight.fighter))
        fightWin_Lay.addWidget(button)

        self.cenStacked.addWidget(fightWin)
        self.cenStacked.setCurrentWidget(fightWin)

        if self.cenStacked.count() > 1:
            self.cenStacked.layout().takeAt(0)

    def btn_openPlot(self, id=False) -> None:
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
        scene_Resultbox.setPref(standardbutton=self.btn_openScene, col=4)
        scene_Resultbox.resultUpdate(scenes)
        plotWin_Lay.addWidget(scene_Resultbox)

        session_NPC = ex.searchFactory("1", 'Session_Individual_jnt', attributes=['current_Session'],
                                       output="Individuals.individual_ID,indiv_fName,family_Name", shortOut=True)

        self.sesNPC_Res.resultUpdate(session_NPC)

        self.cenStacked.addWidget(plotWin)
        self.cenStacked.setCurrentWidget(plotWin)

        if self.cenStacked.count() > 1:
            self.cenStacked.layout().takeAt(0)

    def btn_enterScene(self) -> None:
        """Updates the sessions time and date if it differs from the scenes time and date and emits the corresponding signal

        """
        id = self.sender().page
        raw_date = ex.getFactory(id, "Events", output="event_Date")[0]
        raw_date = raw_date.split(" ")
        raw_date[-1] = raw_date[-1].split(":")[0]
        date = raw_date[2] + "." + raw_date[1] + "." + raw_date[0]
        time = raw_date[3]

        if self.today != CustomDate(date):
            self.today = CustomDate(date)
            self.now = self.now.replace(hour=int(time))
            self.dateChanged.emit()
            self.timeChanged.emit()

        elif self.now.strftime("%H") != time:
            self.now = self.now.replace(hour=int(time))
            self.timeChanged.emit()
        return

    def btn_openScene(self, id=False):
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
            enterScene_Btn = QPushButton("Enter Scene")
            enterScene_Btn.page = id
            enterScene_Btn.setCheckable(True)
            if id == self.ses_lastScene[0]:
                enterScene_Btn.setChecked(True)
                enterScene_Btn.setText("Scene Active")

            enterScene_Btn.clicked.connect(self.btn_enterScene)
            self.timeChanged.connect(
                lambda: enterScene_Btn.setChecked(True) if self.ses_lastScene[
                                                               0] == enterScene_Btn.page else enterScene_Btn.setChecked(
                    False))
            self.timeChanged.connect(
                lambda: enterScene_Btn.setText("Scene Active") if self.ses_lastScene[
                                                                      0] == enterScene_Btn.page else enterScene_Btn.setText(
                    "Enter Scene"))

            layout.addWidget(enterScene_Btn, 0, 3)
        else:
            date = QLabel("no date assigned")
        layout.addWidget(date, 0, 2)

        if scene["event_Location"]:
            location = QLabel(scene["event_Location"])
        else:
            location = QLabel("no Location assigned")
        layout.addWidget(location, 0, 1)

        shortDesc = CustTextBrowser()
        shortDesc.setText(scene["event_short_desc"])
        layout.addWidget(shortDesc, 1, 0, 1, 4)

        longDesc = CustTextBrowser()
        longDesc.setText(scene["event_long_desc"])
        layout.addWidget(longDesc, 2, 0, 1, 4)

        scene_NPC = ex.searchFactory(str(id), 'Event_Individuals_jnt',
                                     attributes=['Event_Individuals_jnt.fKey_event_ID'], shortOut=True)
        self.sesNPC_Res.resultUpdate(scene_NPC)

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
            button.clicked.connect(lambda: self.btn_startFight(fighterList))
            layout.addWidget(button, 3, 0, 1, 4)

        self.cenStacked.addWidget(scene_scroll)
        self.cenStacked.setCurrentWidget(scene_scroll)

        if self.cenStacked.count() > 1:
            self.cenStacked.layout().takeAt(0)

    def btn_randChar(self) -> None:
        """opens a dialog to create a new (random) NPC, on success links the new NPC to the session

        :return: None
        """
        dialog = DialogRandomNPC(exitfunc=lambda: None)
        if dialog.exec_():
            self.update_searchNPC_Res()
            sessionNPC = ex.searchFactory('1', 'Session_Individual_jnt', attributes=["current_Session"], shortOut=True,
                                          output='Individuals.individual_ID,indiv_fName,family_Name')

            self.sesNPC_Res.resultUpdate(sessionNPC)

    def btn_submitStream(self) -> None:
        """adds a new note to the session and display's it

        :return: None
        """
        text = self.stream_TextEd.toPlainText().strip("\n")
        date = str(self.today)
        hour = self.now.strftime("%H Uhr")
        weather = str(self.weather)
        location = self.location
        if text != "":
            self.temp_streamSave.append((date + " " + hour + " " + location + " " + weather, text))
            self.stream_TextEd.clear()
            self.stream_Res.resultUpdate(self.temp_streamSave)

            text = self.streamEncode()
            id = ex.searchFactory("1", 'Sessions', attributes=["current_Session"])[0][0]
            ex.updateFactory(id, [text], 'Sessions', ['session_stream'])

    # endregion


class Browser(QWidget):
    """Widget that allows to visually present search results and select or modify the underlying dataset"""

    def __init__(self):

        self.filter = {"Events": [], "Individuals": [], "Sessions": []}

        self.timer = QTimer()

        super().__init__()

        main_Lay = QVBoxLayout()
        self.setLayout(main_Lay)

        searchBar_Lay = QHBoxLayout()
        main_Lay.addLayout(searchBar_Lay)

        self.search_LineEd = QLineEdit()
        self.search_LineEd.textChanged.connect(lambda: self.timer_start(500, function=self.updateSearch))
        searchBar_Lay.addWidget(self.search_LineEd, 50)

        self.searchLib_Combo = QComboBox()
        self.searchLib_Combo.addItem("Event", "Events")
        self.searchLib_Combo.addItem("Individual", "Individuals")
        self.searchLib_Combo.addItem("Session", "Sessions")
        self.searchLib_Combo.currentIndexChanged.connect(self.load_filterBar)
        searchBar_Lay.addWidget(self.searchLib_Combo, stretch=10)

        self.searchFullText = QPushButton("Fulltextsearch")
        self.searchFullText.setCheckable(True)
        self.searchFullText.clicked.connect(self.updateSearch)
        searchBar_Lay.addWidget(self.searchFullText, stretch=10)

        button = QPushButton("set Filter")
        button.clicked.connect(self.btn_addFilter)
        searchBar_Lay.addWidget(button, 10)

        self.filter_Stacked = QStackedWidget()
        searchBar_Lay.addWidget(self.filter_Stacked, 30)

        button = QPushButton("new Session")
        button.clicked.connect(lambda: self.btn_viewSession(new=True))
        searchBar_Lay.addWidget(button, 10)

        self.search_Res = Resultbox()
        self.search_Res.setPref(
            buttonList=[['select', self.btn_viewSession], ['delete', self.btn_deleteSession]])
        main_Lay.addWidget(self.search_Res, 90)

        self.load_filterBar()  # initialisiert das searchBarLayout

    def updateSearch(self) -> None:
        """Updates the results of the widget based on lineEdit input data, filter and searchFullText selection

        """

        if self.timer.isActive():
            self.timer.stop()

        text = self.search_LineEd.text()
        library = self.searchLib_Combo.currentData()
        searchFullText = self.searchFullText.isChecked()
        filter = self.filter[library]

        searchresult = ex.searchFactory(text, library, shortOut=True,
                                        Filter=filter, searchFulltext=searchFullText)
        self.search_Res.resultUpdate(searchresult)

    def btn_viewSession(self, new=False) -> None:
        """opens a new SessionEditWindow either with new flag or with existing flag

        :return: ->None
        """
        id = None
        if not new:
            id = self.sender().page

        AppData.setCurrInfo(id, Flag=self.searchLib_Combo.currentData(), origin=self)
        AppData.mainWin.tabAdded.emit()

        widget = AppData.mainWin.man_Tab.currentWidget()
        widget.setExit(lambda: AppData.mainWin.closeTab(widget))
        return

    def btn_deleteSession(self):
        """asks for confirmation of deletion, deletes the Session and reloads the searchResult.

        :return: ->None
        """

        Id = self.sender().page
        library = self.searchLib_Combo.currentData()

        msgBox = QMessageBox()
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        title = ex.getFactory(Id, library)[1]
        msgBox.setText("Do you want to delete %s" % (title))
        value = msgBox.exec()
        if value == 1024:
            ex.deleteFactory(Id, library)

        self.updateSearch()

    def btn_addFilter(self):
        """opens dialogs to set filter specifics for searches and denies request if there are more than 3 active filters

        :param library: str, the library to search in
        :return:
        """
        filterDial = QDialog()
        filterDial.setWindowTitle("Add new Filter")

        filterDialogLayout = QVBoxLayout()
        filterDial.setLayout(filterDialogLayout)

        library = self.searchLib_Combo.currentData()
        filter = self.filter[library]

        if len(filter) > 3:
            filterDialogLayout.addWidget(QLabel("To many Filter aktiv: \n Please delete existing Filter"))

            buttons = QDialogButtonBox.Ok
            buttonBox = QDialogButtonBox(buttons)
            buttonBox.accepted.connect(filterDial.close)
            filterDialogLayout.addWidget(buttonBox)

        else:
            filterDialogHBox = QHBoxLayout()
            filterDialogLayout.addLayout(filterDialogHBox)

            searchWhere = QComboBox()
            filter = ex.get_table_Prop(library)['colName']
            searchWhere.addItems(filter)
            filterDialogHBox.addWidget(searchWhere)

            searchWhat = QLineEdit()
            filterDialogHBox.addWidget(searchWhat)

            fulltext = QPushButton("Search Fulltext")
            fulltext.setCheckable(True)
            filterDialogHBox.addWidget(fulltext)

            buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
            buttonBox = QDialogButtonBox(buttons)

            buttonBox.accepted.connect(filterDial.accept)

            buttonBox.rejected.connect(filterDial.reject)

            filterDialogLayout.addWidget(buttonBox)

        if filterDial.exec_():
            self.filter[library].append({"key": searchWhere.currentText(),
                                         "text": searchWhat.text(),
                                         "fullTextSearch": fulltext.isChecked()})

            self.load_filterBar()

        filterDial.close()
        return

    def timer_start(self, delay=500, function=None) -> None:
        """calls a function after a specific delay

        :param delay: int, optional, milliseconds of delay
        :param function: function, optional, function to call after delay
        :return:
        """
        if not function:
            function = self.linEditChanged_man_searchNPC

        self.timer.timeout.connect(function)
        self.timer.start(delay)

    def load_filterBar(self) -> None:
        """repaints the session searchbar and adds/removes filter

        :return: ->None
        """

        newWid = QWidget()
        layout = QHBoxLayout()
        newWid.setLayout(layout)
        library = self.searchLib_Combo.currentData()
        filterList = self.filter[library]

        if len(self.filter[library]) > 0:
            for filterDict in filterList:
                button = QPushButton("delete Filter " + filterDict["key"] + ": " + filterDict["text"])
                button.page = self.filter[library].index(filterDict)
                button.clicked.connect(self.btn_delFilter)
                layout.addWidget(button, stretch=10)

        if len(self.filter[library]) < 5:
            for number in range(5 - len(filterList)):
                layout.addWidget(QLabel(""), stretch=10)

        self.filter_Stacked.addWidget(newWid)
        self.filter_Stacked.setCurrentWidget(newWid)

        self.updateSearch()
        return

    def btn_delFilter(self) -> None:
        """removes the selected filter from filterlist and reloads corresponding searchbar

        :return: ->None
        """
        index = self.sender().page
        library = self.searchLib_Combo.currentData()

        self.filter[library].pop(index)
        self.load_filterBar()
        return


class ViewDraftboard(QStackedWidget):
    """widget to select use and view draftboards"""
    def __init__(self):

        super().__init__()

        main_Wid = QWidget()
        self.addWidget(main_Wid)

        main_Lay = QHBoxLayout()
        main_Wid.setLayout(main_Lay)

        self.Draftboard = DraftBoard(self)
        self.Draftboard.setRenderHint(QPainter.Antialiasing)
        main_Lay.addWidget(self.Draftboard)

        self.tools_Lay = QGridLayout()
        main_Lay.addLayout(self.tools_Lay)

        self.selDraftboard_Combo = QComboBox()

        draftboards = ex.searchFactory("", "Draftbooks", output="draftbook_Title,draftbook_ID")
        for board in draftboards:
            self.selDraftboard_Combo.addItem(*board)

        self.selDraftboard_Combo.currentIndexChanged.connect(self.Draftboard.updateScene)
        self.tools_Lay.addWidget(self.selDraftboard_Combo, 0, 1, 1, 2)

        newDraftboard_Btn = QPushButton("neues Draftbook")
        newDraftboard_Btn.clicked.connect(self.btn_man_DB_newDB)
        self.tools_Lay.addWidget(newDraftboard_Btn, 1, 1, 1, 2)

        deleteDraftboard_Btn = QPushButton("Draftbook löschen")
        deleteDraftboard_Btn.clicked.connect(self.btn_man_DB_deleteDB)
        self.tools_Lay.addWidget(deleteDraftboard_Btn, 2, 1, 1, 2)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        self.tools_Lay.addWidget(divider, 3, 1, 1, 2)

        viewMode_Btn = QPushButton("Viewmode")
        viewMode_Btn.clicked.connect(self.btn_man_DB_clearMode)
        self.tools_Lay.addWidget(viewMode_Btn, 6, 1, 1, 2)

        self.moveMode_Btn = QPushButton("move")
        self.moveMode_Btn.setCheckable(True)
        self.moveMode_Btn.clicked.connect(self.btn_man_DB_clearMode)
        self.tools_Lay.addWidget(self.moveMode_Btn, 7, 1, 1, 1)

        self.connectMode_Btn = QPushButton("connect")
        self.connectMode_Btn.setCheckable(True)
        self.connectMode_Btn.clicked.connect(self.btn_man_DB_clearMode)
        self.tools_Lay.addWidget(self.connectMode_Btn, 7, 2, 1, 1)

        self.deleteMode_Btn = QPushButton("delete")
        self.deleteMode_Btn.setCheckable(True)
        self.deleteMode_Btn.clicked.connect(self.btn_man_DB_clearMode)
        self.tools_Lay.addWidget(self.deleteMode_Btn, 8, 1, 1, 1)

        self.editMode_Btn = QPushButton("Edit")
        self.editMode_Btn.setCheckable(True)
        self.editMode_Btn.clicked.connect(self.btn_man_DB_clearMode)
        self.tools_Lay.addWidget(self.editMode_Btn, 8, 2, 1, 1)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        self.tools_Lay.addWidget(divider, 9, 1, 1, 2)

        self.placeNote_Btn = QPushButton("Place Note")
        self.placeNote_Btn.setCheckable(True)
        self.placeNote_Btn.clicked.connect(self.btn_man_DB_placeNote)
        self.tools_Lay.addWidget(self.placeNote_Btn, 14, 1, 1, 2)

        self.placeLinked_Btn = QPushButton("Place linked Container")
        self.placeLinked_Btn.setCheckable(True)
        self.placeLinked_Btn.clicked.connect(self.btn_man_DB_placeLinked)
        self.tools_Lay.addWidget(self.placeLinked_Btn, 15, 1, 1, 2)

        self.convertNote_Btn = QPushButton("convert Note to:")
        self.convertNote_Btn.setCheckable(True)
        self.convertNote_Btn.clicked.connect(self.btn_man_DB_clearMode)
        self.tools_Lay.addWidget(self.convertNote_Btn, 16, 1, 1, 2)

        self.tools_LayStack = QStackedWidget()
        self.tools_Lay.addWidget(self.tools_LayStack, 17, 1, 1, 2)

        self.Draftboard.updateScene()

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


        AppData.setCurrInfo(obj.linked[1], Flag=obj.linked[0], origin=self)
        AppData.mainWin.tabAdded.emit()

        widget = AppData.mainWin.man_Tab.currentWidget()
        widget.setExit(lambda: AppData.mainWin.closeTab(widget))

        return

    def init_Draftboard_GraphicScene(self): #ToDo remove?
        """Replaces self.selDraftboard_Combo with new widget and initializes new Draftboard selection

        :return: ->None
        """
        oldWid=self.selDraftboard_Combo
        self.selDraftboard_Combo = QComboBox()

        draftboards = ex.searchFactory("", "Draftbooks", output="draftbook_Title,draftbook_ID")
        for board in draftboards:
            self.selDraftboard_Combo.addItem(*board)

        self.selDraftboard_Combo.currentIndexChanged.connect(self.Draftboard.man_Draftboard.updateScene)
        self.tools_Lay.replaceWidget(oldWid,self.selDraftboard_Combo) # ToDo check if updated works: before addWidget (, 0, 1, 1, 2)
        self.Draftboard.updateScene()
        return

    def btn_man_DB_placeNote(self):
        """opens a dialog to place a label with a note already created in other draftbook

        :return: ->None
        """

        self.btn_man_DB_clearMode()
        self.Draftboard.obj_A = None
        dial = DialogEditItem([], maximumItems=1)
        dial.setSource(lambda x: ex.searchFactory(x, library="Notes", searchFulltext=True, shortOut=True), "Notes")

        if dial.exec_():
            self.Draftboard.obj_A = dial.getNewItems()[0][0]
        else:
            self.placeNote_Btn.setChecked(False)

    def btn_man_DB_placeLinked(self):
        """opens a dialog to place a dynamic [linked] label which contains the selected parameters of the selected dataset

        :return: ->None
        """
        self.Draftboard.obj_A = None
        self.btn_man_DB_clearMode()

        # dialog to select datatype
        dial = QDialog()
        lay = QVBoxLayout()
        dial.setLayout(lay)

        combo = QComboBox()
        combo.addItem("Event", "Events")
        combo.addItem("Individual", "Individuals")
        combo.addItem("Session", "Sessions")
        lay.addWidget(combo)

        buttonbox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonbox.accepted.connect(dial.accept)
        buttonbox.rejected.connect(dial.close)
        lay.addWidget(buttonbox)

        if dial.exec_():
            # dialog to select dataset
            library = combo.currentData()
            dial2 = DialogEditItem(maximumItems=1)
            dial2.setSource(lambda x: ex.searchFactory(x, library=library, searchFulltext=True, shortOut=True), library)

            if dial2.exec_():
                # dialog to select parameters
                indiv_ID = dial2.getNewItems()[0][0]

                dial3 = QDialog()
                lay = QVBoxLayout()
                dial3.setLayout(lay)

                lay.addWidget(QLabel("select shown columns:"))

                collection = []
                for column in ex.searchFactory("", library, searchFulltext=True, dictOut=True)[0]:
                    check = QCheckBox(column)
                    lay.addWidget(check)
                    collection.append(check)

                buttonbox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
                buttonbox.accepted.connect(dial3.accept)
                buttonbox.rejected.connect(dial3.close)
                lay.addWidget(buttonbox)

                if dial3.exec_():
                    text = ""
                    for item in collection:
                        if item.checkState():
                            text += item.text()
                            text += ":"
                    if text != "":
                        text = text.rstrip(":")

                    self.Draftboard.obj_A = (library, indiv_ID, text)
        return

    def btn_man_DB_deleteDB(self):
        """opens a dialog to confirm the deletion, on accept deletes the draftbook"""
        dialog = QDialog()
        lay = QVBoxLayout()
        dialog.setLayout(lay)

        lay.addWidget(QLabel("Soll dieses Draftbook gelöscht werden?"))
        lay.addWidget(QLabel("Draftbook:\n" + self.selDraftboard_Combo.currentText()))

        buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(dialog.accept)
        buttonBox.rejected.connect(dialog.close)
        lay.addWidget(buttonBox)

        if dialog.exec():
            id = self.selDraftboard_Combo.currentData()
            ex.deleteFactory(id, "Draftbooks")
            self.selDraftboard_Combo.removeItem(self.selDraftboard_Combo.findData(id))
        return

    def btn_man_DB_newDB(self):
        """opens a dialog to specify the draftbooks data, on apply creates the new draftbook

        :return: ->None
        """
        dialog = QDialog()
        lay = QVBoxLayout()
        dialog.setLayout(lay)

        lay.addWidget(QLabel("Titel:"))

        title = QLineEdit()
        lay.addWidget(title)

        lay.addWidget(QLabel("kurze Inhaltsbeschreibung:"))

        desc = QTextEdit()
        lay.addWidget(desc)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(dialog.accept)
        buttonBox.rejected.connect(dialog.close)
        lay.addWidget(buttonBox)

        if dialog.exec():
            if title.text() != "" or desc.toPlainText() != "":
                id = ex.newFactory("Draftbooks",
                                   {"draftbook_Title": title.text(), "draftbook_Short_Desc": desc.toPlainText(),
                                    "draftbook_height": 100, "draftbook_width": 500, "draftbook_xPos": 0,
                                    "draftbook_yPos": 0})
                self.selDraftboard_Combo.addItem(title.text(), id)
                self.selDraftboard_Combo.setCurrentIndex(self.selDraftboard_Combo.findData(id))
        return

    def btn_man_DB_clearMode(self):
        """unchecks all draftbook-tool-buttons

        :return: ->None
        """

        self.Draftboard.obj_A = None

        if self.sender() != self.moveMode_Btn:
            self.moveMode_Btn.setChecked(False)
        if self.sender() != self.connectMode_Btn:
            self.connectMode_Btn.setChecked(False)
        if self.sender() != self.deleteMode_Btn:
            self.deleteMode_Btn.setChecked(False)
        if self.sender() != self.convertNote_Btn:
            self.convertNote_Btn.setChecked(False)
        if self.sender() != self.editMode_Btn:
            self.editMode_Btn.setChecked(False)
        return

    def openTextCreator(self, event, obj=None, menu=False): #ToDO extract to Draftboard?
        """opens a dialog to insert the text for the note or in case of a linked note specify the parameters to be
        displayed and saves the note into the database

        :param event: QEvent, incoming event
        :param obj: QWidget, incoming widget
        :return: ->None
        """

        if event.button() == Qt.LeftButton or menu and event.button() == Qt.RightButton:

            Pos = self.Draftboard.mapToScene(event.pos())
            xPos = Pos.x()
            yPos = Pos.y()
            msg = QDialog()
            lay = QVBoxLayout()
            msg.setLayout(lay)

            collection = []
            if obj != None:

                # obj.linked contains the link to the dataset, if object is a linked note
                if obj.linked != None:
                    button = QPushButton("edit Details")
                    lay.addWidget(button)
                    for item in obj.textData:
                        check = QCheckBox(item)
                        collection.append(check)
                        if item in obj.column:
                            check.setChecked(True)
                        lay.addWidget(check)
                    button.clicked.connect(lambda: self.openEditWindow(obj, msg, collection))

                else:
                    text = QTextEdit()
                    text.setText(obj.text())
                    lay.addWidget(text)
            else:
                text = QTextEdit()
                lay.addWidget(text)

            buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)

            buttonBox.accepted.connect(msg.accept)
            buttonBox.rejected.connect(msg.reject)

            lay.addWidget(buttonBox)

            if msg.exec_():
                # save the note
                if obj == None:
                    note_ID = ex.newFactory(data={"note_Content": text.toPlainText()}, library="Notes")
                    label = QLabel()
                    label.setText(text.toPlainText())
                    label.setFrameShape(1)
                    label.setWordWrap(True)
                    label.setAlignment(Qt.AlignLeft)
                    label.setAlignment(Qt.AlignVCenter)
                    label.setGeometry(100, 100, label.sizeHint().width() + 2,
                                      label.sizeHint().height() + 4)

                    newX = int(xPos - label.width() / 2)
                    newY = int(yPos - label.height() / 2)

                    id = ex.newFactory(
                        data={"note_ID": note_ID, "draftbook_ID": self.selDraftboard_Combo.currentData(),
                              "xPos": newX, "yPos": newY, "height": label.height(), "width": label.width()},
                        library="Notes_Draftbook_jnt")



                elif obj.linked != None:
                    text = ""
                    for item in collection:
                        if item.checkState():
                            text += item.text()
                            text += ":"
                    text = text.rstrip(":")
                    ex.updateFactory(obj.labelData["note_ID"], [text], "Notes", ["note_Content"])

                else:
                    ex.updateFactory(obj.labelData["note_ID"], [text.toPlainText()], "Notes", ["note_Content"])

            # reloads the content of the draftboard with new note element
            self.Draftboard.updateScene(True)


class ViewNpc(QWidget):
    """Site-Widget to view any NPC

    """

    def __init__(self, id, standardButton=None):
        """

        :param id: int, id of the individual
        :param standardButton: function, optional, links a button for each familymember to the called function
        """
        super().__init__()
        self.id = id
        self.standardButton = standardButton

        self.updateView()

    def updateView(self):
        """ manages the layout of the widget and inserts the characters data from the database matching the id

        :return: ->None
        """
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)

        char = ex.getFactory(self.id, "Individuals", defaultOutput=True, dictOut=True)

        self.sex = QLabel(char['indiv_sex'])
        self.mainLayout.addWidget(self.sex)

        self.fName = QLabel(char['indiv_fName'])
        self.mainLayout.addWidget(self.fName)

        self.family = QLabel(char['family_Name'])
        self.mainLayout.addWidget(self.family)

        if char['indiv_title'] != None and char['indiv_title'] != "":
            label = QLabel("Title:")
            self.mainLayout.addWidget(label)

            self.title = QLabel(char['indiv_title'])
            self.mainLayout.addWidget(self.title)

        label = QLabel("Other Family Members:")
        self.mainLayout.addWidget(label)

        familyMembers = ex.searchFactory(str(char['fKey_family_ID']), 'Individuals', attributes=['fKey_family_ID'],
                                         shortOut=True)
        self.family_members = Resultbox()
        if self.standardButton != None:
            self.family_members.setPref(standardbutton=self.standardButton)
        self.family_members.resultUpdate(familyMembers)
        self.mainLayout.addWidget(self.family_members)

        if char['indiv_tags'] != None and char['indiv_tags'] != "":
            label = QLabel("Tags:")
            self.mainLayout.addWidget(label)

            self.tags = QLabel(char['indiv_tags'])
            self.mainLayout.addWidget(self.tags)

        self.notes = CustTextBrowser()
        self.notes.setOpenExternalLinks(True)
        self.notes.setText(char['indiv_notes'])
        self.mainLayout.addWidget(self.notes)


class FightView(QWidget):
    """A Window Layout to manage fights

    :signal newRound: pyqt-signal, gets emitted when the combatants list overstepped its last entry and restarts from first

    """

    newRound=pyqtSignal()
    def __init__(self, fighter):
        """initializes the views fighter and prepares layout, calls for createFighter at end

        :param fighter: list of dictionaries, keys: name, life, karma, mana, ini or the values of a fightPrep.fighter Widget
        """
        super().__init__()

        self.fighter=fighter
        self.activeFighter=None

        lay=QVBoxLayout()
        self.stacked=QStackedWidget()
        lay.addWidget(self.stacked)
        self.setLayout(lay)

        wid = QWidget()
        widLay=QVBoxLayout()
        wid.setLayout(widLay)

        self.stacked.addWidget(wid)
        self.stacked.setCurrentWidget(wid)

        self.charList=[]

        self.newRound.connect(self.updateIni)

        self.createFighter()

    def createFighter(self)->None:
        """creates the fighter based on the initialized self.fighter list and starts the fight round order"""
        for fighter in self.fighter:
            dictFighter = fighter
            if not "Fighter_Name" in dictFighter.keys():

                dictFighter={x:int(fighter[x].text()) for x in fighter if x!="name" and x!= "id" and fighter[x].text() !="0" }
                dictFighter.update(**{x: None for x in fighter if x!="name" and x!= "id" and fighter[x].text() =="0"})
                dictFighter["name"]=fighter["name"].text()

            char = FightChar(dictFighter["life"], dictFighter["life"], dictFighter["name"], dictFighter["ini"], dictFighter["mana"],
                             dictFighter["mana"], dictFighter["karma"], dictFighter["karma"])
            self.charList.append(char)

        self.updateIni()

    def nextIni(self)->None:
        """marks the next entry of the charList as active

        """
        index=self.charList.index(self.activeFighter)+1
        if index>len(self.charList)-1:
            self.newRound.emit()
            index=0

        self.activeFighter = self.charList[index]

        if not self.activeFighter.active:
            if len([x for x in self.charList if x.active])==0:
                return
            self.nextIni()
        else:
            self.updateIni()
        return


    def updateIni(self)->None:
        """manages the layout and order of the FightChars"""

        active=sorted([x for x in self.charList if x.active],key=lambda x: x.initiative,reverse = True)
        inactive=sorted([x for x in self.charList if not x.active],key=lambda x: x.initiative,reverse = True)
        self.charList = active + inactive

        if self.activeFighter is None:
            self.activeFighter=self.charList[0]

        scrollLay = QVBoxLayout()

        cenWid=QWidget()
        cenLay=QVBoxLayout()
        cenWid.setLayout(cenLay)

        for char in self.charList:

            if self.activeFighter==char:
                frame=QFrame()
                frame.setLineWidth(1)
                frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
                scrollLay.addWidget(frame)

                frameLay=QVBoxLayout()
                frame.setLayout(frameLay)

                frameLay.addWidget(char)

            else:
                scrollLay.addWidget(char)

        wid=QWidget()
        wid.setLayout(scrollLay)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setAlignment(Qt.AlignTop)
        scroll.setWidget(wid)
        cenLay.addWidget(scroll)

        scroll.ensureWidgetVisible(frame, xMargin=0, yMargin=0)

        button = QPushButton("Nächste Ini")
        button.clicked.connect(self.nextIni)
        cenLay.addWidget(button)

        self.stacked.addWidget(cenWid)
        self.stacked.setCurrentWidget(cenWid)
        return