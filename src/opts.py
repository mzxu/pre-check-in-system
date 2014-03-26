'''
Created on Jul 31, 2012

@author: Mingze
'''
import re, json, copy, oursql, os
from urlparse import urljoin
from datetime import datetime
import config, utils
from log import log
from sqls import *
from exception import *
from adaptor import HTTPAdaptor, SQLAdaptor
import render
from pygments.lexers import get_lexer_for_filename
from pygments.formatters import HtmlFormatter
from pygments import highlight


def CheckAuthorInfo(author):
    if not config.authors.has_key(author):
        return False
    if not config.authors[author].has_key("qe"):
        return False
    if not config.authors[author].has_key("token"):
        return False
    return True

def FormatChangeSet(commit_info):
    '''
       1. Parse the change set
       2. Store the files to hard disk
       3. Replace the file stream to file name in change list
    '''
    uuid = commit_info["uuid"]
    transaction = commit_info["transaction"]
    changes = commit_info["changes"]
    for change in changes:
        if change.has_key("filecontent"):
            index = changes.index(change)
            file = change["filename"].replace("/", "_")
            file = file.replace(" ", "_")
            filename = "_".join([uuid, transaction, file])
            path = os.path.join(config.server["static"], "files", filename)
            log.debug("Write file to path: %s" % path)
            utils.write_to_file(path, change["filecontent"])
            changes[index]["fileurl"] = "/".join(["static","files", filename]) 
            if change["diffcontent"]:
                diff_path = "%s.diff" % path
                changes[index]["diffpath"] = diff_path
                utils.write_to_file(diff_path, change["diffcontent"])
    return commit_info

def FormatDiffs(diff_list):
    log.debug("Formatting diffs: %s" % diff_list)
    code_diffs = []
    for diff in diff_list:
        filename = diff[0]
        filepath = diff[1]
        if os.path.exists(filepath):       
            lexer = get_lexer_for_filename(filepath)
            fn = open(filepath)
            filecontent = fn.read()
        else:
            raise
        code_diff = highlight(filecontent, lexer, HtmlFormatter())
        diff_dict = {
                     "index": diff_list.index(diff),
                     "filename": filename,
                     "filecontent": code_diff
                     }
        code_diffs.append(diff_dict)
    log.debug("Code diffs: %s" % code_diffs)
        
    return code_diffs

def FormatFailedJobs(failed_jobs):
    ci_url = config.ciserver["urlprefix"]
    formatted = []
    if failed_jobs:
        for failed_job in failed_jobs:
            formatted.append({"name":failed_job[0], 
                      "url": "/".join([ci_url,failed_job[0],str(failed_job[1])])
                    })
    return formatted
        
def GetJobs(commit_info):
    jobs = {}
    changes_list = commit_info["changes"]
    
    changes = []
    for change_dict in changes_list:
        change_list = []
        change_list.append(change_dict["type"])
        change_list.append(change_dict["filename"])
        changes.append(change_list)
        
    author = commit_info["author"]
    uuid = commit_info["uuid"]
    comments = commit_info["comments"]
    token = config.authors[author]["token"]
    
    log.debug("changes: %s" % changes)
    log.debug("author: %s" % author)
    log.debug("uuid: %s" % uuid)
    log.debug("comments: %s" % comments)   
    log.debug( "Author validation passed" ) 
    
    if config.mapping:
        for mapping in config.mapping.keys():   
            changelist = []      
            job = None      
            for change in changes:            
                path = change[1]
                re_repo = re.compile(mapping) 
                if re_repo.search(path):
                    job = config.mapping[mapping]
                    changelist.append(change)
            if job:
                change_set = json.dumps(copy.deepcopy(changelist))
                print "changes: %s" % change_set
                jobs[job] = {
                            "changes":change_set,
                            "author": author,
                            "token": token,
                            "uuid": uuid,
                            "comments": comments,
                            "transaction": commit_info["transaction"] if commit_info.has_key("transaction") else '',
                            "revision": commit_info["revision"] if commit_info.has_key("revision") else '' } 
                 
                log.debug("Valid jobs found")
            else:
                log.debug("No valid jobs found for regex: %s" % mapping)        
    return jobs
'''
def CheckDownstreamJobs(job):
    #retrieve from CI
    try:
        downstream_jobs = []
        urlprefix = config.ciserver["urlprefix"]
        urlsuffix = config.ciserver["api_json_depth2"]
        if not urlprefix:            
            raise IncorrectCIServerPrefixError            
        elif not urlsuffix:
            raise IncorrectCIServerSuffixError
        else:
            job_url = "/".join([urlprefix, job[0], job[1], urlsuffix])
            log.debug("Job url: %s" % job_url)
            build_info_raw = HTTPAdaptor.get_url(job_url, return_code = False)
            build_info = utils.json_load_to_str(build_info_raw)
            if build_info.has_key("fingerprint"):
                downstream_jobs = ParseFingerprint(build_info, job[0])
    except Exception, e:
        log.debug("Failed to check downstream jobs")
        log.error(e)
    finally:
        return downstream_jobs
'''

def ParseFingerprint(build_info, current_job_name):
    '''
    Parse fingerprint info and format the return value to a url list
    A sample input data is:
    {
        ...
       "fingerprint":[
          {
             "fileName":"fingerprint",
             "hash":"d6c699818f0d2e7ebf1f950628465708",
             "original":{
                "name":"SP1_GW_Deploy_API_Server",
                "number":275
             },
             "timestamp":1347232586927,
             "usage":[
                {
                   "name":"SP1_T01.GW_Friendlist_Syntax_FT",
                   "ranges":{
                      "ranges":[
                         {
                            "end":252,
                            "start":251
                         }
                      ]
                   }
                },
                {
                   "name":"SP1_GW_Deploy_API_Server",
                   "ranges":{
                      "ranges":[
                         {
                            "end":276,
                            "start":275
                         }
                      ]
                   }
                }
             ]
          }
       ]
    }
    '''
    try:
        downstream_jobs = []
        for fingerprint in build_info["fingerprint"]:
            downstream_builds = fingerprint["usage"]
            for build in downstream_builds:
                build_num = build["ranges"]["ranges"][0]["start"]
                if build["name"] != current_job_name:
                    downstream_jobs.append([build["name"], build_num])
    except Exception,e:
        log.debug("Fingerprint info: %s" % fingerprint)
        log.error("Exception: %s" % e)
        log.error("Fail to parse fingerprint")
    finally:
        return downstream_jobs
        
    
def TriggerJobs(jobs):
    is_triggered = False
    for job_name, job_content in jobs.iteritems():
        urlprefix = config.ciserver["urlprefix"]
        urlsuffix = config.ciserver["urlsuffix"]
        auth = [job_content["author"], job_content["token"]]
        log.debug("auth: %s token: %s" % (job_content["author"], job_content["token"]))
        if not urlprefix:            
            raise IncorrectCIServerPrefixError            
        elif not urlsuffix:
            raise IncorrectCIServerSuffixError
        else:
            job_url = "".join([urlprefix, job_name, urlsuffix])
            log.debug("Job url: %s" % job_url)
            body = utils.format_body_for_ci(job_content)
            code = HTTPAdaptor.get_url(job_url , auth = auth, body = body)
            if not code == 200:
                dbopts = SQLAdaptor()
                dbopts.SetBuildToInvalid(job_name, job_content)
                log.error("Code: %s" % code)
            else:
                is_triggered = True
                log.info("trigger request sent for job '%s'. code returned is %s" % (job_name, code))
    if not is_triggered:
        raise NoJobTriggeredError       
    
def SendEmailToCommitor(build_info, commit_id):
    try:
        title = "Please review your commits"
        author = build_info["build"]["parameters"]["author"]
        mail_to = ["@".join([author,"microstrategy.com"])]                
        content = render.render_email_for_commitor(commit_id, build_info["build"]["parameters"])
        utils.send_email(content, title, mail_to)
        log.debug("author: %s\nmail_to: %s\n" % (author, mail_to))
        return True
    except Exception, e:
        log.error(e)
        log.error("Failed to send email to commitor")
        return False
    
