'''
Created on Apr 26, 2011

@author: root
'''
import web, sys, os


sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import svn

from ci import *
from svn import *

from webpage import *
from ajax import *
from log import log

urls = ('/submitstatus', 'SubmitStatus',   #CI module
        '/submitaction', 'SubmitAction',   #webpage module
        '/checkstatus', 'CheckStatus',     #SVN module
        '/triggerrequest', 'TriggerRequest', #SVN module
        '/reviewrequest', 'ReviewRequest',  #CI module
        '/currentrequest', 'CurrentRequest', #webpage module
        '/mycurrentrequest', 'CurrentRequest',
        '/myunprocessedrequests', 'MyUnprocessedRequests',
        '/dashboard', 'Dashboard',
        #Ajax requests
        "/ajax/testsummarydata", "TestSummaryData" 
        )

""" this is a wsgi function, called by apache + mod_wsgi"""
log.info("python server started")
application = web.application(urls, globals()).wsgifunc()



if __name__ == "__main__" :
    """ Test it with web.py's built-in server"""
    
    web.config.debug = True
    app = web.application(urls, globals())
    app.run()
