from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QStackedWidget, QScrollArea, QFrame, QLabel

import DB_Access as ex

from UI_Browser import Resultbox
from UI_Utility import FightChar, CustTextBrowser


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