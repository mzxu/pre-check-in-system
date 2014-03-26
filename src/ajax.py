'''
Created on Sep 21, 2012

@author: xumingze
'''
import web
from log import log
from adaptor import HTTPAdaptor, SQLAdaptor
from exception import *

class TestSummaryData:
    def GET(self):
        '''
        Method:get
        '''
        try:
            log.info("Ajax:Get")
            query = HTTPAdaptor.format_query(web.ctx.env["QUERY_STRING"])
            if not (query.has_key("commit_id")):
                raise "Invalid query string"
            commit_id = query.get("commit_id")
            return {"s1":[3,4],"s2":[3,10]}
        except Exception, e:
            log.error(e)
            return HTTPAdaptor.format_response("error", "Request processing failed.")
        