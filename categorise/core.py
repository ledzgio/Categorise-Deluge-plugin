#
# core.py
#
# Copyright (C) 2009 ledzgio <ledzgio@writeme.com>
#
# Basic plugin template created by:
# Copyright (C) 2008 Martijn Voncken <mvoncken@gmail.com>
# Copyright (C) 2007-2009 Andrew Resch <andrewresch@gmail.com>
# Copyright (C) 2009 Damien Churchill <damoxc@gmail.com>
#
# Deluge is free software.
#
# You may redistribute it and/or modify it under the terms of the
# GNU General Public License, as published by the Free Software
# Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# deluge is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with deluge.    If not, write to:
#     The Free Software Foundation, Inc.,
#     51 Franklin Street, Fifth Floor
#     Boston, MA  02110-1301, USA.
#
#    In addition, as a special exception, the copyright holders give
#    permission to link the code of portions of this program with the OpenSSL
#    library.
#    You must obey the GNU General Public License in all respects for all of
#    the code used other than OpenSSL. If you modify file(s) with this
#    exception, you may extend this exception to your version of the file(s),
#    but you are not obligated to do so. If you do not wish to do so, delete
#    this exception statement from your version. If you delete this exception
#    statement from all source files in the program, then also delete it here.
#

from deluge.log import LOG as log
from deluge.plugins.pluginbase import CorePluginBase
import deluge.component as component
import deluge.configmanager
from deluge.core.rpcserver import export
from deluge.core.core import Core
import shutil
import os
import random
import mimetypes as mt
from send_message import send_msg
import datetime

DEFAULT_PREFS = {
    #sub directories
    "download_path": "",
    "full_download_path":"",
    "root_folder":"categories",
    "sub_audio":"audio",
    "sub_video":"video",
    "sub_data":"data",
    "sub_documents":"documents",
    "sub_uncat":"uncategorized",
    
    "jabber_id":"",
    "jabber_password":"",
    "jabber_recpt_id":"",
    "enable_notification":False
}
#File formats
DOC_FORMAT = [".pdf",".doc",".ods", ".txt", ".odt", ".xls", ".docx"]
DATA_FORMAT = [".iso", ".img", ".mds", ".mdf", ".nrg", ".bin", ".cue",
               ".zip", ".rar", ".tar", ".bz2", ".tar.gz", ".tgz", ".r00", ".exe", ".msi"]
GREY_LIST = [".txt", ".nfo", ".jpg", ".gif", ".m3u" ".sfv"]

class Core(CorePluginBase):
    def enable(self):
        log.debug("Enabling Categorise plugin..")
        self.config = deluge.configmanager.ConfigManager("categorise.conf", DEFAULT_PREFS)
        
        self.config["full_download_path"] = os.path.join(self.config["download_path"], self.config["root_folder"])
        
        #setting event
        component.get("EventManager").register_event_handler("TorrentFinishedEvent", self._on_torrent_finished)
    
    def disable(self):
        log.debug("Disabling Categorise plugin.")
        
    def update(self):
        pass
        
    def _on_torrent_finished(self, torrent_id):
        """Get the save path"""
        torrent = component.get("TorrentManager")[torrent_id]
        total_download_byte = torrent.get_status(["total_payload_download"])["total_payload_download"]
        total_download_converted = self._convert_bytes(total_download_byte)
        torrent_name = torrent.get_status(["name"])["name"]
        
        log.debug("completed torrent: %s", torrent_name)
        
        files = torrent.get_files()
        
        """create torrent details string"""
        torrent_details = "\nTorrent: "+torrent_name+"\nSize: "+ `total_download_converted` +"\nfile(s): "+`len(files)`+"\n"
        
        """get random file from from the torrent"""
        random_file = self._get_random_elem(files)
                
        #get destination path
        dest = self._guess_destination(random_file, files)
        i = 0
        for f in files:
            i = i + 1
            downloaded_file_path = f["path"]
            torrent_details = torrent_details + downloaded_file_path + "\n"
            if i == 3:
                torrent_details = torrent_details + "..."+`len(files)-i`+" more\n"
                break
	    now = datetime.datetime.now()
	    date_time = now.strftime("%Y-%m-%d %H:%M")
        torrent_details = torrent_details + "Identyfied type: "+dest[1]+"\nCompleted at: "+ date_time +"\nMoved to folder: "+dest[0]
        
        if not os.path.exists(dest[0]):
            log.debug("directory "+ dest[0] +" does not exists, it will be created")
            os.makedirs(dest[0])
            
        """moving torrent storage to final destination"""
        torrent.move_storage(dest[0])
        torrent.is_finished = True
        torrent.update_state()

        log.debug("moving completed torrent containing "+`len(files)`+" file(s) to %s", dest[0])
       
        """sending message to jabber user"""
        
        log.debug("########checking condition..")
        log.debug(self.config["enable_notification"] and self.config["jabber_id"] and self.config["jabber_password"] and self.config["jabber_recpt_id"])
        if(self.config["enable_notification"] and self.config["jabber_id"] and self.config["jabber_password"] and self.config["jabber_recpt_id"]):
            log.debug("#######sending notification....")
            sent = send_msg(torrent_details, self.config["jabber_id"], self.config["jabber_password"], self.config["jabber_recpt_id"])
            if not sent:
                log.debug("Notification not sent. Check if you have pyxmpp module installed on you system")
            
    def _guess_destination(self, file, torrent_files):
        full_download_path = self.config["full_download_path"]
        ext = os.path.splitext(file["path"])[1]
        
         #grab a new file
        if ((ext in GREY_LIST) and len(torrent_files) > 1):
            another_file = self._get_random_elem(torrent_files, file["path"])
            ext = os.path.splitext(another_file["path"])[1]
        
        mt.guess_extension(ext)
        
        """if unknown type put torrent to the uncategorized directory"""
        try:
            res = mt.types_map[ext]
        except KeyError:
            log.debug("unknown extension %s", ext)
            return [os.path.join(full_download_path, self.config["sub_uncat"]), "uncategorized"]
        
        if (res.startswith("audio")):
            return [os.path.join(full_download_path, self.config["sub_audio"]), "audio"]
        elif (res.startswith("video")):
            return [os.path.join(full_download_path, self.config["sub_video"]), "video"]
        elif(ext in DOC_FORMAT):
            return [os.path.join(full_download_path, self.config["sub_documents"]), "doc"]
        elif(ext in DATA_FORMAT):
            return [os.path.join(full_download_path, self.config["sub_data"]), "data"]
        else:
            return [os.path.join(full_download_path, self.config["sub_uncat"]), "uncategorized"]
        
        
    def _get_random_elem(self, list, compare_file=""):
        length = len(list)
        while True:
            if length == 0:
                break
            rand_number = random.randint(0, length - 1)
            choosen_file = list[rand_number]
            if ((compare_file == "") or (compare_file != "" and compare_file != choosen_file)):
                break
        return choosen_file
    
    def _convert_bytes(self, bytes):
        bytes = float(bytes)
        if bytes >= 1099511627776:
            terabytes = bytes / 1099511627776
            size = '%.2fTb' % terabytes
        elif bytes >= 1073741824:
            gigabytes = bytes / 1073741824
            size = '%.2fGb' % gigabytes
        elif bytes >= 1048576:
            megabytes = bytes / 1048576
            size = '%.2fMb' % megabytes
        elif bytes >= 1024:
            kilobytes = bytes / 1024
            size = '%.2fKb' % kilobytes
        else:
            size = '%.2fbytes' % bytes
        return size
        
    @export
    def set_config(self, config):
        "sets the config dictionary"
        for key in config.keys():
            self.config[key] = config[key]
        self.config.save()

    @export
    def get_config(self):
        "returns the config dictionary"
        return self.config.config
