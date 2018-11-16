#!/usr/bin/python
# -> forward POST/GET to next ip/port
#
#

import sys
import cgi
import json
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import time
import os
import ConfigParser
import re

#
CMD_DESCRIPTIONS = '\n\
   %s :\n\
	- forward POST/GET to next ip\n\
	- Usage: \n\
		%s <from-ip(local-ip)> <from-port(local-port)> <to-ip> <to-port>\n\
\n'
DEF_FROM_IP = '127.0.0.1'
DEF_FROM_PORT = 8011
DEF_TO_IP = ''
DEF_TO_PORT = 8011

class LocalData(object):
	records = {}

#This class will handles any incoming request from
#the browser 
class myHandler(BaseHTTPRequestHandler):
	
	#Handler for the POST requests
	def do_POST(self):
		global delay_post_f, delay_post_b, delay_get_f, delay_get_b, time
		if None != re.search('/api/v1/addrecord/*', self.path):
			ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
			if ctype == 'application/json':
				length = int(self.headers.getheader('content-length'))
				data = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)

				attrs = vars(self.headers)
				print ', '.join("%s: %s" % item for item in attrs.items())
				print "pdict: %s" % (pdict)
				print "ctype : %s, length: %d, data: %s" % (ctype, length, data)


		        	import httplib2

				url = 'http://'+_to_ip + ':' + str(_to_port) + self.path
				print '   >>> forwarding POST to %s' % (url)
				h1 = {'Content-type': 'application/json', 'Accept': 'text/plain'}
				d1 = data.keys()[0]

				print "url: %s, h1: %s, d1: %s" % (url, h1, d1)
				h = httplib2.Http()

				# delay
				time.sleep(float(delay_post_f))

	        	        (r, content) = h.request(url, "POST", headers=h1, body=d1)
        	        	print "%s" % (r)

				# delay
				time.sleep(float(delay_post_b))

			self.send_response(200)
			self.send_header('Content-Type', ctype)
			self.end_headers()
		
		elif None != re.search('/api/v1/setdelay/*', self.path):
			ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                        if ctype == 'application/json':
                                length = int(self.headers.getheader('content-length'))
                                data = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
                                dtype = self.path.split('/')[-1]
                                LocalData.records[dtype] = data
                                for kkey in data:
                                        print kkey
                                print "new delay inputted - type: %s, value: %s" % (dtype, kkey)
                                if dtype == 'delay_post_f':
                                        delay_post_f = kkey
                                elif dtype == 'delay_post_b':
                                        delay_post_b = kkey
                                elif dtype == 'delay_get_f':
                                        delay_get_f = kkey
                                elif dtype == 'delay_get_b':
                                        delay_get_b = kkey
                                print "current delay values are:%s, %s, %s, %s" % (delay_post_f, delay_post_b, delay_get_f, delay_get_b)
			else:
                                data = {}
                        self.send_response(200)
                        self.end_headers()

                elif None != re.search('/api/v1/setstress/*', self.path):
			ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
			if ctype == 'application/json':
				length = int(self.headers.getheader('content-length'))
				data = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
				stype = self.path.split('/')[-1]
				LocalData.records[stype] = data
				for num in data:
					value,time = num.split(",")
				
				if stype == 'cpu':
					print "start stressing CPU with load %s%% within %ss" % (value,time)
					subprocess.call("stress-ng --cpu '%s' --timeout '%s'" % (value,time), shell=True)

				if stype == 'mem':
					print "start stressing memory with value %s bytes within %ss" % (value,time)
					subprocess.call("stress-ng --vm 2 --vm-bytes '%s' --timeout '%s'" % (value,time), shell=True)

				if stype == 'io':
					print "start stressing disk with value %s within %ss" % (value,time)
					subprocess.call("stress-ng --io %s --timeout '%s'" % (value,time), shell=True)
			else:
				data = {}
	
			self.send_response(200)
			self.end_headers()
		else:
			self.send_response(403)
			self.send_header('Content-Type', 'application/json')
			self.end_headers()
		return



	#Handler for the GET requests
	def do_GET(self):
                #
#                import requests
##               url = self.headers.getheader('host')+self.path
#                url = "http://127.0.0.1:8001"+self.path
#                print "url: %s" % (url)
#                r = requests.get(url)
#                print(r.status_code, r.reason)

		import httplib2
		url = 'http://'+_to_ip + ':' + str(_to_port) + self.path
		print '   >>> forwarding GET to %s' % (url)
		h = httplib2.Http()

		# delay
		time.sleep(float(delay_get_f))

		(r, content) = h.request(url, 'GET')
		print "%s" % (r)

		# delay
		time.sleep(float(delay_get_b))

		self.send_response(200)
		self.send_header('Content-type','text/html')
		self.end_headers()
		# Send the html message
		self.wfile.write(content)
		return


#
#
# attribute
#   delay=a,b,c,d
#     a : POST forward-path delay
#     b : POST backward-path delay
#     c : GET forward-path delay
#     d : GET backward-path delay
#
attr = '0,0,0,0'
delay_post_f = 0
delay_post_b = 0
delay_get_f = 0
delay_get_b = 0

def extract_delay_attributes(argv):
  global attr, delay_post_f, delay_post_b, delay_get_f, delay_get_b
  try:
        attr = argv.split('=')[1]
        delays = attr.split(',')
        try:
                delay_post_f = float(delays[0])
        except:
                delay_post_f = 0
        try:
                delay_post_b = float(delays[1])
        except:
                delay_post_b = 0
        try:
                delay_get_f = float(delays[2])
        except:
                delay_get_f = 0
        try:
                delay_get_b = float(delays[3])
        except:
                delay_get_b = 0
  except:
        pass

def helper(cmd):
        print CMD_DESCRIPTIONS % (cmd, cmd)


#
# -- main --
#
if __name__=='__main__':
#  parser = argparse.ArgumentParser(description='HTTP Server')
#  parser.add_argument('ip', help='HTTP Server IP')
#  parser.add_argument('port', type=int, help='Listening port for HTTP Server')
#  args = parser.parse_args()


	#
	_from_ip = DEF_FROM_IP
	_from_port = DEF_FROM_PORT
	_to_ip = DEF_TO_IP
	_to_port = DEF_TO_PORT

	# check arguments
	for arg in sys.argv:
        	print (arg)
#		if arg == '-?' or arg == '-h' or arg == '--help':
#                	helper(sys.argv[0])
#	                sys.exit()

	# 
#	if len(sys.argv) < 5:
#		helper(sys.argv[0])
#		sys.exit()

        #configFile = "./fw.conf"
        configFile = "/home/synthesizer/components/web_forward/fw.conf"
        if not os.path.isfile(configFile):
                print '\nERR: config-file %s does not exist!\n' % (configFile)
                sys.exit()
        config = ConfigParser.ConfigParser()
        config.read(configFile)
        section = 'Forwarder'

        _to_ip = config.get(section, 'target_ip_1')
#        _to_port = config.get(section, 'target_port')
        
# 
        
#        _from_ip = sys.argv[1]
#        _from_port = int(sys.argv[2])
#        _to_ip = sys.argv[3]
#        _to_ip = '127.0.0.1'
#        _to_port = int(sys.argv[4])
#        _to_port = 8012

	print '=> forward from %s:%d to %s:%s' % (_from_ip, _from_port, _to_ip, _to_port)

	#
	# attributes
	#
	# delay
	try:
        	extract_delay_attributes(sys.argv[5])
	except:
        	pass
	print '=> delay: %s,%s,%s,%s' % (delay_post_f, delay_post_b, delay_get_f, delay_get_b)

#	sys.exit()


try:
	#Create a web server and define the handler to manage the
	#incoming request
	server = HTTPServer(('', _from_port), myHandler)
	print 'Started httpserver on %s:%s' % (_from_ip, _from_port)
	
	#Wait forever for incoming htto requests
	server.serve_forever()

except KeyboardInterrupt:
	print '^C received, shutting down the web server'
	server.socket.close()
	
