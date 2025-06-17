#ToDo Roadmap:
# stream rework
# implement move by menu
# fighter weapons
# implement family Tree
# GridSnap in Draftbook
# Calender view


#ToDo check Errors:

#TODO Known Errors:
# Drafbook dimension does not shrink when labels are removed
# draftboard.update sometimes leads to view jumps


import sys

from PyQt5 import QtWidgets

from UI_MainWindow import MyWindow

App = QtWidgets.QApplication(sys.argv)
win = MyWindow()
win.show()
App.exec_()
sys.exit()
