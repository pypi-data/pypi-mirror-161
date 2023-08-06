#!/usr/bin/python3
#
# TELETERM - TERMINAL TELETEXT
#
# (c) 2020-2022 Giomiky
#
# Terminal minimum size 44x25
#
# VERSION LOG:
#
# 20210908 - Prvni verze
# 20220408 - Update na novy teletext
# 20220410 - Drobne upravy
# 20220802 - Drobne upravy
#
# The main redrawing of the text starts
# in function pageToText.
#
############################################
#
# [=] EDIT HERE FOR PAGES TMP DIR
#
dirname='/temp'
#
############################################

telelogo = r"""
     ___________    .__
     \__    ___/___ |  |   ____
       |    |_/ __ \|  | _/ __ \
       |    |\  ___/|  |_\  ___/
       |____| \___  >____/\___  >
                  \/          \/
     ___________
     \__    ___/__________  _____
       |    |_/ __ \_  __ \/     \
       |    |\  ___/|  | \/  Y Y  \
       |____| \___  >__|  |__|_|  /
                  \/            \/
"""
DEBUG=0

NEXTP=-21
PREVP=-22
NEXTSP=-31
PREVSP=-32
CLEARC=-10
NOOP=-100
STATLINE=23

from time import localtime, strftime
import datetime
import curses
import os
import sys
import re
import traceback
import requests
import json
from bs4 import BeautifulSoup
from signal import signal, SIGWINCH, SIGINT


he=None # height
wi=None # width
wih=None # width half
heh=None # height half
lb=None # line begin
pb=None # page begin
scrx=0
scry=0
nw=None
scr=None

WHITE=1
CYAN=2
RED=3
BLACK=4
GREEN=5
YELLOW=6
MAGENTA=7
BLUE=8


def dbg(p_str):
  if DEBUG==1:
    print(p_str)

def log_crash(e):
  clog=open("crash.log","w")
  traceback.print_exc(file=clog)
  clog.close()

def nw_move(y,x):
  i=None
  try:
    if y < he and x < wi and y > 0 and x > 0:
      nw.move(y,x)
  except Exception as e:
    nw.clear()
    nw.addstr("[!] [ move ] <q> konec")
    nw.refresh()
    clog=open("crash.log","w")
    traceback.print_exc(file=clog)
    clog.close()
    i = nw.getch()
    if i==ord('q'):
      deinit()
      exit(-1)

def nw_addstr(y,x,p_str,color=0):
  global nw
  i=None
  try:
    nw.addstr(y,x,str(p_str),color)
  except Exception as e:
    nw.clear()
    nw.addstr("[!] [ addstr ] <q> konec")
    nw.refresh()
    clog=open("crash.log","w")
    traceback.print_exc(file=clog)
    clog.close()
    i=nw.getch()
    if i==ord('q'):
      deinit()
      exit(-1)
 
def calc_scr_middle():
  global lb, wih, heh, pb, nw, scr
  he,wi=scr.getmaxyx()
  heh=int(he/2)
  wih=int(wi/2)
  xrowsz=44 # teletext width
  xrowszh=int(xrowsz/2) # rows size half
  xpagesz=25 # teletext height
  xpageszh=int(25/2) # middle of the page vertically
  lb=wih-xrowszh # line begin
  pb=heh-xpageszh # page begin
  # if the calc gets wrong
  if lb<0:
    lb=0
  #nw_addstr(0,0,str(pb)+" "+str(lb))
  #nw.getch()
  nw.refresh()
 
def getUserAgent():
  #ua='Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36'
  ua='Teleterm - Terminal Teletext'
  return(ua)

def getFName(pageNo,subPageNo):
  global dirname
  s=""
  if int(subPageNo)>1:
    s=chr(ord(str(subPageNo))+48-32)
  ret=dirname+'/'+'teletext_'+str(pageNo)+s+'.txt'
  return(ret)

def touchFile(pageNo,subPageNo):
  with open(getFName(pageNo,subPageNo), 'w') as f:
    f.write('')

def getFromFile(pageNo,subPageNo):
  with open(getFName(pageNo,subPageNo), 'r') as f:
    txt=f.read()
  return(txt)

def prn(strng,end='\n',clr=0,sx=0,sy=0,bold=0):
  global scrx, scry, nw, wi
  if end!='\n':
    strng+=end
  w=len(strng)
  if (bold==1):
    nw_addstr(scry+sy,scrx+sx,strng,curses.color_pair(clr)|curses.A_BOLD)
  else:
    nw_addstr(scry+sy,scrx+sx,strng,curses.color_pair(clr))
  scrx+=w
  if end=='\n':
    scrx=0
    scry+=1
  nw_move(0,wi-1)

def extractCharacters(inpStr):
  res=""
  for i in inpStr:
    if ord(i)>=32 and ord(i) <= 126:
      res = "".join([res, i])
  return(res)

def pageToText(pageNo,subPageNo):
  global pb, lb, nw
  dpage=[]
  pagestr=''
  ret=getPage(pageNo,subPageNo)
  pg=getFromFile(pageNo,subPageNo)
  currentPage=0
  lineno=0
  thisPage=0
  sy=0
  pages=0
  subPagesAvail=0
  firstPage=0
  rowno=0 
  for line in pg.split('\n'):
    nw_addstr(rowno+pb,lb,line)
    rowno+=1
  pagestr='\n'.join(dpage)
  return(pagestr)
    
def getIndex():
  url='http://teastop.plus.com/svn/teletext'
  requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
  try:
    requests.packages.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += 'HIGH:!DH:!aNULL'
  except AttributeError:
    pass
  headers = { 'User-Agent': getUserAgent()}
  page = requests.get(url,headers=headers)
  txt=page.content.decode('utf8',"ignore")
  f = open(getFName(0), 'w')
  f.write(txt)
  f.close()

def getPages():
  ua = 'Teleterm - Terminal Teletext'
  url='https://www.ceskatelevize.cz/teletext-api/v2/text'
  requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
  try:
    requests.packages.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += 'HIGH:!DH:!aNUL'
  except AttributeError:
    pass
  headers = { 'User-Agent': ua }
  page = requests.get(url,headers=headers)
  #print(str(page.text)[:20])
  pages = json.loads(page.text)
  f = open(getFName(000,000), 'w')
  f.write(json.dumps(pages))
  f.close()
  return(0)

def getPage(pageNo,subPageNo):
  try:
    f = open(getFName(000,000), 'r')
    pages = json.loads(f.read())
    f.close()
    subPageChar = chr(int(subPageNo) + 64)
    #print(subPageChar)
    if str(pageNo) in pages["data"]:
      if len(pages["data"][str(pageNo)]["subpages"])>0:
        if subPageChar in pages["data"][str(pageNo)]["subpages"]:
          page = pages["data"][str(pageNo)]["text"][str(pageNo)+subPageChar]
        else:
          page = pages["data"][str(pageNo)]["text"][str(pageNo)+"A"]
      else:
        page = pages["data"][str(pageNo)]["text"][str(pageNo)]
      txt=[]
      soup = BeautifulSoup(page, "html.parser")
      for div in soup.findAll('pre'):
        txt.append(div.text)
      txt=''.join(txt)
      f = open(getFName(pageNo,subPageNo), 'w')
      f.write(txt)
      f.close()
    else:
      txt = []
  except:
    txt = []
  return(0)

def main(pageNo,subPageNo):
  try:
    os.path.getmtime(getFName(pageNo,subPageNo))
  except Exception:
    touchFile(pageNo,subPageNo)
  now = localtime() # get struct_time
  ftime=localtime(os.path.getmtime(getFName(pageNo,subPageNo)))
  ftimei=int(strftime("%Y%m%d%H", ftime))
  cur_time=strftime("%Y%m%d%H%m", now)
  upd_time=strftime("%Y%m%d0515", now)
  mod_time=strftime("%Y%m%d%H%m", ftime)
  s=""
  ret=0
  #if int(subPageNo)>1:
  s=chr(ord(str(subPageNo))+48-32)
  if ((mod_time < upd_time and cur_time > upd_time) or (getFromFile(pageNo,subPageNo)=='')):
    #umsg="---| Downloading page ..."+str(pageNo) + " |---"
    #umsg="---| Downloading page ..."+str(pageNo) + " |---"
    umsg="[ "+str(pageNo) + s + " ] "
    #nw_addstr(1,48,umsg,curses.color_pair(WHITE)|curses.A_NORMAL)
    nw_addstr(STATLINE+pb,lb,umsg,curses.color_pair(WHITE)|curses.A_NORMAL)
    ret=getPage(pageNo,subPageNo)
    if ret == 0:
      pageToText(pageNo,subPageNo)
    else:
      s=""
      umsg="[ "+str(pageNo) + s +" ] "
      nw_addstr(STATLINE+pb,lb,umsg,curses.color_pair(WHITE)|curses.A_NORMAL)
      pageToText(pageNo,1)
  else:
    umsg="[ "+str(pageNo) + s +" ] "
    nw_addstr(STATLINE+pb,lb,umsg,curses.color_pair(WHITE)|curses.A_NORMAL)
    pageToText(pageNo,subPageNo)
  nw.refresh()
  if ret == -1:
    return(-1)

def ctrlc_handler(signum, frame):
  nw.refresh()
  deinit()
  print("[*] Nashledanou...")
  exit(1)

def terminal_resize(p_he,p_wi):
  global nw, scr, lb, pb
  try:
    curses.endwin()
    scr.refresh()
    calc_scr_middle()
    nw.refresh()
  except Exception as e:
    log_crash(e)
  
def init():
  global nw, he, wi, heh, wih, scr
  #print("\x1b[0;31m")
  scr=curses.initscr()
  he,wi=scr.getmaxyx()
  if he < 24 and wi < 44:
    deinit()
    print("[*] The minimum terminal size needed is 44x24") 
  nw = curses.newwin(he, wi)
  calc_scr_middle()
  curses.start_color()
  curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
  curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
  curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
  curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_BLACK)
  curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)
  curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK)
  curses.init_pair(7, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
  curses.init_pair(8, curses.COLOR_BLUE, curses.COLOR_BLACK)
  curses.noecho()
  curses.doupdate()
  #curses.curs_set(0)
  nw.keypad(1)

def inpc():
  nw.refresh()
  a=nw.getch()
  if not (a >= 32 and a <= 122):
    a=ord('o')
  if chr(a)=='q':
    deinit()
    exit(0)
  elif chr(a)=='h':
    return(ord("h"))
  elif chr(a)=='l':
    return(ord("l"))
  elif chr(a)=='j':
    return(ord("j"))
  elif chr(a)=='k':
    return(ord("k"))
  elif chr(a)=='n':
    return(ord("n"))
  elif chr(a)=='c':
    return(ord("c"))
  elif chr(a)=='p':
    return(ord("p"))
  elif chr(a)=='o':
    return(ord("o"))
  return(a)

def deinit():
  global curses, nw
  nw.clear()
  curses.nocbreak()
  curses.echo()
  curses.doupdate()
  curses.endwin()

def getPageNo():
  nw_addstr(STATLINE+pb,lb+10,"> ",curses.color_pair(WHITE)|curses.A_BOLD)
  nw_move(STATLINE+pb,lb+12)
  pageStr=""
  i=0
  while i < 3:
    ic=inpc()
    pchar=chr(ic)
    if pchar=='h':
      nw_move(STATLINE+pb,lb+12)
      nw.refresh()
      return(PREVP)
    elif pchar=='l':
      nw_move(STATLINE+pb,lb+12)
      nw.refresh()
      return(NEXTP)
    elif pchar=='k':
      nw_move(STATLINE+pb,lb+12)
      nw.refresh()
      return(NEXTSP)
    elif pchar=='j':
      nw_move(STATLINE+pb,lb+12)
      nw.refresh()
      return(PREVSP)
    elif pchar=='c':
      nw_move(STATLINE+pb,lb+12)
      nw.refresh()
      return(CLEARC)
    elif pchar=='o':
      # TERMINAL RESIZE OR UNKNOWN CHARACTER
      nw_move(STATLINE+pb,lb+12)
      nw.refresh()
      return(NOOP)
    if (ord(pchar)>=ord('0') and ord(pchar)<=ord('9')): # or \
      nw_addstr(STATLINE+pb,lb+12+i,pchar,curses.color_pair(WHITE)|curses.A_BOLD)
      nw.refresh()
      pageStr+=pchar
      i+=1
  try:
    pageNo=int(pageStr)
  except Exception as e:
    if DEBUG==1:
      nw_addstr(15,32,"Invalid page Number",curses.color_pair(WHITE)|curses.A_NORMAL)
      nw.refresh()
    pageNo=100
  nw_move(STATLINE+pb,12)
  return(pageNo)

def maxrowsize(txt):
  xlinsz=0
  for i in telelogo.split('\n'):
    if len(i)>xlinsz:
      xlinsz=len(i)
  return(xlinsz)
 
def entry():
  global dirname
  init()
  row=0
  #print(str(lb))
  for i in telelogo.split('\n'):
    nw_addstr(row+pb,lb,i)
    row+=1
  nw_addstr(row+pb,lb,"    -=[ Downloading pages ... ]=-")
  nw.refresh()
  #nw.getch()
  getPages()
  nw.clear()
  nw.refresh()
  #pg=getIndex()
  pageNo=100
  subPageNo=1
  pg=getPage(pageNo,subPageNo)
  ret=main(str(pageNo),str(subPageNo))
  subPageNo=1
  #nw.getch()
  origPage=100
  clearTag=0
  while 1:
    try:
      pageNo=getPageNo()
      nw.clear()
      # clear cache
      if pageNo==NOOP:
        pageNo=origPage
        ret=main(str(pageNo),1)
      elif pageNo==CLEARC:
        clearTag=1
        test = dirname+"/teletext_*.txt"
        os.system('rm '+test)
        #pageNo=100
        pageNo=origPage
        subPageNo=1
        row=0
        for i in telelogo.split('\n'):
          nw_addstr(row+pb,lb,i)
          row+=1
        nw_addstr(row+pb,lb,"    -=[ Downloading pages ... ]=-")
        nw.refresh()
        getPages()
      # next subpage
      elif pageNo==NEXTSP:
        if subPageNo < 9:
          subPageNo+=1
        else:
          subPageNo=1
        pageNo=origPage
      # previous subpage
      elif pageNo==PREVSP:
        if subPageNo>1:
          subPageNo-=1
        pageNo=origPage
      # next page
      elif pageNo==NEXTP:
        if pageNo<999:
          pageNo=origPage+1
          subPageNo=1
        else:
          pageNo=origPage
      # prev page
      elif pageNo==PREVP:
        if origPage-1>=100:
          pageNo=origPage-1
          subPageNo=1
        else:
          pageNo=origPage
      else:
        subPageNo=1
      if (len(str(pageNo))==3 
        and int(pageNo)>=100 
        and int(pageNo)<=999):
        ret=main(str(pageNo),str(subPageNo))
        if ret==-1:
          subPageNo=1
      else:
        ret=main(str(100),1)
      origPage=pageNo
      if clearTag==1:
        #nw_addstr(0,0,"[ cache cleared ... ]")
        clearTag=0
      nw_move(0,wi-1)
    except Exception as e:
      print("Incorrect Page Number: " + str(e),end='')
      log_crash(e)
      nw.clear()
      ret=main(str(pageNo),str(subPageNo))
      deinit()
      pass
  deinit()
  exit(0)

def create_tmp_dir():
  global dirname
  import tempfile
  from tempfile import gettempdir
  dirname=os.path.join(gettempdir(), '.{}'.format(hash(os.times())))
  os.makedirs(dirname) 
  dbg("vytvoren docasny adresar: "+dirname)

def is_tmp_dir_writable():
  global dirname
  try:
    test_fname=dirname+os.sep+'teleterm_test.tmp'
    dbg("Testovaci nazev souboru: "+test_fname)
    file = open(test_fname, 'w') 
    file.write('hello!')                                                    
    file.close()                                                            
    return(1)
  except IOError as error: 
    return(0)

def test_dir_name():
  global dirname
  dir_exists = os.path.exists(dirname)
  dbg("adresar existuje: " +str(dir_exists))
  dir_writable = is_tmp_dir_writable()
  dbg("adresar zapisovatelny: " +str(dir_writable))
  if not dir_exists or dir_writable == 0:
    dbg("Neexistuje nebo neni zapisovatelny")
    create_tmp_dir()
    dir_writable = is_tmp_dir_writable()
    dbg("docasny adresar zapisovatelny: " +str(dir_writable))
    if dir_writable == 0:
      deb("Zadny pouzitelny adresar neni k nalezeni...")
      exit()
  

signal(SIGWINCH, terminal_resize)
signal(SIGINT, ctrlc_handler)

def cli():
  print("Vytvarim docasny adresar...")
  test_dir_name()
  try:
    entry()
  except Exception as e:
    deinit()
    clog=open("crash.log","w")
    traceback.print_exc(file=sys.stdout)
    traceback.print_exc(file=clog)
    clog.close()
    print("ERR: " + str(e))
  
if __name__ == "__main__":
  cli()
