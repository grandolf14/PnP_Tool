#ToDo Roadmap:
# switchWindowMode rework
# tabNames
# setExit on automatic close
# global updateData signal if anything was changed
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
# open old (missing campaign) values for json.loads in lastSessionValues leads to crash
# pycharm sometimes crashes with -1073741819 exitCode, looks lika a pycharm problem


import sys

from PyQt5 import QtWidgets

from UI_MainWindow import MyWindow

App = QtWidgets.QApplication(sys.argv)
win = MyWindow()
win.show()
App.exec_()
sys.exit()
