########################################################################
#                                                                      #
#  Riccardo Soldini - riccardo.soldini@gmail.com                       #
#                                                                      #
#  reversE.py - 2017                                                   #
#                                                                      #
#  Modulo per la decostruzione di parti di carpenteria da file STEP    #
#  ricostruzione in parti in formato makEasy                           #
#  e generazione del processo di costruzione  (workflow)               #
#                                                                      #
########################################################################

from FreeCAD import Vector,Placement,Rotation
import pprint
from io import StringIO
import math
import g2
import makEasy
import json
import xlsxwriter
from MeFunctions import *
from MeFreeCADClasses import *
from PySide import QtGui
VARS=[]

POSSIBLE_THK=[2.0,2.5,3.0,4.0,5.0,6.0,8.0,10.0,12.0,15.0,20.0,25.0,30.0,35.0,40.0]
POSSIBLE_UNP=[40,50,60,65,80,100,120,140,160,180,180,200,220,240,300]
POSSIBLE_HEA={220:[220,210]}
COMMON_COMP={'RIDUZIONE_CONCENTRICA_114_76':{'name':'Riduzione concentrica D114-76'},
             'ROSETTA_DIN7980_d_10':{'name':'Rosetta piana d10'},
             'VITE_UNI5739_M10x30':{'name':'Vite TE M10x30'},
             '3572_BB14_00':{'name':'Profilo a U 28x14 L=200'},
             'p9.1.1.1.1.1.1':{'name':'Piastrina fissatubo'},
             'S400-1102D':{'name':'Piastrina fissatubo'},
             'supporto.1.1.1.1':{'name':'Supporto ripari L=20'},
             'supporto.1.2.1.1':{'name':'Supporto ripari L=40'},
             'S300-1191A_00.1':{'name':'Piastrina supporto ripari L=40'},
             'S300-1191A_00.2':{'name':'Piastrina supporto ripari L=20'},
             'S300-1126B':{'name':'Blocchetti 30x20x10 filettati'}}



# Function to find Longest Common Sub-string

from difflib import SequenceMatcher

def longestSubstring(str1,str2):

    result=''
	# initialize SequenceMatcher object with
	# input string
    seqMatch = SequenceMatcher(None,str1,str2)

	# find match of longest sub-string
	# output will be like Match(a=0, b=0, size=5)
    match = seqMatch.find_longest_match(0, len(str1), 0, len(str2))

	# print longest substring
    if (match.size!=0):
        result= (str1[match.a: match.a + match.size])
    return result


def is_in_POSSIBLE_HEA(obj):
    keys=list(POSSIBLE_HEA.keys())
    result=[False]
    found=False
    bb=get_box_dimensions(obj)
    ax=['X','Y','Z']
    while len(keys)>0 and not found:
        k=keys.pop()
        c=POSSIBLE_HEA[k]
        for i in range(0,3):
            a=ax.pop(0)
            ax.append(a)
            b=bb.pop(0)
            bb.append(b)
            for i in range (0,2):
                a=ax.pop(1)
                ax.append(a)
                b=bb.pop(1)
                bb.append(b)
                if round(bb[0],4)==c[0] and round(bb[1],4)==c[1]:
                    found=True
                    result=[True,list(bb)]
                    #print (result)
                    #print (ax)
    return result

def is_in_POSSIBLE_RECT_TUBE(obj):
    result=True
    return result


def deconstruct_object(obj):


 def get_any_blends(c_surf):# da togliere !!!!
    #c_surf=list(faces_tree['Cylinder'])
    nblend=0
    blend_faces=[]
    while len(c_surf)>0:
      s1=c_surf.pop(0)
      not_found=True
      ind=0
      while ind<len(c_surf) and not_found:
          c1=OGG.FacesTree['Cylinder'][s1]
          c2=OGG.FacesTree['Cylinder'][c_surf[ind]]
          blend_thk=round(c1.distToShape(c2)[0],2)
          cc1=c1.Surface.Axis
          cc2=c2.Surface.Axis
          eqX=round(cc1.x, 2)==round(cc2.x, 2)
          eqY=round(cc1.y, 2)==round(cc2.y, 2)
          eqZ=round(cc1.z, 2)==round(cc2.z, 2)
          equal_center= (eqX and eqY) or (eqX and eqZ) or (eqZ and eqY)
          if (equal_center) and (abs(blend_thk)==thk):
             nblend+=1
             not_found=False
             #print ('bt ',blend_thk)
             #print ('blend faces...: ',s1,' and ',c_surf[ind])
             #print (c1.Surface.Axis)
             #print (c2.Surface.Axis)
             blend_faces.append(s1)
             blend_faces.append(c_surf[ind])
          ind+=1
    return blend_faces


 #def unfold_sheet(faces,eight_bigger_faces):
 def unfold_sheet(ogg):
    faces=ogg.Faces
    eight_bigger_faces=ogg.EightBiggerFaces
    #print 'find adjacent...maybe..',eight_bigger_faces
    contacts=find_adjacent(faces,eight_bigger_faces[0])
    #print (contacts)
    adc=contacts[eight_bigger_faces[0]]
    print ('adc:',adc)
    if eight_bigger_faces[0] in OGG.FacesTree['Plane']:
        for b in blend_faces:
            for ad in adc:
                if b==adc[ad][0]:
                    #print (' Trovato!!!' ,adc[ad])
                    f1=faces[eight_bigger_faces[0]]
                    f2=faces[adc[ad][0]]
                    e1= f1.OuterWire.Edges[ad]
                    e2= f2.OuterWire.Edges[adc[ad][1]]
                    fp=e1.Vertexes[0]
                    ep=e1.Vertexes[1]
                    dx=round(fp.X-ep.X,3)
                    dy=round(fp.Y-ep.Y,3)
                    dz=round(fp.Z-ep.Z,3)
                    a=angle_between_planes(f1,f2)
                    #print (angle_to_Z(f1))
                    #print ('deltas:',dx,'|',dy,'|',dz,'->',a)

    return True



 print ('... sto analizzando '+obj.Label+'...')
 OGG=FCObject(obj)
 part_name='indefinito'
 classified=False
 thk=0
 paths=None
 me_class='INDEFINED'

 if OGG._isCommonComponent(COMMON_COMP): classified=True
 print (classified)

 if not classified:
  faces=obj.Shape.Faces
  OGG.parse()
  #eight_bigger_faces=OGG.EightBiggerFaces
  classified=False

  ##### is it round tube? #####
  curved_faces=True
  group=list(OGG.EightBiggerFaces)
  for i in range(0,4):
      if group[i] not in OGG.FacesTree['Cylinder']:
          curved_faces=False

  if curved_faces:
      dd=[]
      for n in range (0,4):
          nn=OGG.EightBiggerFaces[n]
          for m in range (0,4):
              mm=OGG.EightBiggerFaces[m]
              dist=round(OGG.FacesTree['Cylinder'][mm].distToShape(OGG.FacesTree['Cylinder'][nn])[0],2)
              if dist not in dd: dd.append(dist)
      if len(dd)==2:
          dd.remove(0)
          diam=0
          lenght=0
          for i in range (0,4):
              ff=OGG.FacesTree['Cylinder'][OGG.EightBiggerFaces[i]]
              d=ff.Surface.Radius*2
              if d>diam:diam=d
              edges=ff.OuterWire.Edges
              for e in edges:
                  if str(e.Curve.__class__)=="<type 'Part.GeomLineSegment'>":
                      if e.Length>lenght:lenght=e.Length

          part_name= "Tubo tondo diam."+str(diam)+"x"+str(dd[0])+" L="+str(lenght)
          me_class="PROFILE"
          classified=True


  if not classified:
     six_faces=[]
     four_faces=[]
     two_faces=[]
     pface_count=0
     group=[]
     #print faces_tree['Plane'].keys()
     #print eight_bigger_faces
     for g in list(OGG.EightBiggerFaces):
        if g in OGG.FacesTree['Plane'].keys():
          pface_count+=1
          group.append(g)
     #print 'gr',group
     while len(group)>0:
         sample=group.pop(0)
         #print sample
         matched=[]
         matched_count=1
         for i in group:
             #print i
             if is_planes_parallels(OGG.FacesTree['Plane'][sample],OGG.FacesTree['Plane'][i]):
                 matched_count+=1
                 matched.append(i)
         matched.append(sample)
         #print  ('mached_count:',matched_count)
         if matched_count==6:
             six_faces.append(matched)
         if matched_count==4:
             #print ("4 parallels faces found:",matched)
             four_faces.append(matched)
         if matched_count==2:
             #print ("2 parallels faces found:",matched)
             two_faces.append(matched)

     #print ('six faces macthed:',len(six_faces))
     #print ('four faces macthed:',len(four_faces))
     #print ('two faces macthed:',len(two_faces))
     ##### is it a H or I profile? #####
     if len(four_faces)==1 and len(two_faces)==2:
         f1=OGG.FacesTree['Plane'][four_faces[0][0]]
         za=angle_to_X(f1)
         pos = obj.Placement.Base
         rot = Rotation(Vector(1,0,0),-za)
         newplace = Placement(pos,rot,Vector(0,0,0))
         obj.Placement = newplace
         faces=obj.Shape.Faces
         OGG.FacesTree=build_faces_tree(faces)
         f1=OGG.FacesTree['Plane'][four_faces[0][0]]
         za=angle_to_Y(f1)
         pos = obj.Placement.Base
         rot = Rotation(Vector(0,1,0),-za)
         newplace = Placement(pos,rot,Vector(0,0,0))
         obj.Placement = newplace
         faces=obj.Shape.Faces
         OGG.FacesTree=build_faces_tree(faces)
         f1=OGG.FacesTree['Plane'][four_faces[0][0]]
         hea=is_in_POSSIBLE_HEA(obj)
         #print (hea)
         if hea[0]==True:
             #print (hea[1])
             part_name='HEA '+str(hea[1][0])+' L='+str(round(hea[1][2]))+' ('+str(OGG.Weight)+')'
             me_class="PROFILE"
             classified=True

     ##### is it a rect/square tube? #####
     if not classified and len(four_faces)==2:
         classified=True
         size1=int(max_faces_distance(list(four_faces[0]),OGG.FacesTree['Plane']))
         size2=int(max_faces_distance(list(four_faces[1]),OGG.FacesTree['Plane']))
         thk=min_faces_distance(list(four_faces[0]),OGG.FacesTree['Plane'])
         lenght=max_found_len(list(four_faces[0]),OGG.FacesTree['Plane'])
         if size1==size2:
             part_name= "Tubo quadro "+str(size1)+"x"+str(thk)+" L="+str(lenght)
             me_class="PROFILE"
         elif size1>size2:
             part_name= "Tubo rettangolare "+str(size1)+"x"+str(size2)+"x"+str(thk)+" L="+str(lenght)
             me_class="PROFILE"
         else:
             part_name= "Tubo rettangolare "+str(size2)+"x"+str(size1)+"x"+str(thk)+" L="+str(lenght)
             me_class="PROFILE"
     ##### is it a UNP profile? #####
     elif len(two_faces)==2:
         size1=int(max_faces_distance(list(two_faces[0]),OGG.FacesTree['Plane']))
         size2=int(max_faces_distance(list(two_faces[1]),OGG.FacesTree['Plane']))
         lenght=max_found_len(list(two_faces[0]),OGG.FacesTree['Plane'])
         #print size1
         if size1>size2 and size1 in POSSIBLE_UNP:
             classifed=True
             part_name= "UNP "+str(size1)+" L="+str(lenght)
             me_class="PROFILE"
         elif size2 in POSSIBLE_UNP:
             classifed=True
             part_name= "UNP "+str(size2)+" L="+str(lenght)
             me_class="PROFILE"


  ### find thickness
  if not classified:
   same_geometry=False
   group=list(OGG.EightBiggerFaces)

   if (group[0] in OGG.FacesTree['Plane']) and (group[1] in OGG.FacesTree['Plane']):
     f1=OGG.FacesTree['Plane'][group[0]]
     f2=OGG.FacesTree['Plane'][group[1]]
     same_geometry=True
   if (group[0] in OGG.FacesTree['Cylinder']) and (group[1] in OGG.FacesTree['Cylinder']):
     f1=OGG.FacesTree['Cylinder'][group[0]]
     f2=OGG.FacesTree['Cylinder'][group[1]]
     same_geometry=True

   if same_geometry:
    thk=round(f1.distToShape(f2)[0],1)
    #print ('thk: ',thk)

    if thk in POSSIBLE_THK:
          part_name= 'Sagoma sp. '+str(thk)+' mm'
          me_class="SHEET"

    part_name+=' ('+str(OGG.Weight)+'kg)'


    blend_faces=get_any_blends(list(OGG.FacesTree['Cylinder']))
    #OGG._getAnyBlends()
    nblend=len(blend_faces)/2
    if nblend==1: part_name+=" con nr "+str(nblend)+" piega"
    if nblend>1: part_name+=" con nr "+str(nblend)+" pieghe"

    #if nblend==0:
    cp=Part.Face(faces[OGG.EightBiggerFaces[0]].Wires)
    if cp.Surface.__str__()=="<Plane object>":
        align_face_to_Zplane(cp)
        if cp.BoundBox.XLength<cp.BoundBox.YLength:
            cp.rotate(FreeCAD.Vector(0,0,0),FreeCAD.Vector(0,0,1),-90)
        gg=geos_from_face(cp)
        paths=g2.PathsFromGeos(gg['geos'],gg['nodes'])


    if nblend>0:
        unfolded=unfold_sheet(OGG)


 if part_name in PARTS:
     PARTS[part_name]['count']+=1
     PARTS[part_name]['objects'].append(obj.Label)
 else:
     PARTS[part_name]={'count':1,
                       'objects':[obj.Label],
                       'weight':OGG.Weight,
                       'class':me_class,
                       'paths':paths,
                       'thk':thk}
 return

###############################################################################

PARTS={}

print ("Let's begin...")
pp = pprint.PrettyPrinter(indent=4)

sels=Gui.Selection.getSelectionEx()

count=0
for sel in sels:
    obj=sel.Object
    if hasattr(obj,"Shape"):
        if obj.Shape.Volume>0:
            #print "Object ", obj.Label
            count+=1
            try:
                deconstruct_object(obj)
                #break
            except Exception as err:
                print("Error on ",obj.Label,": ",err)


#print ('Rilevati nr ',count,' oggetti')
#for item in PARTS:
#    print (item+'  |  '+str(PARTS[item]['count']))


#salva disegni
DWG={'SHEET':{'THK':{}},'PROFILE':{},'COMPONENT':{}}
for item in PARTS:
    c=PARTS[item]['class']
    if c=="SHEET":
        t=PARTS[item]['thk']
        if t in DWG['SHEET']['THK']:
            p=DWG['SHEET']['THK'][t]
            dr=p['Drawing']
            yo=p['Yoffset']
            gc=p['Gcount']
        else:
            dr=g2.Drawing()
            yo=0.0
            gc=0
            DWG['SHEET']['THK'][t]={'Drawing':dr,'Yoffset':yo,'Gcount':gc}
            p=DWG['SHEET']['THK'][t]

        if PARTS[item]['paths']!=None:
            np={}
            for i in PARTS[item]['paths']:
                np[i.area]=i
            bigger=np[sorted(np)[-1]]
            tr=bigger.boundBox.bottomleft
            trX=-tr.x
            trY=-tr.y+yo
            bigger.traslateXY(trX,trY)
            DWG['SHEET']['THK'][t]['Yoffset']=yo+bigger.boundBox.height*1.15+200

            for k in PARTS[item]['paths']:
                for i in range(0,len(k.geometries)):
                    g=k.geo(i)
                    #print(g)
                    dr.insertGeo(gc,g)
                    gc+=1
            DWG['SHEET']['THK'][t]['Gcount']=gc

base_path='\\10.0.0.199\Archivio\COMMESSE'
dir = QtGui.QFileDialog.getExistingDirectory(None, 'Seleziona commessa', base_path, QtGui.QFileDialog.ShowDirsOnly)


for t in DWG['SHEET']['THK']:
    output_dxf=DWG['SHEET']['THK'][t]['Drawing'].getDXF()
    f=open(dir+'/SP'+str(int(t))+'.dxf',"w")
    f.write(output_dxf)
    f.close()


s=pprint.pformat(PARTS, indent=4)
f=open(dir+'/ElencoParti.txt',"w")
f.write(s)
f.close()

# Create an new Excel file and add a worksheet.
workbook = xlsxwriter.Workbook(dir+'/DistintaParti.xlsx')
worksheet = workbook.add_worksheet()
worksheet.set_column('A:A', 45)
worksheet.write(0, 0,'NOME')
worksheet.write(0, 1,'PEZZI')
worksheet.write(0, 2,'PESO')
worksheet.write(0, 3,'KG TOT')
row=1
for p in PARTS:
    worksheet.write(row, 0, p)
    worksheet.write(row, 1, PARTS[p]['count'])
    worksheet.write(row, 2, PARTS[p]['weight'])
    worksheet.write_formula(row, 3, '=B'+str(row+1)+'*C'+str(row+1))
    row+=1
worksheet.write(row, 0, 'TOTALI')
worksheet.write_formula(row, 1, '=SUM(B2:B'+str(row))
worksheet.write_formula(row, 3, '=SUM(D2:D'+str(row))
workbook.close()

#f=open(dir+'/DistintaParti.txt',"w")
#for p in PARTS:
#    wl=p+'|'+str(PARTS[p]['count'])+'|'+str(PARTS[p]['weight'])
#    f.write(wl+"\n")
#    print (wl)
#f.close()
