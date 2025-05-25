#ToDo Roadmap:
# implement family browser
# Calender view

#ToDo check Errors:
# choose setting filedialog should start in Libraries/Setting
# linked datalabels misses a newline
# Drafbook dimension does not shrink when labels are removed

#TODO Known Errors:
# pycharm sometimes crashes with -1073741819 exitCode, looks lika a pycharm problem


import sys

from PyQt5 import QtWidgets

from Models import ApplicationValues
from AppVar import DataStore as DS
from UI_MainWindow import MyWindow


ApplicationValues.load()
App = QtWidgets.QApplication(sys.argv)
DS.win_intern = MyWindow()
DS.win_intern.show()
App.exec_()
ApplicationValues.save()
sys.exit()
