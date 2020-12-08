######################################################
#                                                                                                                             
#  Riccardo Soldini - riccardo.soldini@gmail.com                                                      
#                                                                                                                           
#  unFold.py - 2020                                                                                               
#                                                                                                                          
#  Modulo per la decostruzione di parti di carpenteria piegate                                  
#                                                                                                                         
######################################################


import math
import g2
import makEasy
import json
from MeFunctions import *
from MeFreeCADClasses import *
from PySide import QtGui
import FreeCAD as FC
import Part

def rotateObj(obj,axis,rotationPoint,angle):
    return Placement(Vector(0,0,0), Rotation(axis,angle),rotationPoint).multiply(obj.Placement)

print ("Let's begin...")
pp = pprint.PrettyPrinter(indent=4)

sel=Gui.Selection.getSelectionEx()[0]
obj=sel.Object
OGG=FCObject(obj)
OGG.parse()
OGG._getThickness()
OGG._getAnyBends()

sheet_tree=FCTreeSheet(OGG)


print (' ')
for b in sheet_tree.Branches:
    bb=sheet_tree.Branches[b]
    print ('faces:',bb.FaceUp,bb.FaceDown)
    print (b,bb.Class,bb.Joints)
    print (bb.FaceUp,bb.FaceDown)
    if bb.Class=='Cylinder':
        print(bb.Radius,bb.Axis,bb.PointOfRotation)


doc=FC.newDocument()
Gui.ActiveDocument=doc
for b in sheet_tree.Branches:
    bb=sheet_tree.Branches[b]
    if bb.Class=='Plane':
        f_up=OGG.Faces[bb.FaceUp].copy()
        f_down=OGG.Faces[bb.FaceDown].copy()
        Part.show(f_up)
        Part.show(f_down)
    if bb.Class=='Cylinder':
       p1=bb.PointOfRotation
       p2=p1+bb.Axis
       l = Part.LineSegment(p1,p2)
       shape = l.toShape()
       Part.show(shape)
       ids = list(bb.Joints.keys()) 
       print (ids)
       j1=bb.Joints[ids[0]]
       j2=bb.Joints[ids[1]]
       print (ids[0],ids[1])
       face1=OGG.Faces[j1.JoinUp[1]]
       face2=OGG.Faces[j2.JoinUp[1]]
       vns1 = face1.normalAt(0,0)
       vns2 = face2.normalAt(0,0)
       alpha = math.degrees( vns1.getAngle( vns2 ) )
       print ('angle of bend:',alpha)   
       f_up.Placement=rotateObj(f_up,bb.Axis,p1,90.0)
       
       
Gui.SendMsgToActiveView("ViewFit")
