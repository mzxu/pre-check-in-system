'''
Created on Jul 27, 2012

@author: Mingze
'''

import web, json, re, copy
from log import log
from adaptor import HTTPAdaptor,SQLAdaptor
import config
from exception import *
import opts
import utils

class CheckStatus:
    '''
    API for checking verification result 
    '''
    def GET(self):
        '''
        Method: get
        '''  
        try:
            query = HTTPAdaptor.format_query(web.ctx.env["QUERY_STRING"])
            transaction = query["transaction"] if query.has_key("transaction") else ""
            revision = query["revision"] if query.has_key("revision") else ""
            if not transaction and not revision:
                raise "Invalid query string"

            sopt = SQLAdaptor()
            status = sopt.CheckCommitStatus(transaction, revision)
            return HTTPAdaptor.format_response("ok", status_id = status, msg = "Status %s returned" % status)
        
        except Error, e:
            return HTTPAdaptor.format_response("err", code = e.status, msg = e.message)
        
        except Exception, e:
            return HTTPAdaptor.format_response("err", msg = "Server execution failed")
        
class SVNCallBack:
    '''
    API for submitting call back request
    '''
    def POST(self):
        try:
            #@Step 1: Parse commit info
            try:
                data = web.data()
                callback = utils.json_load_to_str(data)
                log.debug("callback: %s" % callback)
                uuid = callback["uuid"]
                txn = callback["transaction"]
                status = callback["status"]
                           
            except Exception, e:
                log.error(e)
                raise UnableParsePostDataError     
            dbopts = SQLAdaptor()
            dbopts.UpdateStatusByTxn(uuid, txn, status)
            
            return HTTPAdaptor.format_response("ok", "00", "Jobs are triggered. Please wait for the response.")
        
        except Error, e:
            return HTTPAdaptor.format_response("err", code = e.status, msg = e.message)
        
        except Exception, e:
            return HTTPAdaptor.format_response("err", msg = "Server execution failed")
            
            
                   
    
class TriggerRequest:
    '''
    API for submitting trigger request
    '''    
    def POST(self):
        '''
        Method:post
        '''       
        try:
            #@Step 1: Parse commit info
            try:
                data = web.data()
                commit_info = utils.json_load_to_str(data)
                commit_info = opts.FormatChangeSet(commit_info)
                log.debug("commit info: %s" % commit_info)           
            except Exception, e:
                log.error(e)
                raise UnableParsePostDataError               
            
            #@Step 2: Check author info
            if not opts.CheckAuthorInfo(commit_info["author"]):
                return HTTPAdaptor.format_response("pass", "001", "No authors available.")
                
#                log.error(NoAuthorFoundError.message)
#                raise NoAuthorFoundError
            #@Step 3: Check jobs needed to be triggerred
            jobs = opts.GetJobs(commit_info)
            if not jobs:
                log.warning(NoValidJobFoundError.message)
                return HTTPAdaptor.format_response("ok", "001", "No tests can be executed.")
            
            #@Step 4: Insert commit info
            
            dbopts = SQLAdaptor()
            dbopts.InsertCommitInfo(commit_info)
            dbopts.InsertJobInfo(jobs)
            log.debug("set status id to :%s" % 7)
            #@Step 5: Trigger jobs 
            opts.TriggerJobs(jobs) 
            
            return HTTPAdaptor.format_response("ok", "003", "Jobs are triggered. Please wait for the response.")
        
        except Error, e:
            return HTTPAdaptor.format_response("err", code = e.status, msg = e.message)
        
        except Exception, e:
            return HTTPAdaptor.format_response("err", msg = "Server execution failed")
            
            
