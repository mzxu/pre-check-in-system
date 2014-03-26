# Implements a Subversion-to-Hudson notifier for the post-commit hook.
# Using "svnlook changed" on a repository, the script filters all the
# paths in a specified commit revision (usually the latest).
# The paths are mapped into a normalised form used for Hudson project
# names. These are then used to request the corresponding URLs from the
# Hudson server. These requests cause builds to be triggered.
#
# Copyright (c) 2009 Rick Beton & Gustavo Niemeyer
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.


import sys, os, time, getpass
import getopt
import urllib, urllib2
import logging
import copy
import base64
import json
import re
from datetime import datetime
from subprocess import Popen, PIPE
__diff_metric__ = ("Modified", "Deleted", "Added")

try:
  # Python >=3.0
  from subprocess import getstatusoutput as subprocess_getstatusoutput
except ImportError:
  # Python <3.0
  from commands import getstatusoutput as subprocess_getstatusoutput
try:
    my_getopt = getopt.gnu_getopt
except AttributeError:
    my_getopt = getopt.getopt
import re
from array import array

class Error(Exception): pass

LOG_FILENAME = 'svn-jenkins.log'
SECTION = re.compile(r'\[([^]]+?)(?:\s+extends\s+([^]]+))?\]')
OPTION = re.compile(r'(\S+)\s*=\s*(.*)$')

#{{{  Config

class Config:
    def __init__(self, filename):
        # Options are stored in __sections_list like this:
        # [(sectname, [(optname, optval), ...]), ...]
        self._sections_list = []
        self._sections_dict = {}
        self._read(filename)

    def _read(self, filename):
        # Use the same logic as in ConfigParser.__read()
        file = open(filename)
        cursectdict = None
        optname = None
        lineno = 0
        for line in file:
            lineno = lineno + 1
            if line.isspace() or line[0] == '#':
                continue
            if line[0].isspace() and cursectdict is not None and optname:
                value = line.strip()
                cursectdict[optname] = "%s %s" % (cursectdict[optname], value)
                cursectlist[-1][1] = "%s %s" % (cursectlist[-1][1], value)
            else:
                m = SECTION.match(line)
                if m:
                    sectname = m.group(1)
                    parentsectname = m.group(2)
                    if parentsectname is None:
                        # No parent section defined, so start a new section
                        cursectdict = self._sections_dict.setdefault( sectname, {} )
                        cursectlist = []
                    else:
                        # Copy the parent section into the new section
                        parentsectdict = self._sections_dict.get( parentsectname, {} )
                        cursectdict = self._sections_dict.setdefault( sectname, parentsectdict.copy() )
                        cursectlist = self.walk( parentsectname )
                    self._sections_list.append( (sectname, cursectlist) )
                    optname = None
                elif cursectdict is None:
                    raise Error("%s:%d: no section header" % \
                                 (filename, lineno))
                else:
                    m = OPTION.match(line)
                    if m:
                        optname, optval = m.groups()
                        optval = optval.strip()
                        cursectdict[optname] = optval
                        cursectlist.append([optname, optval])
                    else:
                        raise Error("%s:%d: parsing error" % \
                                     (filename, lineno))

    def sections(self):
        return list(self._sections_dict.keys())

    def options(self, section):
        return list(self._sections_dict.get(section, {}).keys())

    def get(self, section, option, default=None):
        return self._sections_dict.get(section, {}).get(option, default)

    def walk(self, section, option=None):
        ret = []
        for sectname, options in self._sections_list:
            if sectname == section:
                for optname, value in options:
                    if not option or optname == option:
                        ret.append((optname, value))
        return ret

#}}}  Config
#{{{  SVNLook: Wraps /usr/bin/svnlook in Python API

class SVNLook:
    def __init__(self, repospath, txn=None, rev=None):
        self.repospath = repospath
        self.txn = txn
        self.rev = rev
        
    def _execcmd(self, cmd, *args, **kwargs):
        try:
            process = Popen(cmd, stdin = PIPE, stdout = PIPE)
            output = process.communicate()
            logging.debug(output)
            return output
        except Exception,e:
            logging.error(e)
            raise Error("command failed")       

    def _execsvnlook(self, cmd, **kwargs):
        execcmd_args = ["svnlook.exe", cmd, self.repospath]
        self._add_txnrev(execcmd_args)
        logging.debug(execcmd_args)
        return self._execcmd(execcmd_args)

    def _add_txnrev(self, cmd_args):
        if self.txn is not None:
            cmd_args += ["-t", self.txn]
        if self.rev is not None:
            cmd_args += ["-r", self.rev]

    def changed(self,  **kwargs):
        output, status = self._execsvnlook("changed", **kwargs)
        changes = []
        for line in output.splitlines():
            line = line.rstrip()
            if not line: continue
            entry = [None, None, None]
            changedata, changeprop, path = None, None, None
            if line[0] != "_":
                changedata = line[0]
            if line[1] != " ":
                changeprop = line[1]
            path = line[4:]
            changes.append((changedata, changeprop, path))
        return changes

    def author(self, **kwargs):
        output, status  = self._execsvnlook("author", **kwargs)
        return output.strip()
    
    def uuid(self):
        output, status = self._execcmd(["svnlook.exe", "uuid", self.repospath])
        return output.strip()
    
    def comments(self, **kwargs):
        output, status = self._execsvnlook("log", **kwargs)
        return output
    
    def cat(self, file):
        output, status = self._execcmd(["svnlook", "cat", "-t", self.txn, self.repospath, file])
        return output
    
    def diff(self):
        output, status = self._execcmd(["svnlook", "diff", "-t", self.txn, self.repospath])
        return output
#====================
#}}}   End of SVNlook

#Generates valid body for jenkins
def format_body(json):
    try: 
        param_list = []

        for k,v in json.iteritems():
            param_dict = {"name":k,
                          "value":v}
            param_list.append(param_dict)  
             
        body = {"Submit":"Build",
                "json":{
                        "parameter":param_list}
                }
        logging.debug(body)
        return urllib.urlencode(body)
    except Exception, e:
        logging.error(e)
        
        
# Gets a particular HTTP URL and returns the status code.
def get_url(url, query_string = None, auth = None, body = None, url_encoded = False, proxy = None):
    try:
        
        request = urllib2.Request(url)
        logging.debug(url)
	
        if auth:
            username = auth[0]
            password = auth[1]
            if url_encoded:
                auth_string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
            else:
                auth_string = ('%s:%s' % (username, password)).replace('\n', '')
            request.add_header("Authorization", "Basic %s" % auth_string)
            logging.debug("add auth to request")
        
        if body:
#            logging.debug(body) 
            body = json.dumps(body)
            request.add_data(body)
            logging.debug("add body to request")
            
        if proxy:                
            proxy_handler = urllib2.ProxyHandler({"http" : proxy,"https" : proxy})        
            opener = urllib2.build_opener( proxy_handler)
            urllib2.install_opener(opener) 
            logging.debug("add proxy to request")
#        logging.debug(url)                        
#        logging.debug(body)
        response = urllib2.urlopen(request)   
        
        data = response.read()
#        logging.debug("data: %s" % data)
        
        return json.loads(data) 

    except Exception, e:
        logging.error(e)
        logging.error("Cannot get correct response from server. Mark the commit to success.")
        sys.exit(0)     

# Ask Hudson to start a build.
def request_build (urlprefix, string, urlsuffix, author):
    url.prefix = opts.urlprefix
    jobname = job, job, opts.urlsuffix, author
    if not urlprefix:
      print string
      return 200
    elif not urlsuffix:
      return getUrl( urlprefix + string, author )
    else:
      return getUrl( urlprefix + string + urlsuffix, author )


# Process a path and decide what builds to start.
def process_path (opts, mappings, reposName, path, done):
    steps = path.split('/')
    if len(steps)>0 and steps[len(steps)-1] != "":
      base = steps[0]
      if base in levels:
        levellist = levels[base]
        code = 404
        logging.debug( reposName + " " + path )
        for level in levellist:
          logging.debug( "  " + base + " with " + str(level) + " levels" )
          if code == 404 and len(steps)>level:
            string = opts.alias
            for i in range(level):
              string += opts.separator + steps[i]
            if not string in done:
              done[string] = 1
              code = request_build( opts.urlprefix, string, opts.urlsuffix )
      else:
        logging.debug( "unwanted " + reposName + " " + path )
    else:
      logging.debug( "ignored " + reposName + " " + path )


# Construct a dict where every key is one of the options in the config file and
# the value is a reverse-sorted array of integers.
def construct_levels (config):
    levels = {}
    for option, value in config.walk("mappings"):
      levellist = array('i')
      for a in value.split():
        levellist.append( int(a) )
      levels[option] = levellist
      levels[option].reverse()
      logging.debug( "level for " + option + "=" + value + " as " + str(levels[option]) )
    return levels

def get_mapping(config):
    return config.options("mappings")

def get_author(config):
    return config.options("authors")

def get_diffs(diffstream, filename):       
    diff_list = diffstream.split('\n') 
    diff = []
    grep_flag = False
    for line in diff_list:
        for metric in __diff_metric__:
            if line.startswith(metric):
                if filename in line:
                    grep_flag = True
                else: 
                    grep_flag = False
        if grep_flag:
            diff.append(line)
    return '\n'.join(diff)
    
def get_jobs(opts, mappings, config):
    jobs = {}
    svnlook = SVNLook( opts.repository, txn=opts.transaction, rev=opts.revision )
    changes = svnlook.changed()
    author = svnlook.author()
    uuid = svnlook.uuid()
    comments = svnlook.comments()
    diffstream = svnlook.diff()
    
    logging.debug("changes: %s" % changes)
    logging.debug("author: %s" % author)
    logging.debug("uuid: %s" % uuid)
    logging.debug("comments: %s" % comments)
    
    
    if author in get_author(config):
        token = config.get("authors", author)
        logging.debug( "Author validation passed" ) 
    
        re_repos = []
        if mappings:
            for mapping in mappings:   
                changelist = []      
                job = None      
                for changedata, changeprop, path in changes:            
                    re_repo = re.compile(mapping) 
                    if re_repo.search(path):
                        job = config.get("mappings",mapping)
                        changelist.append([changedata, path])
                if job:
                    jobs[job] = {
                                "change set":json.dumps(copy.deepcopy(changelist)),
                                "author": author,
                                "token": token,
                                "comments": comments,
                                "transaction": opts.transaction if opts.transaction else '',
                                "revision": opts.revision if opts.revision else '' } 
                     
                    logging.debug("Valid jobs found")
                else:
                    logging.debug("No valid jobs found for regex: %s" % mapping)
 
    else:
        logging.debug( "Invalid author: %s" % author ) 
        
    return jobsPOST

def trigger_jobs(opts, jobs):
    for job_name, job_content in jobs.iteritems():
        urlprefix = opts.urlprefix
        urlsuffix = opts.urlsuffix
        auth = [job_content["author"], job_content["token"]]
        logging.debug("auth: %s token: %s" % (job_content["author"], job_content["token"]))
        if not urlprefix:
            print string
            code = 200
        elif not urlsuffix:
            code = getUrl( urlprefix + job_name, auth, job_content )
        else:
            code = getUrl( urlprefix + job_name + urlsuffix, auth, job_content )
        logging.info("trigger request sent for job '%s'. code returned is %s" % (job_name, code))
        

    
def notify_ci (opts, config):
    for option, value in config.walk("general"):
        logging.debug( option + " = " + value )
    reposParts = opts.repository.split('/')
    reposName = reposParts[len(reposParts) - 1]
    opts.alias     = config.get( "general", "alias", reposName )
    opts.separator = config.get( "general", "separator", '~' )
    opts.urlprefix = config.get( "general", "urlprefix" )
    opts.urlsuffix = config.get( "general", "urlsuffix" )
    
    mappings = get_mapping(config)  
    
    jobs = get_jobs(opts, mappings, config)
    
    if jobs:
        logging.info("Trigger jobs begin")
        trigger_jobs(opts, jobs)
    logging.info("Commit finished")

def filter_by_author(config, author):
    logging.info("Filtering by author...")
    author_filter = config.get("filters","author")
    if not author in author_filter.split(","):
        logging.info("The author is not in author list. Mark the commit as success." )
        sys.exit(0)

def filter_by_path(config,changes):
    logging.info("Filtering by path...")
    change_list = []
    filters = config.get("filters", "repos").split(",")
    exclusions = config.get("filters", "exclusions").split(",")
    logging.debug("filters: %s" % filters)
    logging.debug("changes: %s" % changes)
    for change in changes:            
        path = change[2]
        logging.debug("path: %s" % path)
        for filter in filters:
            re_repo = re.compile(filter) 
            if re_repo.search(path):
                change_list.append(change)
                
        for exclusion in exclusions:
            re_excl = re.compile(exclusion)
            if re_excl.search(path):
                change_list.remove(change)
            
    if not change_list:    
        logging.info("All changes doesn't match the filters. Mark the commit as success." )
        sys.exit(0)        
    return change_list
       

def notify_cvproxy (opts, config):
    try:
        svnlook = SVNLook( opts.repository, txn=opts.transaction, rev=opts.revision )
        logging.debug("get commit info")
        logging.debug("repos: %s" % opts.repository)
        logging.debug("txn: %s" % opts.transaction)
        logging.debug("rev: %s" % opts.revision)
        logging.debug("evn: %s" % os.environ['PATH'])
        logging.debug("user: %s" % getpass.getuser())
        changes = svnlook.changed()
        author = svnlook.author()
        uuid = svnlook.uuid()
        comments = svnlook.comments()
        logging.debug("author: %s" % author)
        
        filter_by_author(config, author)
        filtered_changes = filter_by_path(config, changes)
        
        change_list  = []
        diffstream = svnlook.diff()
#        logging.debug("changes %s", changes)
        for change in filtered_changes:
            change_dict = {
                           "type": change[0],
                           "filename": change[2]
                           }
            if change[0] != "D" and change[2][-1] != "/":                
                file_content = svnlook.cat(change[2].replace(" ", "\ "))
#                logging.debug("file content \n %s" % file_content)
                change_dict["filecontent"] = file_content
            if change[2][-1] != "/":
                change_dict["diffcontent"] = get_diffs(diffstream, change[2])

            change_list.append(change_dict)
        logging.debug("change_list: %s" % change_list)
        #send request to trigger the tests
        data_trigger_jobs = {"changes": change_list,
                "author": author,
                "uuid": uuid,
                "comments": comments,
                "transaction": opts.transaction if opts.transaction else '',
                "revision": opts.revision if opts.revision else ''}
#        if svnlook.author() == "ycao":
#            sys.exit(0)
        logging.debug("get ci server info")
        
        url_trigger_jobs = "/".join([config.get("general", "cvproxy"), "triggerrequest"])
        logging.debug("url %s" % url_trigger_jobs)
#        logging.debug("body %s" % data_trigger_jobs)
        response = get_url(url_trigger_jobs, body = data_trigger_jobs)
        
        logging.debug("response %s" % response)    
        try:
            if response["status"] == "ok":
                pass
            elif response["status"] == "pass":
                sys.exit(0)
            else:
                sys.exit("Error status found. Please contact the administrator")
        except Exception, e:
            logging.error("Cannot get correct repsonse from cvproxy. Reject the commit request")
            logging.error(e) 
            sys.exit("Something wrong during the verification. Please contact the administrator!")
        
        #check status 
        
        query_string = "transaction=%s&revision=%s" % (opts.transaction if opts.transaction else '',
                                                       opts.revision if opts.revision else '')
        url_check_status = "/".join([config.get("general", "cvproxy"), "checkstatus?%s" % query_string])

        start_time = datetime.utcnow() 
        timeout = config.get("general", "timeout")
        passtime = config.get("general", "passtime")
        logging.debug("check status returned by cvproxy")
        
        while (True):
            response = get_url(url_check_status, query_string = query_string)
            logging.debug("dict? %s" % response.has_key("status_id"))
            logging.debug("response data: %s" %response)
#            if not response.has_key["status_id"]:
#                sys.exit("Something wrong during the verification. Please contact the administrator!")
            status_id = response["status_id"]
            logging.debug("status_id: %s" % status_id)
            current_time = datetime.utcnow()
            timespan = current_time - start_time
            if status_id in (1,5,13):
                break
            elif status_id in (2,6,8,9,10,11):
                sys.exit("Your commit has been rejected due to test failures.")
            elif status_id == 3:                
                #pending for test
                #If the tests are pending too long, set the commit passed
                if timespan.seconds > int(passtime):
                    logging.debug("The test lasts too long, set the commit pass")
                    sys.exit(0)

            logging.debug("Time left: %is" % (int(timeout)-timespan.seconds))
            if timespan.seconds > int(timeout):
                logging.debug("time out")
                sys.exit("Time out. Your commit has been rejected.")
#                sys.exit(0)
            time.sleep(10)

            
    except Exception, e:
        logging.error(e)
        sys.exit("Something wrong with the hook scripts. Please contact the administrator!")
    
        

def init_logging (repoDir, loglevel):
    logdir = os.path.join( repoDir, "logs" )
    if not os.path.isdir(logdir):
      os.mkdir( logdir, 0755 );
    logfile = os.path.join( logdir, LOG_FILENAME )
#    logging.basicConfig( filename=logfile, level=loglevel )
#    logfile = "/usr/local/workspace/svn-hook.log"
    logger = logging.getLogger()
    logger.setLevel( loglevel )
    # create console handler and set level to debug
    ch = logging.FileHandler(logfile)
    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - {%(pathname)s:%(lineno)d} - %(message)s")
    # add formatter to ch
    ch.setFormatter( formatter )
    # add ch to logger
    logger.addHandler( ch )
    logger.setLevel(loglevel)
    #handler = logging.handlers.RotatingFileHandler(
    #          logfile, maxBytes=20, backupCount=5)
    #logger.addHandler( handler )


# Command:

USAGE = """\
Usage: svn-jenkins.py OPTIONS

Options:
    -p PATH    Use repository at PATH to check changes
    -f PATH    Use PATH as configuration file (default is repository
               path + /conf/svn-jenkins.conf)
    -t TXN     Optional Subversion transaction TXN for commit information
    -r REV     Optional Subversion revision REV for commit information (for tests)
    -v, -d     Verbose or debug logging
    -h         Show this message

The path, transaction and revision options are passed to "svnlook changed".

Example:
  svn-jenkins.py -p repos
"""

class MissingArgumentsException(Exception):
    "Thrown when required arguments are missing."
    pass

def parse_options():
    try:
        opts, args = my_getopt(sys.argv[1:], "f:p:r:t:hvd", ["help"])
    except getopt.GetoptError, e:
        raise Error(e.msg)
    class Options: pass
    obj = Options()
    obj.filename = None
    obj.repository = None
    obj.transaction = None
    obj.revision = None
    obj.loglevel = logging.DEBUG
    obj.alias = None

    for opt, val in opts:
        if opt == "-f":
            obj.filename = val
        elif opt == "-p":
            obj.repository = val
        elif opt == "-t":
            obj.transaction = val
        elif opt == "-r":
            obj.revision = val
        elif opt == "-v":
            obj.loglevel = logging.INFO
        elif opt == "-d":
            obj.loglevel = logging.DEBUG
        elif opt in ["-h", "--help"]:
            sys.stdout.write(USAGE)
            sys.exit(0)

    missingopts = []
    if not obj.repository:
        missingopts.append("repository")
    if missingopts:
        raise MissingArgumentsException("missing required option(s): " + ", ".join(missingopts))
    if obj.filename is None:
        obj.filename = os.path.join(obj.repository, "conf", "svn-ci.conf")

    obj.repository = os.path.abspath(obj.repository)
    if not (os.path.isdir(obj.repository) and
            os.path.isdir(os.path.join(obj.repository, "db")) and
            os.path.isdir(os.path.join(obj.repository, "hooks")) and
            os.path.isfile(os.path.join(obj.repository, "format"))):
        raise Error("path '%s' doesn't look like a repository" % \
                     obj.repository)

    init_logging( obj.repository, obj.loglevel )
    return obj


def main():
    try:
        opts = parse_options()
        config = Config( opts.filename )
#        notify_ci( opts, config )
        notify_cvproxy(opts, config)

    except MissingArgumentsException, e:
        sys.stderr.write("%s\n" % str(e))
        sys.stderr.write(USAGE)
        sys.exit(1)
    except Error, e:
        sys.stderr.write("error: %s\n" % str(e))
        sys.exit(1)

if __name__ == "__main__":
    os.environ["PATH"] = "C:\\Program Files (x86)\\VisualSVN Server\\bin;"+ os.environ["PATH"]
    main()