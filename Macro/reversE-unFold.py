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
#OGG._getFacesMap()

sheet_tree=FCTreeSheet(OGG)


for t in OGG.FacesMap:
	print(t,'-->',OGG.FacesMap[t])

root=list(OGG.FacesMap.keys())[0]
#area=OGG.Faces[root].Area
#ff=list(OGG.FacesByArea)
aa=sorted(OGG.FacesByArea,reverse=True)
tree_filled=False
id_key=0
while (not tree_filled) and (id_key<len(aa)):
    #verifica se il blocco è multiplo
    id_block=aa[id_key]
    block=OGG.FacesByArea[id_block]
    if len(block)==1 and (id_key<len(aa)-1):
        id_key+=1
        id_compare=aa[id_key]
        compare=OGG.FacesByArea[id_compare]
        f1=OGG.Faces[block[0]]
        f2=OGG.Faces[compare[0]]
        print(block[0],compare[0])
    elif len(block)==2:
        f1=OGG.Faces[block[0]]
        f2=OGG.Faces[block[1]]
        print(block[0],block[1])
    #print(block,'-',len(block))
    #print(compare,'-',len(compare))
    #f1=OGG.Faces[block[0]]
    #f2=OGG.Faces[compare[0]]
    print('thk:',round(f1.distToShape(f2)[0],1))
    id_key+=1
#thk=round(f1.distToShape(f2)[0],1)
