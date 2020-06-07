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



#def get_branches(face_up_from,map,couples):
#
#	next_calls=[]
#	branches=[]
#	face_down=None
#	for c in couples:
#		if face_up_from==c[0]:
#			face_down_from=c[1]
#			couple=c
#		if face_up_from==c[1]:
#			face_down_from=c[0]
#			couple=c
	#print ('...lookin for face up from ',face_up_from)

#	links_up=map[face_up_from]
	#print ('links up:',links_up)
#	for geo_up_from in links_up:
#		for p in couples:
#			face_up_to=links_up[geo_up_from][0]
#			if face_up_to in p:
				#print (face_up_to,' found in',p,' with geo id ',geo_up_from)
				#print ('...lookin for face down from ',face_down_from)
#				links_down=map[face_down_from]
				#print('links_down:',links_down)
#				for geo_down_from in links_down:
#					face_down_to=links_down[geo_down_from][0]
#					if face_down_to in p:
						#print (face_down_to,' found in',p,' with geo id ',geo_down_from)
#						branches.append(dict(face_up_from=face_up_from,
#											 geo_up_from=geo_up_from,
#											 face_up_to=face_up_to,
#											 geo_up_to=links_up[geo_up_from][1],
#											 face_down_from=face_down_from,
#											 geo_down_from=geo_down_from,
#											 face_down_to=face_down_to,
#											 geo_down_to=links_down[geo_down_from][1]))
#						next_calls.append(face_up_to)
						#branches+=get_branches_from_face(face_up_to,map,c)

#	c=list(couples)
#	c.remove(couple)
#	for n in next_calls:
#		branches+=get_branches(n,map,c)

#	return branches



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

#planes=[]
#root=list(OGG.FacesMap.keys())[0]
#fba=get_faces_by_area(OGG.Faces,OGG.FacesMap['Faces'])
#af=sorted(fba,reverse=True)
#tree_filled=False
#id_key=0
#while id_key<len(af):
#	id_block=af[id_key]
#	block=OGG.FacesByArea[id_block]
#	idf1=block[0]
#	found=False
#	if not found:
#		if len(block)==1 and (id_key<len(af)-1):
#			id_key+=1
#			id_next_block=af[id_key]
#			next_block=OGG.FacesByArea[id_next_block]
#			idf2=next_block[0]
#		elif len(block)==2:
#			idf2=block[1]

#		f1=OGG.Faces[idf1]
#		f2=OGG.Faces[idf2]
#		dist=round(f1.distToShape(f2)[0],1)
#		if dist==OGG.Thk:
			#print('thk:',dist,' ->',idf1,'-',idf2)
#			planes.append([idf1,idf2])
#	id_key+=1


#bb=OGG.BendedFaces[0]

#print('planes:',planes)
#print('bends:',OGG.BendedFaces)
#planes+=OGG.BendedFaces

for b in sheet_tree.Branches:
    print (b,sheet_tree.Branches[b].FaceUp)
#branches=[]
#branches=get_branches(planes[0][0],OGG.FacesMap['Map'],planes)
#print (branches)
