'''
Created on Aug 20, 2012

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



class CurrentRequest:
    '''
    Processing request for viewing current request 
    '''
    
    def GET(self):
        '''
        Method:get
        '''
        try:
            log.info("CI:Get")
            query = HTTPAdaptor.format_query(web.ctx.env["QUERY_STRING"])
            if not (query.has_key("author") and query.has_key("commit_id") and query.has_key("token")):
                raise InvalidQueryStringError
            author = query.get("author")
            commit_id = query.get("commit_id")
            token = query.get("token")
#            if not utils.validate_token( author = author, commit_id = commit_id, url = config.server["cvproxy"],token = token):
#                raise AuthenticationError
            
            sopt = SQLAdaptor()
            request_num = sopt.GetUnprocessedRequest(author)
            request_url = "/".join([config.server["cvproxy"],"myunprocessedrequests"])
                        
            author_info = {"name":author,
                           "request_url":request_url,
                           "request_num":request_num}
            
            dashboard_url = "/".join([config.server["cvproxy"], "dashboard"])
            navi = [
#                    {"name":"Dashboard",
#                     "url":dashboard_url,
#                     "theme":"unselected"
#                    },
                    {"name":"Current review request",
                     "url":"#",
                     "theme":"selected"
                    }
                    ]
            

            
            url = {"ignore":
                    {"absolute": "/".join([config.server["cvproxy"],"submitaction?action=ignore&commit_id=%s" % commit_id]),
                     "relative": "submitaction?action=Ignore&commit_id=%s" % commit_id},
                   "revoke":
                    {"absolute": "/".join([config.server["cvproxy"],"submitaction?action=revoke&commit_id=%s" % commit_id]),
                     "relative": "submitaction?action=Revoke&commit_id=%s" % commit_id}
                   }
            
            cijob = sopt.GetJobNameByCommit(commit_id)
            files_committed = sopt.GetCommitedFilesNum(commit_id)
            
            
            downstreamjobs = sopt.GetDownstreamJobs(cijob)
            if downstreamjobs:                
                project_info = sopt.GetProjectInfo(downstreamjobs[0])
                test_info = sopt.GetTestSummary(downstreamjobs)
                results, failed_jobs = sopt.GetTestResult(downstreamjobs)
                            
            else:
                project_info = sopt.GetProjectInfo(cijob) 
                test_info = sopt.GetTestSummary([cijob])
                results, failed_jobs = sopt.GetTestResult([cijob])
                    
            log.debug("downstream jobs: %s" % downstreamjobs)
            log.debug("project_info: %s" % project_info) 
            log.debug("test_info: %s" % test_info)
            
            
            info = {"product": project_info["product"],
                    "platform":project_info["platform"],
                    "version":project_info["version"],
                    "files_committed": files_committed,
                    "tests_executed": test_info["tests"],
                    "failures":test_info["failures"]}             

            ci_url = config.ciserver["urlprefix"]
            jobs = []

            jobs.append(
                       {"jobpage":"/".join([ci_url,cijob[0]]),
                        "name":cijob[0],
                        "overview": "/".join([ci_url,cijob[0],cijob[1]]),
                        "console": "/".join([ci_url,cijob[0],cijob[1],"console"]),
                        "workspace": "/".join([ci_url,cijob[0],"ws"]),
                        "testresult": "/".join([ci_url,cijob[0],cijob[1],"TestReport/?"]),
                        "logs": "/".join([ci_url,cijob[0],cijob[1],"artifact/logs"]),
                        "results": results,
                        "failed_jobs": opts.FormatFailedJobs(failed_jobs)
                        }                               
                        )    
                           
                  
                               
            categories = sopt.GetCategory()
            
            diff_list = sopt.GetDiffSetByCommit(commit_id)
            codes = opts.FormatDiffs(diff_list)
        
            return render.render_template('current_review_request.tmpl',
                           author = author_info,
                           navi = navi, 
                           url = url, 
                           commit_id = commit_id,
                           info = info,
                           categories = categories,
                           jobs = jobs,
                           codes = codes)
        except Exception, e:
            log.error(e)
            return HTTPAdaptor.format_response("error", "Request processing failed.")
             
class SubmitAction:
    '''
    Proecessing request for submitting actions 
    '''
    
    def GET(self):
        '''
        Method:get
        '''
        try:
            log.info("CI:Get")
            query = HTTPAdaptor.format_query(web.ctx.env["QUERY_STRING"])
            if not (query.has_key("action") and query.has_key("commit_id")):
                raise "Invalid query string"
            
            sopt = SQLAdaptor()
            
            author = "mxu"
            commit_id = query["commit_id"]
            sopt.SetCommitStatus(commit_id, 6)
            request_num = sopt.GetUnprocessedRequest(author)
            
            request_url = "/".join([config.server["cvproxy"],"myunprocessedrequests"])
                        
            author_info = {"name":author,
                           "request_url":request_url,
                           "request_num":request_num}
            
            dashboard_url = "/".join([config.server["cvproxy"], "dashboard"])
            navi = [
                    {"name":"Dashboard",
                     "url":dashboard_url,
                     "theme":"unselected"
                    },
                    {"name":"Current review request",
                     "url":"#",
                     "theme":"selected"
                    }
                    ]

            sopt.InsertActionInfo(commit_id, query["action"], author, comment)
            
            result = {
                      "category": "An issue",
                      "comment": "Haha!",
                      "choice": query["action"]
                      }
            
            return render.render_template('current_review_result.tmpl',
                                            author = author_info,
                                            navi = navi, 
                                            commit_id = commit_id,
                                            result = result
               )
            
        except Exception, e:
            log.error(e)
            return HTTPAdaptor.format_response("error", "Request processing failed.")

    def POST(self):
        '''
        Method:post
        '''
        try:
            log.info("CI:Post")
            query = HTTPAdaptor.format_query(web.ctx.env["QUERY_STRING"])
            body = HTTPAdaptor.format_form_data(web.data())
            if not (query.has_key("action") and query.has_key("commit_id")):
                raise "Invalid query string"

            commit_id = query["commit_id"]

            sopt = SQLAdaptor()
            if query["action"] == "Revoke":
                sopt.SetCommitStatus(commit_id, 6)
            elif query["action"] == "Ignore":
                sopt.SetCommitStatus(commit_id, 5)
                
            author = "mxu"
            
            request_num = sopt.GetUnprocessedRequest(author)
            
            request_url = "/".join([config.server["cvproxy"],"myunprocessedrequests"])
                        
            author_info = {"name":author,
                           "request_url":request_url,
                           "request_num":request_num}
            
            dashboard_url = "/".join([config.server["cvproxy"], "dashboard"])
            navi = [
                    {"name":"Dashboard",
                     "url":dashboard_url,
                     "theme":"unselected"
                    },
                    {"name":"Current review request",
                     "url":"#",
                     "theme":"selected"
                    }
                    ]

            
            result = {
                      "category": body["category"],
                      "comment": body["comment"],
                      "choice": query["action"]
                      }
            
            sopt.InsertActionInfo(commit_id, author, query["action"], body["category"], body["comment"])
            
            return render.render_template('current_review_result.tmpl',
                                            author = author_info,
                                            navi = navi, 
                                            commit_id = commit_id,
                                            result = result
               )
            
        except Exception, e:
            log.error(e)
            return HTTPAdaptor.format_response("error", "Request processing failed.")
        
   
class Dashboard:
    '''
    Proecessing request for view dashboard
    '''
    
    def GET(self):
        '''
        Method:post
        '''
        try:
            log.info("Dashboard:Get")
            render.render_template("layout.tmpl")
        except Exception, e:
            log.error(e)
            return HTTPAdaptor.format_response("error", "Request processing failed.")
        