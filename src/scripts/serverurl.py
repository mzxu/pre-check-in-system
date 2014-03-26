'''
Created on Nov 8, 2012

@author: mxu
'''
import sys,json
from optparse import OptionParser

def ModifyServerInfo(url, ip, port, filename):
    #url = "http://%s:8088/gwapiserver_pcv/client_servive/" % ip
    value = "http://%s:%s/%s" % (ip, port, url)
    print "url: %s" % value
    f = open(filename)
    dict = json.loads(f.read())
    dict["gwAPIserver"]["url"] = value
    f = open(filename,'wb')
    json.dump(dict, f)
    
if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-u", "--url", dest="url", 
                      help="The url of gateway api server")
    parser.add_option("-i", "--ip", dest="ip", 
                      help="The ip address of gateway api server")
    parser.add_option("-p", "--port", dest="port",
                      help="The port of gateway api server")
    parser.add_option("-f", "--filename", dest="filename",
                      help="The file to modify")
    (options, args) = parser.parse_args()
    ModifyServerInfo(options.url, options.ip, options.port, options.filename)
