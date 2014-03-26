'''
Created on Jan 30, 2013

@author: Mingze
'''
import re, pysvn, sys
from subprocess import Popen, PIPE

metric = '.*/trunk/tools/.*.json' #metric to match the repos path
app_ids = ['153729021352139','300956023300284'] 

def _execcmd(cmd, *args, **kwargs):
    try:
        process = Popen(cmd, stdin = PIPE, stdout = PIPE)
        output = process.communicate()   
        return output     
    except Exception,e:
        print e

def check_schema_changes():
    client = pysvn.Client()
    headrev = client.info(".").revision.number
    
    rev_list = client.update(".") 
    currev = client.info(".").revision.number
    if not headrev == currev:
        log_list = client.log(".",
                              revision_start = rev_list[0],
                              revision_end = rev_list[0], 
                              discover_changed_paths = True)
        if log_list:
            path_list = log_list[0].data['changed_paths']
            p_re = re.compile(metric)
            for path in path_list:
                p = path.data['path']
                if p_re.match(p):
                    return True
    print "no db schema changes" 
    return False

def apply_schema_changes():
    try:
        print "updating db schema"
        for app_id in app_ids:
            cmd = 'php upgradeDatabase.php --appid=%s --ignore-all' % app_id
            output = _execcmd(cmd)
            print output
    except:
        sys.exit(1)

if __name__ == "__main__":
    if check_schema_changes():
        apply_schema_changes()
