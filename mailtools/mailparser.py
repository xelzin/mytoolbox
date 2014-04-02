#!/usr/bin/env python
import sys
import email
import string
import magic
import pprint

from email.header import decode_header
from email.utils import getaddresses

def decodestring(decode):
    decoded=decode_header(decode)
    if  decoded[0][1] == None :
        return decoded[0][0],"None"
    else:
        return decoded[0][0], decoded[0][1]

def guesstype(attbuffer):
    mdetect = magic.open(magic.NONE)
    mdetect.load()
    guess = mdetect.buffer(attbuffer)
    return guess

def main():
    try:
        filename = sys.argv[1]
        mail = open(filename,'r')
    except:
        print 'Cannot open file or no file specified'
        sys.exit(1)

    msg = email.message_from_file(mail)
    
    print 'File      : %s ' % filename
    print 'Message-Id: %s ' % msg['Message-Id']  

    
    sanitizefrom = msg['From'].replace('\n', '').replace('\r', '')
    froms = decode_header(sanitizefrom)

    if froms[0][1] == None :
        encoding = "None"
        frommail = froms[0][0]
        fromname = ""
    else:
        encoding = froms[0][1]
        frommail = froms[1][0]
        fromname = froms[0][0]

    print  "From      : [%s] [%s] encoding: [%s]" % (fromname, frommail, encoding)

    toaddresses = email.utils.parseaddr(msg.get_all('to',[]))
    tospaddresses = toaddresses[1].split(',')

    for adress in tospaddresses:
        adress = adress.replace('\n', '').replace('\r', '')
        prut = decode_header(adress)
        
        if prut[0][1] == None :
            encoding = "None"
            toaddr = prut[0][0]
            toname = ""
        else:
            encoding = prut[0][1]
            toaddr = prut[1][0]
            toname = prut[0][0]
    
        print  "To        : [%s] [%s] encoding: [%s]" % (toname, toaddr, encoding)
            
    (subject,subencoding) = decodestring(msg['Subject'])
    print 'Subject   : [%s] encoding: [%s]' % (subject, subencoding )
    

    if msg.get('X-Spam-Flag') == "YES":
        print "Spam      : Yes"    
    else:
        print "Spam      : No"    

    counter = 0
    for part in msg.walk():
        
        if part == None: 
           print "Empty"
        else:
            type = part.get_content_maintype()
            subtype= part.get_content_subtype()
            attname= part.get_filename()
            charset = msg.get_charsets()[counter]
            
            print '\nMultipart number: %s  ' % (counter)
            print '          Type: %s/%s ' % (type, subtype)
            if (charset):
                print '          Charset %s ' % charset
            if (attname):
                
                (filename,fileencod)=decodestring(attname)
                print '          Attachment Filename: [%s] encoding: [%s]' % (filename, fileencod)
                attbuffer = part.get_payload(decode=True)
                print '          Detected Type: %s ' % guesstype(attbuffer)

            values=part.values()
            try:
                if values[2] == 'inline':
                    print '          Content-Disposition: Inline'
            except:
                pass
            counter = counter + 1
    
    print ""

if __name__ == "__main__":
    main()
