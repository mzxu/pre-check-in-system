'''
Created on Jul 31, 2012

@author: Mingze
'''
import os, json, re, urllib, sys, urllib2, base64, errno, stat, shutil
from xml.dom.minidom import parse

metric = '.*//.*/.*' #metric to match the repos path

def get_changes():
    changes_str = os.environ['changes']
    changes_str = changes_str[1:-1]
    print "changes: %s" % changes_str
    try:
        print "Convert changes string to json format"
        changes_json = json.loads(changes_str)
    except Exception,e:
        print "Converting failed"
        print e
        changes_json = None
    return changes_json

def apply_changes(path = None, changes = None):
    try:
        global metric
        #get the workspace directory
        if path:
            workspace = path
        else:
            workspace = os.environ['WORKSPACE']    
        repo_piece = __get_repo_info_from_entries(workspace)
        print "Repo piece: %s" % repo_piece
        if not changes:
            sys.exit("No changes found") 
        for change in changes:
            path = change[1][repo_piece.__len__():].encode('utf-8')
            path = path[1:] if path.startswith("/") else path
            basepath = os.environ["WORKSPACE"]
            fullpath = os.path.join(basepath, path)
            if __is_file(path):
                if not change[0] == "D":
                    file_stream = __get_file(change[1])
            else:
                file_stream = None
            print "Path is %s" % path
            if change[0] == "U":
                print "Updating %s" % fullpath
                __remove_path(fullpath)
                __add_path(fullpath, file_stream)
            if change[0] == "A":
                print "Adding %s" % fullpath
                __add_path(fullpath, file_stream)
            if change[0] == "D":
                print "Deleting %s" % fullpath
                __remove_path(fullpath)
            print "Repository synchronized successfully"
    except Exception,e:
        print "Error: %s" % e



        
    
def __add_path(path, content):        
    if __is_file(path):
        write_to_file(path, content)
    else:
        if not os.path.exists(path):
            os.makedirs(path)
        
        
def __remove_path(path):
    __rm_r(path)
    
    
def __get_file(filename):
    print "Retrieving source file: %s" % filename
    global server_url
    file = filename.replace("/", "_")
    file = file.replace(" ", "_")
    filename = "_".join([os.environ["uuid"], os.environ["transaction"],file])
    url = "/".join([server_url, "static", "files", filename])
    print "file url:%s" % url
    file_content = __get_url(url)
    return file_content
    
def __get_repo_info_from_entries(workspace):
    '''
    Get repo info from .svn/entries. 
    To do:Support two formats: xml and plain text 
    '''    
    entries_file = os.path.join(workspace,".svn/entries")    
    if not os.path.exists(entries_file):
        raise
    try: 
        dom1 = parse(entries_file) # parse an XML file by name
        
    except:
        print "Entries file is not xml format. Switch to plain text mode!"
    repos = []
    p = re.compile(metric)
    print "Metric: %s" % metric
    with open(entries_file) as efile:
        for line in efile:
            if repos.__len__() == 2:
                break
            if p.match(line):                
                repos.append(line.lstrip()[0:-1])
    print "Repos: %s" % repos
    if not repos.__len__() == 2:
        raise
    
    if repos[0].__len__() > repos[1].__len__():
        repo_piece = urllib.unquote(repos[0][repos[1].__len__():]) 
    else:
        repo_piece = urllib.unquote(repos[1][repos[0].__len__():])
    print "Repo_piece: %s" % repo_piece
    if repo_piece[0] == "/":
        return repo_piece[1:]
    else:
        return repo_piece    

def __is_file(path):
    if path.endswith("/"):
        return False
    else:
        return True
    
def write_to_file(filename, content):
    try:
        file_handler = open(filename, 'wb')
        file_handler.write(content)
        file_handler.close()
    except Exception, e:
        sys.exit(e)
        
def __get_url(url, query_string = None, auth = None, body = None, url_encoded = False, proxy = None):
    try:
        
        request = urllib2.Request(url)
    
        if auth:
            username = auth[0]
            password = auth[1]
            if url_encoded:
                auth_string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
            else:
                auth_string = ('%s:%s' % (username, password)).replace('\n', '')
            request.add_header("Authorization", "Basic %s" % auth_string)
        
        if body:
            body = json.dumps(body)
            request.add_data(body)
            
        if proxy:                
            proxy_handler = urllib2.ProxyHandler({"http" : proxy,"https" : proxy})        
            opener = urllib2.build_opener( proxy_handler)
            urllib2.install_opener(opener) 
#        logging.debug(url)                        
#        logging.debug(body)
        response = urllib2.urlopen(request)   
        
        data = response.read()
        
        return data

    except Exception, e:
        sys.exit("cannot get the source code!")

def __rm_r(path):
    try:
        
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=False, onerror=__handle_remove_readonly)
        elif os.path.exists(path):
            os.remove(path)
    except Exception,e:
        print e
        print "Cannot remove the directory"
        
def __handle_remove_readonly(func, path, exc):
    excvalue = exc[1]
    if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
        func(path)
    else:
        raise
    
if __name__ == "__main__":
    global server_url
    server_url = "http://10.197.84.230/pcv"
#    os.environ["change set"] = "[[\"U\", \"emma/src/common/emma_email.py\"],[\"D\", \"emma/src/common/a1/b1/\"],[\"D\", \"emma/src/common/a1/\"]]"
#    os.environ["WORKSPACE"] = "/usr/local/workspace/pre-check-in-trail"
#    os.environ["uuid"] = "274f8cb5-5abf-4111-8702-94e20f53315e"
#    os.environ["transaction"] = "11-f"
    changes = get_changes()
    apply_changes(changes = changes) 
    
        
                
                
        
    