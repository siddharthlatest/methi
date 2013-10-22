from customerio import CustomerIO
from mixpanel import Mixpanel
from collections import deque
import threading
import cPickle
import os
from time import sleep
import traceback

class Analytics:

	def __init__(self):
		dump_file = "../data/analytic_dump.dmp"
		mp_project_token = "50a705866eaa634de5a27b30bc2af519"
		cio_siteid = "b17a48b1443e4c155066"
		cio_apikey = "da11f41df124032d41ba"
		mp = Mixpanel(mp_project_token)
		cio = CustomerIO(cio_siteid, cio_apikey)
		self.storage = deque()
		self.email_id = None
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
				except Exception:
					storage.append(data)
			elif data["job"] == "identify":
				try:
					#mp.people_set()
					cio.identify(id=data["user_id"], email=data["user_id"], name=data["user_name"])
				except Exception:
					storage.append(data)
			else:
				continue

	def track(self, event, properties):
		if not self.email_id:
			return
		data = {"job":"track", "user_id":self.email_id, "event":event, "properties":properties}
		self.storage.appendleft(data)

	def identify(self, user_id, user_name):
		data = {"job":"identify", "user_id":user_id, "user_name":user_name}
		self.email_id = user_id
		self.fullname = user_name
		self.storage.appendleft(data)

	def finish(self):
		data = {"job":"finish"}
		self.storage.append(data)