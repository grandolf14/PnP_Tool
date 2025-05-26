from PyQt5.QtCore import Qt, pyqtSignal,QTimer
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QStackedWidget, QScrollArea, QFrame, QLabel, QHBoxLayout, \
                            QGridLayout, QComboBox, QDialogButtonBox, QDialog, QCheckBox,QLineEdit,QTextEdit, QMessageBox

import DB_Access as ex

from AppVar import InternVar as InVar
from UI_Browser import Resultbox
from UI_DataEdit import DraftBoard
from UI_Utility import FightChar, CustTextBrowser, DialogEditItem


#ToDo doc and rename
class Browser(QWidget):

    def __init__(self):

        self.filter = {"Events": [], "Individuals": [],"Sessions": []}

        self.timer = QTimer()

        super().__init__()

        lay=QVBoxLayout()
        self.setLayout(lay)

        self.man_Session_cen_stackWid = QStackedWidget()
        lay.addWidget(self.man_Session_cen_stackWid)

        man_Session_startpageWid = QWidget()
        self.man_Session_cen_stackWid.addWidget(man_Session_startpageWid)

        self.man_Session_startpageLay = QVBoxLayout()
        man_Session_startpageWid.setLayout(self.man_Session_startpageLay)

        self.man_Session_searchbar_layQH = QHBoxLayout()
        self.man_Session_startpageLay.addLayout(self.man_Session_searchbar_layQH)

        self.man_Session_searchBar_lEdit = QLineEdit()
        self.man_Session_searchBar_lEdit.textChanged.connect(lambda: self.timer_start(500, function=self.updateSearch))
        self.man_Session_searchbar_layQH.addWidget(self.man_Session_searchBar_lEdit, 50)

        self.selLib=QComboBox()
        self.selLib.addItem("Event", "Events")
        self.selLib.addItem("Individual", "Individuals")
        self.selLib.addItem("Session", "Sessions")
        self.selLib.currentIndexChanged.connect(self.load_man_Session_searchbar)
        self.man_Session_searchbar_layQH.addWidget(self.selLib, stretch=10)

        self.searchFullText = QPushButton("Fulltextsearch")
        self.searchFullText.setCheckable(True)
        self.searchFullText.clicked.connect(self.updateSearch)
        self.man_Session_searchbar_layQH.addWidget(self.searchFullText, stretch=10)

        button = QPushButton("set Filter")
        button.clicked.connect(self.btn_man_setFilter)
        self.man_Session_searchbar_layQH.addWidget(button, 10)

        self.man_Session_searchbar_filter_stWid = QStackedWidget()
        self.man_Session_searchbar_layQH.addWidget(self.man_Session_searchbar_filter_stWid, 30)

        button = QPushButton("new Session")
        button.clicked.connect(lambda: self.btn_man_viewSession(new=True))
        self.man_Session_searchbar_layQH.addWidget(button, 10)

        self.man_Session_searchresultWid = Resultbox()
        self.man_Session_searchresultWid.setPref(
            buttonList=[['select', self.btn_man_viewSession], ['delete', self.btn_man_DeleteSession]])
        self.man_Session_startpageLay.addWidget(self.man_Session_searchresultWid, 90)

        self.load_man_Session_searchbar()  # initialisiert das searchBarLayout

    def updateSearch(self)->None:

        if self.timer.isActive():
            self.timer.stop()

        text=self.man_Session_searchBar_lEdit.text()
        library=self.selLib.currentData()
        searchFullText=self.searchFullText.isChecked()
        filter=self.filter[library]

        searchresult = ex.searchFactory(text, library, shortOut=True,
                                        Filter=filter, searchFulltext=searchFullText)
        self.man_Session_searchresultWid.resultUpdate(searchresult)
        return

    def btn_man_viewSession(self,new=False):
        """opens a new SessionEditWindow either with new flag or with existing flag

        :return: ->None
        """
        id=None
        if not new:
            id=self.sender().page

        InVar.setCurrInfo(id, "Sessions", None)
        InVar.mainWindow.TabAdded.emit()

        widget=InVar.mainWindow.man_cen_tabWid.currentWidget()
        widget.setExit(lambda: InVar.mainWindow.closeTab("Current"))
        return

    def btn_man_DeleteSession(self):
        """asks for confirmation of deletion, deletes the Session and reloads the searchResult.

        :return: ->None
        """

        Id = self.sender().page
        library=self.selLib.currentData()

        msgBox = QMessageBox()
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        title=ex.getFactory(Id, library)[1]
        msgBox.setText("Do you want to delete %s" %(title))
        value = msgBox.exec()
        if value == 1024:
            ex.deleteFactory(Id, library)

        self.updateSearch()

    def btn_man_setFilter(self):
        """opens dialogs to set filter specifics for searches and denies request if there are more than 3 active filters

        :param library: str, the library to search in
        :return:
        """
        self.filterDialog = QDialog()
        self.filterDialog.setWindowTitle("Add new Filter")

        filterDialogLayout = QVBoxLayout()
        self.filterDialog.setLayout(filterDialogLayout)


        library = self.selLib.currentData()
        filter=self.filter[library]


        if len(filter) > 3:
            filterDialogLayout.addWidget(QLabel("To many Filter aktiv: \n Please delete existing Filter"))

            buttons = QDialogButtonBox.Ok
            buttonBox = QDialogButtonBox(buttons)
            buttonBox.accepted.connect(self.filterDialog.close)
            filterDialogLayout.addWidget(buttonBox)

        else:
            filterDialogHBox = QHBoxLayout()
            filterDialogLayout.addLayout(filterDialogHBox)

            self.search_Where = QComboBox()
            filter = ex.get_table_Prop(library)['colName']
            self.search_Where.addItems(filter)
            filterDialogHBox.addWidget(self.search_Where)

            self.search_What = QLineEdit()
            filterDialogHBox.addWidget(self.search_What)

            self.filterFulltext = QPushButton("Search Fulltext")
            self.filterFulltext.setCheckable(True)
            filterDialogHBox.addWidget(self.filterFulltext)


            buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
            buttonBox = QDialogButtonBox(buttons)

            buttonBox.accepted.connect(self.filterDialog.accept)

            buttonBox.rejected.connect(self.filterDialog.reject)

            filterDialogLayout.addWidget(buttonBox)

        if self.filterDialog.exec_():
            self.filter[library].append({"key":self.search_Where.currentText(),
                                        "text":self.search_What.text(),
                                        "fullTextSearch":self.filterFulltext.isChecked()})

            self.updateSearch()
            self.load_man_Session_searchbar()

        self.filterDialog.close()
        return

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

    def load_man_Session_searchbar(self):
        """repaints the session searchbar and adds/removes filter

        :return: ->None
        """

        newWid = QWidget()
        layout = QHBoxLayout()
        newWid.setLayout(layout)
        library=self.selLib.currentData()

        if len(self.filter[library]) > 0:
            for filterDict in self.filter[library]:
                button = QPushButton("delete Filter " + filterDict["key"] + ": " + filterDict["text"])
                button.page = self.filter[library].index(filterDict)
                button.clicked.connect(self.btn_man_delFilter)
                layout.addWidget(button, stretch=10)



        if len(self.filter[library]) < 5:
            for number in range(5 - len(self.filter[library])):
                layout.addWidget(QLabel(""), stretch=10)

        self.man_Session_searchbar_filter_stWid.addWidget(newWid)
        self.man_Session_searchbar_filter_stWid.setCurrentWidget(newWid)

        self.updateSearch()

        return

    def btn_man_delFilter(self):
        """removes the selected filter from filterlist and reloads corresponding searchbar

        :param library: current active library
        :return: ->None
        """
        index = self.sender().page
        library=self.selLib.currentData()

        self.filter[library].pop(index)
        self.load_man_Session_searchbar()
        return


#ToDo doc
class ViewDraftboard(QWidget):
    def __init__(self, win=None):

        super().__init__()

        mainLay=QVBoxLayout()
        self.setLayout(mainLay)

        self.man_Draftboard_startpageStack = QStackedWidget()
        mainLay.addWidget(self.man_Draftboard_startpageStack)

        self.man_Draftboard_startpageWid = QWidget()
        self.man_Draftboard_startpageStack.addWidget(self.man_Draftboard_startpageWid)

        self.man_Draftboard_startpageLay = QHBoxLayout()
        self.man_Draftboard_startpageWid.setLayout(self.man_Draftboard_startpageLay)

        self.man_Draftboard = DraftBoard(self)
        self.man_Draftboard.setRenderHint(QPainter.Antialiasing)
        self.man_Draftboard_startpageLay.addWidget(self.man_Draftboard)

        self.man_Draftboard_sidebar = QGridLayout()
        self.man_Draftboard_startpageLay.addLayout(self.man_Draftboard_sidebar)

        self.man_Draftboard_menu_selDB = QComboBox()

        draftboards = ex.searchFactory("", "Draftbooks", output="draftbook_Title,draftbook_ID")
        for board in draftboards:
            self.man_Draftboard_menu_selDB.addItem(*board)

        self.man_Draftboard_menu_selDB.currentIndexChanged.connect(self.man_Draftboard.updateScene)
        self.man_Draftboard_sidebar.addWidget(self.man_Draftboard_menu_selDB, 0, 1, 1, 2)

        self.man_Draftboard_btn_newDraftbook = QPushButton("neues Draftbook")
        self.man_Draftboard_btn_newDraftbook.clicked.connect(self.btn_man_DB_newDB)
        self.man_Draftboard_sidebar.addWidget(self.man_Draftboard_btn_newDraftbook, 1, 1, 1, 2)

        self.man_Draftboard_btn_deleteDB = QPushButton("Draftbook löschen")
        self.man_Draftboard_btn_deleteDB.clicked.connect(self.btn_man_DB_deleteDB)
        self.man_Draftboard_sidebar.addWidget(self.man_Draftboard_btn_deleteDB, 2, 1, 1, 2)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        self.man_Draftboard_sidebar.addWidget(divider, 3, 1, 1, 2)

        self.man_Draftboard_btn_clearMode = QPushButton("Viewmode")
        self.man_Draftboard_btn_clearMode.clicked.connect(self.btn_man_DB_clearMode)
        self.man_Draftboard_sidebar.addWidget(self.man_Draftboard_btn_clearMode, 6, 1, 1, 2)

        self.man_Draftboard_btn_moveMode = QPushButton("move")
        self.man_Draftboard_btn_moveMode.setCheckable(True)
        self.man_Draftboard_btn_moveMode.clicked.connect(self.btn_man_DB_clearMode)
        self.man_Draftboard_sidebar.addWidget(self.man_Draftboard_btn_moveMode, 7, 1, 1, 1)

        self.man_Draftboard_btn_connectMode = QPushButton("connect")
        self.man_Draftboard_btn_connectMode.setCheckable(True)
        self.man_Draftboard_btn_connectMode.clicked.connect(self.btn_man_DB_clearMode)
        self.man_Draftboard_sidebar.addWidget(self.man_Draftboard_btn_connectMode, 7, 2, 1, 1)

        self.man_Draftboard_btn_deleteMode = QPushButton("delete")
        self.man_Draftboard_btn_deleteMode.setCheckable(True)
        self.man_Draftboard_btn_deleteMode.clicked.connect(self.btn_man_DB_clearMode)
        self.man_Draftboard_sidebar.addWidget(self.man_Draftboard_btn_deleteMode, 8, 1, 1, 1)

        self.man_Draftboard_btn_editMode = QPushButton("Edit")
        self.man_Draftboard_btn_editMode.setCheckable(True)
        self.man_Draftboard_btn_editMode.clicked.connect(self.btn_man_DB_clearMode)
        self.man_Draftboard_sidebar.addWidget(self.man_Draftboard_btn_editMode, 8, 2, 1, 1)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        self.man_Draftboard_sidebar.addWidget(divider, 9, 1, 1, 2)

        self.man_Draftboard_btn_placeNote = QPushButton("Place Note")
        self.man_Draftboard_btn_placeNote.setCheckable(True)
        self.man_Draftboard_btn_placeNote.clicked.connect(self.btn_man_DB_placeNote)
        self.man_Draftboard_sidebar.addWidget(self.man_Draftboard_btn_placeNote, 14, 1, 1, 2)

        self.man_Draftboard_btn_placelinked = QPushButton("Place linked Container")
        self.man_Draftboard_btn_placelinked.setCheckable(True)
        self.man_Draftboard_btn_placelinked.clicked.connect(self.btn_man_DB_placeLinked)
        self.man_Draftboard_sidebar.addWidget(self.man_Draftboard_btn_placelinked, 15, 1, 1, 2)

        self.man_Draftboard_btn_convert = QPushButton("convert Note to:")
        self.man_Draftboard_btn_convert.setCheckable(True)
        self.man_Draftboard_btn_convert.clicked.connect(self.btn_man_DB_clearMode)
        self.man_Draftboard_sidebar.addWidget(self.man_Draftboard_btn_convert, 16, 1, 1, 2)

        self.man_Draftboard_sidebarStack = QStackedWidget()
        self.man_Draftboard_sidebar.addWidget(self.man_Draftboard_sidebarStack, 17, 1, 1, 2)

        self.man_Draftboard.updateScene(window=win)

    def btn_man_DB_placeNote(self):
        """opens a dialog to place a label with a note already created in other draftbook

        :return: ->None
        """

        self.btn_man_DB_clearMode()
        self.man_Draftboard.obj_A = None
        dial2 = DialogEditItem([], maximumItems=1)
        dial2.setSource(lambda x: ex.searchFactory(x, library="Notes", searchFulltext=True, shortOut=True), "Notes")

        if dial2.exec_():
            self.man_Draftboard.obj_A = dial2.getNewItems()[0][0]
        else:
            self.man_Draftboard_btn_placeNote.setChecked(False)

    def btn_man_DB_placeLinked(self):
        """opens a dialog to place a dynamic [linked] label which contains the selected parameters of the selected dataset

        :return: ->None
        """
        self.man_Draftboard.obj_A = None
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

                    self.man_Draftboard.obj_A = (library, indiv_ID, text)
        return

    def btn_man_DB_deleteDB(self):
        """opens a dialog to confirm the deletion, on accept deletes the draftbook"""
        dialog = QDialog()
        lay = QVBoxLayout()
        dialog.setLayout(lay)

        lay.addWidget(QLabel("Soll dieses Draftbook gelöscht werden?"))
        lay.addWidget(QLabel("Draftbook:\n" + self.man_Draftboard_menu_selDB.currentText()))

        buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(dialog.accept)
        buttonBox.rejected.connect(dialog.close)
        lay.addWidget(buttonBox)

        if dialog.exec():
            id = self.man_Draftboard_menu_selDB.currentData()
            ex.deleteFactory(id, "Draftbooks")
            self.man_Draftboard_menu_selDB.removeItem(self.man_Draftboard_menu_selDB.findData(id))
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
                self.man_Draftboard_menu_selDB.addItem(title.text(), id)
                self.man_Draftboard_menu_selDB.setCurrentIndex(self.man_Draftboard_menu_selDB.findData(id))
        return

    def btn_man_DB_clearMode(self):
        """unchecks all draftbook-tool-buttons

        :return: ->None
        """

        self.man_Draftboard.obj_A = None

        if self.sender() != self.man_Draftboard_btn_moveMode:
            self.man_Draftboard_btn_moveMode.setChecked(False)
        if self.sender() != self.man_Draftboard_btn_connectMode:
            self.man_Draftboard_btn_connectMode.setChecked(False)
        if self.sender() != self.man_Draftboard_btn_deleteMode:
            self.man_Draftboard_btn_deleteMode.setChecked(False)
        if self.sender() != self.man_Draftboard_btn_convert:
            self.man_Draftboard_btn_convert.setChecked(False)
        if self.sender() != self.man_Draftboard_btn_editMode:
            self.man_Draftboard_btn_editMode.setChecked(False)
        return

    def openTextCreator(self, event, obj=None):
        """opens a dialog to insert the text for the note or in case of a linked note specify the parameters to be
        displayed and saves the note into the database

        :param event: QEvent, incoming event
        :param obj: QWidget, incoming widget
        :return: ->None
        """

        if event.button() == Qt.LeftButton:

            Pos = self.man_Draftboard.mapToScene(event.pos())
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
                        data={"note_ID": note_ID, "draftbook_ID": self.man_Draftboard_menu_selDB.currentData(),
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
            self.man_Draftboard.updateScene(True)

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