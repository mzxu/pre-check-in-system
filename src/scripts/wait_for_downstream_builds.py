'''
Created on Jul 31, 2012

@author: Mingze
'''
import sys, os, urllib2, base64, urlparse, json, time, logging
from optparse import OptionParser

_ci_base_url = os.environ["JENKINS_URL"] if os.environ.has_key("JENKINS_URL") else ""
_ci_upstream_job_url = os.environ["JOB_URL"] if os.environ.has_key("JOB_URL") else ""
_ci_upstream_build_num = os.environ["BUILD_NUMBER"] if os.environ.has_key("BUILD_NUMBER") else ""
_ci_upstream_job_name = os.environ["JOB_NAME"] if os.environ.has_key("JOB_NAME") else ""
_json_api_url_depth2 = "api/json?depth=2" 

def run(maxwait=1800, interval=20):
    """
    Wait until all of the jobs in the list are complete.
    """
    urls = _get_downstream_builds()
    logging.debug("Urls: %s" % urls)
    if not urls:
        logging.error("No downstream jobs detected")
        sys.exit(1)
    for time_left in xrange(maxwait, 0, -interval):
        still_running = [url for url in urls if not _is_finished(url)]
        if not still_running:
            logging.info("All downstream jobs are finished")
            failure = [url for url in urls if _is_failure(url)]
            logging.info("%s" % failure)
            if failure:
                sys.exit("Failed tests found! Mark the build status to 'Failure'")
            sys.exit(0)            
        str_still_running = ", ".join('"%s"' % str(a) for a in still_running)
        logging.info("Time left: %s" % time_left)
        time.sleep(interval)
    logging.info("Waited too long for these jobs to complete: %s" % str_still_running)
    sys.exit(1)



def _is_failure(url):
    try:
        raw_data = get_url(url)
        data = json.loads(raw_data)
        if data["result"] != "SUCCESS":
            return True
        else:
            return False
    except Exception, e:
        logging.error("Exception: %s" % e)
        logging.error("Fail to get status of build: %s" % url)
        return True

def _is_finished(url):
    try:
        raw_data = get_url(url)
#        logging.debug("Data: %s" % raw_data)
        data = json.loads(raw_data)
        if data["result"] is not None and data["building"] is False:
            return True
        else:
            return False
    except Exception, e:
        logging.error("Exception: %s" % e)
        logging.error("Fail to get status of build: %s" % url)
        sys.exit(1)
        
def _is_in_queue(url):
    try:
        raw_data = get_url(url)
#        logging.debug("Data: %s" % raw_data)
        data = json.loads(raw_data)
        if data["inQueue"]:
            return True
        else:
            return False
    except Exception, e:
        logging.error("Exception: %s" % e)
        logging.error("Fail to get status of queue: %s" % url)
        sys.exit(1)
    
def _get_downstream_builds():
    '''
    Get downstream builds from current builds. 
    Exit code is 1 if:
        1. No downstream builds
        2. Errors thrown
    '''
    
    try:
        url = _ci_upstream_job_url + _json_api_url_depth2 + "&tree=downstreamProjects[name,url]"
                    
        data = get_url(url)
        d_build_urls = []
        build_info = json.loads(data)
        d_builds = build_info["downstreamProjects"]
        for d_build in d_builds:
            d_job_url = d_build["url"]
            d_build_url = _search_build(d_job_url)
            if d_build_url:
                d_build_urls.append(d_build_url) 
        return d_build_urls
    except Exception, e:
        logging.error("Exception: %s" % e)
        logging.error("Fail to get downstream builds")
        sys.exit(1)
        
def _search_build(url):
    '''
    Search downstream build triggerred by the upstream build
    '''
    try:
        d_build_url = ""
        d_job_url = urlparse.urljoin(url, _json_api_url_depth2)  

        data = get_url(d_job_url)
        job_info = json.loads(data)
        builds = job_info["builds"]
        for build in builds:
            for action in build["actions"]:
                if action.has_key("causes"):
                    for cause in action["causes"]:
#           	    	logging.debug("Upstream info: %s" % cause)
                        if cause.has_key("upstreamBuild") and cause.has_key("upstreamProject"):
                            if cause["upstreamBuild"] == int(_ci_upstream_build_num) and cause["upstreamProject"] == _ci_upstream_job_name:
                                d_build_url = urlparse.urljoin(build["url"], _json_api_url_depth2)           	            
            if job_info["inQueue"] and not d_build_url:
                logging.info("The job is in the queue, please wait!")
        for time_left in xrange(18000, 0, -10):
            is_in_queue = _is_in_queue(d_job_url)
            logging.debug("Is in Queue? %s" % is_in_queue)
            if not is_in_queue:		    	
                break
            time.sleep(30)
#                for item in job_info["queue_item"]["queue_item"]:
#                    if item.has_key("causes"):
#                    	for cause in item["causes"]:

        return d_build_url
    except Exception, e:
        logging.error("Exception: %s" % e)
        logging.error("Fail to search downstream builds")
        sys.exit(1)


        
        

def init_logging(level):
    if level == "noset":
        loglevel = logging.NOTSET
    if level == "debug":
        loglevel = logging.DEBUG    
    if level == "info":
        loglevel = logging.INFO    
    if level == "warning":
        loglevel = logging.WARNING    
    if level == "error":
        loglevel = logging.ERROR    
    if level == "critical":
        loglevel = logging.CRITICAL
#    logging.basicConfig( filename=logfile, level=loglevel )
#    logfile = "/usr/local/workspace/svn-hook.log"
    logger = logging.getLogger()
    logger.setLevel( loglevel )
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - {%(pathname)s:%(lineno)d} - %(levelname)s - %(message)s")
    # add formatter to ch
    ch.setFormatter( formatter )
    # add ch to logger
    logger.addHandler( ch )
    logger.setLevel(loglevel)
    #handler = logging.handlers.RotatingFileHandler(
    #          logfile, maxBytes=20, backupCount=5)
    #logger.addHandler( handler )


      

    
def get_url(url, query_string = None, auth = None, body = None, url_encoded = False, proxy = None):
    try:
        
        request = urllib2.Request(url, None)

        if auth:
            username = auth[0]
            password = auth[1]
            auth_string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
            request.add_header("Authorization", "Basic %s" % auth_string)
        
        if body:
            if url_encoded:                    
                request.add_data(base64.encodestring(body))
            else:
                request.add_data(body)
            
        if proxy:                
            proxy_handler = urllib2.ProxyHandler({"http" : proxy,"https" : proxy})        
            opener = urllib2.build_opener( proxy_handler)
            urllib2.install_opener(opener)                         

        response = urllib2.urlopen(request)   
#            data = response.read()
        return response.read()    

    except:
        return None  
    
if __name__ == "__main__":

    parser = OptionParser()
    parser.add_option("-l", "--log-level", dest="level", 
                      default="info", 
                      choices=["notset", "debug", "info", "warning", "error", "critical"],
                      help="Set log level, only can be 'notset', 'debug', 'info', 'warning', 'error', 'critical'. Default is 'info'.")
    parser.add_option("-t", "--timeout", dest = "timeout", 
                      default = 18000, type = int,
                      help="Set checking timeout. If exceeds, mark the build as failure. Default is 30 minutes.")
    parser.add_option("-i", "--interval", dest="interval",
                      default = 20, type = int,
                      help="Set time interval for checking status of downstream jobs. Default is 20s.")
    (options, args) = parser.parse_args()

    init_logging(options.level)

    logging.info("Waiting for downstream jobs finished...")
    time.sleep(10)
    run(options.timeout, options.interval)
