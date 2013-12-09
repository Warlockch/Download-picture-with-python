#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys,os,re   
import urllib
import time
import threading
# an example of Baidu image search :http://image.baidu.com/i?ct=201326592&lm=-1&tn=result_pageturn&pv=&word=%E5%91%B5%E5%91%B5&z=0&pn=0&cl=2&ie=utf-8#pn=0
dirname = raw_input('Please choose where you want to store your picture\n(example: D:\picture ): ')
content = raw_input('Please input the content you want to search: ')
num = input('Please input the amount of pictures: ')
url1 = "http://image.baidu.com/i?ct=201326592&lm=-1&tn=result_pageturn&pv=&word="
url2 = "&z=0&pn=0&cl=2&ie=utf-8#pn=0"
url3 = "&z=0&pn="
url4 = "&cl=2&ie=utf-8#pn=0"# these urls make up the url of the Baidu image's source code
mylock = threading.RLock()  # use myblock to help share data between threads
count = 0                   # count the downloaded picture
total_urls = []             # the url index
thread_list = []            # thread list
# set the path from you input,create one if not exists.
if os.access(dirname,0):
        pass
else:
	os.makedirs(dirname)
#down with wget.exe 	
def down_pic_wget(url):
        global count,mylock
        os.chdir(dirname)
        dlcommand = "wget -N --timeout=30 --tries=3 %s" %(url)     
        if os.system(dlcommand)==0:      # needs to improve
                        print "Download %s ..." %(url)
                        mylock.acquire()  # Get the lock  
                        count += 1        
                        #print '\nThread(%d) released'%(self.thread_num)
                        mylock.release()  # release the lock
        else:
                        print "Fail download %s ..." %(url)
        print "done"
        
class Paradownload(threading.Thread): #The timer class is derived from the class threading.Thread  
    def __init__(self, id_num, interval,aimurl):  
        threading.Thread.__init__(self)  
        self.thread_num = id_num         # thread's number
        self.interval = interval      # this attribute doesn't mean anything now,but it's future is bright...
        self.url = aimurl             # url list that thread seek in 
        self.thread_stop = False      # flag to control thread
   
    def run(self): 
        global count
        while not self.thread_stop and count < len(self.url):
            down_pic_wget(self.url[count][0])
            if count > num:
                    self.thread_stop = True                
    def stop(self):  
        self.thread_stop = True 


        
# you can change the max amount of picture that is allowed to download,now is 60*10
for i in range(10):
        if i*60 <= num:
                url = url1 + content + url3 + str(i*60) +url4
        else:break
        sock = urllib.urlopen(url) 
        reg = re.compile("(?<=objURL\":\")(http.*?\.(jpg|gif|png|bmp|jpeg|JPG))")#正则表达式匹配下载地址·
        html = sock.read()
        results = reg.findall(html)
        total_urls.extend(results)     # set the picture's url list

# start threads to download the picture
for i in range((len(total_urls)/30) % 10):
        thread = Paradownload(i,1,total_urls)
        thread_list.append(thread)
        thread_list[i].start()
# stop the threads
##time.sleep(10) 
if count > num:
        for i in range(len(thread_list)):
                thread_list[i].stop()
                print "thread ",i," stop\n"
         

