#ToDo Roadmap:
# check if values are changed editViews
# stream rework
# setExit on automatic close
# implement move by menu
# opening same draftboard views parallel, opening same DataEdits parallel
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
