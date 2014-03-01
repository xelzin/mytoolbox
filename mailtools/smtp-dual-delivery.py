#!/usr/bin/env python
# SMTP dual delivery relay (proxy) 
# Warning no queueing implemented mail might get lost if one of the proxyto servers is not handling the mail correctly.
# 2014 bkram

# Set variables below

# Listen on this ip and port
bindip = '127.0.0.1'
bindport = 25

# Proxy to these SMTP servers
proxytoip_a ='smtp.mydomain.tld'
proxytoport_a='25'

proxytoip_b ='smtp.otherdomain.tld'
proxytoport_b='25'

import asyncore
import smtpd
import smtplib
import time
	
def logtime():
	return time.strftime('%D %H:%M:%S')

def proxymailto(ip,port,mailfrom,rcpttos,data):

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

	state_a = proxymailto(proxytoip_a,proxytoport_a,mailfrom,rcpttos,data,peer)
	print '%s %s' % (logtime(),state_a)

	state_b = proxymailto(proxytoip_b,proxytoport_b,mailfrom,rcpttos,data,peer)
	print '%s %s' % (logtime(),state_b)

	print '%s End Proxy action' %logtime()

	return

server = CustomSMTPServer((bindip, bindport), None)

asyncore.loop()