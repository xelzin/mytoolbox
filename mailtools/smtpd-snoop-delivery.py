#!/usr/bin/env python
# SMTP snooping relay proxy daemon
# Warning no queueing implemented mail might get lost if one of the receiving servers is not handling the mail correctly.
# No Warranty whatsoever
# (c) 2014 bkraM

import asyncore
import ConfigParser
import email
import smtpd
import smtplib
import time
import uuid
    
def getconfig():
    Config=ConfigParser.ConfigParser()
    try:
        Config.read('smtpd-snoop-delivery.cfg')
        bindip=Config.get('daemon','bindip')
        bindport=Config.get('daemon','bindport')
        destip=Config.get('destination','ip')
        destport=Config.get('destination','port')
        path=Config.get('file','path')
        return(bindip, bindport, destip, destport, path)
    except:
        exit('Configuration error, please check smtpd-snoop-delivery.cfg')

def logtime():
    return time.strftime('%D %H:%M:%S')

def ftime():
    return time.strftime('%H-%M-%S')

def getmesid(data):
    mailbody = email.message_from_string(data)
    return mailbody['Message-Id']

def deliverto(ip, port, mailfrom, rcpttos, data,messageid):
    print '%s %s Relay mail to %s:%s' % (logtime(), messageid, ip, port)
    try:
        sendserver = smtplib.SMTP(ip, port)
    except:
        return 'Error: could not open connection to %s:%s' % (ip, port)
    try:
        sendserver.sendmail(mailfrom, rcpttos, data)
    except:
        return "Error: could not relay message to server %s:%s" % (ip, port)
    try:
        sendserver.quit()
    except:
        return "Error: could not close connection to server %s:%s" % (ip, port)
    return 'Message relayed to %s:%s' % (ip, port)

def savetofile(mailfrom, rcpttos, data,messageid):
    fname = "%s%s-%s.eml" % (path,ftime(),str(uuid.uuid4()))
    try:
        f = open(fname, 'w+')
        f.write(data)
        f.closed
        return 'Message saved to : %s' % (fname)
    except:
        return 'Error: Message could not be saved to : %s' % (fname)

class CustomSMTPServer(smtpd.SMTPServer):
    def process_message(self, peer, mailfrom, rcpttos, data):
        messageid=getmesid(data)
        print '%s %s Start Proxy action' % (logtime(), messageid)
        print '%s %s Message from %s to %s size %s via %s' % (logtime(), messageid, mailfrom, rcpttos, len(data), peer)
        state = deliverto(destip, destport, mailfrom, rcpttos, data, messageid)
        print '%s %s %s' % (logtime(), messageid, state)
        state = savetofile(mailfrom, rcpttos, data, messageid)
        print '%s %s %s' % (logtime(), messageid, state)
        print '%s %s End Proxy action' % (logtime(), messageid)
        return

def main():
    server = CustomSMTPServer((bindip, int(bindport)), None)
    asyncore.loop()

if __name__ == "__main__":
    (bindip, bindport, destip, destport, path) = getconfig()
    main()
