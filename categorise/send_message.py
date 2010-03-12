'''
Created on 8/mar/2010

pyxmpp module is required in order to work
With Debian/ubuntu just type:

sudo apt-get install python-pyxmpp
'''
import sys

try:
    pyxmpp_exception = True
    from pyxmpp.jid import JID
    from pyxmpp.jabber.simple import send_message
except ImportError:
    print("pyxmpp module is required to work properly, notificazion won't be sent")
    pyxmpp_exception = False

"""send jabber message using pyxmpp module"""
def send_msg(message, jabber_id, jabber_password, jabber_recpt):
    if pyxmpp_exception:
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
    return pyxmpp_exception