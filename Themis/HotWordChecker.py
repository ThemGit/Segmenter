#!/usr/bin/python



class Line:
   'Common base class for all lines'

   def __init__(self, blockIdx):
      #self.baseline = baseline
      self.words = []
      #self.fontSize = fontSize 
      self.blockIdx = blockIdx 

   def string(self):
      s=''
      for w in self.words:
         s+=w.text
      return s 

   def getBroadcaster(self):
      broadcasterList = ['NOS','AVRO','VARA','NCRV','KRO','VPRO','KRO/RKK','NOS/NOT','ROF','TELEAC']
      #score = process.extractOne(self.string(), broadcasterList)
      #print "%", b, score
      #if score[1] > 89: 
      #      return score[0]
       #  score = fuzz.token_set_ratio(self.string(), b)
         #if score > 80:
         #print '# ',self.string(), b, score
        # return b

      for bb in broadcasterList:
         b = re.search('([\(|\s]'+bb+')|^'+bb+'', self.string(), re.I)
         if b is not None:
            return bb

   def getNet(self):
      netList = ['NEDERLAND 1','NEDERLAND 2','NEDERLAND 3']
      #return process.extractOne(self.string(), netList)

      for nn in netList:
         n = re.search('([\(|\s]'+nn+')|^'+nn+'', self.string(), re.I)
         if n is not None:
            return nn

            


   def getTime(self):
      t = re.findall('([\d]{1,2}[.|:|,][\d]{2}){1,}', l.string(), re.I)
      y = ''
      if len(t) is 1:
         return t[0]
      elif len(t) is 2:
         return t[0]+' tot en met '+t[1]

class Word:
   'Common base class for all words'

   def __init__(self, text, fontSize, confidence,mSW):
      self.text = text
      self.confidence = confidence
      self.fontSize = fontSize
      self.mSW=mSW
   #@property
   def getConfidence(self):
      return self.confidence / len(self.text)

def sortIndex( block ):
   l=block.get('l')
   t=block.get('t')
   r=block.get('r')
   b=block.get('b')
   w = int(r) - int(l)
   h = int(b) - int(t)
   x= int(l) + w/2 
   y= int(t) + h/2

   return (x)+(y*99)
 
def displaymatch(match):
    if match is None:
        return None
    return '<Match: %r, groups=%r>' % (match.group(), match.groups())


import sys,os
import pymysql
import bunch
import xml.etree.cElementTree as ET
from xml.etree.ElementTree import QName
from pprint import pprint
import re
import json
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
import fuzzy


con = pymysql.connect(host='localhost', port=3306, user='root', passwd='19871987', db='guides',autocommit=True)

filesarray=[]
prefix="/Users/tkaravellas/Desktop/Comerda/Picturae/selection_raw/"
for dir in os.listdir(prefix):
   if os.path.isdir(prefix+dir):
      for file in os.listdir(prefix+dir):
         if file.endswith(".xml"):
            #print file
            filesarray.append([dir,file])
            #filesarray.append(file)
for i in range(0,len(filesarray)):
   
   path=prefix+filesarray[i][0]+'/'+filesarray[i][1]
   path=str(path)
   print '==========================================================='
   print path
   tree = ET.parse(path)
   doc = tree.getroot()
   namespace = 'http://www.abbyy.com/FineReader_xml/FineReader10-schema-v1.xml'
   
   lineList = []
   wordList = []
   
   word = ''
   confidence = 0
   
   for block in doc.iter(str( QName( namespace, 'block' ) )):
      for line in block.iter(str( QName( namespace, 'line' ) )):
         lineobj = Line(sortIndex(block))
         for formatting in line.iter(str( QName( namespace, 'formatting' ) )):
            for c in formatting.iter(str( QName( namespace, 'charParams' ) )):
               if c.get('charConfidence') is not None: confidence=int(c.get('charConfidence'))
               if c.get('meanStrokeWidth') is not None: mSW=int(c.get('meanStrokeWidth'))
               if c.get('wordStart') == '1': 
                  if word is not '': lineobj.words.append(Word(word, formatting.get('fs'), confidence,mSW))
                  word=c.text
               else:
                  word+=c.text
                  #print c.get('meanStrokewidth')
         if word is not '': lineobj.words.append(Word(word, formatting.get('fs'), confidence,mSW))
         word=''
         lineList.append(lineobj)   
   
   #lineList.sort(key=lambda x: x.blockIdx, reverse=False)
   
   b=n=t=' '
   Ct=Cb=Cn=0
   for l in lineList: 
   
      if l.getNet() is not None:
         n=l.getNet()
         #print "NEEETTT"
         Cn+=1
      if l.getBroadcaster() is not None:
         b=l.getBroadcaster()
         Cb+=1
      if l.getTime() is not None:
         Ct+=1
         print '==========================================================='
         print "GOING to ADD-------"
         print l.getTime()
         time=str(l.getTime())
         title=" "
         print n
         print b
         print l.string().encode('utf-8')
         desc=l.string().encode('utf-8')
         print desc
         n=str(n)
         b=str(b)
         cur=con.cursor()
         query="INSERT INTO test1 VALUES ('"+time+"','"+title+"','"+desc+"','"+b+"','"+n+"','"+path+"')"
         #print query
         cur.execute(query)
      else:
         print l.string().encode('utf-8')
   
  
   print "Broadcastyers!"
   print Cb
   print "Times!"
   print Ct
   print "Nets!"
   print Cn

print lineList[0].words[0].text, lineList[0].words[0].mSW      



