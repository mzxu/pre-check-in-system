'''
Created on Jul 27, 2012

@author: Mingze
'''
import logging,os,sys

ciserver = {
            "urlprefix": "http://10.197.84.226:8080/job/",
            "urlsuffix": "/build?delay=1sec",
            "api_json_depth2":"api/json?depth=2"}

mapping = {
           "^Emma-CI/.*": "svn_hook_trail",
           "^branches/(.+?)/.*": "main~branches~\1",
           "^releases/(.+?)/(.+?)/.*": "main~releases~\1~\2",
           "^cCI.*": "svn_hook_trail",
           "^emma.*": "svn_hook_trail_mapping_improved",
#           "^trunk.*src.*": "SP_PCV1_GW_Deploy_API_Server_New",
           "^trunk.*": "Usher_Connector_PCV",
           "^PhysicalAccessProduction/Connectors/GenericConnector/.*": "Usher_Adapter_PCV_Unit_Test"
           }        
        
authors = {
           "mxu":
                {
                 "token": "0b432978282f5bc6e318d5e58a863495",
                 "qe": "ycao"
                 },
            "ycao":
                {
                 "token": "2089419048762efd831d2a2050349eb3",
                 "qe": "ycao"
                 },
            "xlai":
                {
                 "token": "fe202de2d15cb7c3d42484a8c68c60c6",
                 "qe": "ycao"
                 },
            "jgao":
                {
                 "token": "8eeaecf0e4e4e1cbcbc12990edfa9148",
                 "qe": "ycao"
                 },
            "dfeng":
                {
                 "token": "f234626ca0ad73c9874424c66f51b828",
                 "qe": "ycao"
                 },
            "cuwang":
                {
                 "token": "7697f227f02e1fc88b0131284c4f882e",
                 "qe": "ycao"
                 },
            "kewang":
                {
                 "token": "b40f6bf24f0ce078d426d5a98e3f9a56",
                 "qe": "mxu"
                 },
            "shzhang":
                {
                 "token": "dd412702d4d553cf1262a107ad598bc6",
                 "qe": "mxu"
                 },               
            "qzhao":
                {
                 "token": "ab0defa9bda6ef416b61d7dfd7782df4",
                 "qe": "mxu"
                 },               
            "relin":
                {
                 "token": "b46d71139c2b79ba8d50efe5fd350a26",
                 "qe": "mxu"
                 },               
            "jhuangfu":
                {
                 "token": "3c5cf3a9892db70007026174e5d01ab1",
                 "qe": "mxu"
                 }                                   
            }

database = {
            "host": "10.197.84.226",
            "port": "3306",
            "username": "ci_dev",
            "password": "mstr123",
            "database": "cvproxy"
            }

database_test_result = {
                  "host": "10.197.84.226",
                  "port": "3306",
                  "username": "ci_dev",
                  "password": "mstr123",
                  "database": "test_result"
                  }

server = {
          "templates": "/usr/local/pcv/src/templates",
          "static": "/usr/local/pcv/src/static",
          "cvproxy": "http://10.197.84.230/pcv",
          "cvkey": "a1b2c3d4"
         }

log = {
       "location": "/usr/local/pcv/logs",
       "level": logging.DEBUG
       }

email = {   
             "mail_from": "cibuilder@microstrategy.com",
             "smtp_server": "10.15.70.24",
             "templates" : {
                            "to_commitor": "templates/review_request.tmpl",
                            "to_qe": "templates/review_request_qe.tmpl"
                            }
        }                

#Run "python config.py" to validate the the configuration
if __name__ == "__main__":    
    paths = os.environ['PATH'].split(os.pathsep)
    lol = {}
    for path in paths:
            for arg in sys.argv[1:]:
                    if os.path.exists(path + os.sep + arg):
                            if lol.has_key(arg):
                                    lol[arg].append(path)
                            else:
                                    lol[arg] = [path]
    
    for k in lol.keys():
            print k, 'is in:',
            for p in lol[k]:
                    print p,
            print
