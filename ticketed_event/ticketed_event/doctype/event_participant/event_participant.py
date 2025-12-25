# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
import uuid
from frappe.model.document import Document

class EventParticipant(Document):
	def before_insert(self):
		if not self.qr_code_id:
			self.qr_code_id = str(uuid.uuid4())
