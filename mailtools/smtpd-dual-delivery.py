#!/usr/bin/env python
# SMTP dual delivery relay proxy daemon
# Warning no queueing implemented mail might get lost if one of the receiving servers is not handling the mail correctly.
# No Warranty whatsoever
# (c) 2014 bkram

import asyncore
import smtpd
import smtplib
import time
import ConfigParser
	
def getconfig():
	Config=ConfigParser.ConfigParser()
	try:
		Config.read('smtpd-dual-delivery.cfg')

		bindip=Config.get('daemon','bindip')
		bindport=Config.get('daemon','bindport')
		
		destip_a=Config.get('destination_a','ip')
		destport_a=Config.get('destination_a','port')

		destip_b=Config.get('destination_b','ip')
		destport_b=Config.get('destination_b','port')

		return(bindip,bindport,destip_a,destport_a,destip_b,destport_b)
	except:
		exit('Configuration error')

def logtime():
	return time.strftime('%D %H:%M:%S')

def deliverto(ip,port,mailfrom,rcpttos,data):

	print '%s Relay mail to %s:%s' % (logtime(),ip, port)

	try:
		sendserver = smtplib.SMTP(ip, port)
	except:
		return 'Error: could not open connection to %s:%s' % (ip, port)
	try:
		sendserver.sendmail(mailfrom, rcpttos, data)
	except:
		return "Error: could not relay message to server %s:%s" % (ip,port)
	try:
		sendserver.quit()
	except:
		return "Error: could not close connection to server %s:%s" % (ip,port)

	return 'Message relayed to %s:%s' % (ip,port)

class CustomSMTPServer(smtpd.SMTPServer):
    
    def process_message(self, peer, mailfrom, rcpttos, data):
	
	print '%s Start Proxy action' %logtime()
	print '%s Message from %s to %s size %s via %s' % (logtime(),mailfrom,rcpttos,len(data),peer)

	state_a = deliverto(destip_a,destport_a,mailfrom,rcpttos,data)
	print '%s %s' % (logtime(),state_a)

	state_b = deliverto(destip_b,destport_b,mailfrom,rcpttos,data)
	print '%s %s' % (logtime(),state_b)

	print '%s End Proxy action' %logtime()

	return

(bindip,bindport,destip_a,destport_a,destip_b,destport_b)=getconfig()

server = CustomSMTPServer((bindip, int(bindport)), None)

asyncore.loop()
