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
OGG._getAnyBends()
#OGG._getFacesMap()

sheet_tree=FCTreeSheet(OGG)


for t in OGG.FacesMap:
	print(t,'-->',OGG.FacesMap[t])

root=list(OGG.FacesMap.keys())[0]
#area=OGG.Faces[root].Area
#ff=list(OGG.FacesByArea)
fba=get_faces_by_area(OGG.Faces,OGG.FacesMap['Faces'])
af=sorted(fba,reverse=True)
tree_filled=False
id_key=0
while (not tree_filled) and (id_key<len(af)):
	id_block=af[id_key]
	block=OGG.FacesByArea[id_block]
	idf1=block[0]
	found=False
	#for bf in OGG.BendedFaces:
	#	if idf1 == bf[0]:
	#		af.remove(bf[1])
	#		print('thk:',OGG.Thk,' ->',bf[0],'-',bf[1],' - bend')
	#		found=True
	#	elif idf1==bf[1]:
	#		af.remove(bf[0])
	#		print('thk:',OGG.Thk,' ->',bf[1],'-',bf[0],' - bend')
    #        found=True
	if not found:
		if len(block)==1 and (id_key<len(af)-1):
			id_key+=1
			id_next_block=af[id_key]
			next_block=OGG.FacesByArea[id_next_block]
			idf2=next_block[0]
		elif len(block)==2:
			idf2=block[1]

		f1=OGG.Faces[idf1]
		f2=OGG.Faces[idf2]
		dist=round(f1.distToShape(f2)[0],1)
		if dist==OGG.Thk:
			print('thk:',dist,' ->',idf1,'-',idf2)
	id_key+=1
#thk=round(f1.distToShape(f2)[0],1)
