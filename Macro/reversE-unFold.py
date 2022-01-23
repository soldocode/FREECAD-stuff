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

def angleBetweenFaces(f1,f2):
    vns1 = f1.normalAt(0,0)
    vns2 = f2.normalAt(0,0)
    #ref=FC.Vector( 0,0,1)
    #a1=math.degrees(ref.getAngle( vns1))
    #a2=math.degrees(ref.getAngle( vns2))
    #return  a1-a2
    return math.degrees(vns1.getAngle(vns2))


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
           #vns1 = face1.normalAt(0,0)
           #vns2 = face2.normalAt(0,0)
           #print('????',vns1.getAngle(vns2))
           #bb.Angle = math.degrees(vns1.getAngle(vns2))
           bb.Angle=angleBetweenFaces(face1,face2)
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
        vals['Axis']=str(branch.Axis)
        vals['FaceUp']=branch.FaceUp
        vals['FaceDown']=branch.FaceDown
        vals['Joints']=[]
        jj=list(branch.Joints)
        for j in jj:
             vals['Joints'].append(branch.Joints[j].ToBranch.FaceUp)
        result[b]=vals
    return result

def toJson(ts):
    return(json.dumps(toDict(ts), indent=4))


def linkedBranches(st,branch_id,id,b_list):
    branch=st.Branches[branch_id]
    #print(branch,id)
    jj=list(branch.Joints)
    for j in jj:
        look=branch.Joints[j].ToBranch.FaceUp
        if id!=look:
            if look not in b_list:b_list.append(look)
            #print(look)
            linkedBranches(st,look,branch_id,b_list)
    return b_list



def vectorToXYZAxisDegrees(v):
    '''
    return [angle to XY plane,
            angle to XZ plane,
            angle to YZ plane]
    '''
    result={'X':0,'Y':0,'Z':0}
    if abs(v.x)==1.0:
        result={'X':0,'Y':90.0*1/v.x,'Z':90.0*1/v.x}
    elif abs(v.y)==1.0:
        result={'X':90.0*1/v.y,'Y':0,'Z':90.0*1/v.y}
    elif abs(v.z)==1.0:
        result={'X':90.0*1/v.z,'Y':90.0*1/v.z,'Z':0}
    else:
        vns1 = FreeCAD.Vector(1,0,0)
        vns2 = FreeCAD.Vector(v.x,0,v.z).normalize()
        result['X'] = math.degrees( vns1.getAngle( vns2 ))
        vns1 = FreeCAD.Vector(0,1,0)
        vns2 = FreeCAD.Vector(v.x,v.y,0).normalize()
        result['Y'] = math.degrees( vns1.getAngle( vns2 ))
        vns1 = FreeCAD.Vector(0,0,1)
        vns2 = FreeCAD.Vector(0,v.y,v.z).normalize()
        result['Z'] = math.degrees( vns1.getAngle( vns2 ))
    print (result)

    return result




def splitTree(st,id_curve):
    tree={'root':id_curve,'before':[],'after':[]}
    if id_curve in st.Branches:
        branch=st.Branches[id_curve]
        jj=list(branch.Joints)
        before_id=branch.Joints[jj[0]].ToBranch.FaceUp
        after_id=branch.Joints[jj[1]].ToBranch.FaceUp
        tree['before'].append(before_id)
        tree['after'].append(after_id)
        tree['before']+=linkedBranches(st,before_id,id_curve,[])
        tree['after']+=linkedBranches(st,after_id,id_curve,[])
        print('SPLITED TREE:',tree)
    return tree


def alignBendToX(st,id_curve):
    '''
    align bend to X axis
    '''
    print ('Start alignBendToX function...')
    if id_curve in st.Branches:
        if st.Branches[id_curve].Class=="Cylinder":
            branch=st.Branches[id_curve]
            pof=branch.PointOfRotation
            axis=branch.Axis
            jj=list(branch.Joints)
            f1=st.FCObject.Faces[branch.Joints[jj[0]].ToBranch.FaceUp]
            f2=st.FCObject.Faces[branch.Joints[jj[1]].ToBranch.FaceUp]
            #print('...faces joint:',faces)
            print('...bend vector:',list(branch.Axis))
            print('...face1 normal:',
                  f1.normalAt(0,0))
            vectorToXYZAxisDegrees(f1.normalAt(0,0))
            print('...face2 normal:',
                  f2.normalAt(0,0))
            vectorToXYZAxisDegrees(f2.normalAt(0,0))
            branches=list(st.Branches)
            for b in branches:
                print('Branch nr ',b)
                if st.Branches[b].Class=="Plane":
                    obj=st.Branches[b].PartFeatureUp
                    print ('obj:',obj)
                    print('placement:',obj.Placement)
                    z_axis = FreeCAD.Vector(0,0,1)
                    y_axis = FreeCAD.Vector(0,1,0)
                    d=vectorToXYZAxisDegrees(axis)
                    obj.Placement=rotateObj(obj,z_axis,pof,d['Z'])
                    obj.Placement=rotateObj(obj,y_axis,pof,d['Y'])
                    obj=st.Branches[b].PartFeatureDown
                    obj.Placement=rotateObj(obj,z_axis,pof,d['Z'])
                    obj.Placement=rotateObj(obj,y_axis,pof,d['Y'])


    return


def unBend(st,id_curve,angle=0.0):
    '''
    input:
     - st = sheetTree
	 - id_curve = face id of curve to unbend
     - angle = angle selected or plane it
    '''
    print()
    print('Start unBend function!!!!!')
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
            print('SWITCH LIST:')
            print(switch_list)


            j_up=branch.Joints[jj[1]].JoinUp
            j_wire=st.FCObject.Faces[j_up[1]].OuterWire
            je=j_wire.Edges[j_up[2]]
            for e in j_wire.Edges:
                 print(e.Vertexes[0].X,e.Vertexes[0].Y,e.Vertexes[0].Z)

            axis=branch.Axis
            print('assi???:', je.Curve.Direction,axis)

            pof=branch.PointOfRotation
            if angle==0.0:
               angle=-branch.Angle
            print('angle:',angle)
            for o in switch_list['after']:
                print('Branch nr ',o)
                if st.Branches[o].Class=="Plane":
                    obj=st.Branches[o].PartFeatureUp
                    print ('obj:',obj)
                    print('placement:',obj.Placement)
                    obj.Placement=rotateObj(obj,axis,pof,angle)
                    obj=st.Branches[o].PartFeatureDown
                    obj.Placement=rotateObj(obj,axis,pof,angle)
                elif st.Branches[o].Class=="Cylinder":
                    obj=st.Branches[o].PartFeatureBendAxis
                    print ('obj:',obj)
                    print('placement:',obj.Placement)
                    obj.Placement=rotateObj(obj,axis,pof,angle)
                    #print ('pof',st.Branches[o].PointOfRotation)
                    #print ('bendaxis',st.Branches[o].PartFeatureBendAxis.Shape.CenterOfMass)
                    st.Branches[o].PointOfRotation=st.Branches[o].PartFeatureBendAxis.Shape.CenterOfMass


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
    #print (sheet_tree.Branches[b].Class)
    if sheet_tree.Branches[b].Class=="Cylinder":
        print('bend:',b)
        #if axis.x+axis.y+axis.z<0:
        #    angle=-angle
        #unBend(sheet_tree,b)
