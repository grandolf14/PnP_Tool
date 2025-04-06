#vor Release alle comments mit !!release: beachten
#Character_sex fehl nach random Char als update function

import random
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize, Qt,QTimer,QEvent
from PyQt5.QtGui import QFont,QPainter,QBrush,QImage,QPixmap,QColor,QPicture,QTransform,QPen
from PyQt5.QtWidgets import QMainWindow, QLabel, QWidget, QPushButton, QHBoxLayout, QGridLayout, QLineEdit, QMessageBox, \
    QVBoxLayout, \
    QStackedWidget, QFileDialog, QTabWidget, QFormLayout, QTextEdit, QScrollArea, QDialog, QComboBox, QDialogButtonBox, QFrame,\
    QGraphicsScene,QGraphicsView, QGraphicsTextItem,QGraphicsDropShadowEffect, QRadioButton, QCheckBox, QTextBrowser
    

from datetime import  datetime, timedelta

import Executable as ex
import DataHandler as dh


class QTextEdit (QTextEdit):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.searchTracker=False

    def keyPressEvent(self, e):

        if self.searchTracker:
            if e.key()==Qt.Key_Return:
                #build html code
                self.searchTracker=False
            else:
                self.searchTracker+=e.text()
                super().keyPressEvent(e)
        else:

            if e.key()==64:
                self.searchTracker="@"

            super().keyPressEvent(e)







class CustTextBrowser(QTextBrowser):

    def mousePressEvent(self, e):
        self.link = self.anchorAt(e.pos())




    def mouseReleaseEvent(self, e):
        if self.link:
            self.link=self.link.split(":")
            if self.link[0]=="char":
                win.load_ses_NpcInfo(custId=self.link[1])
            if self.link[0]=="date":
                win.openInfoBox("4 wochen",delay=3000)
            self.link = None



class DataLabel(QLabel):

    def __init__(self, linked=None, *args, **kwargs, ):
        super().__init__(*args, **kwargs)
        self.linked = linked

        r = random.randint(0, 1)

        if self.linked!=None:
            self.setStyleSheet("color : blue")




    def setLink(self,text):
        self.linked=text
        r=random.randint(0,1)

        if self.linked!=None:
            self.setStyleSheet("color : blue")
        else:
            self.setStyleSheet("color : black")

        return

class Resultbox(QStackedWidget):

    def __init__(self):
        super().__init__()
        self.setPref()
        self.source = None
        self.resultUpdate()

    def setPref(self, reloadBottom=False, paintItemFrame=False, buttonList=None, spacer=True, paintLight:list=[None], standardbutton=None,standardButtonVerticalAlignment=True, ignoreIndex=[0], spacing=10, col=4):
        self.buttons = buttonList
        self.spacing = spacing
        self.col = col
        self.standardbutton=standardbutton
        self.standardButtonVerticalAlignment=standardButtonVerticalAlignment
        self.ignoreIndex=ignoreIndex
        self.paintLight=paintLight
        self.spacer=spacer
        self.reloadBottom=reloadBottom
        self.paintItemFrame=paintItemFrame

    def setSource(self, source):
        self.source = source

    def resultUpdate(self, manualResult=None):

        if manualResult is None:
            result = self.source
        else:
            result = manualResult

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        wid = QWidget()
        scroll.setWidget(wid)

        lay = QGridLayout()
        lay.setVerticalSpacing(20)
        lay.setHorizontalSpacing(20)
        wid.setLayout(lay)

        if result == None:
            self.addWidget(scroll)
            self.setCurrentWidget(scroll)
            return


        for itemIndex, item in enumerate(result):
            row = itemIndex % self.col
            col = itemIndex // self.col
            layout = QVBoxLayout()
            lay.addLayout(layout, col, row)
            layout.addStretch(30)

            if self.standardButtonVerticalAlignment:
                innerLayout =QVBoxLayout()
            else:
                innerLayout=QHBoxLayout()

            if self.standardbutton == None:
                if self.paintItemFrame:
                    frame=QFrame()
                    frame.setLayout(innerLayout)
                    layout.addWidget(frame)
                    frame.setLineWidth(1)
                    frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
                else:
                    layout.addLayout(innerLayout)

            else:
                mainButton = QPushButton()
                mainButton.setLayout(innerLayout)
                mainButton.page=item[0]
                mainButton.clicked.connect(self.standardbutton)
                layout.addWidget(mainButton, stretch=1)

            newtext=""
            for lineIndex, line in enumerate(item):
                if lineIndex in self.ignoreIndex:
                    continue


                text = line
                if type(line) is not str:
                    text = str(line)

                if not self.standardButtonVerticalAlignment:
                    newtext+=text+" "
                else:
                    label = QLabel(text)
                    innerLayout.addWidget(label)

                    if lineIndex in self.paintLight:
                        label.setStyleSheet('color: grey')
                        font=label.font()
                        font.setItalic(True)
                        label.setFont(font)

            if not self.standardButtonVerticalAlignment:
                if self.buttons==None:
                    mainButton.setText(newtext)
                else:
                    label = QLabel(newtext)
                    innerLayout.addWidget(label,alignment=Qt.AlignHCenter)

            if self.buttons is not None:
                for button in self.buttons:
                    pBut = QPushButton(button[0])
                    pBut.page = item[0]
                    pBut.clicked.connect(button[1])
                    innerLayout.addWidget(pBut)


            if self.standardbutton!= None and self.standardButtonVerticalAlignment:
                mainButton.setFixedHeight(innerLayout.minimumSize().height())

            layout.addStretch(30)

            if self.spacer:
                layout.addWidget(QLabel(""))

        widget= self.currentWidget()
        self.removeWidget(widget)

        self.addWidget(scroll)
        self.setCurrentWidget(scroll)

        if self.reloadBottom:
            vbar = scroll.verticalScrollBar()
            vbar.setValue(vbar.maximum())



class ViewNpc(QWidget):
    
    def __init__(self,id,standardButton=None):
        super().__init__()
        self.id=id
        self.standardButton=standardButton

        self.updateView()
        
    def updateView(self):
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)

        char = ex.getFactory(self.id,"Individuals", defaultOutput=True,dictOut=True)

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

        familyMembers = ex.searchFactory(str(char['fKey_family_ID']), 'Individuals',attributes=['fKey_family_ID'], shortOut=True)
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



class EventEditWindow(QWidget):

    def __init__(self, id, new=False, notes={}):
        super().__init__()

        self.id=id
        self.new=new

        if self.new:
            self.id=ex.newFactory("Events")

        cenLayout = QHBoxLayout()
        self.setLayout(cenLayout)

        # Mainroom
        mainLayout = QVBoxLayout()
        cenLayout.addLayout(mainLayout, stretch=8)

        self.active_event= ex.getFactory(self.id,'Events',dictOut=True)

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

        self.short_des = QTextEdit("no short_description set")
        if self.active_event["event_short_desc"] != " " and self.active_event["event_short_desc"] != None:
            self.short_des.setText(self.active_event["event_short_desc"])
        elif notes != {}:
            self.short_des.setText(notes["notes"])
        mainLayout.addWidget(self.short_des)

        self.long_des = QTextEdit("no description set")
        if self.active_event["event_long_desc"] != " " and self.active_event["event_long_desc"] != None:
            self.long_des.setText(self.active_event["event_long_desc"])
        mainLayout.addWidget(self.long_des)

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

        self.session=QLabel("related Session:")
        sidebarLayout.addWidget(self.session)

        self.setActiveBtn = QPushButton("no related Session set")
        self.setActiveBtn.clicked.connect(self.buttonclicked2)
        if self.active_event["fKey_Session_ID"]:
            session_data=ex.getFactory(self.active_event["fKey_Session_ID"],"Sessions",dictOut=True)
            self.setActiveBtn.setText(session_data["session_Name"])
        sidebarLayout.addWidget(self.setActiveBtn)

        self.eventNPC=[]
        if not self.new:
            self.eventNPC = ex.searchFactory(str(self.id),'Event_Individuals_jnt', attributes=['fKey_event_ID'],
                                          shortOut=True)

        self.result = Resultbox()
        self.result.setPref(col=1)
        self.result.resultUpdate(self.eventNPC)
        sidebarLayout.addWidget(self.result)

        button = QPushButton("edit Event NPC")
        button.clicked.connect(self.buttonclicked)
        sidebarLayout.addWidget(button)



    def cancel(self,id):
        if self.new:
            ex.deleteFactory(id, 'Events')
        if self.onDecline!=None:
            self.onDecline()
        self.exitFunc()


    def apply(self, id):

        oldValues = ex.getFactory(id,'Events',dictOut=True)
        # save title
        text = self.title.text().strip(" ")
        if text != oldValues['event_Title'] and text !="No title set":
            ex.updateFactory(id, [text], 'Events', ['event_Title'])


        # save date
        text = self.date.text().strip(" ")
        if text != oldValues['event_Date'] and text!="No date set":
            ex.updateFactory(id, [text], 'Events', ['event_Date'])


        # save location
        text = self.location.text().strip(" ")
        if text != oldValues['event_Location'] and text!="No location set":
            ex.updateFactory(id, [text], 'Events', ['event_Location'])

        #save related Session
        if self.active_event["fKey_Session_ID"] != oldValues["fKey_Session_ID"]:
            ex.updateFactory(id, [self.active_event["fKey_Session_ID"]], 'Events', ["fKey_Session_ID"])



        # save short desc
        text = self.short_des.toPlainText().strip(" ")
        if text != oldValues['event_short_desc'] and text != "no short_description set":
            ex.updateFactory(id, [text], 'Events', ['event_short_desc'])



        #save long descr
        text = self.long_des.toPlainText().strip(" ")
        if text != oldValues['event_long_desc'] and text != "no description set":
            ex.updateFactory(id, [text], 'Events', ['event_long_desc'])

        # save Scene NPC
        old_eventNPC = ex.searchFactory(id,"Event_Individuals_jnt",attributes=["fKey_event_ID"],
                                        output="Individuals.individual_ID",shortOut=True,dictOut=True)
        old_eventNPC_id = [x['individual_ID'] for x in old_eventNPC]
        new_eventNPC_id = [x[0] for x in self.eventNPC]

        # adds new NPC-Session relationship to database and deletes already existing ones from old_session_scene_id, that is used for deletionbase lateron
        for new_id in new_eventNPC_id:

            if new_id not in old_eventNPC_id:
                ex.newFactory("Event_Individuals_jnt", {"fKey_event_ID":str(id),"fKey_individual_ID":new_id})
            else:
                index = old_eventNPC_id.index(new_id)
                old_eventNPC.pop(index)
                old_eventNPC_id.pop(index)

        # deletes NPC of Database that are not in session anymore
        for remove_NPC in old_eventNPC:
            rowid=ex.searchFactory(remove_NPC["individual_ID"],"Event_Individuals_jnt",output="individual_ID",Filter={"fKey_event_ID":[id,False]})
            ex.deleteFactory(rowid[0][0],  "Event_Individuals_jnt")

        if self.onApply!=None:
            self.onApply()
        self.exitFunc()


    def setExit(self, exitFunc, onApply=None, onDecline=None):
        self.exitFunc = exitFunc
        self.onApply = onApply
        self.onDecline = onDecline

    def buttonclicked(self):

        dialog = DialogEditItem(self.eventNPC)
        dialog.setSource(lambda x:ex.searchFactory(x, library='Individuals', searchFulltext=True, shortOut=True),
                         'Individuals')
        if dialog.exec_():
            self.eventNPC = dialog.getNewItems()
            self.result.resultUpdate(self.eventNPC)

    def buttonclicked2(self):
        if self.new or self.active_event["fKey_Session_ID"]==None:
            dialog = DialogEditItem([],maximumItems=1)
        else:
            oldSession = ex.getFactory(self.active_event["fKey_Session_ID"], "Sessions", shortOutput=True, dictOut=True)
            dialog = DialogEditItem([(oldSession["session_ID"], oldSession["session_Name"])], maximumItems=1)
        dialog.setSource(lambda x:ex.searchFactory(x, library='Sessions', searchFulltext=True, shortOut=True),
                         'Sessions')

        if dialog.exec_():
            self.active_event["fKey_Session_ID"] = dialog.getNewItems()[0][0]
            self.setActiveBtn.setText(dialog.getNewItems()[0][1])

    def returnID(self):
        return self.id

        
class SessionEditWindow(QWidget):

    def __init__(self, id, new=False, notes={}):
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

        self.notes = QTextEdit()
        if active_session["session_notes"] != " " and active_session["session_notes"] != None:
            self.notes.setText(active_session["session_notes"])
        elif notes!={}:
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
        if self.new:
            ex.deleteFactory(id, 'Sessions')
        if self.onDecline!=None:
            self.onDecline()
        self.exitFunc()

    def apply(self, id):

        oldValues = ex.getFactory(id,'Sessions',dictOut=True)

        # save title
        text = self.title.text().strip(" ")
        if text != oldValues['session_Name']:
            ex.updateFactory(id, [text], 'Sessions', ['session_Name'])

        # save planned_date

        # save notes
        text = self.notes.toPlainText().strip(" ")
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
        self.exitFunc = exitFunc
        self.onApply = onApply
        self.onDecline = onDecline

    def buttonclicked(self):

        dialog = DialogEditItem(self.sessionScenes)
        dialog.setSource(lambda x:ex.searchFactory(x, library='Events', searchFulltext=True, shortOut=True),'Events')
        if dialog.exec_():
            self.sessionScenes = dialog.getNewItems()
            self.result.resultUpdate(self.sessionScenes)

    def buttonclicked2(self):

        dialog = DialogEditItem(self.sessionNPC)
        dialog.setSource(lambda x:ex.searchFactory(x, library='Individuals', searchFulltext=True, shortOut=True),'Individuals')
        if dialog.exec_():
            self.sessionNPC = dialog.getNewItems()
            self.result2.resultUpdate(self.sessionNPC)

    def returnID(self):
        return self.id

class NPCEditWindow(QWidget):

    def __init__(self, id, new=False, notes={}):
        super().__init__()

        self.id=id
        self.new=new

        if self.new:
            self.id=ex.newFactory('Individuals',{'indiv_fName':'@N€w Ch4r4ct€r','fKey_family_ID':ex.DataStore.defaultFamily})

        cenLayout = QHBoxLayout()
        self.setLayout(cenLayout)

        # Mainroom
        mainLayout = QVBoxLayout()
        cenLayout.addLayout(mainLayout, stretch=8)

        loadedChar= ex.getFactory(self.id,"Individuals", defaultOutput=True,dictOut=True)

        label=QLabel("forename")
        mainLayout.addWidget(label)

        self.fName = QLineEdit()
        if  loadedChar['indiv_fName'] != " " and loadedChar['indiv_fName'] != None:
            self.fName.setText(loadedChar['indiv_fName'])
        mainLayout.addWidget(self.fName)

        label = QLabel("family")
        mainLayout.addWidget(label)


        if  loadedChar['family_Name'] != " " and loadedChar['family_Name'] != None:
            self.family_Name = QLabel(loadedChar['family_Name'])
            mainLayout.addWidget(self.family_Name)

        hboxLayout=QHBoxLayout()
        mainLayout.addLayout(hboxLayout)
        self.family_Btn=QPushButton('set Family')
        if  loadedChar['family_Name'] != " " and loadedChar['family_Name'] != None:
            self.family_Btn.setText('change Family')
        self.family_Btn.clicked.connect(self.man_selFamily)
        hboxLayout.addWidget(self.family_Btn)

        self.family_new_Btn = QPushButton('new Family')
        self.family_new_Btn.clicked.connect(self.man_newFamily)
        hboxLayout.addWidget(self.family_new_Btn)

        self.family_id=loadedChar['fKey_family_ID']
        self.familyMembers=Resultbox()
        self.familyMembers.resultUpdate(ex.searchFactory(str(self.family_id), 'Individuals',attributes=['fKey_family_Id'], shortOut=True))
        mainLayout.addWidget(self.familyMembers)

        label = QLabel("title")
        mainLayout.addWidget(label)


        self.title = QLineEdit()
        if  loadedChar['indiv_title'] != " " and loadedChar['indiv_title'] != None:
            self.title.setText(loadedChar['indiv_title'])
        mainLayout.addWidget(self.title)

        label = QLabel("tags")
        mainLayout.addWidget(label)


        self.tags = QLineEdit()
        if  loadedChar['indiv_tags'] != " " and loadedChar['indiv_tags'] != None:
            self.tags.setText(loadedChar['indiv_tags'])
        mainLayout.addWidget(self.tags)

        label = QLabel("notes")
        mainLayout.addWidget(label)

        self.notes = QTextEdit()
        if  loadedChar['indiv_notes'] != " " and loadedChar['indiv_notes'] != None:
            self.notes.setPlainText(loadedChar['indiv_notes'])
        elif notes!={}:
            self.notes.setPlainText(notes["notes"])
        mainLayout.addWidget(self.notes)

        buttonLayout = QHBoxLayout()
        mainLayout.addLayout(buttonLayout)

        cancelButton = QPushButton("cancel")
        cancelButton.clicked.connect(lambda: self.cancel(id))
        buttonLayout.addWidget(cancelButton)

        applyButton = QPushButton("Apply changes")
        applyButton.clicked.connect(lambda: self.apply(id))
        buttonLayout.addWidget(applyButton)

        # sidebar
        sidebarLayout = QVBoxLayout()
        cenLayout.addLayout(sidebarLayout, stretch=1)

        if self.new:
            random=QPushButton('random NPC')
            random.clicked.connect(self.man_randomNPC)
            sidebarLayout.addWidget(random)

        self.newFamily=False


    def man_randomNPC(self):
        char=ex.randomChar()


        family_Bib=ex.searchFactory(char['family_Name'],'Families')

        if family_Bib == []:
            family_ID=ex.newFactory('Families',{'family_Name':char['family_Name']})

            if self.newFamily ==False:
                self.newFamily= [family_ID]
            else:
                self.newFamily.append(family_ID)
        else:
            family_ID=family_Bib[0][0]

        self.family_Name.setText(char['family_Name'])
        self.fName.setText(char['indiv_fName'])
        self.family_id=family_ID
        self.familyMembers.resultUpdate(ex.searchFactory(str(self.family_id), 'Individuals',attributes=['fKey_family_ID'], shortOut=True))



    def man_newFamily(self):

        self.dialog2=QDialog()
        dLay=QVBoxLayout()
        self.dialog2.setLayout(dLay)

        label=QLabel('insert new Family Name:')
        dLay.addWidget(label)

        lineEdit=QLineEdit()
        dLay.addWidget(lineEdit)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)

        buttonBox.accepted.connect(self.dialog2.accept)
        buttonBox.rejected.connect(self.dialog2.reject)
        dLay.addWidget(buttonBox)

        if self.dialog2.exec_():
            newName=lineEdit.text()

            self.family_id=ex.newFactory('Families',{'family_Name':newName})
            self.family_Name.setText(newName)
            self.familyMembers.resultUpdate(ex.searchFactory(str(self.family_id), 'Individuals',attributes=['fkey_family_ID'], shortOut=True))

    def man_selFamily(self):

        dialog=DialogEditItem([(self.family_id,self.family_Name.text())],maximumItems=1)
        dialog.setSource(lambda x=None: ex.searchFactory(x,library='Families',searchFulltext=True),'Families')
        if dialog.exec_() and len(dialog.getNewItems())>0:
            family=dialog.getNewItems()[0]
            self.family_id=family[0]
            self.family_Name.setText(family[1])
            self.familyMembers.resultUpdate(ex.searchFactory(str(self.family_id), 'Individuals', shortOut=True,attributes=['fKey_family_ID']))


    def cancel(self,id):
        if self.new:
            ex.deleteFactory(id, 'Individuals')

            if not self.newFamily==False:
                for id in self.newFamily:
                    ex.deleteFactory(id,'Families')
        if self.onDecline!=None:
            self.onDecline()
        self.exitFunc()

    def apply(self, id):

        if self.new:
            if not self.newFamily==False:
                for id in self.newFamily:
                    if id != self.family_id:
                        ex.deleteFactory(id,'Families')

        oldValues = ex.getFactory(id,"Individuals", defaultOutput=True,dictOut=True)
        # save fName
        text = self.fName.text().strip(" ")
        if text != oldValues['indiv_fName']:
            if text == None or text == "":
                text = 'No forename'
            ex.updateFactory(id, [text], 'Individuals', ['indiv_fName'])


        #save family_Name
        text = self.family_Name.text()
        family_id=self.family_id
        if text != oldValues["family_Name"]:
            ex.updateFactory(id, [family_id], 'Individuals', ['fKey_family_ID'])

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
        text = self.notes.toPlainText().strip(" ")
        if text != oldValues["indiv_notes"]:
            if text == None or text == "":
                text = 'No Notes'
            ex.updateFactory(id, [text], 'Individuals', ['indiv_notes'])

        if self.onApply!=None:
            self.onApply()
        self.exitFunc()


    def setExit(self, exitFunc, onApply=None , onDecline=None ):
        self.exitFunc = exitFunc
        self.onApply=onApply
        self.onDecline=onDecline

    def buttonclicked(self):

        dialog = DialogEditItem(self.sessionNPC)
        dialog.setSource(lambda x: ex.searchFactory(x, library='Individuals', searchFulltext=True, shortOut=True),'Individuals')
        if dialog.exec_():
            self.sessionNPC = dialog.getNewItems()
            self.result.resultUpdate(self.sessionNPC)

    def sourceItems(self, id):
        return ex.searchFactory(id, library='Individuals', attributes=['individual_ID'])[0][3]

    def sourceSearch(self, text):
        return ex.searchFactory(text, library='Individuals', searchFulltext=True, shortOut=True)

    def showAppliedList(self, ids):
        charakterList = []
        if ids[0] != "":
            for id in ids:
                char = ex.getFactory(id,"Individuals", defaultOutput=True,dictOut=True)
                charakterList.append((char["individual_ID"], char["indiv_fName"], char["family_Name"]))
        return charakterList

    def returnID(self):
        return self.id
class DialogEditItem(QDialog):

    def __init__(self, sourceAdded=[],maximumItems=None):
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

        self.timer_start()

    def removeItem(self):
        id = self.sender().page
        for item in self.addedItems:
            if item[0] == id:
                self.addedItems.remove(item)
                break
        self.added.resultUpdate(self.addedItems)
        return

    def addItem(self):
        id = self.sender().page
        if self.maximumItems!=None:
            if len(self.addedItems)>self.maximumItems-1:
                self.message=QMessageBox()
                self.message.setText('You have more than the limit of %i items selected, please remove at least one item before adding new ones.'%(self.maximumItems))
                self.message.show()
                #self.timer.singleShot(3000,lambda: self.message.close())
                return

        if id not in [x[0] for x in self.addedItems]:
            item = ex.getFactory(id,self.pool,shortOutput=True)
            self.addedItems.append(item)
            self.added.resultUpdate(self.addedItems)
        return

    def timer_start(self):
        self.timerMark = True
        self.timer.stop()
        self.timer.timeout.connect(self.searchbarChanged)
        self.timer.start(1000)

    def searchbarChanged(self):
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
        self.source = source
        self.pool=pool
        self.searchResult.resultUpdate(self.source(""))


    def getNewItems(self):
        return self.addedItems





class DialogRandomNPC(QDialog):

    def __init__(self,exitfunc=None):
        self.exitFunc = exitfunc
        self.timer=QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(lambda:self.existing_families.resultUpdate(ex.searchFactory(self.family.text(),'Families',searchFulltext=True)))


        super().__init__()
        layout=QVBoxLayout()
        self.setLayout(layout)



        char=ex.randomChar()

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
        char = ex.randomChar()
        self.familyID=None
        self.family.setText(char['family_Name'])
        self.family.setStyleSheet('Color: black')
        self.fName.setText(char['indiv_fName'])
        self.sex=char['indiv_sex'][0]
        self.existing_families.resultUpdate(ex.searchFactory(char['family_Name'],'Families'))
        self.family_members.resultUpdate([])

    def save_family_id(self):
        self.familyID=self.sender().page
        family=ex.getFactory(str(self.familyID),'Families')

        self.family.setStyleSheet("color: gray")
        if len(family)>0:
            self.family.setText(family[1])
        self.family_members.resultUpdate(ex.searchFactory(str(self.familyID), 'Individuals',attributes=['fKey_family_ID'], shortOut=True))



    def cancel(self):
        self.reject()
        self.close()
        self.exitFunc()

    def save(self):
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



class MyWindow(QMainWindow):
    windowMode = "SessionMode"                 # EditMode oder SessionMode, Gegenteil auswählen !!release: EditMode!!
    searchMode = False
    sessionSearchFilter = {}
    NPCSearchFilter= {}
    eventSearchFilter= {}
    path_ObjectA=None
    eventPos=None
    last_obj=None
    label_Stored=None

    def __init__(self):
        super().__init__()

        self.timer = QTimer()

        self.mainWin_stWid = QStackedWidget()
        self.setCentralWidget(self.mainWin_stWid)

        #region Management

        self.man_main_Wid = QWidget()
        self.man_main_layVB = QVBoxLayout()
        self.man_main_Wid.setLayout(self.man_main_layVB)
        self.mainWin_stWid.addWidget(self.man_main_Wid)

        man_top_layHB= QHBoxLayout()
        self.man_main_layVB.addLayout(man_top_layHB)

        man_top_layHB.addStretch(85)

        man_top_btn_startSes = QPushButton("start Session")
        man_top_btn_startSes.clicked.connect(self.btn_switch_windowMode)
        man_top_layHB.addWidget(man_top_btn_startSes,stretch=15)

        self.source='Dsa Daten.db'
        man_top_btn_selectDB = QPushButton("Select source")
        man_top_btn_selectDB.clicked.connect(self.btn_man_setSource)
        man_top_layHB.addWidget(man_top_btn_selectDB, stretch=15)

        man_cen_tabWid = QTabWidget()
        self.man_main_layVB.addWidget(man_cen_tabWid)

        #region DraftboardTab

        self.man_Draftboard_startpageStack =QStackedWidget()
        man_cen_tabWid.addTab(self.man_Draftboard_startpageStack, "Draftboard")

        self.man_Draftboard_startpageWid = QWidget()
        self.man_Draftboard_startpageStack.addWidget(self.man_Draftboard_startpageWid)


        self.man_Draftboard_startpageLay = QHBoxLayout()
        self.man_Draftboard_startpageWid.setLayout(self.man_Draftboard_startpageLay)

        self.man_Draftboard_oldScene = None
        self.man_Draftboard_graphicView = QGraphicsView()
        self.man_Draftboard_graphicView.installEventFilter(self)

            # prepares eventFilter multitrigger Prevention
        lbl = DataLabel()
        lbl.lbl_parent = None
        self.last_obj = lbl

        self.man_Draftboard_graphicView.setRenderHint(QPainter.Antialiasing)
        self.man_Draftboard_startpageLay.addWidget(self.man_Draftboard_graphicView)


        self.man_Draftboard_sidebar=QGridLayout()
        self.man_Draftboard_startpageLay.addLayout(self.man_Draftboard_sidebar)

        self.man_Draftboard_menu_selDB=QComboBox()

        draftboards = ex.searchFactory("", "Draftbooks", output="draftbook_Title,draftbook_ID")
        for board in draftboards:
            self.man_Draftboard_menu_selDB.addItem(*board)

        self.man_Draftboard_menu_selDB.currentIndexChanged.connect(self.load_Draftboard_GraphicScene)
        self.man_Draftboard_sidebar.addWidget(self.man_Draftboard_menu_selDB,0,1,1,2)


        self.man_Draftboard_btn_newDraftbook=QPushButton("neues Draftbook")
        self.man_Draftboard_btn_newDraftbook.clicked.connect(self.btn_man_DB_newDB)
        self.man_Draftboard_sidebar.addWidget(self.man_Draftboard_btn_newDraftbook,1,1,1,2)

        self.man_Draftboard_btn_deleteDB = QPushButton("Draftbook löschen")
        self.man_Draftboard_btn_deleteDB.clicked.connect(self.btn_man_DB_deleteDB)
        self.man_Draftboard_sidebar.addWidget(self.man_Draftboard_btn_deleteDB, 2, 1, 1, 2)

        divider=QFrame()
        divider.setFrameShape(QFrame.HLine)
        self.man_Draftboard_sidebar.addWidget(divider,3,1,1,2)


        self.man_Draftboard_btn_clearMode=QPushButton("Viewmode")
        self.man_Draftboard_btn_clearMode.clicked.connect(self.btn_man_DB_clearMode)
        self.man_Draftboard_sidebar.addWidget(self.man_Draftboard_btn_clearMode, 6,1,1,2)

        self.man_Draftboard_btn_moveMode=QPushButton("move")
        self.man_Draftboard_btn_moveMode.setCheckable(True)
        self.man_Draftboard_btn_moveMode.clicked.connect(self.btn_man_DB_clearMode)
        self.man_Draftboard_sidebar.addWidget(self.man_Draftboard_btn_moveMode, 7, 1,1,1)

        self.man_Draftboard_btn_connectMode = QPushButton("connect")
        self.man_Draftboard_btn_connectMode.setCheckable(True)
        self.man_Draftboard_btn_connectMode.clicked.connect(self.btn_man_DB_clearMode)
        self.man_Draftboard_sidebar.addWidget(self.man_Draftboard_btn_connectMode, 7, 2,1,1)

        self.man_Draftboard_btn_deleteMode = QPushButton("delete")
        self.man_Draftboard_btn_deleteMode.setCheckable(True)
        self.man_Draftboard_btn_deleteMode.clicked.connect(self.btn_man_DB_clearMode)
        self.man_Draftboard_sidebar.addWidget(self.man_Draftboard_btn_deleteMode, 8, 1,1,1)

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
        self.man_Draftboard_sidebar.addWidget(self.man_Draftboard_btn_convert, 16, 1,1,2)


        self.man_Draftboard_sidebarStack=QStackedWidget()
        self.man_Draftboard_sidebar.addWidget(self.man_Draftboard_sidebarStack,17,1,1,2)

        self.load_Draftboard_GraphicScene()



        #endregion

        #region SessionTab

        self.man_Session_cen_stackWid = QStackedWidget()
        man_cen_tabWid.addTab(self.man_Session_cen_stackWid, "Session")

        man_Session_startpageWid = QWidget()
        self.man_Session_cen_stackWid.addWidget(man_Session_startpageWid)

        self.man_Session_startpageLay = QVBoxLayout()
        man_Session_startpageWid.setLayout(self.man_Session_startpageLay)

        self.man_Session_searchbar_layQH = QHBoxLayout()
        self.man_Session_startpageLay.addLayout(self.man_Session_searchbar_layQH)

        self.man_Session_searchBar_lEdit=QLineEdit()
        self.man_Session_searchBar_lEdit.textChanged.connect(lambda: self.timer_start(500, function=self.linEditChanged_man_searchSession))
        self.man_Session_searchbar_layQH.addWidget(self.man_Session_searchBar_lEdit,50)

        button = QPushButton("Fulltext search is off")
        if self.searchMode:
            button.setText("Fulltext search is on")

        button.clicked.connect(self.btn_switch_searchMode)
        self.man_Session_searchbar_layQH.addWidget(button, stretch=10)


        button=QPushButton("set Filter")
        button.clicked.connect(lambda: self.btn_man_setFilter('Sessions'))
        self.man_Session_searchbar_layQH.addWidget(button,10)

        self.man_Session_searchbar_filter_stWid=QStackedWidget()
        self.man_Session_searchbar_layQH.addWidget(self.man_Session_searchbar_filter_stWid, 30)

        button = QPushButton("new Session")
        button.clicked.connect(self.btn_man_viewSession)
        button.page = None
        self.man_Session_searchbar_layQH.addWidget(button, 10)

        self.man_Session_searchresultWid = Resultbox()
        self.man_Session_searchresultWid.setPref(buttonList=[['select', self.btn_man_viewSession],['delete',self.btn_man_DeleteSession]])
        self.man_Session_searchresultWid.resultUpdate(ex.searchFactory("", library='Sessions', shortOut=True,searchFulltext=self.searchMode))
        self.man_Session_startpageLay.addWidget(self.man_Session_searchresultWid,90)

        self.load_man_Session_searchbar()  # initialisiert das searchBarLayout

        # endregionTab

        # region Event Tab

        self.man_Event_cen_stackWid = QStackedWidget()
        man_cen_tabWid.addTab(self.man_Event_cen_stackWid, "Event")

        man_Event_startpageWid = QWidget()
        self.man_Event_cen_stackWid.addWidget(man_Event_startpageWid)

        self.man_Event_startpageLay = QVBoxLayout()
        man_Event_startpageWid.setLayout(self.man_Event_startpageLay)

        self.man_Event_searchbar_layQH = QHBoxLayout()
        self.man_Event_startpageLay.addLayout(self.man_Event_searchbar_layQH)

        self.man_Event_searchBar_lEdit = QLineEdit()
        self.man_Event_searchBar_lEdit.textChanged.connect(
            lambda: self.timer_start(500, function=self.linEditChanged_man_searchEvent))
        self.man_Event_searchbar_layQH.addWidget(self.man_Event_searchBar_lEdit, 50)

        button = QPushButton("Fulltext search is off")
        if self.searchMode:
            button.setText("Fulltext search is on")

        button.clicked.connect(self.btn_switch_searchMode)
        self.man_Event_searchbar_layQH.addWidget(button, stretch=10)

        button = QPushButton("set Filter")
        button.clicked.connect(lambda: self.btn_man_setFilter('Events'))
        self.man_Event_searchbar_layQH.addWidget(button, 10)

        self.man_Event_searchbar_filter_stWid = QStackedWidget()
        self.man_Event_searchbar_layQH.addWidget(self.man_Event_searchbar_filter_stWid, 30)

        button = QPushButton("new Event")
        button.clicked.connect(self.btn_man_viewEvent)
        button.page = None
        self.man_Event_searchbar_layQH.addWidget(button, 10)

        self.man_Event_searchresultWid = Resultbox()
        self.man_Event_searchresultWid.setPref(
            buttonList=[['select', self.btn_man_viewEvent], ['delete', self.btn_man_DeleteEvent]])
        self.man_Event_searchresultWid.resultUpdate(
            ex.searchFactory("", library='Events', output="Events.event_ID,Events.event_Title",
                             searchFulltext=self.searchMode, OrderBy="Events.event_Date ASC"))
        self.man_Event_startpageLay.addWidget(self.man_Event_searchresultWid, 90)

        self.load_man_Event_searchbar()  # initialisiert das searchBarLayout

        # endregionTab

        # region NPCTab

        self.man_NPC_cen_stackWid = QStackedWidget()
        man_cen_tabWid.addTab(self.man_NPC_cen_stackWid, "NPC")

        man_NPC_startpageWid = QWidget()
        self.man_NPC_cen_stackWid.addWidget(man_NPC_startpageWid)

        self.man_NPC_startpageLay = QVBoxLayout()
        man_NPC_startpageWid.setLayout(self.man_NPC_startpageLay)

        self.man_NPC_searchbar_layQH = QHBoxLayout()
        self.man_NPC_startpageLay.addLayout(self.man_NPC_searchbar_layQH)

        self.man_NPC_searchBar_lEdit = QLineEdit()
        self.man_NPC_searchBar_lEdit.textChanged.connect(
            lambda: self.timer_start(500, function=self.linEditChanged_man_searchNPC))
        self.man_NPC_searchbar_layQH.addWidget(self.man_NPC_searchBar_lEdit, 50)

        button = QPushButton("Fulltext search is off")
        if self.searchMode:
            button.setText("Fulltext search is on")

        button.clicked.connect(self.btn_switch_searchMode)
        self.man_NPC_searchbar_layQH.addWidget(button, stretch=10)

        button = QPushButton("set Filter")
        button.clicked.connect(lambda: self.btn_man_setFilter('Individuals'))
        self.man_NPC_searchbar_layQH.addWidget(button, 10)

        self.man_NPC_searchbar_filter_stWid = QStackedWidget()
        self.man_NPC_searchbar_layQH.addWidget(self.man_NPC_searchbar_filter_stWid, 30)

        button = QPushButton("new NPC")
        button.clicked.connect(self.btn_man_viewNPC)
        button.page = None
        self.man_NPC_searchbar_layQH.addWidget(button, 10)

        self.man_NPC_searchresultWid = Resultbox()
        self.man_NPC_searchresultWid.setPref(
            buttonList=[['select', self.btn_man_viewNPC], ['delete', self.btn_man_DeleteNPC]])
        self.man_NPC_searchresultWid.resultUpdate(
            ex.searchFactory("", library='Individuals', shortOut=True, searchFulltext=True))
        self.man_NPC_startpageLay.addWidget(self.man_NPC_searchresultWid,90)

        self.load_man_NPC_searchbar()             #initialisiert die searchBarLayout


        #endregion

        #endregion


        #region Session
        self.ses_Main_wid = QWidget()
        self.ses_main_layHB = QHBoxLayout()
        self.ses_Main_wid.setLayout(self.ses_main_layHB)
        self.mainWin_stWid.addWidget(self.ses_Main_wid)

        self.ses_side_layVB = QVBoxLayout()
        self.ses_main_layHB.addLayout(self.ses_side_layVB, stretch=15)

        self.ses_cen_stWid = QStackedWidget()
        self.ses_main_layHB.addWidget(self.ses_cen_stWid, stretch=70)

        self.ses_side_stream = QVBoxLayout()
        self.ses_main_layHB.addLayout(self.ses_side_stream,stretch=15)


        ses_side_btn_leaveSes = QPushButton("leave Session")
        ses_side_btn_leaveSes.clicked.connect(self.btn_switch_windowMode)
        self.ses_side_layVB.addWidget(ses_side_btn_leaveSes)

        #region timeWidget_sidebar
        self.ses_side_Time_wid = QWidget()
        self.ses_side_Time_layVB = QVBoxLayout()
        self.ses_side_Time_wid.setLayout(self.ses_side_Time_layVB)
        self.ses_side_layVB.addWidget(self.ses_side_Time_wid)

        ses_side_Time_layHB = QHBoxLayout()
        self.ses_side_Time_layVB.addLayout(ses_side_Time_layHB)

        ses_side_Time_layHB.addWidget(QLabel("Ort:"), alignment=Qt.Alignment(4))

        self.ses_side_Time_Location_lEdit = QLineEdit()
        self.ses_side_Time_Location_lEdit.setText("%s" % (ex.DataStore.location[0]))
        self.ses_side_Time_Location_lEdit.textEdited.connect(self.linEditChanged_ses_location)
        ses_side_Time_layHB.addWidget(self.ses_side_Time_Location_lEdit, alignment=Qt.Alignment(4))

        ses_side_Time_layHB0 = QHBoxLayout()
        self.ses_side_Time_layVB.addLayout(ses_side_Time_layHB0)

        self.ses_side_Time_Date_label = QLabel("Tag: %s" % (ex.DataStore.today))
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

        self.weather_Time = QLabel("Uhrzeit %s" % (ex.DataStore.now.strftime("%H Uhr")))
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

        self.ses_side_Time_weatherCurrent = QLabel("%s" % (ex.DataStore.weather))
        self.ses_side_Time_layVB.addWidget(self.ses_side_Time_weatherCurrent, alignment=Qt.Alignment(5))

        self.ses_side_Time_weatherNext = QLabel("Morgiges Wetter:\n%s" % (ex.DataStore.weatherNext))
        self.ses_side_Time_layVB.addWidget(self.ses_side_Time_weatherNext, alignment=Qt.Alignment(5))

        ses_side_Time_weatherNext_btn = QPushButton("Wetterwandel")
        ses_side_Time_weatherNext_btn.clicked.connect(self.btn_ses_weatherNext)
        self.ses_side_Time_layVB.addWidget((ses_side_Time_weatherNext_btn))

        #endregion_sidebar

        #region NPC_sidebar
        self.ses_side_NPC_tabWid = QTabWidget()
        self.ses_side_layVB.addWidget(self.ses_side_NPC_tabWid)

        self.ses_side_sesNPC_wid = QWidget()
        self.ses_side_searchNPC_wid = QWidget()

        self.ses_side_NPC_tabWid.addTab(self.ses_side_sesNPC_wid, "Session NPCs")
        self.ses_side_NPC_tabWid.addTab(self.ses_side_searchNPC_wid, "search")

        self.ses_side_sesNPC_layVB = QVBoxLayout()
        self.ses_side_sesNPC_wid.setLayout(self.ses_side_sesNPC_layVB)

        button=QPushButton('random Char')
        button.clicked.connect(self.btn_ses_randomChar)
        self.ses_side_layVB.addWidget(button)

        button=QPushButton('open Plot')
        button.clicked.connect(self.btn_ses_openPlot)
        self.ses_side_layVB.addWidget(button)

        #region session NPC Tab


        self.ses_sesNPC= Resultbox()
        self.ses_sesNPC.setPref(standardbutton= self.load_ses_NpcInfo,standardButtonVerticalAlignment=False,col=1)
        self.ses_sesNPC.resultUpdate([])
        self.ses_side_sesNPC_layVB.addWidget(self.ses_sesNPC)
        #endregion

        #region search NPC Tab

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
        self.searchNPCRes.setPref(standardbutton=self.load_ses_NpcInfo,standardButtonVerticalAlignment=False,col=1)
        self.searchNPCRes.resultUpdate(ex.searchFactory("",'Individuals',shortOut=True,searchFulltext=True))
        self.ses_side_searchNPC_layVB.addWidget(self.searchNPCRes)

        self.linEditChanged_ses_searchNPC()
        # endregion


        self.ses_cen_stWid_currentInstance = None
        self.ses_cen_stWid_lastInstance = None
        self.ses_cen_stWid_LastWid = None
        # endregion

        #region StreamSidebar
        self.temp_streamSave = []

        self.ses_scenes= Resultbox()
        self.ses_scenes.setPref(standardbutton=self.btn_ses_openScene,col=1)
        self.ses_side_stream.addWidget(self.ses_scenes, stretch=50)

        self.ses_streamResult = Resultbox()
        self.ses_streamResult.setPref(reloadBottom=True,paintLight=[0],paintItemFrame=True,ignoreIndex=[None],col=1)
        self.ses_streamResult.setSource([x[1] for x in self.temp_streamSave if len(self.temp_streamsave)>0])
        self.ses_streamResult.resultUpdate()

        self.ses_stream_textEdit = QTextEdit()

        button = QPushButton("submit text")
        button.clicked.connect(self.btn_ses_submitStream)


        self.ses_side_stream.addWidget(self.ses_streamResult,stretch=50)
        self.ses_side_stream.addWidget(self.ses_stream_textEdit, stretch=10 )
        self.ses_side_stream.addWidget(button)
        #endregion

        #endregion

        self.btn_switch_windowMode()  # !!release: delete line!!
        self.showMaximized()

    
    
    #region Buttons

    #region window unspecific Buttons
    def btn_switch_searchMode(self):
        if self.searchMode:
            self.sender().setText("search Fulltext is off")
            self.searchMode=False
        else:
            self.sender().setText("search Fulltext is on")
            self.searchMode = True

        if self.windowMode == "SessionMode":
            self.linEditChanged_ses_searchNPC()
        else:
            self.linEditChanged_man_searchNPC()
            self.linEditChanged_man_searchEvent()
            self.linEditChanged_man_searchSession()

    def btn_switch_windowMode(self) -> None:
        if self.windowMode == "SessionMode":
            self.windowMode = "EditMode"
            self.mainWin_stWid.setCurrentWidget(self.man_main_Wid)

        else:
            self.windowMode = "SessionMode"
            sessionActive=ex.searchFactory("1",'Sessions',attributes=["current_Session"])
            if len(sessionActive)>0:
                id=sessionActive[0][0]
                self.btn_ses_openPlot()
            else:
                messagbox=QMessageBox()
                messagbox.setText("pls make active Session first")
                messagbox.exec_()
                return

            self.temp_streamSave = self.streamDecode(id)
            self.ses_streamResult.resultUpdate(self.temp_streamSave)
            self.temp_scenesSave = ex.searchFactory(str(id),"Events",output="Events.event_ID,Events.event_Title",
                                                    attributes=["fKey_Session_ID"],OrderBy="Events.event_Date")
            self.ses_scenes.resultUpdate(self.temp_scenesSave)
            self.mainWin_stWid.setCurrentWidget(self.ses_Main_wid)



            session_NPC= ex.searchFactory("1",'Session_Individual_jnt', attributes=['current_Session'],
                                          output="Individuals.individual_ID,indiv_fName,family_Name",shortOut=True)

            self.ses_sesNPC.resultUpdate(session_NPC)

    #endregion
    
    #region management Buttons
    def btn_man_DB_placeNote(self):
        self.path_ObjectA=None
        dial2 = DialogEditItem([],maximumItems=1)
        dial2.setSource(lambda x: ex.searchFactory(x, library="Notes", searchFulltext=True, shortOut=True), "Notes")

        if dial2.exec_():
            self.path_ObjectA = dial2.getNewItems()[0][0]
        else:
            self.man_Draftboard_btn_placeNote.setChecked(False)

    def btn_man_DB_placeLinked(self):
        self.path_ObjectA=None

        dial=QDialog()
        lay=QVBoxLayout()
        dial.setLayout(lay)

        combo=QComboBox()
        combo.addItem("Event","Events")
        combo.addItem("Individual", "Individuals")
        combo.addItem("Session", "Sessions")
        lay.addWidget(combo)

        buttonbox=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        buttonbox.accepted.connect(dial.accept)
        buttonbox.rejected.connect(dial.close)
        lay.addWidget(buttonbox)

        if dial.exec_():
            library=combo.currentData()
            dial2=DialogEditItem(maximumItems=1)
            dial2.setSource(lambda x: ex.searchFactory(x, library=library, searchFulltext=True, shortOut=True),library)

            if dial2.exec_():

                indiv_ID=dial2.getNewItems()[0][0]

                dial3=QDialog()
                lay=QVBoxLayout()
                dial3.setLayout(lay)

                lay.addWidget(QLabel("select shown columns:"))

                collection=[]
                for column in ex.searchFactory("",library, searchFulltext=True, dictOut=True)[0]:
                    check=QCheckBox(column)
                    lay.addWidget(check)
                    collection.append(check)

                buttonbox=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel)
                buttonbox.accepted.connect(dial3.accept)
                buttonbox.rejected.connect(dial3.close)
                lay.addWidget(buttonbox)

                if dial3.exec_():
                    text=""
                    for item in collection:
                        if item.checkState():
                            text+=item.text()
                            text+=":"
                    if text!="":
                        text=text.rstrip(":")

                    self.path_ObjectA=(library, indiv_ID, text )
        return

    def btn_man_DB_deleteDB(self):
        dialog=QDialog()
        lay=QVBoxLayout()
        dialog.setLayout(lay)

        lay.addWidget(QLabel("Soll dieses Draftbook gelöscht werden?"))
        lay.addWidget(QLabel("Draftbook:\n"+self.man_Draftboard_menu_selDB.currentText()))

        buttonBox=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(dialog.accept)
        buttonBox.rejected.connect(dialog.close)
        lay.addWidget(buttonBox)

        if dialog.exec():
            id=self.man_Draftboard_menu_selDB.currentData()
            ex.deleteFactory(id,"Draftbooks")
            self.man_Draftboard_menu_selDB.removeItem(self.man_Draftboard_menu_selDB.findData(id))
        return
    def btn_man_DB_newDB(self):
        dialog=QDialog()
        lay=QVBoxLayout()
        dialog.setLayout(lay)

        lay.addWidget(QLabel("Titel:"))

        title=QLineEdit()
        lay.addWidget(title)

        lay.addWidget(QLabel("kurze Inhaltsbeschreibung:"))

        desc=QTextEdit()
        lay.addWidget(desc)

        buttonBox=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(dialog.accept)
        buttonBox.rejected.connect(dialog.close)
        lay.addWidget(buttonBox)

        if dialog.exec():
            if title.text()!="" or desc.toPlainText()!="":

                id=ex.newFactory("Draftbooks",{"draftbook_Title":title.text(),"draftbook_Short_Desc":desc.toPlainText(),
                                               "draftbook_height":100,"draftbook_width":500,"draftbook_xPos":0,"draftbook_yPos":0})
                self.man_Draftboard_menu_selDB.addItem(title.text(),id)
                self.man_Draftboard_menu_selDB.setCurrentIndex(self.man_Draftboard_menu_selDB.findData(id))
        return
    def btn_man_DB_clearMode(self):

        self.path_ObjectA = None

        if self.sender()!=self.man_Draftboard_btn_moveMode:
            self.man_Draftboard_btn_moveMode.setChecked(False)
        if self.sender()!=self.man_Draftboard_btn_connectMode:
            self.man_Draftboard_btn_connectMode.setChecked(False)
        if self.sender()!=self.man_Draftboard_btn_deleteMode:
            self.man_Draftboard_btn_deleteMode.setChecked(False)
        if self.sender()!=self.man_Draftboard_btn_convert:
            self.man_Draftboard_btn_convert.setChecked(False)
        if self.sender()!=self.man_Draftboard_btn_editMode:
            self.man_Draftboard_btn_editMode.setChecked(False)
        return


    def btn_man_setSource(self):

        self.chooseDialog=QDialog()
        lay=QGridLayout()
        self.chooseDialog.setLayout(lay)

        label=QLabel("The source you want to change")
        lay.addWidget(label,0,0,1,3)

        button=QPushButton("Campaignsource")
        button.clicked.connect(lambda: self.load_man_source_Filedialog(False))
        lay.addWidget(button,1,0)

        button = QPushButton("Settingsource")
        button.clicked.connect(lambda: self.load_man_source_Filedialog(True))
        lay.addWidget(button, 1, 1)

        button = QPushButton("Cancel")
        button.clicked.connect(self.chooseDialog.close)
        lay.addWidget(button, 1, 2)

        self.chooseDialog.exec_()



    def btn_man_viewSession(self):
        if self.sender().page==None:
            propPage = SessionEditWindow(self.sender().page,True)
        else:
            propPage = SessionEditWindow(self.sender().page)

        propPage.setExit(self.SessionProp_onExit)
        self.man_Session_cen_stackWid.addWidget(propPage)
        self.man_Session_cen_stackWid.setCurrentWidget(propPage)

    def btn_man_viewEvent(self):
        if self.sender().page==None:
            propPage = EventEditWindow(self.sender().page,True)
        else:
            propPage = EventEditWindow(self.sender().page)

        propPage.setExit(self.EventProp_onExit)
        self.man_Event_cen_stackWid.addWidget(propPage)
        self.man_Event_cen_stackWid.setCurrentWidget(propPage)

    def btn_man_DeleteNPC(self):

        id= self.sender().page
        character =ex.getFactory(id,"Individuals", defaultOutput=True,dictOut=True)
        msgBox = QMessageBox()

        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msgBox.setText("Do you want to delete %s" %(character['indiv_fName']+" "+character['family_Name']))
        value= msgBox.exec()

        if value == 1024:
            ex.deleteFactory(id, 'Individuals')

            #Delete Charid from session_charakters
            relevant_Sessions= ex.searchFactory(str(id),'Session_Individual_jnt',attributes=['fKey_individual_ID'],output="rowid",dictOut=True)
            for item in relevant_Sessions:
                ex.deleteFactory(item['rowid'],'Session_Individual_jnt')


        self.linEditChanged_man_searchNPC()

    def btn_man_DeleteSession(self):

        Id = self.sender().page
        msgBox = QMessageBox()

        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msgBox.setText("Do you want to delete %s" %(ex.getFactory(Id,'Sessions')[1]))
        value= msgBox.exec()
        if value == 1024:
           ex.deleteFactory(Id,'Sessions')

        self.linEditChanged_man_searchSession()

    def btn_man_DeleteEvent(self):

        Id = self.sender().page
        msgBox = QMessageBox()

        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msgBox.setText("Do you want to delete %s" %(ex.getFactory(Id,'Events')[1]))
        value= msgBox.exec()
        if value == 1024:
           ex.deleteFactory(Id,'Events')

        self.linEditChanged_man_searchEvent()
    # to be updated
    
    def btn_man_viewNPC(self):
        if self.sender().page == None:
            propPage = NPCEditWindow(self.sender().page, True)
        else:
            propPage = NPCEditWindow(self.sender().page)

        propPage.setExit(self.NPCProp_onExit)
        self.man_NPC_cen_stackWid.addWidget(propPage)
        self.man_NPC_cen_stackWid.setCurrentWidget(propPage)
    

    def btn_man_setFilter(self, library:str):
        self.filterDialog=QDialog()
        self.filterDialog.setWindowTitle("Add new Filter")

        filterDialogLayout= QVBoxLayout()
        self.filterDialog.setLayout(filterDialogLayout)

        if library=="Individuals":
            filter = self.NPCSearchFilter
        elif library=="Sessions":
            filter=self.sessionSearchFilter
        elif library == "Events":
            filter = self.eventSearchFilter
        else:
            raise TypeError("no Valid Library")



        if len(filter)>3:
            filterDialogLayout.addWidget(QLabel("To many Filter aktiv: \n Please delete existing Filter"))

            buttons = QDialogButtonBox.Ok
            buttonBox = QDialogButtonBox(buttons)
            buttonBox.accepted.connect(self.filterDialog.close)
            filterDialogLayout.addWidget(buttonBox)

        else:
            filterDialogHBox= QHBoxLayout()
            filterDialogLayout.addLayout(filterDialogHBox)

            self.search_Where = QComboBox()
            filter=ex.get_table_Prop(library)['colName']
            self.search_Where.addItems(filter)
            filterDialogHBox.addWidget(self.search_Where)

            self.search_What = QLineEdit()
            filterDialogHBox.addWidget(self.search_What)


            self.filterFulltext=QPushButton("Search Fulltext")
            self.filterFulltext.setCheckable(True)
            filterDialogHBox.addWidget(self.filterFulltext)

            buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
            buttonBox = QDialogButtonBox(buttons)
            buttonBox.accepted.connect(lambda: self.btn_man_filterdialog_accepted(library))
            buttonBox.rejected.connect(self.filterDialog.close)
            filterDialogLayout.addWidget(buttonBox)
        self.filterDialog.exec_()
        return

    def btn_man_delFilter(self, library:str):
        index=self.sender().page
        if library=="Sessions":
            self.sessionSearchFilter.pop(list(self.sessionSearchFilter)[index])
            self.load_man_Session_searchbar()
        elif library=="Individuals":
            self.NPCSearchFilter.pop(list(self.NPCSearchFilter)[index])
            self.load_man_NPC_searchbar()
        elif library=="Events":
            self.eventSearchFilter.pop(list(self.eventSearchFilter)[index])
            self.load_man_Event_searchbar()

        return

    
    def btn_man_filterdialog_accepted(self,library:str):

        if library=="Individuals":
            self.NPCSearchFilter[self.search_Where.currentText()]=[self.search_What.text(),self.filterFulltext]
            self.load_man_NPC_searchbar()
        elif library=="Sessions":
            self.sessionSearchFilter[self.search_Where.currentText()]=[self.search_What.text(), self.filterFulltext]
            self.load_man_Session_searchbar()
        elif library=="Events":
            self.eventSearchFilter[self.search_Where.currentText()] = [self.search_What.text(), self.filterFulltext]
            self.load_man_Event_searchbar()

        self.filterDialog.close()

    # endregion
    
    
    #region Session Buttons
    def btn_ses_time(self, Value):
        if Value > 0:
            ex.DataStore.now = ex.DataStore.now + timedelta(hours=Value)
        else:
            ex.DataStore.now = ex.DataStore.now - timedelta(hours=1)

        self.weather_Time.setText("Uhrzeit: %s" % (ex.DataStore.now.strftime("%H Uhr")))

    def bullshit(self,text):
        print(text)

    def btn_ses_date(self,Value):
        if Value>0:
            days="d"+str(Value)
            ex.DataStore.today = ex.DataStore.today + days
        else:
            ex.DataStore.today = ex.DataStore.today - "d1"

        self.ses_side_Time_Date_label.setText("Tag: %s" % (ex.DataStore.today))

    def btn_ses_weatherNext(self):
        weather=ex.DataStore.weather
        ex.DataStore.weather=ex.DataStore.weatherNext

        ex.DataStore.weatherNext=ex.DataStore.weatherNext.next()
        self.ses_side_Time_weatherCurrent.setText("%s" % (ex.DataStore.weather))
        self.ses_side_Time_weatherNext.setText("Morgiges Wetter:\n%s" % (ex.DataStore.weatherNext))

        date = str(ex.DataStore.today)
        hour = ex.DataStore.now.strftime("%H Uhr")
        location = ex.DataStore.location[0]
        self.temp_streamSave.append((date + " " + hour + " " + location + " " + str(weather), str(ex.DataStore.weather)))
        self.ses_streamResult.resultUpdate(self.temp_streamSave)

        streamSave=self.temp_streamSave.copy()

        text=self.streamEncode()

        id=ex.searchFactory("1",'Sessions',attributes=["current_Session"],searchFulltext=True)[0][0]
        ex.updateFactory(id,[text],'Sessions',['session_stream'])
        
    def btn_ses_openPlot(self):

        current_Session=ex.searchFactory("1",library='Sessions',attributes=['current_Session'])[0]


        plotWin=QWidget()
        plotWin_Lay=QVBoxLayout()
        plotWin.setLayout(plotWin_Lay)

        title=QLabel(current_Session[1])
        plotWin_Lay.addWidget(title)

        text=QTextEdit()
        text.setText(current_Session[2])
        text.setReadOnly(True)
        plotWin_Lay.addWidget(text)

        scenes=ex.searchFactory(str(current_Session[0]),"Events",attributes=["fKey_session_ID"],OrderBy="Events.event_Date",
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

        if self.ses_cen_stWid.count()>1:
            self.ses_cen_stWid.layout().takeAt(0)

    def btn_ses_openScene(self):

        id=self.sender().page
        scene=ex.getFactory(id,"Events",output="event_Title,event_Date,event_Location,event_short_desc,event_long_desc",dictOut=True)

        layout=QGridLayout()
        scene_scroll=QScrollArea()
        scene_scroll.setLayout(layout)


        title=QLabel(scene["event_Title"])
        layout.addWidget(title,0,0)

        if scene["event_Date"]:
            date=QLabel(scene["event_Date"])
        else:
            date = QLabel("no date assigned")
        layout.addWidget(date,0,1)

        if scene["event_Location"]:
            location=QLabel(scene["event_Location"])
        else:
            location = QLabel(scene["no Location assigned"])
        layout.addWidget(location,0,2)

        shortDesc=QTextEdit()
        shortDesc.setReadOnly(True)
        shortDesc.setText(scene["event_short_desc"])
        layout.addWidget(shortDesc,1,0,1,3)

        longDesc = QTextEdit()
        longDesc.setReadOnly(True)
        longDesc.setText(scene["event_long_desc"])
        layout.addWidget(longDesc,2,0,1,3)

        scene_NPC = ex.searchFactory(str(id), 'Event_Individuals_jnt', attributes=['Event_Individuals_jnt.fKey_event_ID'], shortOut=True)
        self.ses_sesNPC.resultUpdate(scene_NPC)

        self.ses_cen_stWid.addWidget(scene_scroll)
        self.ses_cen_stWid.setCurrentWidget(scene_scroll)

        if self.ses_cen_stWid.count() > 1:
            self.ses_cen_stWid.layout().takeAt(0)
    def btn_ses_randomChar(self):
        dialog=DialogRandomNPC(exitfunc=lambda:None)
        if dialog.exec_():
            self.linEditChanged_ses_searchNPC()
            sessionNPC = ex.searchFactory('1', 'Session_Individual_jnt', attributes=["current_Session"], shortOut=True,
                                          output='Individuals.individual_ID,indiv_fName,family_Name')


            self.ses_sesNPC.resultUpdate(sessionNPC)

    def btn_ses_submitStream(self):
        text=self.ses_stream_textEdit.toPlainText().strip("\n")
        date= str(ex.DataStore.today)
        hour=ex.DataStore.now.strftime("%H Uhr")
        weather=str(ex.DataStore.weather)
        location= ex.DataStore.location[0]
        if text!="":
            self.temp_streamSave.append((date+" "+hour+" "+location+" "+weather,text))
            self.ses_stream_textEdit.clear()
            self.ses_streamResult.resultUpdate(self.temp_streamSave)

            text=self.streamEncode()
            id=ex.searchFactory("1",'Sessions',attributes=["current_Session"])[0][0]
            ex.updateFactory(id,[text],'Sessions',['session_stream'])
        return


    
    #endregion
    
    #region lineedit signals
    def linEditChanged_ses_location(self):
        ex.DataStore.location=[self.ses_side_Time_Location_lEdit.text()]

    def linEditChanged_ses_searchNPC(self):
        charakters=ex.searchFactory(self.ses_side_searchNPC_wid_LineEdit.text(),"Individuals",shortOut=True,searchFulltext=self.searchMode)
        self.searchNPCRes.resultUpdate(charakters)
        return

    def linEditChanged_man_searchNPC(self):
        self.timer.stop()
        searchresult = ex.searchFactory(self.man_NPC_searchBar_lEdit.text(),"Individuals",shortOut=True,Filter=self.NPCSearchFilter,searchFulltext=self.searchMode)
        self.man_NPC_searchresultWid.resultUpdate(searchresult)
        return

    def linEditChanged_man_searchEvent(self):
        self.timer.stop()
        charakters = ex.searchFactory(self.man_Event_searchBar_lEdit.text(), "Events", shortOut=True,
                                      searchFulltext=self.searchMode,Filter=self.eventSearchFilter, OrderBy="Events.event_Date ASC")
        self.man_Event_searchresultWid.resultUpdate(charakters)
        return


    def linEditChanged_man_searchSession(self):
        self.timer.stop()
        searchresult=ex.searchFactory(self.man_Session_searchBar_lEdit.text(),'Sessions',shortOut=True,Filter=self.sessionSearchFilter,searchFulltext=self.searchMode)
        self.man_Session_searchresultWid.resultUpdate(searchresult)
        return
    #endregion
    
    #region other

    def eventFilter(self, obj, event):


        if event.type()== QEvent.MouseButtonPress and event.button() == Qt.LeftButton:

            #position Move_To
            if type(obj) == QGraphicsView:
                if self.path_ObjectA!=None and self.man_Draftboard_btn_moveMode.isChecked() and self.eventPos!=event.globalPos():
                    pos=self.man_Draftboard_graphicView.mapToScene(event.pos())
                    newX=int(pos.x()-self.path_ObjectA.width()/2)
                    newY=int(pos.y()-self.path_ObjectA.height()/2)

                    id=ex.searchFactory(self.man_Draftboard_menu_selDB.currentData(),"Notes_Draftbook_jnt",attributes=["draftbook_ID"], output="rowid",
                                        Filter={"xPos":[str(self.path_ObjectA.pos().x()),False],
                                                "yPos":[str(self.path_ObjectA.pos().y()),False]})

                    ex.updateFactory(id[0][0],[str(self.path_ObjectA.labelData["note_ID"]),str(self.man_Draftboard_menu_selDB.currentData()),newX,
                                               newY],"Notes_Draftbook_jnt",["note_ID","draftbook_ID","xPos","yPos"])

                    self.load_Draftboard_GraphicScene(True)
                    self.path_ObjectA = None

                if self.man_Draftboard_btn_placelinked.isChecked():
                    if self.path_ObjectA != None:
                        id=self.path_ObjectA[1]
                        library=self.path_ObjectA[0]
                        text=self.path_ObjectA[2]
                        item=ex.getFactory(id,library,dictOut=True)

                        label=QLabel()
                        label.setWordWrap(True)
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

                        pos=self.man_Draftboard_graphicView.mapToScene(event.pos())
                        newX=int(pos.x()-label.width()/2)
                        newY=int(pos.y()-label.height()/2)


                        newID=ex.newFactory("Notes",{"note_Checked":library+":"+str(id),"note_Content":text})
                        ex.newFactory(data={"note_ID":newID,"draftbook_ID":self.man_Draftboard_menu_selDB.currentData(),
                                            "xPos":newX,"yPos":newY,"width":0,"height":0},
                                      library="Notes_Draftbook_jnt")
                        self.load_Draftboard_GraphicScene(True)
                    self.man_Draftboard_btn_placelinked.setChecked(False)

                if self.man_Draftboard_btn_placeNote.isChecked():
                    if self.path_ObjectA!=None:
                        id=self.path_ObjectA
                        item = ex.getFactory(id, "Notes", dictOut=True)
                        text= item["note_Content"]
                        label = QLabel()
                        label.setWordWrap(True)
                        label.setAlignment(Qt.AlignLeft)
                        label.setAlignment(Qt.AlignVCenter)
                        label.setFrameStyle(1)


                        if item["note_Checked"]!=None:

                            label.column = text.split(":")
                            labelText = ""
                            label.linked=item["note_Checked"].split(":")
                            textData = ex.getFactory(label.linked[1], label.linked[0], dictOut=True)
                            for column in label.column:
                                labelText += column + ":\n" + str(textData[column])
                                if column != column[-1]:
                                    labelText += "\n\n"
                        else:
                            labelText=text
                        label.setText(labelText)
                        label.setGeometry(100, 100, label.sizeHint().width() + 2,
                                          label.sizeHint().height() + 4)

                        pos = self.man_Draftboard_graphicView.mapToScene(event.pos())
                        newX = int(pos.x() - label.width() / 2)
                        newY = int(pos.y() - label.height() / 2)
                        ex.newFactory(
                            data={"note_ID": id, "draftbook_ID": self.man_Draftboard_menu_selDB.currentData(),
                                  "xPos": newX, "yPos": newY,},
                            library="Notes_Draftbook_jnt")
                        self.load_Draftboard_GraphicScene(True)


                    self.man_Draftboard_btn_placeNote.setChecked(False)

            if type(obj) == DataLabel:
                if self.man_Draftboard_btn_connectMode.isChecked():

                    if self.path_ObjectA!=None and self.path_ObjectA!=obj:
                        existing=[]
                        existing.append(ex.searchFactory(obj.labelData["pos_ID"], "Note_Note_Pathlib", attributes=["note_DB_ID1"],
                                                         Filter={"note_DB_ID2":[self.path_ObjectA.labelData["pos_ID"],False]}))
                        existing.append(ex.searchFactory(obj.labelData["pos_ID"], "Note_Note_Pathlib", attributes=["note_DB_ID2"],
                                                         Filter={"note_DB_ID1": [self.path_ObjectA.labelData["pos_ID"], False]}))

                        if existing==[[],[]]:
                            ex.newFactory("Note_Note_Pathlib",
                                          {"note_DB_ID1":self.path_ObjectA.labelData["pos_ID"],"note_DB_ID2":obj.labelData["pos_ID"],
                                           "draftbook_ID":self.man_Draftboard_menu_selDB.currentData()})
                        else:
                            id=[*existing[0],*existing[1]][0][0]
                            ex.deleteFactory(id,"Note_Note_Pathlib")
                        self.load_Draftboard_GraphicScene()
                        self.path_ObjectA = None

                    elif self.path_ObjectA==obj:
                        self.path_ObjectA = None
                        obj.setStyleSheet('background-color: light grey')
                        obj.setFrameStyle(1)

                    else:
                        self.path_ObjectA=obj

                        obj.setStyleSheet('background-color: beige')
                        obj.setFrameStyle(3)

                if self.man_Draftboard_btn_moveMode.isChecked():
                    if self.path_ObjectA==None:        #movemode
                        self.eventPos=event.globalPos()
                        obj.setStyleSheet('background-color: beige')
                        obj.setFrameStyle(3)
                        self.path_ObjectA=obj

                if self.man_Draftboard_btn_deleteMode.isChecked():        #deletemode
                    obj.setStyleSheet('background-color: beige')
                    obj.setFrameStyle(3)
                    msg=QDialog()
                    msgLay=QVBoxLayout()

                    msg.setLayout(msgLay)

                    fullRemoveNote=False

                    if len(ex.searchFactory(obj.labelData["note_ID"], "Notes_Draftbook_jnt",
                                            attributes=["note_ID"])) == 1:
                        msgLay.addWidget(QLabel("Do you want to delete this Note?\n There will be no possibility to restore the Data"))
                        fullRemoveNote=True
                    else:
                        msgLay.addWidget(QLabel("Do you want to delete this Note?"))

                    buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

                    buttonBox.accepted.connect(msg.accept)
                    buttonBox.rejected.connect(msg.reject)

                    msgLay.addWidget(buttonBox)

                    if msg.exec():
                        if fullRemoveNote:
                            ex.deleteFactory(obj.labelData["note_ID"], "Notes")
                        ex.deleteFactory(obj.labelData["pos_ID"],"Notes_Draftbook_jnt")

                    self.load_Draftboard_GraphicScene(True)

                if self.man_Draftboard_btn_editMode.isChecked():
                    self.path_ObjectA = None
                    if type(obj) == DataLabel and self.last_obj.lbl_parent != obj.lbl_parent:
                        self.last_obj = obj
                        self.eventPos = event.globalPos()
                        self.openTextCreator(event, obj=obj)

                    elif type(obj) == QGraphicsView and self.eventPos != event.globalPos():  # positioncheck
                        self.openTextCreator(event)

                if self.man_Draftboard_btn_convert.isChecked() and obj.linked==None:

                    obj.setStyleSheet('background-color: beige')
                    obj.setFrameStyle(3)

                    dialog=QDialog()
                    lay=QVBoxLayout()
                    dialog.setLayout(lay)

                    combo=QComboBox()
                    combo.addItem("Session",[SessionEditWindow,"Sessions","session_ID","session_Name:session_notes"])
                    combo.addItem("Event", [EventEditWindow,"Events","event_ID","event_Title:event_short_desc"])
                    combo.addItem("Individual",[NPCEditWindow,"Individuals","individual_ID","indiv_Name"])
                    lay.addWidget(combo)

                    buttonBox=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
                    buttonBox.accepted.connect(dialog.accept)
                    buttonBox.rejected.connect(dialog.close)
                    lay.addWidget(buttonBox)

                    if dialog.exec_():
                        combonew=combo.currentData()
                        widget=combonew[0]
                        widget=widget(id=None, new=True, notes={"notes":obj.text()})
                        widget.setExit(self.DraftboardProp_onExit,
                                       onDecline=lambda: ex.updateFactory(obj.labelData["note_ID"],[None],
                                                                          "Notes", ["note_Checked"]),
                                       onApply=lambda: ex.updateFactory(obj.labelData["note_ID"],[combonew[3]],
                                                                        "Notes", ["note_Content"]))
                        id=widget.returnID()
                        ex.updateFactory(obj.labelData["note_ID"],
                                         [combonew[1] + ":" + str(id)],
                                         "Notes", ["note_Checked"])
                        self.man_Draftboard_startpageStack.addWidget(widget)
                        self.man_Draftboard_startpageStack.setCurrentWidget(widget)
                    else:
                        self.man_Draftboard_btn_convert.setChecked(False)
                        self.load_Draftboard_GraphicScene()



        if event.type()== QEvent.MouseButtonPress and event.button() == Qt.RightButton:
            pass
            #if type(obj)== DataLabel:
             #   self.path_ObjectA=obj

        if event.type()==QEvent.MouseButtonDblClick and event.button() == Qt.LeftButton:
            self.path_ObjectA = None
            if type(obj)==DataLabel and self.last_obj.lbl_parent!= obj.lbl_parent:
                self.last_obj = obj
                self.eventPos = event.globalPos()
                self.openTextCreator(event, obj=obj)

            elif type(obj)== QGraphicsView and self.eventPos!=event.globalPos():    #positioncheck
                self.openTextCreator(event)


        return super().eventFilter(obj,event)

    def openEditWindow(self, obj, dialog,collection):
        dialog.close()
        text=""
        for item in collection:
            if item.checkState():
                text += item.text()
                text += ":"
        text = text.rstrip(":")
        ex.updateFactory(obj.labelData["note_ID"], [text], "Notes", ["note_Content"])

        listeLybraries={"Sessions":SessionEditWindow,"Events":EventEditWindow,"Individuals":NPCEditWindow}
        widget = listeLybraries[obj.linked[0]]
        widget = widget(id=obj.linked[1])
        widget.setExit(self.DraftboardProp_onExit)

        self.man_Draftboard_startpageStack.addWidget(widget)
        self.man_Draftboard_startpageStack.setCurrentWidget(widget)

    def openTextCreator(self,event, obj=None):
        if event.button()==Qt.LeftButton:

            Pos=self.man_Draftboard_graphicView.mapToScene(event.pos())
            xPos=Pos.x()
            yPos=Pos.y()
            msg=QDialog()
            lay=QVBoxLayout()
            msg.setLayout(lay)



            collection=[]
            if obj!=None:

                if obj.linked!=None:
                    button = QPushButton("edit Details")
                    lay.addWidget(button)
                    for item in obj.textData:
                        check=QCheckBox(item)
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
                if obj==None:
                    note_ID=ex.newFactory(data={"note_Content":text.toPlainText()},library="Notes")
                    label=QLabel()
                    label.setText(text.toPlainText())
                    label.setFrameShape(1)
                    label.setWordWrap(True)
                    label.setAlignment(Qt.AlignLeft)
                    label.setAlignment(Qt.AlignVCenter)
                    label.setGeometry(100, 100, label.sizeHint().width() + 2,
                                      label.sizeHint().height() + 4)

                    newX = int(xPos - label.width() / 2)
                    newY = int(yPos - label.height() / 2)

                    id=ex.newFactory(
                        data={"note_ID": note_ID, "draftbook_ID": self.man_Draftboard_menu_selDB.currentData(),
                              "xPos": newX, "yPos": newY,"height":label.height(),"width":label.width()},
                        library="Notes_Draftbook_jnt")



                elif obj.linked!=None:
                    text=""
                    for item in collection:
                        if item.checkState():
                            text+= item.text()
                            text+= ":"
                    text=text.rstrip(":")
                    ex.updateFactory(obj.labelData["note_ID"], [text], "Notes", ["note_Content"])

                else:
                    ex.updateFactory(obj.labelData["note_ID"],[text.toPlainText()],"Notes",["note_Content"])

            self.load_Draftboard_GraphicScene(True)



    def load_Draftboard_GraphicScene(self, move=False):
        notes=ex.searchFactory(str(self.man_Draftboard_menu_selDB.currentData()),"Notes_Draftbook_jnt",attributes=["draftbook_ID"],
                               innerJoin="LEFT JOIN Notes ON Notes_Draftbook_jnt.note_ID = Notes.note_ID", dictOut=True)

        labels=[]
        for note in notes:

            label = DataLabel()
            textData=None
            label.textData=None

            if note["note_Checked"]!=None:
                label.setLink(note["note_Checked"].split(":"))
                textData=ex.getFactory(label.linked[1],label.linked[0],dictOut=True)


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

            label.setWordWrap(True)
            label.labelData={}
            label.labelData["note_ID"]=note["note_ID"]
            label.labelData["pos_ID"] = note["note_DB_ID"]
            label.setAlignment(Qt.AlignLeft)
            label.setAlignment(Qt.AlignVCenter)
            label.setFrameStyle(1)
            label.installEventFilter(self)

            label.setGeometry(note["xPos"], note["yPos"],label.sizeHint().width()+2,
                              label.sizeHint().height()+4)



            if note["height"]!=label.height() or note["width"]!=label.width() or move==True:
                newHeight=label.height()
                newWidth=label.width()
                newxPos=int(note["xPos"]+(note["width"]-label.width())/2)
                newyPos=int(note["yPos"]+(note["height"]-label.height())/2)
                ex.updateFactory(label.labelData["pos_ID"],[newxPos,newyPos,newHeight,newWidth],"Notes_Draftbook_jnt",["xPos","yPos","height","width"])


                minX=ex.searchFactory(self.man_Draftboard_menu_selDB.currentData(),"Notes_Draftbook_jnt",
                                      attributes=["draftbook_ID"],OrderBy="Notes_Draftbook_jnt.xPos ASC",
                                      output=("Notes_Draftbook_jnt.xPos"))[0][0]-200
                maxX=ex.searchFactory(self.man_Draftboard_menu_selDB.currentData(),"Notes_Draftbook_jnt",
                                      attributes=["draftbook_ID"],OrderBy="Notes_Draftbook_jnt.xPos+Notes_Draftbook_jnt.width DESC",
                                      output=("Notes_Draftbook_jnt.xPos+Notes_Draftbook_jnt.width"))[0][0]+200
                minY=ex.searchFactory(self.man_Draftboard_menu_selDB.currentData(),"Notes_Draftbook_jnt",
                                      attributes=["draftbook_ID"],OrderBy="Notes_Draftbook_jnt.yPos ASC",
                                      output=("Notes_Draftbook_jnt.yPos"))[0][0]-200
                maxY=ex.searchFactory(self.man_Draftboard_menu_selDB.currentData(),"Notes_Draftbook_jnt",
                                      attributes=["draftbook_ID"],OrderBy="Notes_Draftbook_jnt.yPos+Notes_Draftbook_jnt.height DESC",
                                      output=("Notes_Draftbook_jnt.yPos + Notes_Draftbook_jnt.height"))[0][0]+200


                ex.updateFactory(self.man_Draftboard_menu_selDB.currentData(),[minX,minY,maxY-minY,maxX-minX],"Draftbooks", attributes=["draftbook_xPos","draftbook_yPos","draftbook_height","draftbook_width"])

                self.load_Draftboard_GraphicScene()
                return

            labels.append(label)

        note_ID=[x["note_DB_ID"] for x in notes]

        lineraw=ex.searchFactory("","Note_Note_Pathlib")
        lines=[]
        for path in lineraw:
            if path[1] in note_ID and path[2] in note_ID:
                lines.append(path)


        if self.man_Draftboard_oldScene==None:
            self.man_Draftboard_oldScene = []
        else:
            self.man_Draftboard_oldScene.append(self.man_Draftboard_GraphicScene)

        draftbook = ex.getFactory(self.man_Draftboard_menu_selDB.currentData(), "Draftbooks", dictOut=True)
        if self.man_Draftboard_oldScene==[]:
            self.showFullScreen()
            self.close()
        view = self.man_Draftboard_graphicView.size()



        if type(draftbook) == dict:

            oldView = self.man_Draftboard_graphicView.mapToScene(self.man_Draftboard_graphicView.pos())

            xPos = min(draftbook["draftbook_xPos"], oldView.x() - 20)
            yPos = min(draftbook["draftbook_yPos"], oldView.y() - 20)
            width = max(draftbook["draftbook_xPos"] + draftbook["draftbook_width"], oldView.x() + view.width()) - xPos
            height = max(draftbook["draftbook_yPos"] + draftbook["draftbook_height"],
                         oldView.y() + view.height()) - yPos

            self.man_Draftboard_GraphicScene = QGraphicsScene(xPos, yPos, width, height)
            self.man_Draftboard_graphicView.setScene(self.man_Draftboard_GraphicScene)
        else:
            self.man_Draftboard_GraphicScene = QGraphicsScene(0, 0, view.width(), view.height())
            self.man_Draftboard_graphicView.setScene(self.man_Draftboard_GraphicScene)



        for line in lines:
            index1=note_ID.index(line[1])
            index2=note_ID.index(line[2])

            x = labels[index1].pos().x() + labels[index1].width() / 2
            y = labels[index1].pos().y() + labels[index1].height() / 2

            x1 = labels[index2].pos().x() + labels[index2].width() / 2
            y1 = labels[index2].pos().y() + labels[index2].height() / 2

            self.man_Draftboard_GraphicScene.addLine(x,y,x1,y1,QPen(Qt.black, 2, Qt.SolidLine))

        for label in labels:
            label.lbl_parent=self.man_Draftboard_GraphicScene
            self.man_Draftboard_GraphicScene.addWidget(label)
            pass

        return


    def load_man_Session_searchbar(self):

        newWid=QWidget()
        layout=QHBoxLayout()
        newWid.setLayout(layout)

        if len(self.sessionSearchFilter)>0:
            for item in self.sessionSearchFilter:
                button=QPushButton("delete Filter "+item+": "+self.sessionSearchFilter[item][0])
                button.page=list(self.sessionSearchFilter).index(item)
                button.clicked.connect(lambda: self.btn_man_delFilter('Sessions'))
                layout.addWidget(button, stretch=10)

        if len(self.sessionSearchFilter)<5:
            for number in range(5-len(self.sessionSearchFilter)):
                layout.addWidget(QLabel(""), stretch=10)

        self.man_Session_searchbar_filter_stWid.addWidget(newWid)
        self.man_Session_searchbar_filter_stWid.setCurrentWidget(newWid)

        self.linEditChanged_man_searchSession()

        return

    def load_man_Event_searchbar(self):
        newWid=QWidget()
        layout=QHBoxLayout()
        newWid.setLayout(layout)

        if len(self.eventSearchFilter)>0:
            for item in self.eventSearchFilter:
                button=QPushButton("delete Filter "+item+": "+self.eventSearchFilter[item][0])
                button.page=list(self.eventSearchFilter).index(item)
                button.clicked.connect(lambda: self.btn_man_delFilter('Events'))
                layout.addWidget(button, stretch=10)

        if len(self.eventSearchFilter)<5:
            for number in range(5-len(self.eventSearchFilter)):
                layout.addWidget(QLabel(""), stretch=10)

        self.man_Event_searchbar_filter_stWid.addWidget(newWid)
        self.man_Event_searchbar_filter_stWid.setCurrentWidget(newWid)

        self.linEditChanged_man_searchEvent()

        return

    def load_man_NPC_searchbar(self):

        newWid = QWidget()
        layout = QHBoxLayout()
        newWid.setLayout(layout)

        if len(self.NPCSearchFilter) > 0:
            for item in self.NPCSearchFilter:
                button = QPushButton("delete Filter " + item + ": " + self.NPCSearchFilter[item][0])
                button.page = list(self.NPCSearchFilter).index(item)
                button.clicked.connect(lambda: self.btn_man_delFilter('Individuals'))
                layout.addWidget(button, stretch=10)

        if len(self.NPCSearchFilter) < 5:
            for number in range(5 - len(self.NPCSearchFilter)):
                layout.addWidget(QLabel(""), stretch=10)

        self.man_NPC_searchbar_filter_stWid.addWidget(newWid)
        self.man_NPC_searchbar_filter_stWid.setCurrentWidget(newWid)

        self.linEditChanged_man_searchNPC()

        return

    
    def load_man_source_Filedialog(self, mode):

        self.chooseDialog.close()

        dialog = QFileDialog()
        if mode:
            dialog.setWindowTitle("open Setting Database")
        else:
            dialog.setWindowTitle("open Campaign Database")

        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter("Databases (*.db)")
        if dialog.exec_():
            if not ex.checkLibrary(dialog.selectedFiles()[0],
                                   mode):  # checklibrary return missing tables in database, empty list [none missing] ==False

                if mode:  # true = Settingmode, false= Campaignmode
                    ex.DataStore.Settingpath = dialog.selectedFiles()[0]
                    # fehlt: überprüfen, ob der Campagnenpfad mit dem Settingpfad kompatibel ist
                else:
                    ex.DataStore.path = dialog.selectedFiles()[0]
                    self.linEditChanged_man_searchNPC()
                    self.linEditChanged_man_searchSession()
                    self.linEditChanged_man_searchEvent()
            else:
                dialog2 = QMessageBox()
                dialog2.setText('select Valid Database')
                dialog2.exec_()
                self.load_man_source_Filedialog(mode)


    def load_ses_NpcInfo(self, custId=False):

        if custId==False:
            print(custId)
            id = self.sender().page
        else:
            id=custId

        print("go go", id, custId)
        NPCWin = ViewNpc(id, self.load_ses_NpcInfo)
        self.ses_cen_stWid.addWidget(NPCWin)
        self.ses_cen_stWid.setCurrentWidget(NPCWin)
        if self.ses_cen_stWid.count() > 1:
            self.ses_cen_stWid.layout().takeAt(0)

    
    def openInfoBox(self,text,delay=3000):

        counter=0
        textNew =""
        for object in text.split(" "):
            counter += len(object)
            while len(object)>20:
                textNew+=object[0:20]+"-\n"
                object=object[20:len(object)]
                continue
            if counter>20:
                counter=0
                textNew+="\n"
                textNew+=object +" "
            else:
                textNew += object+" "


        self.infoBox = QDialog()

        self.infoBox.setWindowFlags(Qt.CustomizeWindowHint)
        infoboxLay=QVBoxLayout()
        self.infoBox.setLayout(infoboxLay)
        infoboxLay.addWidget(QLabel(textNew),alignment=Qt.Alignment(4))
        self.timer2 = QTimer()
        self.timer2.timeout.connect(self.infoBox.close)
        self.timer2.start(delay)
        ph = self.geometry().height()
        pw = self.geometry().width()
        px = self.geometry().x()
        py = self.geometry().y()
        #self.infoBox.move(px+pw -dw, py + ph - dh)
        self.infoBox.setGeometry(px+pw -250, py + ph - 130, 220, 100)
        self.infoBox.open()

    def streamEncode(self):
        streamSave = self.temp_streamSave.copy()
        text = ""
        for set in streamSave:
            text += set[0] + "%€%" + set[1] + "§€§"
        text = text.rstrip("§€§")
        return text

    def streamDecode(self, id):
        values = ex.getFactory(id, 'Sessions', dictOut=True)['session_stream']
        if values != None and values != "":
            values = values.split("§€§")
            listedValues = [tuple(x.split("%€%")) for x in values]
            return listedValues
        else:
            return []

    def timer_start(self, delay=500, function=None):
        if not function:
            function = self.linEditChanged_man_searchNPC

        self.timer.timeout.connect(function)
        self.timer.start(delay)

    def NPCProp_onExit(self):
        self.man_NPC_cen_stackWid.setCurrentIndex(0)
        self.man_NPC_searchresultWid.resultUpdate()
        for index in reversed(range(self.man_NPC_cen_stackWid.count())):
            if index != 0:
                self.man_NPC_cen_stackWid.removeWidget(self.man_NPC_cen_stackWid.widget(index))

        searchresult = ex.searchFactory(self.man_NPC_searchBar_lEdit.text(), "Individuals", shortOut=True,
                                        Filter=self.NPCSearchFilter, searchFulltext=self.searchMode)
        self.man_NPC_searchresultWid.resultUpdate(searchresult)
        return
    
    def SessionProp_onExit(self):
        self.man_Session_cen_stackWid.setCurrentIndex(0)
        for index in reversed(range(self.man_Session_cen_stackWid.count())):
            if index != 0:
                self.man_Session_cen_stackWid.removeWidget(self.man_Session_cen_stackWid.widget(index))
        last_search=ex.searchFactory(self.man_Session_searchBar_lEdit.text(),'Sessions',shortOut=True,
                                     Filter=self.sessionSearchFilter,searchFulltext=self.searchMode)

        self.man_Session_searchresultWid.resultUpdate(last_search)
        return

    def EventProp_onExit(self):
        self.man_Event_cen_stackWid.setCurrentIndex(0)
        for index in reversed(range(self.man_Session_cen_stackWid.count())):
            if index != 0:
                self.man_Session_cen_stackWid.removeWidget(self.man_Session_cen_stackWid.widget(index))
        last_search=ex.searchFactory(self.man_Event_searchBar_lEdit.text(),'Events',shortOut=True,
                                     Filter=self.sessionSearchFilter,searchFulltext=self.searchMode)

        self.man_Event_searchresultWid.resultUpdate(last_search)
        return
    
    def DraftboardProp_onExit(self):
        self.man_Draftboard_startpageStack.setCurrentIndex(0)
        for index in reversed(range(self.man_Draftboard_startpageStack.count())):
            if index != 0:
                self.man_Draftboard_startpageStack.removeWidget(self.man_Draftboard_startpageStack.widget(index))

        self.load_Draftboard_GraphicScene()
        return
    #endregion

    #   region searchdialog unimplimented
    def openSearchDialog(self,text,searchIn:str, createNew=False):

        self.searchDialogResult=[]
        self.searchDialog= QDialog()
        searchDialog_layout= QVBoxLayout()
        self.searchDialog.setLayout(searchDialog_layout)

        searchDialog_layout.addWidget(QLabel(text), stretch=10)

        self.searchDialog_label = QLabel("\n")
        searchDialog_layout.addWidget(self.searchDialog_label)

        self.searchDialog_lineEdit= QLineEdit()
        self.searchDialog_lineEdit.textEdited.connect(lambda : self.timer_start(500,lambda: self.lineEditChanged_searchDialog(searchIn)))
        searchDialog_layout.addWidget(self.searchDialog_lineEdit)
        
        if createNew:
            self.searchDialog_Btn_createNew = QPushButton ("create New")
            self.searchDialog_Btn_createNew.clicked.connect(lambda: self.btn_fastCreate(searchIn))
            searchDialog_layout.addWidget(self.searchDialog_Btn_createNew)

        searchDialog_scroll = QScrollArea()
        searchDialog_scroll.setWidgetResizable(True)
        searchDialog_layout.addWidget(searchDialog_scroll)

        searchDialog_Result=QWidget()
        self.searchDialog_Result_lay = QVBoxLayout()
        searchDialog_Result.setLayout(self.searchDialog_Result_lay)
        searchDialog_scroll.setWidget(searchDialog_Result)

        searchDialog_button_layHB = QHBoxLayout()
        searchDialog_layout.addLayout(searchDialog_button_layHB)

        okButton= QPushButton("apply Changes")
        okButton.clicked.connect(self.searchDialog.close)
        searchDialog_button_layHB.addWidget(okButton)

        cancelButton = QPushButton("cancel")
        cancelButton.clicked.connect(self.btn_searchDialog_cancel)
        searchDialog_button_layHB.addWidget(cancelButton)

        self.lineEditChanged_searchDialog(searchIn)
        self.searchDialog.exec()
        return self.searchDialogResult
    
    def btn_fastCreate(self,Class):

        helpInstanceList=[None for x in range(Class.requiredVar)]
        helpInstance=Class(*helpInstanceList)

        self.fastCreateDialog=QDialog()
        self.fastCreateDialog_layout=QVBoxLayout()
        self.fastCreateDialog.setLayout(self.fastCreateDialog_layout)

        for i in range(Class.requiredVar):
            label =QLabel("%s:" %(helpInstance.__dict__[list(helpInstance.__dict__)[i]]))
            self.fastCreateDialog_layout.addWidget(label)

            lineedit=QLineEdit()
            self.fastCreateDialog_layout.addWidget(lineedit)

        layout2= QHBoxLayout()

        button=QPushButton("create")
        button.clicked.connect(self.btn_fastcreate_create)
        layout2.addWidget(button)

        button = QPushButton("cancel")
        button.clicked.connect(self.fastCreateDialog.close)
        layout2.addWidget(button)
        self.fastCreateDialog_layout.addLayout(layout2)

        self.fastcreate_argumentList=[]
        self.fastCreateDialog.exec()
        instance=Class(*self.fastcreate_argumentList)

        return instance

    def btn_fastcreate_create(self):

        getValues=[]
        counter=0

        for index in range(self.fastCreateDialog_layout.count()):
            if self.fastCreateDialog_layout.itemAt(index) is not None:
                item = self.fastCreateDialog_layout.itemAt(index).widget()
            else:
                continue
            if type(item) == QLineEdit:
                counter+=1
                if item.text() != "":
                    getValues.append(item.text())



        self.fastcreate_argumentList=getValues
        if len(getValues)<counter:
            msgBox = QMessageBox()
            msgBox.setText("Bitte alle Felder ausfüllen!")
            msgBox.exec()

        else:
            self.fastCreateDialog.close()
    def btn_searchDialog_cancel(self):
        self.searchDialogResult = []
        self.searchDialog.close()

    def btn_searchDialog_choose(self,instance):
        self.searchDialogResult = instance
        self.searchDialog_label.setText("chosen: \n"+str(instance))

    def lineEditChanged_searchDialog(self,searchIn):
        self.timer.stop()

        clearLayout(self.searchDialog_Result_lay)

        for instance in ex.searchFactory(self.searchDialog_lineEdit.text(),searchIn,shortOut=True):

            button= QPushButton(str(instance))
            button.clicked.connect(lambda: self.btn_searchDialog_choose(instance))
            self.searchDialog_Result_lay.addWidget(button)

    #endregion
    
    
def clearLayout(layout):
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




#region Main program execution


dh.load()
App = QtWidgets.QApplication(sys.argv)
win = MyWindow()
win.show()
App.exec_()
dh.save()
sys.exit()

#endregion