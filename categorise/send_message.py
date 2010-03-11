'''
Created on 8/mar/2010

pyxmpp module is required in order to work
With Debian/ubuntu just type:

sudo apt-get install python-pyxmpp
'''
import sys
from pyxmpp.jid import JID
from pyxmpp.jabber.simple import send_message

"""send jabber message using pyxmpp"""
def send_msg(message, jabber_id, jabber_password, jabber_recpt):
    try:
        jid = jabber_id
        password = jabber_password
        recpt = jabber_recpt
        subject = "Deluge Torrent completed"
        body=message
        jid=JID(jid)
        if not jid.resource:
            jid=JID(jid.node,jid.domain,"send_message")
            recpt=JID(recpt)
            send_message(jid,password,recpt,body,subject)
    except Error:
        pass