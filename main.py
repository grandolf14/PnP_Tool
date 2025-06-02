#ToDo Roadmap:
# update location in all Libraries
# check Libraries_default/ push
# global updateData signal if anything was changed
# remodel campaign load process
# opening same draftboard views parallel, opening same DataEdits parallel
# tabNames
# fighter weapons
# implement family Tree
# GridSnap in Draftbook
# Calender view


#ToDo check Errors:
# rmb menu draftboards edit and move
# if i click on an datalabel and click on it again to release it the bue color gets black
# open old (missing campaign) values for json.loads in lastSessionValues leads to crash
# setExit on automatic close
# choose setting filedialog should start in Libraries/Setting
# linked datalabels misses a newline
# Drafbook dimension does not shrink when labels are removed

#TODO Known Errors:
# pycharm sometimes crashes with -1073741819 exitCode, looks lika a pycharm problem


import sys

from PyQt5 import QtWidgets

from Models import ApplicationValues
from UI_MainWindow import MyWindow


ApplicationValues.load()
App = QtWidgets.QApplication(sys.argv)
win = MyWindow()
win.show()
App.exec_()
sys.exit()
