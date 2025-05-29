#ToDo Roadmap:
# implement SessionView data Var instead of Userdata.today etc
# update libraries_default
# global updateData signal if anything was changed
# save data on new campaign open and main close
# update save method @ models to json save
# remodel campaign load process
# opening same draftboard views parallel, opening same DataEdits parallel
# tabNames
# doc
# rename ViewDraftbook vars
# implement family Tree
# GridSnap in Draftbook
# Calender view


#ToDo check Errors:
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
