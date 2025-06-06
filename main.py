#ToDo Roadmap:
# check dataChanged signal for draftbook ->Automatic update
# tabNames & check if tab already in tabs
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
# choose setting filedialog should start in Libraries/Setting
# draftboard.update sometimes leads to view jumps
# Drafbook dimension does not shrink when labels are removed


import sys

from PyQt5 import QtWidgets

from UI_MainWindow import MyWindow

App = QtWidgets.QApplication(sys.argv)
win = MyWindow()
win.show()
App.exec_()
sys.exit()
