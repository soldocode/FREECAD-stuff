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
                obj=st.Branches[o].PartFeatureUp
                print ('obj:',obj)
                print('placement:',obj.Placement)
                obj.Placement=rotateObj(obj,axis,pof,angle)
                obj=st.Branches[o].PartFeatureDown
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
        #f_up=OGG.Faces[bb.FaceUp].copy()
        #f_down=OGG.Faces[bb.FaceDown].copy()
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
       alpha = math.degrees( vns1.getAngle( vns2 ) )
       print ('angle of bend:',alpha)
       #f_up.Placement=rotateObj(f_up,bb.Axis,p1,90.0)

pp.pprint(toDict(sheet_tree))
Gui.SendMsgToActiveView("ViewFront")
Gui.SendMsgToActiveView("ViewFit")

#unBend(sheet_tree,5,10)
doc.recompute()
#unBend(sheet_tree,14)
