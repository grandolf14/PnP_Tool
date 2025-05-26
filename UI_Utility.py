from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QPainter, QBrush, QPen, QColor, QIntValidator, QTextCursor
from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout, QMenu, QAction, QDialogButtonBox, QTextBrowser, QLabel, \
                            QHBoxLayout, QLineEdit, QMessageBox, QVBoxLayout, QDialog, QTextEdit

import DB_Access as ex

from AppVar import DataStore, InternVar as InVar
from Models import CustomDate, randomChar
from UI_Browser import Resultbox


class DialogEditItem(QDialog):
    """dialog to manage linked data collections

    """

    def __init__(self, sourceAdded=[],maximumItems=None):
        """initializes the dialog and opens it

        :param sourceAdded: list of tuples, optional containing the id and the text description [i.e. name] of already
            added items
        :param maximumItems: int, optional, maximum number of items that can be selected
        """
        super().__init__()

        self.maximumItems=maximumItems
        self.addedItems = sourceAdded
        self.timer = QTimer()

        self.searchbar = QLineEdit()

        layout = QVBoxLayout()
        self.setLayout(layout)

        label = QLabel("added items")
        layout.addWidget(label)

        self.added = Resultbox()
        self.added.setPref(buttonList=[("remove item", self.removeItem)], col=1)
        if self.addedItems is not []:
            self.added.resultUpdate(self.addedItems)
        layout.addWidget(self.added)

        self.searchbar.textChanged.connect(lambda: self.timer_start())
        layout.addWidget(self.searchbar)

        self.searchResult = Resultbox()
        self.searchResult.setPref(buttonList=[("add item", self.addItem)], col=1)
        layout.addWidget(self.searchResult)

        butLay = QHBoxLayout()
        layout.addLayout(butLay)

        apply = QPushButton("Apply changes")
        apply.clicked.connect(self.accept)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)

        butLay.addWidget(apply)
        butLay.addWidget(cancel)

        self.timer.singleShot(100, lambda:self.searchbar.setFocus())
        self.timer_start()

    def removeItem(self):
        """removes selected item from self.added resultbox

        :return: ->None
        """
        id = self.sender().page
        for item in self.addedItems:
            if item[0] == id:
                self.addedItems.remove(item)
                break
        self.added.resultUpdate(self.addedItems)
        return

    def addItem(self):
        """adds selected item to self.added resultbox, opens warning if the number of added items exceeds maximumItems

        :return:  ->None
        """
        id = self.sender().page
        item = ex.getFactory(id, self.pool, shortOutput=True)
        if self.maximumItems == 1:
            self.addedItems = [item]

        elif self.maximumItems is not None and len(self.addedItems)>self.maximumItems-1:
            self.message=QMessageBox()
            self.message.setText('You have more than the limit of %i items selected, please remove at least one item before adding new ones.'%(self.maximumItems))
            self.message.show()
            return

        elif id not in [x[0] for x in self.addedItems]:
            self.addedItems.append(item)

        self.added.resultUpdate(self.addedItems)
        return

    def timer_start(self):
        """starts timer after the searchbar is changed, if the searchbar does not change for 1 second calls for
            resultbox update

        :return: ->None
        """
        self.timerMark = True
        self.timer.stop()
        self.timer.timeout.connect(self.searchbarChanged)
        self.timer.start(1000)

    def searchbarChanged(self):
        """initializes search if it is the first timer signal coming through

        :return: ->None
        """
        self.timer.stop()
        if self.timerMark:
            if self.searchbar.text() == None:
                text = ""
            else:
                text = self.searchbar.text()

            self.searchResult.resultUpdate(self.source(text))
            self.timerMark = False

        return

    def setSource(self, source,pool):  # source list or source Function
        """specifies where the

        :param source: function to generate data list with input param (text), typically lambda x. ex.searchFactory(x,...)
        :param pool: str, table name for all selectable items
        :return: ->None
        """
        self.source = source
        self.pool=pool
        self.searchResult.resultUpdate(self.source(""))


    def getNewItems(self):
        """returns all selected items of the dialog"""
        return self.addedItems


class DialogRandomNPC(QDialog):
    """Dialog to create a npc with random name and family or custom addition

    """
    def __init__(self,exitfunc=None):
        """initializes dialog and randomly select name and family name, if there is already a family with selected name
            allows their selection and the search of specific families

        :param exitfunc: function, not called, optional
        """
        self.exitFunc = exitfunc
        self.timer=QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(lambda:self.existing_families.resultUpdate(ex.searchFactory(self.family.text(),'Families',searchFulltext=True)))


        super().__init__()
        layout=QVBoxLayout()
        self.setLayout(layout)



        char=randomChar()

        self.fName= QLineEdit()
        self.fName.setText(char['indiv_fName'])
        layout.addWidget(self.fName)

        self.familyID = None
        self.sex=char['indiv_sex'][0]

        self.family=QLineEdit()
        self.family.setText(char['family_Name'])
        self.family.textEdited.connect(lambda :self.family.setStyleSheet("color: black"))
        self.family.textEdited.connect(lambda : self.timer.start(1000))
        layout.addWidget(self.family)


        self.existing_families=Resultbox()
        self.existing_families.setPref(standardbutton=self.save_family_id ,col=1,spacer=False)
        self.existing_families.resultUpdate(ex.searchFactory(char['family_Name'],'Families'))
        layout.addWidget(self.existing_families)

        self.family_members=Resultbox()
        self.family_members.setPref(col=1,spacer=False,paintItemFrame=True)
        layout.addWidget(self.family_members)

        self.title=QLineEdit()
        self.title.setText("no Title")
        layout.addWidget(self.title)

        self.notes = QTextEdit()
        self.notes.setText('no Notes')
        layout.addWidget(self.notes)

        layoutHB = QHBoxLayout()
        layout.addLayout(layoutHB)

        new= QPushButton('new generation')
        new.clicked.connect(self.new)
        layoutHB.addWidget(new)

        cancel=QPushButton('cancel')
        cancel.clicked.connect(self.cancel)
        layoutHB.addWidget(cancel)

        save = QPushButton('save')
        save.clicked.connect(self.save)
        layoutHB.addWidget(save)

    def new(self):
        """reloads the random generation

        :return: ->None
        """
        char = randomChar()
        self.familyID=None
        self.family.setText(char['family_Name'])
        self.family.setStyleSheet('Color: black')
        self.fName.setText(char['indiv_fName'])
        self.sex=char['indiv_sex'][0]
        self.existing_families.resultUpdate(ex.searchFactory(char['family_Name'],'Families'))
        self.family_members.resultUpdate([])

    def save_family_id(self):
        """loads the selected families members

        :return: ->None
        """
        self.familyID=self.sender().page
        family=ex.getFactory(str(self.familyID),'Families')

        self.family.setStyleSheet("color: gray")
        if len(family)>0:
            self.family.setText(family[1])
        self.family_members.resultUpdate(ex.searchFactory(str(self.familyID), 'Individuals',attributes=['fKey_family_ID'], shortOut=True))

    def cancel(self):
        """cancels the random characters generation

        :return: ->None
        """
        self.reject()
        self.close()
        self.exitFunc()

    def save(self):
        """saves random character

        :return:
        """
        if self.familyID !=None:
            if ex.getFactory(self.familyID, 'Families') [1] != self.family.text():
                familyID=ex.newFactory('Families',{'family_Name':self.family.text()})
            else:
                familyID=self.familyID
        else:
            familyID = ex.newFactory('Families',{'family_Name':self.family.text()})

        title=self.title.text()
        if title== "no Title":
            title=""

        notes= self.notes.toPlainText()
        if notes =='no Notes':
            notes=""

        Char_id=ex.newFactory('Individuals',{'indiv_fName':self.fName.text(),'fKey_family_ID':familyID,'indiv_title':title,'indiv_notes':notes, 'indiv_unchecked':True, 'indiv_sex':self.sex})

        current_session = ex.searchFactory("1", 'Sessions', attributes=['current_Session'],dictOut=True)[0]

        if current_session != []:
            ex.newFactory('Session_Individual_jnt', data={'fKey_session_ID':current_session['session_ID'],'fKey_individual_ID':Char_id})

        self.accept()
        self.close()
        self.exitFunc()

class CustTextBrowser(QTextBrowser):
    """QTextBrowser subclass for in-session rederecting on anchor on_click

    """

    def mousePressEvent(self, e):
        """sets self.link on the anchor content at mousePress location, if any anchor exists

        :param e: event
        :return:
        """
        self.link = self.anchorAt(e.pos())

    def mouseReleaseEvent(self, e):
        """on mouse release calls openFunctions to view the linked contentset or in case of a date to show an infobox
        with the timedifference from today

        :param e: event
        :return: ->None
        """
        if self.link:
            self.link=self.link.split(":")

            if self.link[0]=="Individuals":
                InVar.mainWin.load_ses_NpcInfo(custId=self.link[1])
            if self.link[0]=="Sessions":
                InVar.mainWin.btn_ses_openPlot(id=self.link[1])
            if self.link[0]=="Events":
                InVar.mainWin.btn_ses_openScene(id=self.link[1])
            if self.link[0]=="Date":
                today=DataStore.today
                date=CustomDate(self.link[1])
                dif=CustomDate.difference(today,date)
                InVar.mainWin.openInfoBox(dif, delay=5000)
            self.link = None

class TextEdit (QTextEdit):
    """QTextEdit Overwrite for default implementation of html internal link building.

    QTextEdit reimplement now allows to open a insert link Menu via Contextmenu or "@" keystroke. The following menu
    allows to choose which type of Data the link should reference and to choose the dataset.
    """

    def keyPressEvent(self, e):
        """reimplements QTextedit method keyPressEvent and on @-keystroke opens the link-menu to choose data type

        :param e: QKeypressEvent
        :return: ->None
        """
        if e.key()==64:
            self.linkMenu()
            return

        super().keyPressEvent(e)

    def contextMenuEvent(self, e):
        """Added option "insert link" to standard context menu and executes menu

        :param e: QContextMenuEvent
        :return: ->None
        """
        menu=self.createStandardContextMenu(e.globalPos())
        insertLink=QAction("Insert link")
        insertLink.triggered.connect(self.linkMenu)
        menu.addAction(insertLink)
        menu.exec(e.globalPos())

    def linkMenu(self):
        """opens a menu to choose the type of dataset (character, session, event, date) to link to

        :return: ->None
        """
        menu = QMenu()

        char = QAction("Character &C")
        char.triggered.connect(lambda: self.openDialog("Individuals"))
        menu.addAction(char)

        event = QAction("Event &E")
        event.triggered.connect(lambda: self.openDialog("Events"))
        menu.addAction(event)

        ses = QAction("Session &S")
        ses.triggered.connect(lambda: self.openDialog("Sessions"))
        menu.addAction(ses)

        date= QAction("Date &D")
        date.triggered.connect(lambda:self.dateDialog())
        menu.addAction(date)

        menu.exec(self.cursor().pos())

    def dateDialog(self, date=None):
        """opens a dialog to insert a date and validate it. On succeeds build html code and insert it into the TextEdit

        :param date: ex.CurstomDate object, optional
        :return: ->None
        """
        dialog = QDialog()

        dialogLay = QVBoxLayout()
        dialog.setLayout(dialogLay)

        dateLineEdit = QLineEdit()
        dateLineEdit.setText("Insert date")
        dialogLay.addWidget(dateLineEdit)

        buttonbox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttonbox.accepted.connect(dialog.accept)
        buttonbox.rejected.connect(dialog.reject)

        dialogLay.addWidget(buttonbox)

        if dialog.exec_():
            rawDate=dateLineEdit.text()
            date = ex.CustomDate(rawDate)

            if not CustomDate.date_validation(date, checkOnly=True):
                dialog2 = QDialog()
                dialog2Lay = QVBoxLayout()
                dialog2.setLayout(dialog2Lay)

                dialog2Lay.addWidget(QLabel("Date exceeded calendar conventions. Is this the date you want? \n" + str(
                    CustomDate.date_validation(date))))

                d2Buttonbox = QDialogButtonBox(QDialogButtonBox.Apply | QDialogButtonBox.Cancel)
                d2Buttonbox.accepted.connect(dialog2.accept)
                d2Buttonbox.rejected.connect(dialog2.reject)
                dialog2Lay.addWidget(d2Buttonbox)

                if not dialog2.exec_():
                    self.dateDialog(date)
                    return


            #build html
            self.insertPlainText(" ")
            self.moveCursor(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.MoveAnchor)
            text = '<a href="Date:' + rawDate + '">' + str(date)+'</a>'
            self.insertHtml(text)
            self.moveCursor(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor)
            return

    def openDialog(self,library):
        """opens a DialogEditItem to choose the linked dataset, builds and inserts the html into the textEdit

        :param library: the library to search in
        :return: ->None
        """

        searchdialog = DialogEditItem(maximumItems=1)
        source=lambda x: ex.searchFactory(x, library=library, searchFulltext=True, shortOut=True)
        searchdialog.setSource(source, library)
        if searchdialog.exec():
            character = searchdialog.getNewItems()[0][1]
            if library=="Individuals":
                character+=" "+searchdialog.getNewItems()[0][2]
            id = searchdialog.getNewItems()[0][0]

            self.insertPlainText(" ")
            self.moveCursor(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.MoveAnchor)
            text = '<a href="' + library + ":" + str(id) + '">' + character + '</a>'
            self.insertHtml(text)
            self.moveCursor(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor)

        return


class FightChar(QWidget):
    """widget to show and to manage a combatants stats.

    :signal: charInactive: pyqt-signal, emitted when the character loses its active-state i.e. when he dies
    :signal: charActive: pyqt-signal, emitted when the character regains his active-state i.e. he wakes up
    :signal: initiativeChanged: pyqt-signal, emitted when the initiative of the character was changed """

    charInactive=pyqtSignal()
    charActive=pyqtSignal()
    initiativeChanged=pyqtSignal()

    def __init__(self,lifeMax:int,lifeCurr:int,name:str,ini:int,manaMax:int=None,manaCurr:int=None,karmaMax:int=None,karmaCurr:int=None)->None:
        """initiaizes the FightChars defaultvalues and the Layout for the FightChar Widget

        :param lifeMax: int, the maximum healthpoint value
        :param lifeCurr: int, the current healthpoint value, 0<=lifeCurr<= lifeMax
        :param name: str, the name of the FightChar
        :param ini: int, the initiative, the value to sort the characters action order in fight descending
        :param manaMax: int, the maximum manapoints value
        :param manaCurr: int, the current manapoints value, 0<= manaCurr<= manaMax
        :param karmaMax: int, the maximum karmapoints value
        :param karmaCurr: int, the current karmapoints value, 0<=karmaCurr<=karmaMax

        """
        super().__init__()
        self.name=name
        self.lifeMax=lifeMax
        self.lifeCurr=lifeCurr
        self.manaMax=manaMax
        self.manaCurr=manaCurr
        self.karmaMax=karmaMax
        self.karmaCurr=karmaCurr
        self.active=True
        self.initiative=ini

        grid = QGridLayout()
        grid.setColumnStretch(0, 20)
        grid.setColumnStretch(2, 2)
        grid.setColumnStretch(3,2)
        grid.setColumnStretch(4, 76)
        self.setLayout(grid)

        self.nameLbl=QLabel(self.name)
        grid.addWidget(self.nameLbl,0,0)


        self.lifeBar = RessourceBar(lifeMax, lifeCurr)
        grid.addWidget(self.lifeBar, 1, 0)

        self.lifeLabel = QLabel("Lebenspunkte: " + str(self.lifeBar.value()))
        self.lifeBar.valueChanged.connect(lambda: self.lifeLabel.setText("Lebenspunkte: " + str(self.lifeBar.value())))
        grid.addWidget(self.lifeLabel, 1, 1)

        self.lifeEdit = QLineEdit()
        self.lifeEdit.setValidator(QIntValidator(1,10000))
        self.lifeEdit.returnPressed.connect(self.lifeChange)
        grid.addWidget(self.lifeEdit,1, 2)

        self.lifePlus=QPushButton("heilen")
        self.lifePlus.clicked.connect(lambda: self.lifeChange(heal=True))
        grid.addWidget(self.lifePlus,1,3)

        if self.manaMax is not None and self.manaMax!=0:
            self.manaBar = RessourceBar(manaMax, manaCurr)
            self.manaBar.setColor(QColor(29, 147, 207))
            grid.addWidget(self.manaBar, 2, 0)

            self.manalabel = QLabel("Astralpunkte: " + str(self.manaBar.value()))
            self.manaBar.valueChanged.connect(lambda: self.manalabel.setText("Astralpunkte: " + str(self.manaBar.value())))
            grid.addWidget(self.manalabel, 2, 1)

            self.manaEdit = QLineEdit()
            self.manaEdit.setValidator(QIntValidator(-10000000, 10000000))
            self.manaEdit.returnPressed.connect(self.manaChange)
            grid.addWidget(self.manaEdit, 2, 2)

            self.manaPlus = QPushButton("Regenerieren")
            self.manaPlus.clicked.connect(lambda: self.manaChange(heal=True))
            grid.addWidget(self.manaPlus, 2, 3)

        if karmaMax is not None and self.karmaMax!=0:
            self.karmaBar = RessourceBar(karmaMax, karmaCurr)
            self.karmaBar.setColor(QColor(245, 233, 140))
            grid.addWidget(self.karmaBar,3, 0)

            self.karmalabel = QLabel("Karmalpunkte: " + str(self.karmaBar.value()))
            self.karmaBar.valueChanged.connect(lambda: self.karmalabel.setText("Karmalpunkte: " + str(self.karmaBar.value())))
            grid.addWidget(self.karmalabel, 3, 1)

            self.karmaEdit = QLineEdit()
            self.karmaEdit.setValidator(QIntValidator(-10000000, 10000000))
            self.karmaEdit.returnPressed.connect(self.karmaChange)
            grid.addWidget(self.karmaEdit, 3, 2)

            self.karmaPlus = QPushButton("Regenerieren")
            self.karmaPlus.clicked.connect(lambda: self.karmaChange(heal=True))
            grid.addWidget(self.karmaPlus, 3, 3)

        self.setMinimumSize(self.width(),self.sizeHint().height()*2)

    def setInitiative(self,initiative:int)->None:
        """setter, sets initiative to new value, emits initiativeChanged signal if the new initiative does not match the old

        :param initiative: int, value to set the initiative to
        """
        if initiative!= self.initiative:
            self.initiative=initiative
            self.initiativeChanged.emit()
        return

    def lifeChange(self,heal=False):
        """substracts the value of self.lifeEdit.text() from the current healthpoints
        :param heal: bool, optional, if True the value of self.lifeEdit.text() is added to the lifebar instead of substracted
        """
        if self.lifeEdit.text() =="":
            return

        if heal:
            if self.lifeBar.value()==0:
                self.active = True
                self.nameLbl.setText(self.name)
                self.charActive.emit()
                self.initiativeChanged.emit()

            if self.lifeBar.value()+int(self.lifeEdit.text())<self.lifeMax:
                self.lifeBar.setValue(self.lifeBar.value() + int(self.lifeEdit.text()))
            else:
                self.lifeBar.setValue(self.lifeMax)
            self.lifeEdit.clear()

        elif int(self.lifeEdit.text())<self.lifeBar.value():
            self.lifeBar.setValue(self.lifeBar.value()-int(self.lifeEdit.text()))
            self.lifeEdit.clear()
        else:
            self.active = False
            self.lifeBar.setValue(0)
            self.charInactive.emit()
            self.initiativeChanged.emit()
            self.nameLbl.setText(self.name+" (tot)")
            self.lifeEdit.clear()


    def manaChange(self, heal=False):
        """substracts the value of self.manaEdit.text() from the current manapoints
        :param heal: bool, optional, if True the value of self.lifeEdit.text() is added to the manabar instead of substracted
        """
        if self.manaEdit.text =="":
            return
        if heal:
            if self.manaBar.value()+int(self.manaEdit.text())<self.manaMax:
                self.manaBar.setValue(self.manaBar.value() + int(self.manaEdit.text()))
            else:
                self.manaBar.setValue(self.manaMax)
            self.manaEdit.clear()

        elif int(self.manaEdit.text()) < self.manaBar.value():
            self.manaBar.setValue(self.manaBar.value() - int(self.manaEdit.text()))
            self.manaEdit.clear()
        else:
            self.manaBar.setValue(0)
            self.manaEdit.clear()

    def karmaChange(self, heal=False):
        """substracts the value of self.lifeEdit.text() from the current kamrapoints
        :param heal: bool, optional, if True the value of self.lifeEdit.text() is added to the karmabar instead of substracted
        """
        if self.karmaEdit.text =="":
            return
        if heal:
            if self.karmaBar.value()+int(self.karmaEdit.text())<self.karmaMax:
                self.karmaBar.setValue(self.karmaBar.value() + int(self.karmaEdit.text()))
            else:
                self.karmaBar.setValue(self.karmaMax)
            self.karmaEdit.clear()

        elif int(self.karmaEdit.text()) < self.karmaBar.value():
            self.karmaBar.setValue(self.karmaBar.value() - int(self.karmaEdit.text()))
            self.karmaEdit.clear()
        else:
            self.karmaBar.setValue(0)
            self.karmaEdit.clear()


class RessourceBar(QWidget):
    """graphical representation as bar, showing the relative current resource availability from a maximum value

    """

    valueChanged= pyqtSignal()
    def __init__(self, maximum:int = 100, value = None)->None:
        super().__init__()

        self.maximum=maximum
        self.minimum=0

        self._value=value
        if value is None:
            self._value=maximum
        self.color= QColor(86,198,66)
        self.setFixedHeight(10)

        self.valueChanged.connect(self.update)
        return

    def setValue(self,value:int)->None:
        """setter, sets the current ressourcebar value to value and emits the valueChanged signal"""
        self._value=value
        self.valueChanged.emit()
        return

    def setColor(self, color:QColor)->None:
        """sets the color of the ressourcebar"""
        self.color=color
        return

    def value(self)->int:
        """getter, returns the value of the ressourcebar"""
        return self._value

    def progress(self)->float:
        """returns the progress relative to the maximumvalue of the ressourcebar"""
        return float(self._value/self.maximum)

    def paintEvent(self, event=None):
        """paints the ressourcebar widget"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        brush = QBrush()
        brush.setColor(QColor("lightGrey"))
        brush.setStyle(Qt.SolidPattern)
        rect = QtCore.QRect(1, 1, painter.device().width() - 2, painter.device().height() - 2)
        painter.fillRect(rect, brush)

        if self.value()>0:
            brush.setColor(self.color)
            rect = QtCore.QRect(1, 1, int(painter.device().width() * self.progress() - 2), painter.device().height() - 2)
            painter.fillRect(rect, brush)

        pen=QPen(Qt.SolidLine)
        pen.setColor(QColor("Grey"))
        painter.setPen(QColor("Grey"))
        painter.drawRoundedRect(QtCore.QRect(0,0,painter.device().width(), painter.device().height()),5,5)

        painter.end()