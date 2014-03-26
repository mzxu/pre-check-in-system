'''
Created on Jul 27, 2012

@author: Mingze
'''
import web
from log import log
from adaptor import HTTPAdaptor, SQLAdaptor
from exception import *
import opts
import utils
import config
import render

class SubmitStatus:
    '''
    API for submitting CI build status 
    '''

    def POST(self):
        '''
        Method: post
        '''   
        try:                  
            try:
                data = web.data()
                build_info = utils.json_load_to_str(data)
                log.debug("build info: %s" % build_info)           
            except Exception, e:
                log.error(e)
                raise UnableParsePostDataError
            
            # update status 
            dbopts = SQLAdaptor()
#            commit_id = dbopts.SetBuildStatus(build_info)            
            
            # if all results are failures, send email to commitor
            #
            
            phase_id, failure_list, commit_id = dbopts.CheckBuildFailures(build_info)
            
            if failure_list:
                if not opts.SendEmailToCommitor(build_info, commit_id):
                    dbopts.SetCommitStatus(commit_id, 10)
                else:
                    dbopts.SetCommitStatus(commit_id, 4)
            elif (not failure_list) and (phase_id == 3):
            
                dbopts.SetCommitStatus(commit_id, 1)
            else:
                dbopts.SetCommitStatus(commit_id, 3)
                 
            return HTTPAdaptor.format_response("ok", "003", "Update status based on CI")
        
        except Error, e:
            return HTTPAdaptor.format_response("err", code = e.status, msg = e.message)
        
        except Exception, e:
            return HTTPAdaptor.format_response("err", msg = "Server execution failed")   
    