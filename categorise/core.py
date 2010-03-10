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
import mimetypes
#from send_message import send_msg
import datetime

#TODO
#New categories: video, audio, data (iso, applications, ecc.), documents, uncategorized

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
}
#File formats
DOC_FORMAT = [".pdf",".doc",".ods", ".txt", ".odt", ".xls", ".docx"]
DATA_FORMAT = [".iso", ".img", ".mds", ".mdf", ".nrg", ".bin", ".cue",
               ".zip", ".rar", ".tar", ".bz2", ".tar.gz", ".tgz", ".r00", ".exe", ".msi"]

class Core(CorePluginBase):
    def enable(self):
        log.debug("###Enabling plugin..")
        self.config = deluge.configmanager.ConfigManager("categorise.conf", DEFAULT_PREFS)
        
        self.config["full_download_path"] = os.path.join(self.config["download_path"], self.config["root_folder"])
        log.debug("### move completed dir %s", self.config["full_download_path"])
        
        #setting event
        component.get("EventManager").register_event_handler("TorrentFinishedEvent", self._on_torrent_finished)
        
        #enable log to file
##        self._init_logger()
##        logging.info("Starting session..")
    
    def disable(self):
        log.debug("###Disabling plugin.")
##        logging.shutdown()
        
    def update(self):
        pass
        
    def _on_torrent_finished(self, torrent_id):
        # Get the save path
        torrent = component.get("TorrentManager")[torrent_id]
        total_download_byte = torrent.get_status(["total_payload_download"])["total_payload_download"]
        total_download_converted = self._convert_bytes(total_download_byte)
        torrent_name = torrent.get_status(["name"])["name"]
##        logging.info("completed torrent "+torrent_name+", downloaded %s", total_download)
        log.debug("#### completed torrent "+torrent_name+", downloaded "+ `total_download_converted`)
        files = torrent.get_files()
        
        #torrent_details = "Torrent: "+torrent_name+" containing\n"+"N files: "+`len(files)`+"\nSize: "+ `total_download_converted`+"\n"
        
        random_file = self._get_random_elem(files)
        log.debug("### analyzing random file %s", random_file["path"])
        #get destination path
        dest = self._guess_destination(random_file, files)
        i = 0
        """
        for f in files:
            i = i + 1
            torrent_details = torrent_details + f + "\n"
            if i == 15:
                torrent_details = torrent_details + "..."+`len(files)-i`+" more"
                break
        torrent_details = torrent_details + "Identyfied type: "+dest[1]+"\nCompleted at: "+_get_current_datetime()+"\nMoved to folder: "+dest[0]
        """
        log.debug("### torrent destination path %s", dest[0])
        if not os.path.exists(dest[0]):
            log.debug("### directory "+ dest[0] +" does not exists, it will be created")
##            logging.info("creating directory %s", dest[0])
            os.makedirs(dest[0])
        #moving torrent storage to final destination
        torrent.move_storage(dest[0])
        torrent.is_finished = True
        torrent.update_state()
##        logging.info("moving finished torrent containing "+`len(files)`+" files to %s", dest[0])
        log.debug("#### moving finished torrent containing "+`len(files)`+" file(s) to %s", dest[0])
        #sending message to jabber user
        #log.debug("#### sending messgage "+torrent_details)
        
        #send_msg(torrent_details)
        
        #log.debug("#### message sent to jabber user ledzgio@jabber.org")
            
    
    def _guess_destination(self, file, torrent_files):
        full_download_path = self.config["full_download_path"]
        ext = os.path.splitext(file["path"])
        
        log.debug("####file path %s", file["path"])
        
        log.debug("#####getting mimetype..")
        
        log.debug("1############################################1")
        #log.debug(dcore.get_config())
	#dcore = Core()
	#print dcore.get_config()
        log.debug("2############################################2")
        #log.debug(dcore.get_config())
        
	#http://dev.deluge-torrent.org/wiki/Development/UiClient1.2

        #res = mimetypes.guess_type(file["path"])[0]
        #download_location = self.get_config()["download_location"]
        
	log.debug("#####download location: %s", download_location)
        res = mimetypes.guess_type(file["path"])[0]
        
        if (res.startswith("audio")):
            return [os.path.join(full_download_path, self.config["sub_audio"]), "audio"]
        elif (res.startswith("video")):
            return [os.path.join(full_download_path, self.config["sub_video"]), "video"]
        elif(ext in DOC_FORMAT):
            return [os.path.join(full_download_path, self.config["sub_documents"]), "doc"]
        elif(ext in DATA_FORMAT):
            return [os.path.join(full_download_path, self.config["sub_data"]), "data"]
        else:
            return [os.path.join(full_download_path, self.config["sub_uncat"]), "uncat"]
            
    def _get_current_datetime(self):
	now = datetime.datetime.now()
	return now.strftime("%Y-%m-%d %H:%M")
        
    def _get_random_elem(self, list):
        length = len(list)
        rand_number = random.randint(0, length - 1)
        return list[rand_number]
    
    def _convert_bytes(self, bytes):
        bytes = float(bytes)
        if bytes >= 1099511627776:
            terabytes = bytes / 1099511627776
            size = '%.2fT' % terabytes
        elif bytes >= 1073741824:
            gigabytes = bytes / 1073741824
            size = '%.2fG' % gigabytes
        elif bytes >= 1048576:
            megabytes = bytes / 1048576
            size = '%.2fM' % megabytes
        elif bytes >= 1024:
            kilobytes = bytes / 1024
            size = '%.2fK' % kilobytes
        else:
            size = '%.2fb' % bytes
        return size
    
##    def _init_logger(self):
##        LOG_FILENAME = os.path.join(self.config["full_download_path"], "folders.log")
##        # create logger
##        logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
##        log.debug("######## log initialized at %s", LOG_FILENAME)
        
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
