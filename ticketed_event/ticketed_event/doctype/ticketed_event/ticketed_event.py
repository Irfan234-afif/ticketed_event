# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import random_string

class TicketedEvent(Document):
	def validate(self):
		if not self.route:
			self.route = random_string(6)
