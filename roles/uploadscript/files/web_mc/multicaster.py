#!/usr/bin/python
# -> multicast POST/GET 
#
#

import sys
import cgi
import json
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import httplib2
import time


#
CMD_DESCRIPTIONS = '\n\
   %s :\n\
	- multicast POST/GET requests\n\
	- Usage: \n\
		%s <from-ip(local-ip)> <from-port(local-port)>\n\
		note: config-file(mc.conf) needs to contain valid data\n\
\n'

# globals
fanout_ip = []
fanout_port = []
fomodulo = 0


#This class will handles any incoming request from
#the browser 
class myHandler(BaseHTTPRequestHandler):
	
	#Handler for the POST requests
	def do_POST(self):
		global fanout_ip, fanout_port, fomodulo, delay_post_f, delay_post_b, delay_get_f, delay_get_b


		if None != re.search('/api/v1/addrecord/*', self.path):
			ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
			if ctype == 'application/json':
				length = int(self.headers.getheader('content-length'))
				data = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)

				for i in range(0, fomodulo):
					_to_ip = fanout_ip[i]
					_to_port = fanout_port[i]
					url = 'http://'+_to_ip + ':' + str(_to_port) + self.path
					h1 = {'Content-type': ctype}
					d1 = data.keys()[0]

					# delay
					time.sleep(delay_post_f)

					print '   >>> multicasting POST to %s (header: %s, data: %s)\n-------------' % (url, h1, d1)
					h = httplib2.Http()
        	        		(r, content) = h.request(url, "POST", headers=h1, body=d1)

					# delay
					time.sleep(delay_post_b)

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

		else:
			self.send_response(403)
			self.send_header('Content-Type', ctype)
			self.end_headers()

		print '-------------\n'
		return



	#Handler for the GET requests
	def do_GET(self):
		global fanout_ip, fanout_port, fomodulo, focon

		for i in range(0, fomodulo):
			_to_ip = fanout_ip[i]
			_to_port = fanout_port[i]
			url = 'http://'+_to_ip + ':' + str(_to_port) + self.path

			# delay
			time.sleep(delay_get_f)

			print '   >>> multicasting GET to %s\n-------------' % (url)
			h = httplib2.Http()
			(r, content) = h.request(url, 'GET')
#	              	print(r.status_code, r.reason)
#			print "%s" % (r)

			# delay
			time.sleep(delay_get_b)

			self.send_response(200)
			self.send_header('Content-type','text/html')
			self.end_headers()
			# Send the html message
			self.wfile.write(content)

		print '-------------\n'
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

	# check arguments
	for arg in sys.argv:
#       	print (arg)
		if arg == '-?' or arg == '-h' or arg == '--help':
                	helper(sys.argv[0])
	                sys.exit()
        # 
        if len(sys.argv) < 3:
                helper(sys.argv[0])
                sys.exit()
        # 
        _from_ip = sys.argv[1]
        _from_port = int(sys.argv[2])

	# fanout
	fanout_ip = []
	fanout_port = []
	fomodulo = 0
	focon = 0


	# config file
	import os
	import ConfigParser
	#configFile = "./mc.conf"
	configFile = "/home/synthesizer/components/web_mc/mc.conf"
	if not os.path.isfile(configFile):
		print '\nERR: config-file %s does not exist!\n' % (configFile)
		sys.exit()
	config = ConfigParser.ConfigParser()
	config.read(configFile)
	section = 'Multicaster'
	try:
		fomodulo = int(config.get(section, 'fanout'))
	except ConfigParser.NoSectionError:
		print '\nERR: mismatch section: %s in config-file!\n' % (section)
		sys.exit()
	for i in range(0, fomodulo):
		option_ip = 'fanout_ip_'+str(i+1)
		try:
			fanout_ip.append(config.get(section, option_ip))
			print '---> fanout_ip_%d : %s' % (i+1, fanout_ip[i])
		except ConfigParser.NoOptionError:
			print '\nERR: mismatch option: %s in config-file!\n' % (option_ip)
			sys.exit()

		option_port = 'fanout_port_'+str(i+1)
		try:
			fanout_port.append(config.get(section, option_port))
			print '---> fanout_port_%d : %s' % (i+1, fanout_port[i])
		except ConfigParser.NoOptionError:
			print '\nERR: mismatch option: %s in config-file!\n' % (option_port)
			sys.exit()

	#
	# attributes
	#
	# delay
	try:
        	extract_delay_attributes(sys.argv[3])
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
	
