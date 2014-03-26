'''
Created on Jul 27, 2012

@author: Mingze
'''

import urllib2, urllib, base64, json, oursql
from datetime import datetime
from log import log
import config
from sqls import *


class SQLAdaptor:
    '''    
    Manipulate MySQL Database
    Default connection is pcv database. However you can specify another connection.    
    '''
    
    def _init_connection(self, connection = config.database):
        host = connection["host"]
        port = connection["port"]
        user = connection["username"]
        passwd = connection["password"]
        database = connection["database"]
        conn = oursql.connect(host = host,
                              port = int(port),
                              user = user,
                              passwd = passwd,
                              db = database)
        
        return conn
    
    
    def InsertCommitInfo(self, commit_info):
        log.debug("Insert commit info into database")        
        try:
            curtime = datetime.utcnow()
            conn = self._init_connection()
            cursor = conn.cursor()            
            cursor.execute("SET AUTOCOMMIT = 0")
            cursor.execute(SQL_INSERT_COMMIT_INFO, (commit_info["author"], 
                                                    commit_info["transaction"],
                                                    commit_info["revision"],
                                                    commit_info["uuid"], 
                                                    commit_info["comments"], 
                                                    7,
                                                    curtime))
            commit_id = cursor.lastrowid
            for change in commit_info["changes"]:
                cursor.execute(SQL_INSERT_CHANGESET_INFO, (
                                                           commit_id,
                                                           change["type"],
                                                           change["filename"] if change.has_key("filename") else "",
                                                           change["fileurl"] if change.has_key("fileurl") else "",
                                                           change["diffname"] if change.has_key("diffname") else "",
                                                           change["diffpath"] if change.has_key("diffpath") else "",
                                                           curtime))
                                                           
                    
            conn.commit()
            
        except Exception, e:
            log.error('commit info into database failed')
            log.error(e)
            conn.rollback()
                        
        finally:
            cursor.execute("SET AUTOCOMMIT = 1")
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()        

    def InsertJobInfo(self, job_info):
        log.debug("Insert job info into database")        
        try:
            curtime = datetime.utcnow()
            conn = self._init_connection()
            cursor = conn.cursor()            
            cursor.execute("SET AUTOCOMMIT = 0")
            for jobname, jobcontent in job_info.iteritems():
                cursor.execute(SQL_SELECT_JOB_ID, (jobname, ))
                for row in cursor:
                    job_id = row[0]
                tnx = jobcontent["transaction"]
                if tnx:
                    cursor.execute(SQL_SELECT_COMMIT_ID_BY_TRANSACTION, (tnx, ))
                else:
                    cursor.execute(SQL_SELECT_COMMIT_ID_BY_REVISION, (jobcontent["revision"], ))
                for row in cursor:
                    commit_id = row[0]
                cursor.execute(SQL_INSERT_BUILD_INFO, (job_id, commit_id, curtime))
                
            conn.commit()
            
        except Exception, e:
            log.error('Insert job info into database failed')
            log.error(e)
            conn.rollback()
                        
        finally:
            cursor.execute("SET AUTOCOMMIT = 1")
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def SetBuildToInvalid(self,job_name, job_content):
        log.debug("Set the build to invalid")        
        try:
            conn = self._init_connection()
            cursor = conn.cursor()            

            cursor.execute(SQL_SELECT_JOB_ID, (job_name, ))
            for row in cursor:
                job_id = row[0]
            tnx = job_content["transaction"]
            if tnx:
                cursor.execute(SQL_SELECT_COMMIT_ID_BY_TRANSACTION, (tnx, ))
            else:
                cursor.execute(SQL_SELECT_COMMIT_ID_BY_REVISION, (job_content["revision"], ))
            for row in cursor:
                commit_id = row[0]
            cursor.execute(SQL_SET_BUILD_INVALID, (job_id, commit_id))                
            
        except Exception, e:
            log.error('Set the build to invalid failed')
            log.error(e)
                        
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.close() 
                
    def UpdateStatusByTxn(self,uuid, txn, status):
        log.debug("Update the status by commit transaction")
        try:
            conn = self._init_connection()
            cursor = conn.cursor()          
            cursor.execute(SQL_SET_COMMIT_STATUS_BY_TXN, (status, txn, uuid ))
        except Exception, e:
            log.error('Update status by commit transaction failed')
            log.error(e)
                        
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.close()         
            
                
    def InsertActionInfo(self, commit_id, author, action_name, category_name, comment):
        log.debug("Insert action for the commit %s" % commit_id)        
        try:
            curtime = datetime.now()
            
            conn = self._init_connection()
            cursor = conn.cursor()          
            cursor.execute(SQL_SELECT_ACTION_ID, (action_name, ))
            for row in cursor:
                action_id = row[0]
                 
            cursor.execute(SQL_SELECT_CATEGORY_ID, (category_name, ))
            for row in cursor:
                category_id = row[0]

            cursor.execute(SQL_SELECT_PERSON_ID, (author, ))
            for row in cursor:
                person_id = row[0]
                               
            cursor.execute(SQL_INSERT_ACTION_INFO, (commit_id, person_id, action_id, category_id, comment, curtime))
            
        except Exception, e:
            log.error('Insert action failed')
            log.error(e)
                        
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.close()         
                
    def SetCommitStatus(self,commit_id, status_id):
        log.debug("Set the status to %s for commit id: %s" % (status_id, commit_id))        
        try:
            conn = self._init_connection()
            cursor = conn.cursor()          
            cursor.execute(SQL_SET_COMMIT_STATUS, (status_id, commit_id ))
            conn.commit()
        except Exception, e:
            log.error('Set the status failed')
            log.error(e)
                        
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.close() 
                
                
    def GetUnprocessedRequest(self, author):
        
        
        log.debug("Get unprocessed requests by author:  %s" % author)        
        try:
            num = 0
            conn = self._init_connection()
            cursor = conn.cursor()          
            cursor.execute(SQL_SELECT_UNPROCESSED_REQUEST_BY_AUTHOR, (author, ))
            for row in cursor:
                num = row[0]
                           
        except Exception, e:
            log.error('Get unprocessed requests failed')
            log.error(e)
                        
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.close()
            return num 

    def GetCategory(self):       
        log.debug("Get category")        
        try:
            category = []
            conn = self._init_connection()
            cursor = conn.cursor()          
            cursor.execute(SQL_SELECT_CATEGORY)
            for row in cursor:
                category.append(row[0])
                           
        except Exception, e:
            log.error('Get category failed')
            log.error(e)
                        
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.close()
            return category         

    def GetDownstreamJobs(self, job):       
        log.debug("Get downstream Jobs")        
        try:
            downstream_jobs = []
            conn = self._init_connection(config.database_test_result)
            cursor = conn.cursor()          
            cursor.execute(SQL_SELECT_DOWNSTREAM_JOBS, (job[0], job[1]))
            for row in cursor:
                downstream_jobs.append([row[0],row[1]])
                           
        except Exception, e:
            log.error('Get downstream Jobs failed')
            log.error(e)
                        
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.close()
            return downstream_jobs  

    def GetJobNameByCommit(self, commit_id):       
        log.debug("Get jobs by commit: %s" % commit_id)        
        try:
            jobname = []
            conn = self._init_connection()
            cursor = conn.cursor()          
            cursor.execute(SQL_SELECT_JOB_BY_COMMIT, (commit_id, ))
            
            for row in cursor:
                jobname=[row[0],str(row[1])]
                           
        except Exception, e:
            log.error('Get category failed')
            log.error(e)
                        
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.close()
            return jobname 
        
    def GetCommitedFilesNum(self, commit_id):
        log.debug("Get number of committed files by commit: %s" % commit_id)
        try:
            num = 0
            conn = self._init_connection()
            cursor = conn.cursor()
            cursor.execute(SQL_COUNT_FILES_BY_COMMIT, (commit_id, ))
            
            for row in cursor:
                num = row[0]
        except Exception, e:
            log.error("Get number of committed files failed")
            log.error(e)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.close()
            return num
        
    def GetProjectInfo(self, job):
        '''Query from test result database'''
        log.debug("Get project info")
        try:
            job_name = job[0]
            job_build_num = job[1]
            info = {"product":"",
                    "version":"",
                    "platform":""
                    }
            conn = self._init_connection(config.database_test_result)
            cursor = conn.cursor()
            cursor.execute(SQL_SELECT_PROJECT_INFO, (job_name, job_build_num))
            
            for row in cursor:
                info["product"] = row[0]
                info["version"] = row[1]
                info["platform"] = row[2]
                break;
        except Exception, e:
            log.error("Get project info failed")
            log.error(e)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.close()
            return info   
            
    def GetTestSummary(self, jobs):
        '''Query from test result database'''
        log.debug("Get test summary")
        try:

            conn = self._init_connection(config.database_test_result)
            cursor = conn.cursor()
            test_num = 0
            failures = 0
            tests = [] 
            for job in jobs:                
                cursor.execute(SQL_SELECT_TEST_NUM, (job[0], job[1]))
                for row in cursor:
                    tests.append(row[0])
                    
#                test_num = tests.__len__() 
                for test in tests:
                    cursor.execute(SQL_SELECT_TEST_RESULT_ID, (job[0], job[1], test))
                    for row in cursor:
                        test_num += 1
                        if row[0] == 2:
                            failures += 1
     
        except Exception, e:
            log.error("Get test summary failed")
            log.error(e)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.close()
            test_info = {"tests": test_num,
                         "failures": failures}
            return test_info


    def GetTestResult(self, jobs):
        '''Query from test result database'''
        log.debug("Get test result")
        try:

            conn = self._init_connection(config.database_test_result)
            cursor = conn.cursor()

            results = []  
            failed_jobs = []
            for job in jobs: 
                is_failure = False               
                cursor.execute(SQL_SELECT_TEST_RESULT, (job[0], job[1]))
                for row in cursor:
                    results.append(row)
                    if row[3] == "Failure":
                        is_failure = True
                if is_failure:
                    failed_jobs.append([job[0],job[1]])
                    
     
        except Exception, e:
            log.error("Get test result failed")
            log.error(e)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.close()
            return results,failed_jobs
                     
    def GetDiffSetByCommit(self, commit_id):
        log.debug("Get diff info by commit: %s" % commit_id)
        try:
            diff_list = []
            conn = self._init_connection()
            cursor = conn.cursor()
            cursor.execute(SQL_SELECT_DIFF_BY_COMMIT, (commit_id, ))
            for row in cursor:
                if (not row[0].endswith("/")) and row[1]:
                    diff_list.append(row)
        except Exception, e:
            log.error("Get diff info failed")
            log.error(e)
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.close()
                
            return diff_list
        
    def CheckCommitStatus(self, transaction, revision):       
        log.debug("Check status by transaction: %s and revision: %s" % (transaction, revision))        
        try:
            status = 11
            conn = self._init_connection()
            cursor = conn.cursor()          
            cursor.execute(SQL_SELECT_COMMIT_STATUS, (transaction, revision))
            
            for row in cursor:
                status = row[0]
                           
        except Exception, e:
            log.error('Check status failed')
            log.error(e)
                        
        finally:
            if cursor != None:
                cursor.close()
            if conn != None:
                conn.close()
            return status 
#    def SetBuildStatus(self,build_info):
#        log.debug("Update the build status")        
#        try:
#            commit_id = -1
#            conn = self._init_connection()
#            cursor = conn.cursor()  
#            job_name = build_info["name"]
#            tnx = build_info["build"]["parameters"]["transaction"]
#            revision = build_info["build"]["parameters"]["revision"]
#            url = build_info["build"]["full_url"]
#            build_num = build_info["build"]["number"]
#            phase_name = build_info["phase"] if build_info.has_key("phase") else build_info["build"]["phase"]
#            status_name =  build_info["build"]["status"] if build_info["build"].has_key("status") else "Initializing"
#
#            cursor.execute(SQL_SELECT_PHASE_ID, (phase_name, ))
#            for row in cursor:
#                phase_id = row[0]
#            log.debug("phase: %s" % phase_id)
#                
#            cursor.execute(SQL_SELECT_STATUS_ID, (status_name, ))
#            for row in cursor:
#                status_id = row[0]
#            
#            cursor.execute(SQL_SELECT_JOB_ID, (job_name, ))
#            for row in cursor:
#                job_id = row[0]                
#            
#            if tnx:
#                cursor.execute(SQL_SELECT_COMMIT_ID_BY_TRANSACTION, (tnx, ))
#            else:
#                cursor.execute(SQL_SELECT_COMMIT_ID_BY_REVISION, (revision, ))
#            for row in cursor:
#                commit_id = row[0]
#                
#            cursor.execute(SQL_UPDATE_BUILD_STATUS, (build_num,
#                                                     status_id, 
#                                                     phase_id,                                                    
#                                                     url,
#                                                     job_id,
#                                                     commit_id))
#
#        except Exception, e:
#            log.error('Set the build to invalid failed')
#            log.error(e)
#                        
#        finally:
#            if cursor != None:
#                cursor.close()
#            if conn != None:
#                conn.close()         
#            return commit_id       
                                             
    def CheckBuildFailures(self, build_info):
        log.debug("Check whether all jobs are failed")        
        try:
            result = []
            conn = self._init_connection()
            cursor = conn.cursor()  

            commit_id = -1
            job_name = build_info["name"]
            tnx = build_info["build"]["parameters"]["transaction"]
            revision = build_info["build"]["parameters"]["revision"]
            url = build_info["build"]["full_url"]
            build_num = build_info["build"]["number"]
            phase_name = build_info["phase"] if build_info.has_key("phase") else build_info["build"]["phase"]
            status_name =  build_info["build"]["status"] if build_info["build"].has_key("status") else "Initializing"

            cursor.execute(SQL_SELECT_PHASE_ID, (phase_name, ))
            for row in cursor:
                phase_id = row[0]
            log.debug("phase: %s" % phase_id)
                
            cursor.execute(SQL_SELECT_STATUS_ID, (status_name, ))
            for row in cursor:
                status_id = row[0]
            
            cursor.execute(SQL_SELECT_JOB_ID, (job_name, ))
            for row in cursor:
                job_id = row[0]                
            
            if tnx:
                cursor.execute(SQL_SELECT_COMMIT_ID_BY_TRANSACTION, (tnx, ))
            else:
                cursor.execute(SQL_SELECT_COMMIT_ID_BY_REVISION, (revision, ))
            for row in cursor:
                commit_id = row[0]
            
            cursor.execute("SET AUTOCOMMIT=0")
            cursor.execute(SQL_UPDATE_BUILD_STATUS, (build_num,
                                                     status_id, 
                                                     phase_id,                                                    
                                                     url,
                                                     job_id,
                                                     commit_id))

            cursor.execute(SQL_CHECK_IS_ANY_FAILURES, (commit_id, commit_id, commit_id))
            for row in cursor:
                dict = {"job_id": row[0], 
                        "build_num": row[1], 
                        "commit_id": row[2], 
                        "url": row[3]
                        }
                result.append(row)
            conn.commit()
        except Exception, e:
            log.error('Failed to check failures of jobs')
            log.error(e)
            conn.rollback()
        finally:
            cursor.execute("SET AUTOCOMMIT = 0")
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
            log.debug('failure list: %s' % result)
            return phase_id, result, commit_id
                        
class HTTPAdaptor:
    '''
    Manipulate http request.
    All methods are static methods
    '''
    @staticmethod
    def format_query(query_string):
        try: 
            query_dict = {}
            query_list = query_string.split("&")
            for query in query_list:
                q_list = query.split("=",1)
                query_dict[q_list[0]] = q_list[1]
            return query_dict
        except:
            log.error("Parsing query string (%s) failed" % query_string)
    
    @staticmethod
    def format_form_data(data):
        try:
            body_dict = {}
            body_list = data.split("&")
            for item in body_list:
                item_list = item.split("=")
                body_dict[item_list[0]] = urllib.unquote_plus(item_list[1])
            return body_dict
        except:
            log.error("Parsing form data (%s) failed" % data)
            
    @staticmethod
    def format_response(status, code = None, msg = None, status_id = None):
        response = {"status": status}
        if msg:
            response["info"] = msg
        if code:
            response["code"] = code  
        if status:
            response["status_id"] = status_id
        return json.dumps(response)    
        
            
    @staticmethod
    def get_url(url, query_string = None, auth = None, body = None, url_encoded = False, proxy = None, return_code = True):
        try:
            
            request = urllib2.Request(url, None)

            if auth:
                username = auth[0]
                password = auth[1]
                auth_string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
                request.add_header("Authorization", "Basic %s" % auth_string)
                log.debug("auth: %s" % auth_string)
            
            if body:
                if url_encoded:                    
                    request.add_data(base64.encodestring(body))
                    request.add_header("Content-Type", "application/x-www-form-urlencoded")
                else:
                    request.add_data(body)
                log.debug("body: %s" % body)
                
            if proxy:                
                proxy_handler = urllib2.ProxyHandler({"http" : proxy,"https" : proxy})        
                opener = urllib2.build_opener( proxy_handler)
                urllib2.install_opener(opener)                         

            response = urllib2.urlopen(request)   
#            data = response.read()
            if return_code:
                return 200
            else:
                return response.read()
        
        except urllib2.HTTPError, e:
            if e.code == 404:
                log.debug( "    " + str(e) + ":" + url )
            else:
                log.error( str(e) + ":" + url )
            return e.code
        except urllib2.URLError, e:
            log.error( str(e) + ":" + url )
            return 500  
        except Exception, e:
            log.error(e)   