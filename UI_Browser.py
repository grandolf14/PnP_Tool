
from PyQt5.QtCore import  Qt
from PyQt5.QtWidgets import  QLabel, QWidget, QPushButton, QHBoxLayout, QGridLayout, QVBoxLayout, QStackedWidget, \
    QScrollArea, QFrame

class Resultbox(QStackedWidget):
    """Widget for dynamic display of data lists with buttons for data manipulation.

    """
    def __init__(self):
        """initializes empty Resultbox

        """
        super().__init__()
        self.setPref()
        self.source = None
        self.resultUpdate()

    def setPref(self, reloadBottom=False, paintItemFrame=False, paintItemLight=[], buttonList=None, spacer=True, paintLight:list=[None], standardbutton=None,standardButtonVerticalAlignment=True, ignoreIndex=[0], spacing=10, col=4):
        """ sets the preferences for the specific Resultbox

        :param reloadBottom: Bool, optional
                reloads the Resultbox scroll widget bottom
        :param paintItemFrame: Bool, optional
                adds a frame for each dataset
        :param paintItemLight: List[int], optional
                List of the item indexes that should be fully painted in light grey
        :param buttonList: list of [buttonName, function without parenthesis], optional
                adds specified Buttons for each dataset, self.sender().page = item[0] of dataset
        :param spacer: Bool, optional
                adds spaceritems between the single datasets
        :param paintLight: List of int
                specifies which index of the Dataset should be painted in light grey
        :param standardbutton: function without parenthesis, optional
                defines which function to call when the button gets pressed
        :param standardButtonVerticalAlignment: Bool, optional
                align the contents in the button vertical [True] or horizontal [False]
        :param ignoreIndex: list of int, optional
                do not display the contents of each dataset with chosen index
        :param spacing: int, optional
                defines spacing span
        :param col: int, optional
                how many columns should the Resultbox have
        :return: -> None
        """
        self.buttons = buttonList
        self.spacing = spacing
        self.col = col
        self.standardbutton=standardbutton
        self.standardButtonVerticalAlignment=standardButtonVerticalAlignment
        self.ignoreIndex=ignoreIndex
        self.paintLight=paintLight
        self.paintItemLight=paintItemLight
        self.spacer=spacer
        self.reloadBottom=reloadBottom
        self.paintItemFrame=paintItemFrame

    def setSource(self, source):
        self.source = source

    def resultUpdate(self, manualResult=None):
        """repaints the resultbox with given data as content

        :param manualResult: list of datasets, optional
            the content of the Resultbox
        :return: ->None
        """

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

                    if itemIndex in self.paintItemLight:
                        label.setStyleSheet('color: grey')

                    elif lineIndex in self.paintLight:
                        label.setStyleSheet('color: grey')
                        font=label.font()
                        font.setItalic(True)
                        label.setFont(font)



            if not self.standardButtonVerticalAlignment:
                if self.buttons==None:
                    if itemIndex in self.paintItemLight:
                        mainButton.setStyle('color: grey')
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