######################################################
#
#  Riccardo Soldini - riccardo.soldini@gmail.com
#
#  unFold.py - 2020
#
#  Modulo per la decostruzione di parti di carpenteria piegate
#
######################################################

from importlib import reload
import math
import g2
import makEasy
import json
from MeFunctions import *
from MeFreeCADClasses import *
from PySide import QtGui
import FreeCAD as FC
import Part


def createFCSheetDocument(sheetTree):
    doc=FC.newDocument()
    Gui.ActiveDocument=doc
    for b in sheetTree.Branches:
        bb=sheetTree.Branches[b]
        if bb.Class=='Plane':
            feat = doc.addObject("Part::Feature","Face_"+str(bb.FaceUp))
            feat.Shape=bb.ShapeUp
            bb.PartFeatureUp=feat
            feat = doc.addObject("Part::Feature","Face_"+str(bb.FaceDown))
            feat.Shape=bb.ShapeDown
            bb.PartFeatureDown=feat
        if bb.Class=='Cylinder':
           p1=bb.PointOfRotation
           p2=p1+bb.Axis
           l = Part.LineSegment(p1,p2)

           feat = doc.addObject("Part::Feature","BendAxis_"+str(bb.FaceUp))
           feat.Shape= l.toShape()
           bb.PartFeatureBendAxis=feat
           ids = list(bb.Joints.keys())
           print (ids)
           j1=bb.Joints[ids[0]]
           j2=bb.Joints[ids[1]]
           print (ids[0],ids[1])
           face1=OGG.Faces[j1.JoinUp[1]]
           face2=OGG.Faces[j2.JoinUp[1]]
           vns1 = face1.normalAt(0,0)
           vns2 = face2.normalAt(0,0)
           bb.Angle = math.degrees(vns1.getAngle(vns2))
    doc.recompute()
    Gui.SendMsgToActiveView("ViewFront")
    Gui.SendMsgToActiveView("ViewFit")
    return doc

def rotateObj(obj,axis,rotationPoint,angle):
    return Placement(FC.Vector(0,0,0), Rotation(axis,angle),rotationPoint).multiply(obj.Placement)

def toDict(ts):
    result={}
    for b in ts.Branches:
        vals={}
        branch=ts.Branches[b]
        vals['Class']=branch.Class
        vals['Angle']=branch.Angle
        vals['Axis']=branch.Axis
        vals['FaceUp']=branch.FaceUp
        vals['FaceDown']=branch.FaceDown
        vals['Joints']=[]
        jj=list(branch.Joints)
        for j in jj:
             vals['Joints'].append(branch.Joints[j].ToBranch.FaceUp)
        result[b]=vals
    return result

def linkedBranches(st,branch_id,id,b_list):
    branch=st.Branches[branch_id]
    print(branch,id)
    jj=list(branch.Joints)
    for j in jj:
        look=branch.Joints[j].ToBranch.FaceUp
        if id!=look:
            if look not in b_list:b_list.append(look)
            print(look)
            linkedBranches(st,look,branch_id,b_list)
    return b_list

def unBend(st,id_curve,angle=0.0):
    '''
    input:
     - st = sheetTree
	 - id_curve = face id of curve to unbend
     - angle = angle selected or plane it
    '''
    msg=''
    if id_curve in st.Branches:
        if st.Branches[id_curve].Class=="Cylinder":
            branch=st.Branches[id_curve]
            msg='unbend curve  '+str(id_curve)
            switch_list={'before':[],'after':[]}
            jj=list(branch.Joints)
            before_id=branch.Joints[jj[0]].ToBranch.FaceUp
            after_id=branch.Joints[jj[1]].ToBranch.FaceUp
            switch_list['before'].append(before_id)
            switch_list['after'].append(after_id)
            switch_list['before']+=linkedBranches(st,before_id,id_curve,[])
            switch_list['after']+=linkedBranches(st,after_id,id_curve,[])
            print(switch_list)

            axis=branch.Axis
            pof=branch.PointOfRotation
            if angle==0.0:
               angle=-branch.Angle
            for o in switch_list['after']:
                print('Branch nr ',o)
                if st.Branches[o].Class=="Plane":
                    obj=st.Branches[o].PartFeatureUp
                    print ('obj:',obj)
                    print('placement:',obj.Placement)
                    if axis.x+axis.y+axis.z<0:
                        angle=-angle
                    print('axis',axis.x+axis.y+axis.z)
                    obj.Placement=rotateObj(obj,axis,pof,angle)
                    obj=st.Branches[o].PartFeatureDown
                    obj.Placement=rotateObj(obj,axis,pof,angle)
                elif st.Branches[o].Class=="Cylinder":
                    obj=st.Branches[o].PartFeatureBendAxis
                    print ('obj:',obj)
                    print('placement:',obj.Placement)
                    obj.Placement=rotateObj(obj,axis,pof,angle)


        else: msg='not a curve!'
    else: msg='id not avaible!'
    return msg


print ("Let's begin...")
pp = pprint.PrettyPrinter(indent=4)

sel=Gui.Selection.getSelectionEx()[0]
obj=sel.Object
OGG=FCObject(obj)
OGG.parse()
OGG._getThickness()
OGG._getAnyBends()

#if sheet_tree: del sheet_tree

sheet_tree=FCTreeSheet(OGG)


print (' ')
for b in sheet_tree.Branches:
    bb=sheet_tree.Branches[b]
    print ('faces:',bb.FaceUp,bb.FaceDown)
    print (b,bb.Class,bb.Joints)
    print (bb.FaceUp,bb.FaceDown)
    if bb.Class=='Cylinder':
        print(bb.Radius,bb.Axis,bb.PointOfRotation)


createFCSheetDocument(sheet_tree)

for b in sheet_tree.Branches:
    print (sheet_tree.Branches[b].Class)
    if sheet_tree.Branches[b].Class=="Cylinder":
        unBend(sheet_tree,b,sheet_tree.Branches[b].Angle)
