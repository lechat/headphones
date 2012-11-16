#  This file is part of Headphones.
#
#  Headphones is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Headphones is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Headphones.  If not, see <http://www.gnu.org/licenses/>.

import time, threading

#
# Process reporting
#

progressLock = None
progressData = []

#
# Progress Object
#
class ProgressStatus:
    # identifier
    name = None
    description = None
    message=None
    # ID of the thread
    threadID = None
    threadName = None
    # name of the module that started the process
    startModule = None
    # time at which the process started
    startTime = None
    lastTime = None
    # counter variables 
    maxCount = -1
    currentCount = -1
    
    def stats(self):
        cnt = None
        estimate = None
        pct = None
        elapsed = None
        try:
            if self.currentCount <> -1:
                if self.maxCount <> -1:
                    cnt = "%i/%i" % (self.currentCount+1,self.maxCount)
                else:
                    cnt = "%i" % (self.currentCount + 1)
            elapsed = self.lastTime-self.startTime
            if self.maxCount <> -1:
                pct = float(self.currentCount+1) / float(self.maxCount) * 100.0
                if pct > 100:
                    pct = 100
            else:
                pct = "N/A"
            if pct <> None and pct > 0:
                estimate = (elapsed / pct * 100) - elapsed
                e1 = estimate / 60
                eh = e1 / 60
                em = e1 % 60
                es = estimate % 60
                estimate = "%i:%i:%i" % (eh,em,es)
            else:
                estimate = "N/A"
                
        except Exception as e:
            print e
        return { "cnt":cnt, "estimate":estimate,"pct":pct,"elapsed":elapsed}
    
    def update(self,count=None,msg = None):
        if count <> None:
            self.currentCount = count
        if msg <> None:
            self.message = msg 
        self.lastTime = time.time()
        

#
# Maintenance functions
#

def findFirstByThread(progressData,threadId):
    for p in progressData:
        if p.threadID == threadId:
            return p
    return None
        
def findByName(progressData,name):
    t = threading.current_thread()
    for p in progressData:
        if p.name == name and p.threadID == t.ident:
            return p
    return None

#
# External interface
#
       
def get(name=None,mod=None,desc=None,max=None):
    global progressLock, progressData
    lock()
    check()
    p = None
    try:
        if name == None:
            p = findFirstByThread(progressData,threading.currentThread().ident)
        else:
            p = findByName(progressData,name)
        if p == None:
            p = ProgressStatus()
            t = threading.current_thread()
            p.name = name
            p.threadName = t.name
            p.threadID = t.ident
            progressData.append(p)
        p.startTime = time.time()
        p.lastTime = p.startTime
        p.currentCount = 0
        if mod <> None:
            p.startModule = mod
        if desc <> None:
            p.description = desc
        if max <> None:
            p.maxCount = max
    except:
        pass
    unlock()
    return p

def check():
    global progressLock, progressData
    lock()
    try:
        if progressData == None:
            progressData=[]
        
        tl = threading.enumerate()
        
        for t in tl:
            p = findFirstByThread(progressData,t.ident)
            if p == None:
                p = ProgressStatus()
            p.threadID = t.ident
            p.threadName = t.name
            p.startTime = time.time()
            # p.name = t.name
            p.description = ""
            progressData.append(p)
        for p in progressData[:]:
            if (p.lastTime - time.time()) < 5*60 and p.lastTime <> 0:
                progressData.remove(p)
    except:
        pass 
    unlock()
    
def lock():
    global progressLock
    if progressLock == None:
        progressLock = threading.RLock()
    progressLock.acquire()
    
def unlock():
    global progressLock
    progressLock.release()
    
    