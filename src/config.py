'''
Created on Jul 27, 2012

@author: Mingze
'''
import logging,os,sys

ciserver = {
            "urlprefix": "http://127.0.0.1:8080/job/",
            "urlsuffix": "/build?delay=1sec",
            "api_json_depth2":"api/json?depth=2"}

mapping = {
           "^Emma-CI/.*": "svn_hook_trail",
           "^branches/(.+?)/.*": "main~branches~\1",
           "^releases/(.+?)/(.+?)/.*": "main~releases~\1~\2",
           "^cCI.*": "svn_hook_trail",
           "^emma.*": "svn_hook_trail_mapping_improved"
           }        
        
authors = {
           "mmm":
                {
                 "token": "0b432978282f5bc6e318d5e58a863495",
                 "qe": "yyy"
                 }                       
            }

database = {
            "host": "127.0.0.1",
            "port": "3306",
            "username": "ci_dev",
            "password": "***",
            "database": "cvproxy"
            }

database_test_result = {
                  "host": "127.0.0.1",
                  "port": "3306",
                  "username": "ci_dev",
                  "password": "***",
                  "database": "test_result"
                  }

server = {
          "templates": "/usr/local/pcv/src/templates",
          "static": "/usr/local/pcv/src/static",
          "cvproxy": "http://127.0.0.1/pcv",
          "cvkey": "a1b2c3d4"
         }

log = {
       "location": "/usr/local/pcv/logs",
       "level": logging.DEBUG
       }

email = {   
             "mail_from": "cibuilder@xxx.com",
             "smtp_server": "127.0.0.1",
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
