'''
Created on Jul 31, 2012

@author: Mingze
'''
import json, os, hashlib, urllib
from email.MIMEText import MIMEText
import smtplib
import config
from log import log

def send_email(content, title, mail_to, mail_from = "cibuilder@microstrategy.com"):
    try:
        msg = MIMEText(content, 'html')
        msg['Subject'] = title
        msg['From'] = mail_from
        
        address_str = ';'.join(mail_to)
        msg['To'] = address_str        
        
        s = smtplib.SMTP(config.email["smtp_server"])
#        s.login('corp\is_portal','broadcaster')
        s.sendmail(mail_from, mail_to, msg.as_string())
        
        s.quit()
        log.info("email is sent")
    except Exception,e:
        print e
        pass
    


def md5_encryption(*args):
    try:
        input = ''.join([str(i) if i is not None else '' for i in args])
        input += config.server["cvkey"]
        md5 = hashlib.md5()
        md5.update(input) 
        return md5.hexdigest()
    except Exception, e:
        log.warning(e)
        return None
    
def validate_token(**kwargs):
    try:
        tokenA = kwargs["token"]
        tokenB = md5_encryption(kwargs["author"], kwargs["commit_id"], kwargs["url"])
        if tokenA == tokenB:
            return True
        else:
            return False
    except:
        return False

def write_to_file(filename, content):
    try:
        file_handler = open(filename, 'wb')
        file_handler.write(content)
        file_handler.close()
    except Exception, e:
        log.error(e) 
        
def format_body_for_ci(body):
    try:
        body_list = []
        for k,v in body.iteritems():
            body_list.append({
                              "name":k,
                              "value":v
                              })
            
        param_dict = {
                      "parameter":body_list
                      }
        
        param_str = json.dumps(param_dict)
        
        body = "json=%s&Submit=Build" % param_str
        body = {"json":param_str,
                "Submit":"Build"}
        body_urlencoded = urllib.urlencode(body)
        
        return body_urlencoded
        
    except Exception,e:
        log.error(e)
        return ""
    
def _decode_list(lst):
    newlist = []
    for i in lst:
        if isinstance(i, unicode):
            i = i.encode('utf-8')
        elif isinstance(i, list):
            i = _decode_list(i)
        newlist.append(i)
    return newlist

def _decode_dict(dct):
    newdict = {}
    for k, v in dct.iteritems():
        if isinstance(k, unicode):
            k = k.encode('utf-8')
        if isinstance(v, unicode):
            v = v.encode('utf-8')
        elif isinstance(v, list):
            v = _decode_list(v)
        newdict[k] = v
    return newdict
    
def json_load_to_str(s):
    return json.loads(s, object_hook=_decode_dict)