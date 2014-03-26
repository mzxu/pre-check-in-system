'''
Created on Aug 7, 2012

@author: Mingze
'''

from Cheetah.Template import Template

templateDef = """
    <HTML>
    <HEAD><TITLE>$title</TITLE></HEAD>
    <BODY>
    $contents
    ##This is the single line
    #* This is the multiple lines 
    
    *#
    
    </BODY>
    </HTML>"""

nameSpace = {"title": "Hello World Example", "contents": "Hello World!"}
t = Template(templateDef, searchList=[nameSpace])

t2 = Template(file = "../templates/review_request.tmpl")
t2.url = "http://10.197.84.110:8011"
t2.commit_id = "10086"

if __name__ == "__main__" :
    print t2
