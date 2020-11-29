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
import FreeCAD as FC
import Part


print ("Let's begin...")
pp = pprint.PrettyPrinter(indent=4)

sel=Gui.Selection.getSelectionEx()[0]
obj=sel.Object
OGG=FCObject(obj)
OGG.parse()
OGG._getThickness()
OGG._getAnyBends()

sheet_tree=FCTreeSheet(OGG)



for b in sheet_tree.Branches:
    bb=sheet_tree.Branches[b]
    print (b,bb.Class,bb.Joints)
    print (bb.FaceUp,bb.FaceDown)
    if bb.Class=='Cylinder':
        print(bb.Radius,bb.Axis,bb.PointOfRotation)


doc=FC.newDocument()
Gui.ActiveDocument=doc
for b in sheet_tree.Branches:
    bb=sheet_tree.Branches[b]
    f_up=OGG.Faces[bb.FaceUp].copy()
    f_down=OGG.Faces[bb.FaceDown].copy()
    Part.show(f_up)
    Part.show(f_down)
       
Gui.SendMsgToActiveView("ViewFit")
