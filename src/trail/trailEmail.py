'''
Created on Aug 7, 2012

@author: Mingze
'''
from email.MIMEText import MIMEText
import smtplib
from Cheetah.Template import Template

def send_mail(content, title, mail_to, mail_from):
    try:
        msg = MIMEText(content, 'html')
        msg['Subject'] = title
        msg['From'] = mail_from
        
        address_str = ';'.join(mail_to)
        msg['To'] = address_str        
        
        s = smtplib.SMTP("10.15.70.24")
#        s.login('corp\is_portal','broadcaster')
        s.sendmail(mail_from, mail_to, msg.as_string())
        
        s.quit()
        print "email is sent"
    except Exception,e:
        print e
        pass
 
t2 = Template(file = "../templates/review_request.tmpl")
t2.url = "http://10.197.84.110:8011"
t2.commit_id = "10086" 
 
   
if __name__ == "__main__" :
    send_mail(content = str(t2), title = "Test mail", mail_to = ["mxu@microstrategy.com"], mail_from = "cibuilder@microstrategy.com")
