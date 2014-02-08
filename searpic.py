#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys,os,re   
import urllib
import time
import threading
# an example of Baidu image search :http://image.baidu.com/i?ct=201326592&lm=-1&tn=result_pageturn&pv=&word=%E5%91%B5%E5%91%B5&z=0&pn=0&cl=2&ie=utf-8#pn=0
dirname = raw_input('Please choose where you want to store your picture\n(example: D:/picture ): ')
content = raw_input('Please input the content you want to search: ')
num = input('Please input the amount of pictures: ')
##dirname = "E:/picture"    # for test
##content = "火车" 
##num = 100
url1 = "http://image.baidu.com/i?ct=201326592&lm=-1&tn=result_pageturn&pv=&word="
url2 = "&z=0&pn=0&cl=2&ie=utf-8#pn=0"
url3 = "&z=0&pn="
url4 = "&cl=2&ie=utf-8#pn=0"# these urls make up the url of the Baidu image's source code
mylock = threading.RLock()  # use myblock to help share data between threads
count = 0                   # count the downloaded picture
total_urls = []             # the url index
thread_list = []            # thread list
downamount = 0
# set the path from you input,create one if not exists.
if os.access(dirname,0):
	pass
else:
	os.makedirs(dirname)
#########################################################
###########my picture download function################## 
def getneedinfo(url):
    """get the infomation about the picture's size and type"""
    try:
	    conn = urllib.urlopen(url)
	    connhead = conn.info().headers
    except:
	    print "Get info error!"
	    return 0
    info = []
    for header in connhead:
	if header.find('Length') != -1:
	    length = header.split(':')[-1].strip()
	    length = int(length)
	if header.find("Type") != -1:
	    type_hty = header.split('/')[-1].strip()
    try:
	    info = [length,type_hty]
    except:
	    return 1
    return info

def set_pic_name(pic_type,num):
    """set the picture's name"""
    return str(num) + "." + pic_type
   
def check_pic(length,path_name):
    """check whether the picture has been downloaded correctly,use picture's size"""
    global downamount,mylock
    print "info_length: ",length," actual size: ",int(os.path.getsize(path_name))
    if length != int(os.path.getsize(path_name)):
	print "Picture ",downamount,"error,Delete: "+ path_name
	os.remove(path_name)
	return 1
    else:
	return 0        
def pic_url_down(path_name,url):
    """download the picture from the given url"""
    data = urllib.urlopen(url).read()
    f = file(path_name,"wb")
    f.write(data)
    print "download: ",url,path_name
    f.close()               
def pic_down_mine(url_list,path,thread_id):
    """main download function"""
    global count,mylock,downamount
    mylock.acquire()
    count += 1
    print "thread: ",thread_id,"--count: ",count
    url = url_list[count][0]
    mylock.release()
    try:
       conn = urllib.urlopen(url)
    except:
	print "Url open error"
	return 1
    pic_info = getneedinfo(url)
    if pic_info == 1:
	    print "Got something wrong with head info!"
	    return 1
    mylock.acquire()
    downamount += 1
    pic_name = set_pic_name(pic_info[1],downamount)
    mylock.release()
    path_name = path + "/" + pic_name
    try:
	print "thread: ",thread_id,"downloading: ",downamount,".jpg"
	pic_url_down(path_name,url)
    except:
	print "downerror"
	downamount -= 1
	return 1
    #print "Ready to check: ",path_name
    check_pic(pic_info[0],path_name)
    return 0
##########################################################    
class Paradownload(threading.Thread): #The timer class is derived from the class threading.Thread  
    def __init__(self, id_num, interval,aimurl):  
	threading.Thread.__init__(self)  
	self.thread_num = id_num      # thread's number
	self.interval = interval      # this attribute doesn't mean anything now,but it's future is bright...
	self.url = aimurl             # url list that thread seek in 
	self.thread_stop = False      # flag to control thread
   
    def run(self): 
	global count,downamount
	while not self.thread_stop and count < len(self.url):
	    pic_down_mine(self.url,dirname,self.thread_num)
	    if downamount >= num:
		    self.thread_stop = True                
    def stop(self):  
	self.thread_stop = True

####### main #######
	
# you can change the max amount of picture which is allowed to download,now is 60*10
for i in range(10):
	if i*60 <= num:
		url = url1 + content + url3 + str(i*60) +url4
	else:break
	sock = urllib.urlopen(url) 
	reg = re.compile("(?<=objURL\":\")(http.*?\.(jpg|png|bmp|jpeg|JPG))")#find image url·
	html = sock.read()
	results = reg.findall(html)
	total_urls.extend(results)     # set the picture's url list

# start threads to download the picture
for i in range((len(total_urls)/30) % 10):
	thread = Paradownload(i,1,total_urls)
	thread_list.append(thread)
	thread_list[i].start()
##thread = Paradownload(1,1,total_urls)
##thread.start()
# stop the threads
##time.sleep(10) 
if count > num:
	for i in range(len(thread_list)):
		thread_list[i].stop()
		print "thread ",i," stop\n"
     

