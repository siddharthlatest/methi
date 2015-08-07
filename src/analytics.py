from customerio import CustomerIO
from mixpanel import Mixpanel
from collections import deque
import threading
import cPickle
import os
from time import sleep
import logging

class Analytics:

	def __init__(self):
		self.className = "Analytics"
		dump_file = "../data/analytic_dump.dmp"
		mp_project_token = "50a705866eaa634de5a27b30bc2af519"
		cio_siteid = "b17a48b1443e4c155066"
		cio_apikey = "da11f41df124032d41ba"
		mp = Mixpanel(mp_project_token)
		cio = CustomerIO(cio_siteid, cio_apikey)
		self.storage = deque()
		self.email_id = None
		
		self.logger = logging.getLogger("daemon.analytics")
		self.logger.info(self.__class__.__name__+": Init")
		
		if os.path.isfile(dump_file):
			analytic_dump = open(dump_file, "rb")
			self.storage = cPickle.load(analytic_dump)
			analytic_dump.close()
			os.remove(dump_file)
			try:
				if self.storage:
					pass
				else:
					self.storage = deque()
			except:
				self.storage = deque()
		t = threading.Thread(target=self.start_upload, args=(self.storage, mp, cio))
		t.start()

	def start_upload(self, storage, mp, cio):
		while True:
			while not storage:
				sleep(2)

			data = storage.pop()

			if data["job"] == "finish":
				try:
					
					analytic_dump = open("../data/analytic_dump.dmp", "wb")
					cPickle.dump(storage, analytic_dump)
					analytic_dump.close()
					return
				except:
					return
			elif data["job"] == "track":
				try:
					mp.track(data["user_id"], data["event"], data["properties"])
					cio.track(customer_id=data["user_id"], name=data["event"], **data["properties"])
				except Exception as e:
					self.logger.info(self.__class__.__name__+".start_upload[track].Exc: Exception:"+str(e))
					self.logger.info(self.__class__.__name__+".start_upload[track].Exc: data appended:", data)
					storage.append(data)
					
			elif data["job"] == "identify":
				try:
					#mp.people_set()
					cio.identify(id=data["user_id"], email=data["user_id"], name=data["user_name"], **data["properties"])
				except Exception:
					storage.append(data)
			else:
				continue

	def track(self, event, properties):
		self.logger.info(self.__class__.__name__+".track: called")
		if not self.email_id:
			self.logger.info(self.__class__.__name__+".track: no email")
			return
		
		data = {"job":"track", "user_id":self.email_id, "event":event, "properties":properties}
		self.storage.appendleft(data)
		self.logger.info(self.__class__.__name__+".track: data appended:"+ str(data))

		
	def identify(self, user_id, user_name, properties={}):
		data = {"job":"identify", "user_id":user_id, "user_name":user_name, "properties":properties}
		self.email_id = user_id
		self.fullname = user_name
		self.storage.appendleft(data)

	def finish(self):
		data = {"job":"finish"}
		self.storage.append(data)