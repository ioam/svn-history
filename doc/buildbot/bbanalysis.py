
import sys
import re
import pickle
from glob import glob

from sys import argv

#logfile = 'LOG'
script = "lissom_oo_or.ty"


V=re.compile(r'[0-9]*-log')
def get_build_no(logfilename):
    return int(V.findall(logfilename)[0].rstrip('-log'))


def create_timings(i_am_sure=False):
    if i_am_sure:
        timings = {}
        f = open('/home/ceball/buildbot/timings.pkl','w')
        pickle.dump(timings,f,0)
        f.close()

def create_startups(i_am_sure=False):
    if i_am_sure:
        startups = {}
        f = open('/home/ceball/buildbot/startups.pkl','w')
        pickle.dump(startups,f,0)
        f.close()

    
def get_timings():
    f = open('/home/ceball/buildbot/timings.pkl')
    timings = pickle.load(f)
    f.close()
    return timings

def save_timings(timings):
    f = open('/home/ceball/buildbot/timings.pkl','w')
    pickle.dump(timings,f,0)
    f.close()


def get_startups():
    f = open('/home/ceball/buildbot/startups.pkl')
    startups = pickle.load(f)
    f.close()
    return startups

def save_startups(startups):
    f = open('/home/ceball/buildbot/startups.pkl','w')
    pickle.dump(startups,f,0)
    f.close()


def get_date_version_time(logfile,timings=None,startups=None):

    build = get_build_no(logfile)
    
    f = open(logfile)
    all_lines = f.readlines()
    f.close()

    ok = ok2 = False
    #datei=versioni=timingi=cpusei=startupi=-1
    i = 0;
    for line in all_lines:
        if line.find("Running at")>=0:
            
            datei=i
        elif line.find("svnversion")>=0:
            
            versioni=i
        elif line.startswith("[examples/%s]"%script):
            timingi=i
            
        elif line.find("[examples/%s startup]"%script)>=0:
            startupi=i
            
        elif line.find("Results from examples/%s have not changed."%script)>=0:
            ok2=True
        elif line.find('program finished')>=0:
            ok=True

        i+=1;

    if not ok:
        print "...build %s currently incomplete"%build
        return None

    if not ok2:
        print "...speed test invalid because results didn't match"
        return None


#
#    try:
#        startupi
#    except:
#        print build
#        for l in all_lines:
#            if l.startswith("[examples/%s startup]"%script):
#                print "*****",l,script
#     
#        raise
#


    datel= all_lines[datei]
    d=re.compile(r'at [0-9]*')
    date = float(d.findall(datel)[0][3::])

    versionl = all_lines[versioni]
    v=re.compile(r'n [0-9]*')
    version = int(v.findall(versionl)[0][2::])

    timel = all_lines[timingi]
    t=re.compile(r'Now: [0-9.]* ')
    start,stop = t.search(timel).span()
    timing = float(timel[start+5:stop-1])

    cpusel = all_lines[timingi+1]
#    if cpusel.find('elapsed')>0:
    start,stop = cpusel.index('elapsed')+8,cpusel.index('%CPU')
    cpu_usage = float(cpusel[start:stop])

    startupl = all_lines[startupi]
    t=re.compile(r'Now: [0-9.]* ')
    start,stop = t.search(startupl).span()
    startup = float(startupl[start+5:stop-1])

    startcpusel = all_lines[startupi+1]
#    if cpusel.find('elapsed')>0:

    try:
        start,stop = startcpusel.index('elapsed')+8,startcpusel.index('%CPU')
        startcpusage = float(startcpusel[start:stop])
    except ValueError:
        startcpusage = 99  # HACK to get some data
    

    
#    timingl = all_lines[timingi]
#    u=re.compile(r'[0-9\.]*user')
#    user = float(u.findall(timingl)[0].rstrip('user'))
#    s=re.compile(r'[0-9\.]*system')
#    system = float(s.findall(timingl)[0].rstrip('system'))
#    cpu_time=user+system

    if timings:

        if cpu_usage>95:            
            timings[script][build] = (date,version,timing,cpu_usage)
        else:
            timings[script][build]=None
            print "...build %s had %s percent cpu during timing (not >95)"%(build,cpu_usage)

    if startups:

        if startcpusage>95:
            startups[script][build] = (date,version,startup,startcpusage)
        else:
            startups[script][build] = None
            print "...build %s had %s percent cpu during startup (not >95)"%(build,startcpusage)

    return (build,date,version,timing,startup,cpu_usage)


MIN_BUILD=153
filename_pattern = '*-log-shell_2-stdio'
def update_timings(location="/home/ceball/buildbot/buildmaster/slow-tests_x86_ubuntu7.04/"):

    timings = get_timings()

    if script not in timings:
        timings[script]={}


    startups = get_startups()

    if script not in startups:
        startups[script]={}

    filenames = glob(location+filename_pattern)
    for filename in filenames:

        build = get_build_no(filename)

        if build>=MIN_BUILD:
            
	    do_timings=do_startups=False

            if build not in timings[script]: 
                print "Adding timing for build...",build
		do_timings=True
            
            if build not in startups[script]:
                print "Adding startup time for build...",build
            	do_startups=True
		
	    if do_timings and do_startups:
                get_date_version_time(filename,timings,startups)
            if do_timings and not do_startups:
                get_date_version_time(filename,timings,None)
            if not do_timings and do_startups:
                get_date_version_time(filename,None,startups)

    save_timings(timings)
    save_startups(startups)
    #print timings
    




    
if __name__=='__main__':
    if len(sys.argv)>1:
        if sys.argv[1]=='update':
            update_timings()
