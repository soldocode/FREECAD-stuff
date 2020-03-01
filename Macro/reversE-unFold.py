########################################################################
#                                                                      #
#  Riccardo Soldini - riccardo.soldini@gmail.com                       #
#                                                                      #
#  unFold.py - 2020                                                    #
#                                                                      #
#  Modulo per la decostruzione di parti di carpenteria piegate         #
#                                                                      #
########################################################################


import math
import g2
import makEasy
import json
from MeFunctions import *
from MeFreeCADClasses import *
from PySide import QtGui


print ("Let's begin...")
pp = pprint.PrettyPrinter(indent=4)

sel=Gui.Selection.getSelectionEx()[0]
obj=sel.Object
OGG=FCObject(obj)
OGG.parse()
OGG._getThickness()
OGG._getAnyBlends()

sheet_tree=FCTreeSheet(OGG)
