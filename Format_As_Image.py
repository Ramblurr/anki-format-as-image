from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtWebKit import QWebPage, QWebFrame

from ankiqt import ui
from anki.models import CardModel, formatQA
from anki.hooks import addHook
from anki import DeckStorage
from anki.utils import checksum, hexifyID

import os

def formatQAAsImage(html, type, cid, mid, fact, tags, cm, deck):
  
  # build up the html 
  div = '''<div class="card%s" id="cm%s%s">%s</div>''' % (
            type[0], type[0], hexifyID(cm.id),
            html)

  attr = type + 'Align'
  if getattr(cm, attr) == 0:
      align = "center"
  elif getattr(cm, attr) == 1:
      align = "left"
  else:
      align = "right"
  html = (("<center><table width=95%%><tr><td align=%s>" % align) +
          div + "</td></tr></table></center>")
  
  t = "<body><br><center>%s</center></body>" % (html)
  bg = "body { background-color: #fff; }\n"
  html = "<style>\n" + bg + deck.rebuildCSS() + "</style>\n" + t

  # create the web page object
  page = QWebPage()
  page.mainFrame().setHtml(html)

  # size everything all nice
  page = fitContentsInPage(page)  

  image= QImage(page.viewportSize(), QImage.Format_ARGB32_Premultiplied)
  painter = QPainter(image)

  page.mainFrame().render(painter)
  painter.end()
  path = saveImage(image, deck)

  link = u"<img src=\"%s\">" % ( path )
  #print link
  #print html
  return link

def saveImage(image, deck):
  media = deck.mediaDir(create=True)
  print media

  # TODO error checking
  temp = QTemporaryFile("XXXXXX.png")
  temp.open()

  #save the image to a temp file
  image.save( temp.fileName(), "PNG" )
  path = str( temp.fileName() )

  #add it to the media dir
  return deck.addMedia( unicode(temp.fileName()) )
  
def fitContentsInPage(webpage):
  webpage.setViewportSize(webpage.mainFrame().contentsSize())
  
  #starting dimensions
  w = 320
  h = 100
  webpage.setViewportSize(QSize(w,h))
  
  #print "initial %dx%d" % (w,h)
  
  # incrementally increase size of the viewportSize
  # until no scrollbars remain
  frame = webpage.mainFrame()
  #print frame.scrollBarMaximum(Qt.Horizontal)
  #print frame.scrollBarMaximum(Qt.Vertical)
  while frame.scrollBarMaximum(Qt.Horizontal) != 0:
    w += 1
    webpage.setViewportSize( QSize( w, h ) )
    print "hi"
  while frame.scrollBarMaximum(Qt.Vertical) != 0:
    h += 1
    webpage.setViewportSize( QSize( w, h ) )
  ##print "after %dx%d" % (w,h)
  return webpage

addHook( "formatQA", formatQAAsImage )
