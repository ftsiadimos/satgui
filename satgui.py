#!/usr/bin/env python
## Fotios Tsiadimos
import base64
import urllib2
import json
import ssl
from array import array

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject
import threading
import time
import subprocess
from datetime import datetime

columns = ["Label",
           "Result",
           "State",
           "Started_at",
           "Ended_at"]

class satmonitor(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Satellite-Task-Monitor")
        self.set_border_width(10)
        self.set_resizable(False)
        self.set_default_size(600,630)
        self.grid = Gtk.Grid()
        self.grid.set_row_spacing(15)

        self.grid.set_column_spacing(8)

        self.label1 = Gtk.Label("Server")
        self.grid.attach(self.label1, 1, 0, 1, 1)

        self.label2 = Gtk.Label("Uername")
        self.grid.attach(self.label2, 2, 0, 1, 1)

        self.label3 = Gtk.Label("Password")
        self.grid.attach(self.label3, 3, 0, 1, 1)

        ###   insert box
        self.name_box1 = Gtk.Entry()
        self.grid.attach(self.name_box1, 1, 1, 1, 1)
        self.name_box2 = Gtk.Entry()
        self.grid.attach(self.name_box2, 2, 1, 1, 1)
        self.name_box3 = Gtk.Entry()
        self.name_box3.set_visibility(False)
	self.name_box3.connect("key-release-event", self.on_key_event)
        self.grid.attach(self.name_box3, 3, 1, 1, 1)
        ### insert button

        self.label4 = Gtk.Label("")
        self.grid.attach(self.label4, 1, 2, 1, 1)


        self.button = Gtk.Button("Log in")
        self.button.connect("clicked", self.login)
        self.grid.attach(self.button, 2, 2, 1, 1)
        ### close button
        button = Gtk.Button.new_with_mnemonic("_Close")
        button.connect("clicked", self.on_close_clicked)
        self.grid.attach(button, 3, 2, 1, 1)

        self.listmodel = Gtk.ListStore(str, str, str, str, str)
        self.view = Gtk.TreeView(model=self.listmodel)
        self.view.set_can_default(False)
        for i in range(len(columns)):
               cell = Gtk.CellRendererText()
               if i == 0:
                   cell.props.weight_set = True
               col = Gtk.TreeViewColumn(columns[i], cell, text=i)
               self.view.append_column(col)

        self.selection = self.view.get_selection()
        self.grid.attach(self.view, 1, 4, 3, 1)
        self.cur_view = []


        ### show on gui
        self.add(self.grid)
	i = datetime.now()
	self.error_time = i.strftime('%Y-%m-%dT%H:%M:%S')
    def on_key_event(self, widget, ev, data=None):
	    if ev.keyval == 65293: 
		self.login(True)
    def autore(self):
                try:
                  self.call_api()
                except:
                 pass
                for i in self.rowsm:
                  if i not in self.cur_view:
                    self.listmodel.append(i)
                    self.cur_view.append(i)
                    if i[1] == "error" and self.error_time < i[3]:
			  print i[3]
                          self.sendmessage("Error task " + i[0])
                    if len(self.listmodel) > 20:
                      path = Gtk.TreePath(0)
                      treeiter = self.listmodel.get_iter(path)
                      self.listmodel.remove(treeiter)
                  if  len(self.cur_view) > 50:
                       del self.cur_view[0]
                GObject.timeout_add(900, self.autore)

    def login(self, button):

        self.running =  True
        self.label4.set_label(" ")
        url = self.name_box1.get_text()
        username = self.name_box2.get_text()
        password = self.name_box3.get_text()
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE

        systemsurl = 'https://'+url+'/foreman_tasks/api/tasks/'
        try:
           self.systemsreq = urllib2.Request(systemsurl)
           systemsbase64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
           self.systemsreq.add_header("Authorization", "Basic %s" % systemsbase64string)
           systemsresult = urllib2.urlopen(self.systemsreq, context=self.ctx)
           self.name_box1.set_editable(False)
           self.name_box2.set_editable(False)
           self.name_box3.set_editable(False)
           self.button.set_sensitive(False)				
           self.th = threading.Thread(target=self.autore)
           self.th.daemon = True
           self.th.start()
        except:
            self.label4.set_label("Not Connected!")

 
    def call_api(self):
        systemsresult = urllib2.urlopen(self.systemsreq, context=self.ctx)
        mysystems = systemsresult.read()
        parsedsystems = json.loads(mysystems)
        mysystems = (parsedsystems['results'])
        self.rows = []
        self.rowsm = []
        for system in mysystems:
           te = (system['label'], system['result'], system['state'], system['started_at'], system['ended_at'])
           self.rows.append(te)
        for i in self.rows:
            i = list(i)
            label = i[0]
            start_time = i[3]
            end_time = i[4]
            i[3] = start_time.replace(".000Z", '')
            if i[4]:       
                i[4] = end_time.replace(".000Z", '')       
            i[0] = label.lstrip("Actions::Katello::")
            self.rowsm.insert(0, i)
            
        return self.rowsm


    def on_close_clicked(self, button):
        Gtk.main_quit()

    def sendmessage(self, message):
        subprocess.Popen(['notify-send', message])
        return


GObject.threads_init()
win = satmonitor()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
