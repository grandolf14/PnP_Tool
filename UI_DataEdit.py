from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIntValidator, QPen
from PyQt5.QtWidgets import QLabel, QGraphicsScene, QGraphicsView, QWidget, QPushButton, QHBoxLayout,  QLineEdit, \
    QVBoxLayout, QScrollArea, QDialog, QDialogButtonBox, QTabWidget, QAction, QComboBox, QMenu

import DB_Access as ex

from AppVar import UserData, AppData
from Models import randomChar
from UI_Browser import Resultbox
from UI_Utility import DialogEditItem, TextEdit


class DataLabel(QLabel):
    """label for dynamic display of library datasets

    """

    def __init__(self, board, linked=None, *args, **kwargs, ):
        """

        :param linked: the corresponding dataset link, optional
        :param args: pass forward to QLabel class
        :param kwargs: pass forward to QLabel class
        """
        super().__init__(*args, **kwargs)
        self.linked = linked
        self.board=board

        self.setTextInteractionFlags(Qt.LinksAccessibleByMouse)

        if self.linked!=None:
            self.setStyleSheet("color : blue")


    def setLink(self,text):
        """sets the link of the datalabel

        :param text: str, contains the link
        :return: ->None
        """
        self.linked=text
        if self.linked!=None:
            self.setStyleSheet("color : blue")
        else:
            self.setStyleSheet("color : black")
        return

    def deleteNote(self):
        """Deletes the selected Notes dataset and reloads the draftbook to remove label

        :return: ->None
        """
        self.setStyleSheet('background-color: beige')
        self.setFrameStyle(3)
        msg = QDialog()
        msgLay = QVBoxLayout()

        msg.setLayout(msgLay)

        fullRemoveNote = False

        if len(ex.searchFactory(self.labelData["note_ID"], "Notes_Draftbook_jnt",
                                attributes=["note_ID"])) == 1:
            msgLay.addWidget(QLabel(
                "Do you want to delete this Note?\n There will be no possibility to restore the Data"))
            fullRemoveNote = True
        else:
            msgLay.addWidget(QLabel("Do you want to delete this Note?"))

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        buttonBox.accepted.connect(msg.accept)
        buttonBox.rejected.connect(msg.reject)

        msgLay.addWidget(buttonBox)

        if msg.exec():
            if fullRemoveNote:
                ex.deleteFactory(self.labelData["note_ID"], "Notes")
            ex.deleteFactory(self.labelData["pos_ID"], "Notes_Draftbook_jnt")
        else:
            self.setStyleSheet('background-color: light grey')

        self.board.updateScene(True)
        return

    def editNote(self,event):
        """Calls a function to open a Dialog and edit the Notes content

        :param event: the calling event
        :return: ->None
        """
        self.view.obj_A = None
        self.board.view.openTextCreator(event, obj=self)
        return

    def moveNote(self,event):
        """Selects a Note to be moved in ongoing process

        :param event: the calling event
        :return: ->None
        """
        if self.view.obj_A == None:
            self.setStyleSheet('background-color: beige')
            self.setFrameStyle(3)
            self.view.obj_A = self

    def convertNote(self):
        """Opens dialogs to choose the type of data to in which the note will be converted and opens correponding
            editing window

        :return: ->None
        """

        self.setStyleSheet('background-color: beige')
        self.setFrameStyle(3)

        dialog = QDialog()
        lay = QVBoxLayout()
        dialog.setLayout(lay)

        combo = QComboBox()

        combo.addItem("Session", ["Sessions", "session_Name:session_notes"])
        combo.addItem("Event", ["Events", "event_Title:event_short_desc"])
        combo.addItem("Individual", ["Individuals", "indiv_Name"])
        lay.addWidget(combo)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(dialog.accept)
        buttonBox.rejected.connect(dialog.close)
        lay.addWidget(buttonBox)

        if dialog.exec_():

            combonew = combo.currentData()

            AppData.current_ID=None
            AppData.current_Flag=combonew[0]
            AppData.current_Data={"notes": self.text()}
            AppData.mainWin.tabAdded.emit()

            # updates dataLabels content in Database
            widget = AppData.mainWin.man_cen_tabWid.currentWidget()
            id = widget.returnID()
            exitFunc=lambda: AppData.mainWin.closeTab(widget)

            widget.setExit(exitFunc,
                           onDecline=lambda: ex.updateFactory(self.labelData["note_ID"], [None],
                                                              "Notes", ["note_Checked"]),
                           onApply=lambda: ex.updateFactory(self.labelData["note_ID"], [combonew[1],combonew[0] + ":" + str(id)],
                                                            "Notes", ["note_Content","note_Checked"]))

        else:
            self.board.view.man_Draftboard_btn_convert.setChecked(False)
            self.board.updateScene()
        return

    def connectNote(self):
        """Select a note if none is selected, deselect it if it is selected again and create a connection between
            two notes if a note is selected

        :return: ->None
        """

        if self.view.obj_A != None and self.view.obj_A != self:
            existing = []
            existing.append(ex.searchFactory(self.labelData["pos_ID"], "Note_Note_Pathlib",
                                             attributes=["note_DB_ID1"],
                                             Filter=[{  "key":"note_DB_ID2",
                                                        "text": self.view.obj_A.labelData["pos_ID"],
                                                        "fullTextSearch":False}]))
            existing.append(ex.searchFactory(self.labelData["pos_ID"], "Note_Note_Pathlib",
                                             attributes=["note_DB_ID2"],
                                             Filter=[{"key":"note_DB_ID1",
                                                      "text":self.view.obj_A.labelData["pos_ID"],
                                                      "fullTextSearch":False}]))

            if existing == [[], []]:
                ex.newFactory("Note_Note_Pathlib",
                              {"note_DB_ID1": self.view.obj_A.labelData["pos_ID"],
                               "note_DB_ID2": self.labelData["pos_ID"],
                               "draftbook_ID": self.board.view.man_Draftboard_menu_selDB.currentData()})
            else:
                id = [*existing[0], *existing[1]][0][0]
                ex.deleteFactory(id, "Note_Note_Pathlib")
            self.board.updateScene()
            self.view.obj_A = None

            # removes current object
        elif self.view.obj_A == self:
            self.view.obj_A = None
            self.setStyleSheet('background-color: light grey')
            self.setFrameStyle(1)

            # saves current object in displaying view.obj_A for further use
        else:
            self.view.obj_A = self
            self.setStyleSheet('background-color: beige')
            self.setFrameStyle(3)

        return

    def mousePressEvent(self, event):
        """overwrite QLabel mousePressEvent

        :param event: QMousePressEvent
        :return: ->None
        """
        super().mousePressEvent(event)
        event.accept()
        return

    def linkHovered(self,link):
        pass

    def linkActivated2(self, link):
        print("abc")

    def mouseReleaseEvent(self, event):
        """Overwrite mouseReleaseEvent of QLabel if any mode activated or RMB

        :param event: QMouseEvent
        :return: ->None
        """
        super().mouseReleaseEvent(event)
        if event.button() == Qt.RightButton:
            event.accept()

            menu=QMenu()

            editAction = QAction("Edit")
            editAction.triggered.connect(lambda: self.editNote(event))
            menu.addAction(editAction)

            if self.linked == None:
                convertAction = QAction("Convert")
                convertAction.triggered.connect(self.convertNote)
                menu.addAction(convertAction)

            deleteAction=QAction("Delete")
            deleteAction.triggered.connect(self.deleteNote)
            menu.addAction(deleteAction)

            moveAction=QAction("Move")
            moveAction.triggered.connect(lambda: self.moveNote(event))
            menu.addAction(moveAction)

            menu.addSeparator()

            connectAction=QAction("Connect")
            connectAction.triggered.connect(self.connectNote)
            menu.addAction(connectAction)

            menu.exec_(event.globalPos())
            return

        if event.button() == Qt.LeftButton:
            # deletemode
            if self.board.view.man_Draftboard_btn_deleteMode.isChecked():
                event.accept()
                self.deleteNote()
                return

            # selects the note to edit and opens the configuration dialog
            if self.board.view.man_Draftboard_btn_editMode.isChecked():
                event.accept()
                self.editNote(event)
                return

            # connect two notes
            if self.board.view.man_Draftboard_btn_connectMode.isChecked():
                event.accept()
                self.connectNote()
                return


            # select container to move
            if self.board.view.man_Draftboard_btn_moveMode.isChecked():
                event.accept()
                self.moveNote(event)
                return

            # converts a note to linked note and opens the window to creates the corresponding session, event or NPC
            if self.board.view.man_Draftboard_btn_convert.isChecked() and self.linked == None:
                event.accept()
                self.convertNote()
                self.board.view.man_Draftboard_btn_convert.setChecked(False)
                return

        event.ignore()
        return

    def mouseDoubleClickEvent(self, event):
        """Overwrite of mouseDoubleClickEvent of QLabel

        :param event: QMouseEvent
        :return: ->None
        """
        # open dialog to edit the containers content
        if event.button() == Qt.LeftButton:
            event.accept()
            self.board.view.openTextCreator(event, obj=self)
            return

        return


class DraftBoard(QGraphicsView):


    def __init__(self, view, *args,**kwargs):
        super().__init__(*args,**kwargs)
        self.obj_A = None
        self.view=view

    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)
        if event.isAccepted():
            return

        if event.button() == Qt.LeftButton:
            event.accept()

            self.obj_A = None
            self.board.view.openTextCreator(event)
            return


        event.ignore()
        return

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.isAccepted():
            return

        if event.button() == Qt.LeftButton:
            # move container to position
            if self.obj_A != None and self.view.man_Draftboard_btn_moveMode.isChecked():
                pos = self.view.man_Draftboard.mapToScene(event.pos())
                newX = int(pos.x() - self.obj_A.width() / 2)
                newY = int(pos.y() - self.obj_A.height() / 2)

                id = ex.searchFactory(self.view.man_Draftboard_menu_selDB.currentData(), "Notes_Draftbook_jnt",
                                      attributes=["draftbook_ID"], output="rowid",
                                      Filter=[{"key":"xPos", "text":str(self.obj_A.pos().x()),"fullTextSearch": False},
                                              {"key":"yPos", "text": str(self.obj_A.pos().y()),"fullTextSearch": False}])

                ex.updateFactory(id[0][0], [str(self.obj_A.labelData["note_ID"]),
                                            str(self.view.man_Draftboard_menu_selDB.currentData()), newX,
                                            newY], "Notes_Draftbook_jnt",
                                 ["note_ID", "draftbook_ID", "xPos", "yPos"])

                self.view.man_Draftboard.updateScene(True)
                self.obj_A = None
                self.view.man_Draftboard.updateScene()

            # place linked container at position
            if self.view.man_Draftboard_btn_placelinked.isChecked():
                if self.obj_A != None:
                    id = self.obj_A[1]
                    library = self.obj_A[0]
                    text = self.obj_A[2]
                    item = ex.getFactory(id, library, dictOut=True)

                    label = QLabel()
                    label.setWordWrap(True)
                    label.setTextFormat(Qt.RichText)
                    label.setAlignment(Qt.AlignLeft)
                    label.setAlignment(Qt.AlignVCenter)
                    label.setFrameStyle(1)
                    label.column = text.split(":")
                    labelText = ""
                    for column in label.column:
                        labelText += column + ":\n" + str(item[column])
                        if column != column[-1]:
                            labelText += "\n\n"
                    label.setText(labelText)
                    label.setGeometry(100, 100, label.sizeHint().width() + 2,
                                      label.sizeHint().height() + 4)

                    pos = self.mapToScene(event.pos())
                    newX = int(pos.x() - label.width() / 2)
                    newY = int(pos.y() - label.height() / 2)

                    newID = ex.newFactory("Notes", {"note_Checked": library + ":" + str(id), "note_Content": text})
                    ex.newFactory(
                        data={"note_ID": newID, "draftbook_ID": self.view.man_Draftboard_menu_selDB.currentData(),
                              "xPos": newX, "yPos": newY, "width": 0, "height": 0},
                        library="Notes_Draftbook_jnt")
                    self.updateScene(True)
                self.view.man_Draftboard_btn_placelinked.setChecked(False)

            # place text Note container at position
            if self.view.man_Draftboard_btn_placeNote.isChecked():
                if self.obj_A != None:
                    id = self.obj_A
                    item = ex.getFactory(id, "Notes", dictOut=True)
                    text = item["note_Content"]
                    label = QLabel()
                    label.setWordWrap(True)
                    label.setAlignment(Qt.AlignLeft)
                    label.setAlignment(Qt.AlignVCenter)
                    label.setTextFormat(Qt.RichText)
                    label.setFrameStyle(1)

                    if item["note_Checked"] != None:

                        label.column = text.split(":")
                        labelText = ""
                        label.linked = item["note_Checked"].split(":")
                        textData = ex.getFactory(label.linked[1], label.linked[0], dictOut=True)
                        for column in label.column:
                            labelText += column + ":\n" + str(textData[column])
                            if column != column[-1]:
                                labelText += "\n\n"
                    else:
                        labelText = text

                    label.setText(labelText)
                    label.setGeometry(100, 100, label.sizeHint().width() + 2,
                                      label.sizeHint().height() + 4)

                    pos = self.mapToScene(event.pos())
                    newX = int(pos.x() - label.width() / 2)
                    newY = int(pos.y() - label.height() / 2)
                    ex.newFactory(
                        data={"note_ID": id, "draftbook_ID": self.view.man_Draftboard_menu_selDB.currentData(),
                              "xPos": newX, "yPos": newY, "width":0, "height":0 },
                        library="Notes_Draftbook_jnt")
                    self.view.man_Draftboard.updateScene(True)

                self.view.man_Draftboard_btn_placeNote.setChecked(False)



            return

    #ToDo refactor window
    def updateScene(self, move=False, window=None):
        """ updates the scene of Draftbook with all saved notes in database

        :param move: bool, optional, did any label changed position since last appearance
        :param window: bool|MyWindow, optional, if None the defaultName of the MainWindow is inserted
        :return: ->None
        """

        window = self.view

        notes=ex.searchFactory(str(window.man_Draftboard_menu_selDB.currentData()),"Notes_Draftbook_jnt",attributes=["draftbook_ID"],
                               innerJoin="LEFT JOIN Notes ON Notes_Draftbook_jnt.note_ID = Notes.note_ID", dictOut=True)

        labels=[]
        for note in notes:

            label = DataLabel(self)
            label.setTextFormat(Qt.RichText)
            textData=None
            label.textData=None

            # creates link for linked label
            if note["note_Checked"]!=None:
                label.setLink(note["note_Checked"].split(":"))
                textData=ex.getFactory(label.linked[1],label.linked[0],dictOut=True)

            # sets text for linked or unlinked labels
            if textData!=None:
                text=""
                label.textData=textData
                label.column=note["note_Content"].split(":")
                for column in label.column:
                    text+=column+":\n"+str(textData[column])
                    if column!=column[-1]:
                        text+="\n\n"
                label.setText(text)
            else:
                label.setText(note["note_Content"])

            #positions labels
            label.setWordWrap(True)
            label.labelData= {"note_ID": note["note_ID"], "pos_ID": note["note_DB_ID"]}
            label.setAlignment(Qt.AlignLeft)
            label.setAlignment(Qt.AlignVCenter)
            label.setFrameStyle(1)

            label.setGeometry(note["xPos"], note["yPos"],label.sizeHint().width()+2,
                              label.sizeHint().height()+4)

            # if content changed or the label was moved recalculate height width and position, updates database and calls
            # itself
            if note["height"]!=label.height() or note["width"]!=label.width() or move==True:
                newHeight=label.height()
                newWidth=label.width()
                newxPos=int(note["xPos"]+(note["width"]-label.width())/2)
                newyPos=int(note["yPos"]+(note["height"]-label.height())/2)
                ex.updateFactory(label.labelData["pos_ID"],[newxPos,newyPos,newHeight,newWidth],"Notes_Draftbook_jnt",["xPos","yPos","height","width"])


                minX=ex.searchFactory(window.man_Draftboard_menu_selDB.currentData(),"Notes_Draftbook_jnt",
                                      attributes=["draftbook_ID"],OrderBy="Notes_Draftbook_jnt.xPos ASC",
                                      output=("Notes_Draftbook_jnt.xPos"))[0][0]-200
                maxX=ex.searchFactory(window.man_Draftboard_menu_selDB.currentData(),"Notes_Draftbook_jnt",
                                      attributes=["draftbook_ID"],OrderBy="Notes_Draftbook_jnt.xPos+Notes_Draftbook_jnt.width DESC",
                                      output=("Notes_Draftbook_jnt.xPos+Notes_Draftbook_jnt.width"))[0][0]+200
                minY=ex.searchFactory(window.man_Draftboard_menu_selDB.currentData(),"Notes_Draftbook_jnt",
                                      attributes=["draftbook_ID"],OrderBy="Notes_Draftbook_jnt.yPos ASC",
                                      output=("Notes_Draftbook_jnt.yPos"))[0][0]-200
                maxY=ex.searchFactory(window.man_Draftboard_menu_selDB.currentData(),"Notes_Draftbook_jnt",
                                      attributes=["draftbook_ID"],OrderBy="Notes_Draftbook_jnt.yPos+Notes_Draftbook_jnt.height DESC",
                                      output=("Notes_Draftbook_jnt.yPos + Notes_Draftbook_jnt.height"))[0][0]+200


                ex.updateFactory(window.man_Draftboard_menu_selDB.currentData(),[minX,minY,maxY-minY,maxX-minX],"Draftbooks", attributes=["draftbook_xPos","draftbook_yPos","draftbook_height","draftbook_width"])


                self.updateScene(window=window)
                return

            labels.append(label)


        note_ID=[x["note_DB_ID"] for x in notes]
        lineraw=ex.searchFactory("","Note_Note_Pathlib")
        lines=[]

        #connects the notes, if a connection is intended
        for path in lineraw:
            if path[1] in note_ID and path[2] in note_ID:
                lines.append(path)

        draftboard = ex.getFactory(window.man_Draftboard_menu_selDB.currentData(), "Draftbooks", dictOut=True)

        view = self.size()

        # if draftbook exists load last draftbook view else initializes default view
        if type(draftboard) == dict:

            oldView = self.mapToScene(self.pos())

            xPos = min(draftboard["draftbook_xPos"], oldView.x() - 20)
            yPos = min(draftboard["draftbook_yPos"], oldView.y() - 20)
            width = max(draftboard["draftbook_xPos"] + draftboard["draftbook_width"], oldView.x() + view.width()) - xPos
            height = max(draftboard["draftbook_yPos"] + draftboard["draftbook_height"],
                         oldView.y() + view.height()) - yPos

            self.graphicScene = QGraphicsScene(xPos, yPos, width, height)
            self.setScene(self.graphicScene)
        else:
            self.graphicScene = QGraphicsScene(0, 0, view.width(), view.height())
            self.setScene(self.graphicScene)


        # adds the connection lines
        for line in lines:
            index1=note_ID.index(line[1])
            index2=note_ID.index(line[2])

            x = labels[index1].pos().x() + labels[index1].width() / 2
            y = labels[index1].pos().y() + labels[index1].height() / 2

            x1 = labels[index2].pos().x() + labels[index2].width() / 2
            y1 = labels[index2].pos().y() + labels[index2].height() / 2

            self.graphicScene.addLine(x,y,x1,y1,QPen(Qt.black, 2, Qt.SolidLine))
        # adds the labels to view
        for label in labels:
            label.view = self
            self.graphicScene.addWidget(label)


        return


class FightPrep(QWidget):
    """Widget to prepare a fights combatants

    :param fighter: holds the current added fighter
    :param deleteID: holds the id's of removed fighters that are already saved in the database"""
    def __init__(self)->None:
        """Initializes the widgets Layout"""
        super().__init__()
        widLay=QVBoxLayout()
        self.setLayout(widLay)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        widLay.addWidget(scroll)

        scWid = QWidget()
        scroll.setWidget(scWid)

        self.scLay = QVBoxLayout()
        scWid.setLayout(self.scLay)

        self.fighter = []
        self.deleteID=[]

        button = QPushButton("Kombatanten hinzufügen")
        widLay.addWidget(button)
        button.clicked.connect(lambda: self.newFighter(fighter=None))

    def newFighter(self,fighter:dict)->None:
        """Adds a new Fighter with standardvalues to the scroll Layout

        :param fighter: dict|None, a dictionary specifying the keys: Fighter_Name, Fighter_HP, Fighter_Mana, Fighter_Karma,
                                    Fighter_Initiative, if None default Values are inserted"""

        lay=QHBoxLayout()
        self.scLay.addLayout(lay)

        lay.addWidget(QLabel("Name:"))
        name=QLineEdit()
        name.setText("Kämpfer "+str(len(self.fighter)))
        lay.addWidget(name)


        lay.addWidget(QLabel("LeP:"))
        life = QLineEdit()
        life.setText("32")
        life.setValidator(QIntValidator(1,10000))
        lay.addWidget(life)


        lay.addWidget(QLabel("Ini:"))
        ini = QLineEdit()
        ini.setText("12")
        ini.setValidator(QIntValidator(1, 10000))
        lay.addWidget(ini)


        lay.addWidget(QLabel("AsP:"))
        mana = QLineEdit()
        mana.setText("0")
        mana.setValidator(QIntValidator(1,10000))
        lay.addWidget(mana)


        lay.addWidget(QLabel("KaP:"))
        karma = QLineEdit()
        karma.setText("0")
        karma.setValidator(QIntValidator(1,10000))
        lay.addWidget(karma)

        button=QPushButton("Kämpfer löschen")
        button.layoutValue = lay
        lay.addWidget(button)

        if fighter is not None:
            name.setText(fighter["Fighter_Name"])
            life.setText(str(fighter["Fighter_HP"]))
            mana.setText(str(fighter["Fighter_Mana"]))
            karma.setText(str(fighter["Fighter_Karma"]))
            ini.setText(str(fighter["Fighter_Initiative"]))
            #weapon.setText(fighter["Fighter_Weapon"]) #TODO Add Weapon


        self.fighter.append({"name":name,"life":life,"ini":ini,"mana":mana, "karma":karma})
        if fighter is not None:
            self.fighter[-1]["id"]=fighter["Fighter_ID"]
            button.clicked.connect(lambda: self.deleteCombatant(fighter["Fighter_ID"]))
        else:
            self.fighter[-1]["id"] ="new"
            button.clicked.connect(lambda:self.deleteCombatant(None))

    def deleteCombatant(self,id):
        """removes a combatant from the widget and adds the id to self.deleteID if any is linked"""
        if id != None:
            self.deleteID.append(id)

        layout=self.sender().layoutValue
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)


class NPCEditWindow(QWidget):
    """Site widget to manage the contents of any NPC

    """

    def __init__(self, id, new=False, notes={}):
        """initializes the widgets content layout

        :param id: int, id of the session in database
        :param new: bool, optional, set true the session is treated as not existing event
        :param notes: first note draft for shortnotes
        """
        super().__init__()

        self.id = id
        self.new = new

        if self.new:
            self.id = ex.newFactory('Individuals',
                                    {'indiv_fName': '@N€w Ch4r4ct€r', 'fKey_family_ID': UserData.defaultFamily})

        cenLayout = QHBoxLayout()
        self.setLayout(cenLayout)

        # Mainroom
        mainLayout = QVBoxLayout()
        cenLayout.addLayout(mainLayout, stretch=8)

        loadedChar = ex.getFactory(self.id, "Individuals", defaultOutput=True, dictOut=True)

        label = QLabel("forename")
        mainLayout.addWidget(label)

        self.fName = QLineEdit()
        if loadedChar['indiv_fName'] != " " and loadedChar['indiv_fName'] != None:
            self.fName.setText(loadedChar['indiv_fName'])
        mainLayout.addWidget(self.fName)

        label = QLabel("family")
        mainLayout.addWidget(label)

        if loadedChar['family_Name'] != " " and loadedChar['family_Name'] != None:
            self.family_Name = QLabel(loadedChar['family_Name'])
            mainLayout.addWidget(self.family_Name)

        hboxLayout = QHBoxLayout()
        mainLayout.addLayout(hboxLayout)
        self.family_Btn = QPushButton('set Family')
        if loadedChar['family_Name'] != " " and loadedChar['family_Name'] != None:
            self.family_Btn.setText('change Family')
        self.family_Btn.clicked.connect(self.man_selFamily)
        hboxLayout.addWidget(self.family_Btn)

        self.family_new_Btn = QPushButton('new Family')
        self.family_new_Btn.clicked.connect(self.man_newFamily)
        hboxLayout.addWidget(self.family_new_Btn)

        self.family_id = loadedChar['fKey_family_ID']
        self.familyMembers = Resultbox()
        self.familyMembers.resultUpdate(
            ex.searchFactory(str(self.family_id), 'Individuals', attributes=['fKey_family_Id'], shortOut=True))
        mainLayout.addWidget(self.familyMembers)

        sexLay = QHBoxLayout()
        mainLayout.addLayout(sexLay)

        self.sex_male = QPushButton("male")
        self.sex_male.setCheckable(True)
        self.sex_male.setChecked(False)
        sexLay.addWidget(self.sex_male)

        self.sex_female = QPushButton("female")
        self.sex_female.setCheckable(True)
        self.sex_female.setChecked(True)
        sexLay.addWidget(self.sex_female)

        self.sex_male.clicked.connect(lambda: self.sex_female.setChecked(False))
        self.sex_female.clicked.connect(lambda: self.sex_male.setChecked(False))

        if loadedChar["indiv_sex"] == "male":
            self.sex_male.setChecked(True)
            self.sex_female.setChecked(False)

        label = QLabel("title")
        mainLayout.addWidget(label)

        self.title = QLineEdit()
        if loadedChar['indiv_title'] != " " and loadedChar['indiv_title'] != None:
            self.title.setText(loadedChar['indiv_title'])
        mainLayout.addWidget(self.title)

        label = QLabel("tags")
        mainLayout.addWidget(label)

        self.tags = QLineEdit()
        if loadedChar['indiv_tags'] != " " and loadedChar['indiv_tags'] != None:
            self.tags.setText(loadedChar['indiv_tags'])
        mainLayout.addWidget(self.tags)

        label = QLabel("notes")
        mainLayout.addWidget(label)

        self.notes = TextEdit()
        if loadedChar['indiv_notes'] != " " and loadedChar['indiv_notes'] != None:
            self.notes.setText(loadedChar['indiv_notes'])
        elif notes != {}:
            self.notes.setText(notes["notes"])
        mainLayout.addWidget(self.notes)

        buttonLayout = QHBoxLayout()
        mainLayout.addLayout(buttonLayout)

        cancelButton = QPushButton("cancel")
        cancelButton.clicked.connect(self.cancel)
        buttonLayout.addWidget(cancelButton)

        applyButton = QPushButton("Apply changes")
        applyButton.clicked.connect(self.apply)
        buttonLayout.addWidget(applyButton)

        # sidebar
        sidebarLayout = QVBoxLayout()
        cenLayout.addLayout(sidebarLayout, stretch=1)

        if self.new:
            random = QPushButton('random NPC')
            random.clicked.connect(self.man_randomNPC)
            sidebarLayout.addWidget(random)

        self.newFamily = False

    def man_randomNPC(self):
        """creates random name and family, if family_name already existent inserts the NPC into family

        :return: ->None
        """
        char = randomChar()

        family_Bib = ex.searchFactory(char['family_Name'], 'Families')

        if family_Bib == []:
            family_ID = ex.newFactory('Families', {'family_Name': char['family_Name']})

            if self.newFamily == False:
                self.newFamily = [family_ID]
            else:
                self.newFamily.append(family_ID)
        else:
            family_ID = family_Bib[0][0]

        self.family_Name.setText(char['family_Name'])
        self.fName.setText(char['indiv_fName'])
        self.family_id = family_ID
        self.familyMembers.resultUpdate(
            ex.searchFactory(str(self.family_id), 'Individuals', attributes=['fKey_family_ID'], shortOut=True))

    def man_newFamily(self):
        """opens a dialog to create a new family

        :return: ->None
        """
        self.dialog2 = QDialog()
        dLay = QVBoxLayout()
        self.dialog2.setLayout(dLay)

        label = QLabel('insert new Family Name:')
        dLay.addWidget(label)

        lineEdit = QLineEdit()
        dLay.addWidget(lineEdit)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)

        buttonBox.accepted.connect(self.dialog2.accept)
        buttonBox.rejected.connect(self.dialog2.reject)
        dLay.addWidget(buttonBox)

        if self.dialog2.exec_():
            newName = lineEdit.text()

            self.family_id = ex.newFactory('Families', {'family_Name': newName})
            self.family_Name.setText(newName)
            self.familyMembers.resultUpdate(
                ex.searchFactory(str(self.family_id), 'Individuals', attributes=['fkey_family_ID'], shortOut=True))

    def man_selFamily(self):
        """opens a dialog to choose an existing family and updates the family member widget

        :return: ->None
        """

        dialog = DialogEditItem([(self.family_id, self.family_Name.text())], maximumItems=1)
        dialog.setSource(lambda x=None: ex.searchFactory(x, library='Families', searchFulltext=True), 'Families')
        if dialog.exec_() and len(dialog.getNewItems()) > 0:
            family = dialog.getNewItems()[0]
            self.family_id = family[0]
            self.family_Name.setText(family[1])
            self.familyMembers.resultUpdate(
                ex.searchFactory(str(self.family_id), 'Individuals', shortOut=True, attributes=['fKey_family_ID']))

    def cancel(self):
        """cancels the current edit and deletes the corresponding individual and family dataset if they were newly created

        :param id: the id of the current NPC
        :return:
        """
        id = self.id
        if self.new:
            ex.deleteFactory(id, 'Individuals')

            if not self.newFamily == False:
                for id in self.newFamily:
                    ex.deleteFactory(id, 'Families')
        if self.onDecline != None:
            self.onDecline()
        self.exitFunc()

    def apply(self):
        """updates the current individuals data and deletes families that were created unnecessary

        :param id: int, id of npc
        :return:
        """
        id = self.id
        if self.new:
            if not self.newFamily == False:
                for id in self.newFamily:
                    if id != self.family_id:
                        ex.deleteFactory(id, 'Families')

        oldValues = ex.getFactory(id, "Individuals", defaultOutput=True, dictOut=True)
        # save fName
        text = self.fName.text().strip(" ")
        if text != oldValues['indiv_fName']:
            if text == None or text == "":
                text = 'No forename'
            ex.updateFactory(id, [text], 'Individuals', ['indiv_fName'])

        # save family_Name
        text = self.family_Name.text()
        family_id = self.family_id
        if text != oldValues["family_Name"]:
            ex.updateFactory(id, [family_id], 'Individuals', ['fKey_family_ID'])

        # save character_sex
        text = "male"
        if self.sex_female.isChecked():
            text = "female"
        if text != oldValues["indiv_sex"]:
            ex.updateFactory(id, [text], 'Individuals', ['indiv_sex'])

        # save title
        text = self.title.text().strip(" ")
        if text != oldValues["indiv_title"]:
            if text == None or text == "":
                text = 'No title'
            ex.updateFactory(id, [text], 'Individuals', ['indiv_title'])

        # save tags
        text = self.tags.text().strip(" ")
        if text != oldValues["indiv_tags"]:
            if text == None or text == "":
                text = 'No tags'
            ex.updateFactory(id, [text], 'Individuals', ['indiv_tags'])

        # save notes
        text = self.notes.toHtml().strip(" ")
        if text != oldValues["indiv_notes"]:
            if text == None or text == "":
                text = 'No Notes'
            ex.updateFactory(id, [text], 'Individuals', ['indiv_notes'])

        if self.onApply != None:
            self.onApply()
        self.exitFunc()

    def setExit(self, exitFunc, onApply=None, onDecline=None):
        """defines the behavior if the EventEditWindow is closed

        :param exitFunc: function, not called
        :param onApply: function, not called, optional
        :param onDecline: function, not called, optional
        :return: ->None
        """
        self.exitFunc = exitFunc
        self.onApply = onApply
        self.onDecline = onDecline

    def returnID(self):
        """returns the current npcs id

        :return: ->int
        """
        return self.id


class SessionEditWindow(QWidget):
    """Site widget to manage the contents of any session

    """

    def __init__(self, id, new=False, notes={}):
        """initializes the widgets content layout

        :param id: int, id of the session in database
        :param new: bool, optional, set true the session is treated as not existing event
        :param notes: first note draft for shortnotes
        """
        super().__init__()

        self.id=id
        self.new=new

        if self.new:
            self.id=ex.newFactory("Sessions")

        cenLayout = QHBoxLayout()
        self.setLayout(cenLayout)

        # Mainroom
        mainLayout = QVBoxLayout()
        cenLayout.addLayout(mainLayout, stretch=8)

        active_session= ex.getFactory(self.id,'Sessions',dictOut=True)
        self.title = QLineEdit()
        if active_session["session_Name"] != " " and active_session["session_Name"] != None:
            self.title.setText(active_session["session_Name"])
        mainLayout.addWidget(self.title)

        self.notes = TextEdit()
        if active_session["session_notes"] != " " and active_session["session_notes"] != None:
            self.notes.setText(active_session["session_notes"])
        elif notes is not None and notes!={}:
            self.notes.setText(notes["notes"])
        mainLayout.addWidget(self.notes)

        buttonLayout = QHBoxLayout()
        mainLayout.addLayout(buttonLayout)

        cancelButton = QPushButton("cancel")
        cancelButton.clicked.connect(lambda: self.cancel(self.id))
        buttonLayout.addWidget(cancelButton)

        applyButton = QPushButton("Apply changes")
        applyButton.clicked.connect(lambda: self.apply(self.id))
        buttonLayout.addWidget(applyButton)

        # sidebar
        sidebarLayout = QVBoxLayout()
        cenLayout.addLayout(sidebarLayout, stretch=1)

        self.setActiveBtn = QPushButton("make active Session")
        self.setActiveBtn.clicked.connect(lambda: self.setActiveBtn.setText("active Session"))
        if active_session["current_Session"]:
            self.setActiveBtn.setText("active Session")
        sidebarLayout.addWidget(self.setActiveBtn)

        if self.new:
            self.sessionScenes=[]
        else:
            self.sessionScenes = ex.searchFactory(str(self.id),'Events', attributes=['fKey_Session_ID'],
                                          output="Events.event_ID,Events.event_Title")

        self.result = Resultbox()
        self.result.setPref(col=1)
        self.result.resultUpdate(self.sessionScenes)
        sidebarLayout.addWidget(self.result)

        button = QPushButton("edit Session Scenes")
        button.clicked.connect(self.buttonclicked)
        sidebarLayout.addWidget(button)

        if self.new:
            self.sessionNPC=[]
        else:
            self.sessionNPC = ex.searchFactory(str(self.id),'Session_Individual_jnt', attributes=['fKey_session_ID'],
                                          shortOut=True,output="Individuals.individual_ID,Individuals.indiv_fName, Families.family_Name")

        self.result2 = Resultbox()
        self.result2.setPref(col=1)
        self.result2.resultUpdate(self.sessionNPC)
        sidebarLayout.addWidget(self.result2)

        button = QPushButton("edit Session NPCs")
        button.clicked.connect(self.buttonclicked2)
        sidebarLayout.addWidget(button)

    def cancel(self,id):
        """cancels the update of datasets and removes the temporary dataset if it was a new event

        :param id: int, id of the current event
        :return: ->None
        """
        if self.new:
            ex.deleteFactory(id, 'Sessions')
        if self.onDecline!=None:
            self.onDecline()
        self.exitFunc()

    def apply(self, id):
        """updates all changed data in database

        :param id: int, id of event
        :return: ->None
        """
        oldValues = ex.getFactory(id,'Sessions',dictOut=True)

        # save title
        text = self.title.text().strip(" ")
        if text != oldValues['session_Name']:
            ex.updateFactory(id, [text], 'Sessions', ['session_Name'])

        # save planned_date

        # save notes
        text = self.notes.toHtml().strip(" ")
        if text != oldValues['session_notes']:
            if text == None or text == "":
                text = 'No Notes'
            ex.updateFactory(id, [text], 'Sessions', ['session_notes'])

        pass

        # save Session NPC missing
        old_SessionNPC = ex.searchFactory(str(id), 'Session_Individual_jnt',output="Session_Individual_jnt.rowid,*", attributes=['fKey_session_ID'],
                                        dictOut=True,shortOut=True)
        old_SessionNPC_id = [x['fKey_individual_ID'] for x in old_SessionNPC]
        new_SessionNPC_id = [x[0] for x in self.sessionNPC]

        # adds new NPC-Session relationship to database and deletes already existing ones from old_session_scene_id, that is used for deletionbase lateron
        for new_id in new_SessionNPC_id:

            if new_id not in old_SessionNPC_id:
                ex.newFactory("Session_Individual_jnt", {"fKey_session_ID":id, "fKey_individual_ID":new_id})
            else:
                index = old_SessionNPC_id.index(new_id)
                old_SessionNPC.pop(index)
                old_SessionNPC_id.pop(index)

        # deletes NPC of Database that are not in session anymore
        for remove_NPC in old_SessionNPC:
            ex.deleteFactory(remove_NPC["rowid"], "Session_Individual_jnt")



        # save Session Scenes
        old_session_scene = ex.searchFactory(str(id), 'Events', output="*", attributes=['fKey_session_ID'],
                                             dictOut=True)
        old_session_scene_id = [x['event_ID'] for x in old_session_scene]
        new_session_scene_id = [x[0] for x in self.sessionScenes]

        # adds new NPC-Session relationship to database and deletes already existing ones from old_session_scene_id, that is used for deletionbase lateron
        for new_id in new_session_scene_id:

            if new_id not in old_session_scene_id:
                ex.updateFactory(new_id, [str(id)], "Events", ["fKey_session_ID"])
            else:
                index = old_session_scene_id.index(new_id)
                old_session_scene.pop(index)
                old_session_scene_id.pop(index)

        # deletes scenes of Database that are not in session anymore
        for remove_scene_id in old_session_scene_id:
            ex.updateFactory(remove_scene_id, [None], "Events", ["fKey_session_ID"])


        # save current active
        if self.setActiveBtn.text() == "active Session" and not oldValues['current_Session']:
            id2 = ex.searchFactory("1", 'Sessions', attributes=['current_Session'],dictOut=True)
            if len(id2) > 0:
                id2 = id2[0]['session_ID']
                ex.updateFactory(id2, ["0"], 'Sessions', attributes=['current_Session'])
            ex.updateFactory(id, ["1"], 'Sessions', attributes=['current_Session'])


        if self.onApply!=None:
            self.onApply()
        self.exitFunc()

    def setExit(self, exitFunc, onApply=None, onDecline=None):
        """defines the behavior if the EventEditWindow is closed

        :param exitFunc: function, not called
        :param onApply: function, not called, optional
        :param onDecline: function, not called, optional
        :return: ->None
        """
        self.exitFunc = exitFunc
        self.onApply = onApply
        self.onDecline = onDecline

    def buttonclicked(self):
        """opens a Dialog to manage sessions events and updates the corresponding database set and reloads resultbox

        :return: ->None
        """
        dialog = DialogEditItem(self.sessionScenes)
        dialog.setSource(lambda x:ex.searchFactory(x, library='Events', searchFulltext=True, shortOut=True),'Events')
        if dialog.exec_():
            self.sessionScenes = dialog.getNewItems()
            self.result.resultUpdate(self.sessionScenes)

    def buttonclicked2(self):
        """opens a Dialog to manage sessions NPC's and updates the corresponding database set and reloads resultbox

        :return: ->None
        """
        dialog = DialogEditItem(self.sessionNPC)
        dialog.setSource(lambda x:ex.searchFactory(x, library='Individuals', searchFulltext=True, shortOut=True),'Individuals')
        if dialog.exec_():
            self.sessionNPC = dialog.getNewItems()
            self.result2.resultUpdate(self.sessionNPC)

    def returnID(self):
        """returns id of event"""
        return self.id


class EventEditWindow(QWidget):
    """Site widget to manage the content of any event

    """

    def __init__(self, id, new=False, notes={}):
        """initializes the widgets content layout

        :param id: int, id of the event in database
        :param new: bool, optional, set true the event is treated as not existing event
        :param notes: first note draft for shortnotes
        """
        super().__init__()

        self.id = id
        self.new = new
        self.onApply=None
        self.onDecline=None
        self.exitFunc=None

        if self.new:
            self.id = ex.newFactory("Events")

        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.East)
        tabLay = QVBoxLayout()
        tabLay.addWidget(self.tabs)
        self.setLayout(tabLay)

        buttonLayout = QHBoxLayout()
        tabLay.addLayout(buttonLayout)

        cancelButton = QPushButton("cancel")
        cancelButton.clicked.connect(self.cancel)
        buttonLayout.addWidget(cancelButton)

        applyButton = QPushButton("Apply changes")
        applyButton.clicked.connect(self.apply)
        buttonLayout.addWidget(applyButton)

        mainWid = QWidget()
        cenLayout = QHBoxLayout()
        mainWid.setLayout(cenLayout)
        self.tabs.addTab(mainWid, "Infos")

        # Mainroom
        mainLayout = QVBoxLayout()
        cenLayout.addLayout(mainLayout, stretch=8)

        self.active_event = ex.getFactory(self.id, 'Events', dictOut=True)

        self.title = QLineEdit("No title set")
        if self.active_event["event_Title"] != " " and self.active_event["event_Title"] != None:
            self.title.setText(self.active_event["event_Title"])
        mainLayout.addWidget(self.title)

        self.date = QLineEdit("No date set")
        if self.active_event["event_Date"] != " " and self.active_event["event_Date"] != None:
            self.date.setText(self.active_event["event_Date"])
        mainLayout.addWidget(self.date)

        self.location = QLineEdit("No location set")
        if self.active_event["event_Location"] != " " and self.active_event["event_Location"] != None:
            self.location.setText(self.active_event["event_Location"])
        mainLayout.addWidget(self.location)

        self.short_des = TextEdit("no short_description set")
        if self.active_event["event_short_desc"] != " " and self.active_event["event_short_desc"] != None:
            self.short_des.setText(self.active_event["event_short_desc"])
        elif notes != {} and notes is not None:
            self.short_des.setText(notes["notes"])
        mainLayout.addWidget(self.short_des)

        self.long_des = TextEdit("no description set")
        if self.active_event["event_long_desc"] != " " and self.active_event["event_long_desc"] != None:
            self.long_des.setText(self.active_event["event_long_desc"])
        mainLayout.addWidget(self.long_des)

        # sidebar
        sidebarLayout = QVBoxLayout()
        cenLayout.addLayout(sidebarLayout, stretch=1)

        self.session = QLabel("related Session:")
        sidebarLayout.addWidget(self.session)

        self.setActiveBtn = QPushButton("no related Session set")
        self.setActiveBtn.clicked.connect(self.buttonclicked2)
        if self.active_event["fKey_Session_ID"]:
            session_data = ex.getFactory(self.active_event["fKey_Session_ID"], "Sessions", dictOut=True)
            self.setActiveBtn.setText(session_data["session_Name"])
        sidebarLayout.addWidget(self.setActiveBtn)

        self.eventNPC = []
        if not self.new:
            self.eventNPC = ex.searchFactory(str(self.id), 'Event_Individuals_jnt', attributes=['fKey_event_ID'],
                                             shortOut=True)

        self.result = Resultbox()
        self.result.setPref(col=1)
        self.result.resultUpdate(self.eventNPC)
        sidebarLayout.addWidget(self.result)

        button = QPushButton("edit Event NPC")
        button.clicked.connect(self.buttonclicked)
        sidebarLayout.addWidget(button)

        # fight tab
        self.fightPrep = FightPrep()
        self.tabs.addTab(self.fightPrep, "Kampf")

        if not self.new:
            self.eventFighter = ex.searchFactory(str(self.id), "Event_Fighter_jnt",
                                                 innerJoin="LEFT JOIN Fighter ON Event_Fighter_jnt.fKey_Fighter_ID=Fighter.Fighter_ID",
                                                 attributes=["fKey_Event_ID"], dictOut=True)
            for item in self.eventFighter:
                self.fightPrep.newFighter(item)

    def cancel(self):
        """cancels the update of datasets and removes the temporary dataset if it was a new event

        :param id: int, id of the current event
        :return: ->None
        """
        id = self.id
        if self.new:
            ex.deleteFactory(id, 'Events')
        if self.onDecline != None:
            self.onDecline()
        self.exitFunc()

    def apply(self):
        """updates all changed data in database

        :param id: int, id of event
        :return: ->None
        """
        for fighterID in set(self.fightPrep.deleteID):
            ex.deleteFactory(fighterID, "Fighter")

        for fighter in self.fightPrep.fighter:
            id = fighter["id"]
            name = fighter["name"].text()
            life = fighter["life"].text()
            ini = fighter["ini"].text()
            mana = fighter["mana"].text()
            karma = fighter["karma"].text()

            dict = {"Fighter_Name": name,
                    "Fighter_HP": life,
                    "Fighter_Mana": mana,
                    "Fighter_Karma": karma,
                    "Fighter_Initiative": ini}

            if id == "new":
                id = ex.newFactory("Fighter", data=dict)
                ex.newFactory("Event_Fighter_jnt", data={"fKey_Fighter_ID": id, "fKey_Event_ID": self.id})
            else:
                ex.updateFactory(id, [name, life, mana, karma, ini], "Fighter", dict.keys())

        id = self.id
        oldValues = ex.getFactory(id, 'Events', dictOut=True)
        # save title
        text = self.title.text().strip(" ")
        if text != oldValues['event_Title'] and text != "No title set":
            ex.updateFactory(id, [text], 'Events', ['event_Title'])

        # save date
        text = self.date.text().strip(" ")
        if text != oldValues['event_Date'] and text != "No date set":
            ex.updateFactory(id, [text], 'Events', ['event_Date'])

        # save location
        text = self.location.text().strip(" ")
        if text != oldValues['event_Location'] and text != "No location set":
            ex.updateFactory(id, [text], 'Events', ['event_Location'])

        # save related Session
        if self.active_event["fKey_Session_ID"] != oldValues["fKey_Session_ID"]:
            ex.updateFactory(id, [self.active_event["fKey_Session_ID"]], 'Events', ["fKey_Session_ID"])

        # save short desc
        text = self.short_des.toHtml().strip(" ")
        if text != oldValues['event_short_desc'] and text != "no short_description set":
            ex.updateFactory(id, [text], 'Events', ['event_short_desc'])

        # save long descr
        text = self.long_des.toHtml().strip(" ")
        if text != oldValues['event_long_desc'] and text != "no description set":
            ex.updateFactory(id, [text], 'Events', ['event_long_desc'])

        # save Scene NPC
        old_eventNPC = ex.searchFactory(id, "Event_Individuals_jnt", attributes=["fKey_event_ID"],
                                        output="Individuals.individual_ID", shortOut=True, dictOut=True)
        old_eventNPC_id = [x['individual_ID'] for x in old_eventNPC]
        new_eventNPC_id = [x[0] for x in self.eventNPC]

        # adds new NPC-Session relationship to database and deletes already existing ones from old_session_scene_id, that is used for deletionbase lateron
        for new_id in new_eventNPC_id:

            if new_id not in old_eventNPC_id:
                ex.newFactory("Event_Individuals_jnt", {"fKey_event_ID": str(id), "fKey_individual_ID": new_id})
            else:
                index = old_eventNPC_id.index(new_id)
                old_eventNPC.pop(index)
                old_eventNPC_id.pop(index)

        # deletes NPC of Database that are not in session anymore
        for remove_NPC in old_eventNPC:
            rowid = ex.searchFactory(remove_NPC["individual_ID"], "Event_Individuals_jnt", output="fKey_individual_ID",
                                     Filter=[{"key":"fKey_event_ID", "text":id, "fullTextSearch": False}])
            ex.deleteFactory(rowid[0][0], "Event_Individuals_jnt")

        if self.onApply != None:
            self.onApply()
        self.exitFunc()

    def setExit(self, exitFunc, onApply=None, onDecline=None):
        """defines the behavior if the EventEditWindow is closed

        :param exitFunc: function, not called
        :param onApply: function, not called, optional
        :param onDecline: function, not called, optional
        :return: ->None
        """
        self.exitFunc = exitFunc
        self.onApply = onApply
        self.onDecline = onDecline

    def buttonclicked(self):
        """opens a Dialog to manage event Npc's and updates the corresponding database set and reloads resultbox

        :return: ->None
        """

        dialog = DialogEditItem(self.eventNPC)
        dialog.setSource(lambda x: ex.searchFactory(x, library='Individuals', searchFulltext=True, shortOut=True),
                         'Individuals')
        if dialog.exec_():
            self.eventNPC = dialog.getNewItems()
            self.result.resultUpdate(self.eventNPC)

    def buttonclicked2(self):
        """opens a dialog to select the session to be assigned to

        :return: ->None
        """
        if self.new or self.active_event["fKey_Session_ID"] == None:
            dialog = DialogEditItem([], maximumItems=1)
        else:
            oldSession = ex.getFactory(self.active_event["fKey_Session_ID"], "Sessions", shortOutput=True, dictOut=True)
            dialog = DialogEditItem([(oldSession["session_ID"], oldSession["session_Name"])], maximumItems=1)
        dialog.setSource(lambda x: ex.searchFactory(x, library='Sessions', searchFulltext=True, shortOut=True),
                         'Sessions')

        if dialog.exec_():
            self.active_event["fKey_Session_ID"] = dialog.getNewItems()[0][0]
            self.setActiveBtn.setText(dialog.getNewItems()[0][1])

    def returnID(self):
        """returns id of event"""
        return self.id
