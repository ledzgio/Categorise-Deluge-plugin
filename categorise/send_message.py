import sys
import threading

try:
    pyxmpp_exception = False
    from pyxmpp.jid import JID
    from pyxmpp.jabber.simple import send_message
except ImportError:
    print("pyxmpp module is required to work properly, notificazion won't be sent")
    pyxmpp_exception = True

class PyXmpp:
    def __init__(self):
        self.lock = threading.Lock()
        
    def send(self, message, jabber_id, jabber_password, jabber_recpt):
        try:
            self.lock.acquire()#acquire lock
            subject = "Deluge Torrent completed"
            jid=JID(jabber_id)
            if not jid.resource:
                jid=JID(jid.node,jid.domain,"send_message")
                recpt=JID(jabber_recpt)
                send_message(jid, jabber_password, recpt, message, subject)
        finally:
            self.lock.release();#release lock

"""send jabber message using pyxmpp module (starting new thread)"""
class PyXmppThread(threading.Thread):
    def __init__(self, message, jabber_id, jabber_password, jabber_recpt):
        threading.Thread.__init__(self)
        self.message=message
        self.jabber_id=jabber_id
        self.jabber_password=jabber_password
        self.jabber_recpt=jabber_recpt
        
    def run(self):
        pyxmpp = PyXmpp()
        pyxmpp.send(self.message, self.jabber_id, self.jabber_password, self.jabber_recpt)
    

def send_msg(message, jabber_id, jabber_password, jabber_recpt):
    if not pyxmpp_exception:
        xmpp = PyXmppThread(message, jabber_id, jabber_password, jabber_recpt)#send message
        xmpp.start()
        return True
    else:
        return False