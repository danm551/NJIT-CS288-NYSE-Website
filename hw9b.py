# CS288 Homework 9
# Read the skeleton code carefully and try to follow the structure
# You may modify the code but try to stay within the framework.

import libxml2
import sys
import os
import commands
import re
import sys

import MySQLdb

from xml.dom.minidom import parse, parseString

# for converting dict to xml
from cStringIO import StringIO
from xml.parsers import expat

def get_elms_for_atr_val(tag,atr,val):
   lst=[]
   elms = dom.getElementsByTagName("tr")
   f_elms = filter(lambda x: len(x.childNodes) == 6, elms)
   del f_elms[0]
   lst = f_elms

   return lst

def get_text(e):
   lst=[]
   if e.nodeType in (3,4):
      lst.append(e.data)
   else:
      for x in e.childNodes:
		   lst = lst + get_text(x)	

   return lst

def replace_non_alpha_numeric(s):
   p = re.compile(r'[^a-zA-Z0-9\.:-]+') #added \.
   #   p = re.compile(r'\W+') # replace whitespace chars
   new = p.sub(' ',s)
   return new.strip()

# convert to xhtml
# use: java -jar tagsoup-1.2.jar --files html_file
def html_to_xml(fn):
  cmd = "java -jar tagsoup-1.2.1.jar --files "+fn
  os.system(cmd)
  xhtml_file = fn.replace(".html", ".xhtml") #adds .xhtml suffix to return name
  return xhtml_file

def extract_values(dm):
   lst = []
   l = get_elms_for_atr_val('table','class','most_actives')

   lst = map(lambda x: get_text(x), l)

   #deletes null items in lst
   for x in lst:
     count = 0
     for y in x:
        if(y == '\n'):
           del x[count]
        count = count + 1 
   
   #splits name from symbol
   for x in lst:
      tmp1 = x[1]
      tmp2 = tmp1.split('(')
      tmp3 = tmp2[1].split(')')
      x[0] = tmp3[0] #symbol
      x[1]=tmp2[0] #name

   #replaces $ in price values
   for x in lst:
      x[2] = replace_non_alpha_numeric(x[2])
      x[2] = x[2].replace(" ", "") #removes spaces where commas used to be
      x[3] = replace_non_alpha_numeric(x[3])
      x[4] = replace_non_alpha_numeric(x[4])
      x[5] = replace_non_alpha_numeric(x[5])

   #creates list of dictionaries where they key is the company symbol
   dic_lst = []
   for x in lst:
      dic = {'symbol': x[0], 'name' : x[1], 'volume' : x[2], 'price' : x[3], 'pchng' : x[5], 'chng' : x[4]}
      dic_lst.append(dic)
  
   return dic_lst

# mysql> describe most_active;
def insert_to_db(l,tbl):
   db = MySQLdb.connect(host = "localhost", db="nyse")
   handle = db.cursor()
   handle.execute("CREATE TABLE IF NOT EXISTS " + tbl + " (symbol varchar(10), name  varchar(80), volume integer, price float, chng float, pchng float)")
   if(handle.execute("SELECT 1 FROM " + tbl) == 0): 
      for x in l:
         insert = ("INSERT INTO " + tbl + "  (symbol, name, volume, price, chng, pchng) VALUES  (%s, %s, %s, %s, %s, %s)")
         data = (x["symbol"], x["name"], x["volume"], x["price"], x["chng"], x["pchng"])
         handle.execute(insert, data)
   #handle.close()
   db.commit()
   #db.close()
   return handle

def select_from_db(cursor,fn):
   #print list of tables
   sql = "SHOW TABLES	"
   cursor.execute(sql)
   response = cursor.fetchall()
   print "\n"
   print "Tables: "
   for row in response:
      print row[0]

   user_input = input("select list: ")
   
   return response[user_input][0]
  
   #sql = "select * from " + fn
   #cursor.execute(sql)
   #response = cursor.fetchall()
   #length = len(response[0])
   #print "Data: "
   #for row in response:
      #n = 0
      #while( n < length):
         #if(n == 5):
            #print row[n]
         #else:
            #print row[n],
         #n = n + 1


# show databases;
# show tables;
def main():
    ####### REMEBER TO USE sudo python hw9b.py
   #name="nyse_`date +%Y_%m_%d_%H_%M`.html"  sets file name
   html_fn = sys.argv[1]
   fn = html_fn.replace('.html','')
   xhtml_fn = html_to_xml(html_fn)
	
   #xhtml_fn = "index.xhtml" #placeholder to keep from writing index.xhtml to hd every time the program runs. Delete after
   global dom
   dom = parse(xhtml_fn)

   lst = extract_values(dom)

   fn = xhtml_fn.replace(".xhtml", "") #removes .xhtml suffix for MySQL syntax rules on db names

   # make sure your mysql server is up and running
   cursor = insert_to_db(lst,fn) # fn = table name for mysql

   l = select_from_db(cursor,fn) # display the table on the screen

   # make sure the Apache web server is up and running
   # write a PHP script to display the table(s) on your browser
   #<?php
   #$link = mysql_connect('localhost');
   #?>
   #return xml
# end of main()

if __name__ == "__main__":
   main()

# end of hw7.py
