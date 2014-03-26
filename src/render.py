'''
Created on Aug 7, 2012

@author: Mingze
'''
import urllib, os
from Cheetah.Template import Template
from jinja2 import Environment,FileSystemLoader
import config
import utils
from log import log

jinja_env = Environment(
            loader=FileSystemLoader(config.server["templates"])
            )

def render_email_for_commitor(commit_id, commit_info):
    author = commit_info["author"]
    token = utils.md5_encryption(author, commit_id, config.server["cvproxy"])
    para_dict = {
                 "author": author,
                 "commit_id": commit_id,
                 "token": token}
    log.debug("check parameters: %s" % para_dict)
    url_base = config.server["cvproxy"]
    params = urllib.urlencode(para_dict)
    url_suffix = "currentrequest?%s" % params
    url = "/".join([url_base, url_suffix])
    
#    Cheetah template engine:
    templ_path = config.server["templates"]
    
    template = Template(file = os.path.join(templ_path, "review_request.tmpl"))
    template.url = url
    template.commit_id = commit_id 
    return str(template)

def render_template(template_name, **context):
    globals = context.pop('globals', {})
    jinja_env.globals.update(globals)
    #jinja_env.update_template_context(context)
    html = jinja_env.get_template(template_name).render(context)
    #log.error("html: %s" % html)
    return html    