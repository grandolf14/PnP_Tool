#ToDo Roadmap:
# check Libraries_default/ push
# implement SessionView data Var instead of Userdata.today etc
# global updateData signal if anything was changed
# remodel campaign load process
# opening same draftboard views parallel, opening same DataEdits parallel
# tabNames
# rename ViewDraftbook vars
# implement family Tree
# GridSnap in Draftbook
# Calender view


#ToDo check Errors:
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
