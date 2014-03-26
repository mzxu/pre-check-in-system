'''
Created on Aug 13, 2012

@author: Mingze
'''
from jinja2 import Environment,FileSystemLoader

jinja_env = Environment(
        loader=FileSystemLoader("../templates/"),
        )

def render_template(template_name, **context):
        #jinja_env.update_template_context(context)
    return jinja_env.get_template(template_name).render(context)

if __name__ == "__main__":
    author = {"name":"mxu","request_url":"http://10.197.84.110:8081","request_num":3}
    navi = {"dashboard":"http://10.197.84.110:8081"}
    url = {"ignore":
                    {"absolute": "http://10.197.84.110:8081/ignore/absolute",
                     "relative": "http://10.197.84.110:8081/ignore/relative"},
           "revoke":{"absolute": "http://10.197.84.110:8081/revoke/absolute",
                     "relative": "http://10.197.84.110:8081/revoke/relative"}
           }
    commit_id = 1
    info = {"project":"emma",
            "release":"3.0.0",
            "platform":"IOS",
            "files_committed": 4,
            "tests_executed": 30,
            "failures":10}
    categories = ["Expected failures", "Dependent commit", "An iusse"]
    ci = {"jobpage":"http://10.197.84.110:8081/svn_hook_trail",
          "overview": "http://10.197.84.110:8081/svn_hook_trail/12",
          "console": "http://10.197.84.110:8081/svn_hook_trail/12/console",
          "workspace": "http://10.197.84.110:8081/svn_hook_trail/workspace",
          "result":"http://10.197.84.110:8081/svn_hook_trail/TestReport/?"}
    results = [["T01_Page_Syntax_Check", "s01_commonProfile_multiple_wisdon", "InitConfig", "Pass", 0.012],
               ["T01_Page_Syntax_Check", "s01_commonProfile_multiple_wisdon", "InitConfig", "Pass", 0.012],
               ["T01_Page_Syntax_Check", "s01_commonProfile_multiple_wisdon", "InitConfig", "Pass", 0.012]
               ]
    codes = [{"filename":"ci",
              "filefullname":"ci.py",
              "filecontent":"import ci<br>"},
             {"filename":"svn",
              "filefullname":"svn.py",
              "filecontent":"import svn<br>"},
             {"filename":"server",
              "filefullname":"server.py",
              "filecontent":"import server<br>"},]
    print render_template('current_review_request.tmpl',
                           author = author,
                           navi = navi, 
                           url = url, 
                           commit_id = commit_id,
                           info = info,
                           categories = categories,
                           ci = ci,
                           results = results,
                           codes = codes)