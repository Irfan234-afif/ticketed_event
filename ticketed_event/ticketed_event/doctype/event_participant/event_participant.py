# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import uuid
from frappe.model.document import Document

class EventParticipant(Document):

	def validate(self):
		if not self.qr_code_id:
			self.qr_code_id = str(uuid.uuid4())
		
		if self.is_new():
			self.check_capacity()

	def after_insert(self):
		self.update_enrollment(1)
	
	def on_trash(self):
		self.update_enrollment(-1)

	def check_capacity(self):
		schedules = self.get_schedules()
		for schedule in schedules:
			if not schedule.is_unlimited_capacity:
				# Lock the schedule row to prevent race conditions
				# We fetch current capacity and enrolled count from DB directly with lock
				capacity_data = frappe.db.sql("""
					SELECT max_capacity, enrolled_count 
					FROM `tabEvent Schedule` 
					WHERE name = %s 
					FOR UPDATE
				""", (schedule.name), as_dict=True)
				
				if capacity_data:
					data = capacity_data[0]
					if data.enrolled_count >= data.max_capacity:
						frappe.throw(_("Event Schedule {0} is full.").format(schedule.title or schedule.name))

	def update_enrollment(self, delta):
		schedules = self.get_schedules()
		for schedule in schedules:
			frappe.db.sql("""
				UPDATE `tabEvent Schedule`
				SET enrolled_count = enrolled_count + %s
				WHERE name = %s
			""", (delta, schedule.name))

	def get_schedules(self):
		if not self.registration:
			return []
		
		# Fetch Registration Document to get schedules
		# We need rows from Event Registration Schedule
		scheduler_rows = frappe.get_all("Event Registration Schedule", 
			filters={"parent": self.registration}, 
			fields=["schedule"]
		)
		
		schedule_names = [row.schedule for row in scheduler_rows]
		if not schedule_names:
			return []

		return frappe.get_all("Event Schedule", 
			filters={"name": ["in", schedule_names]}, 
			fields=["name", "title", "max_capacity", "enrolled_count", "is_unlimited_capacity"]
		)

