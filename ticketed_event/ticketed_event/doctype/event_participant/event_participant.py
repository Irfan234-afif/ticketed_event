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
		self.send_confirmation_email()
	
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

	def get_email_context(self):
		"""Generate context for confirmation email"""
		# Fetch registration details
		registration = frappe.get_doc("Event Registration", self.registration)
		
		# Fetch event details
		event = frappe.get_doc("Ticketed Event", self.event)
		
		# Fetch parent email from Event User
		parent_email = frappe.db.get_value("Event User", registration.user, "email")
		
		# Fetch schedules with all needed fields in one query
		scheduler_rows = frappe.get_all("Event Registration Schedule", 
			filters={"parent": self.registration}, 
			fields=["schedule"]
		)
		
		schedule_names = [row.schedule for row in scheduler_rows]
		schedules = []
		
		if schedule_names:
			schedules = frappe.get_all("Event Schedule", 
				filters={"name": ["in", schedule_names]}, 
				fields=["name", "title", "date", "start_time", "end_time", "last_entry_time"]
			)
		
		# Check if any schedule has last_entry_time
		has_last_entry_time = any(s.get("last_entry_time") for s in schedules)
		
		# Format dates
		from frappe.utils import formatdate
		event_start_date = formatdate(event.start_date, "dd MMM yyyy") if event.start_date else "N/A"
		event_end_date = formatdate(event.end_date, "dd MMM yyyy") if event.end_date else "N/A"
		
		# Format schedules with dates and times
		formatted_schedules = []
		for s in schedules:
			formatted_schedules.append({
				"name": s.get("name"),
				"title": s.get("title"),
				"date": formatdate(s.get("date"), "dd MMM yyyy") if s.get("date") else "N/A",
				"start_time": s.get("start_time"),
				"end_time": s.get("end_time"),
				"last_entry_time": s.get("last_entry_time"),
			})
		
		# Get event image URL (if exists)
		event_image_url = None
		if event.image:
			from frappe.utils import get_url
			event_image_url = get_url() + event.image
		
		# Generate QR code URL using external API
		from urllib.parse import quote
		qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={quote(self.qr_code_id)}"
		
		return {
			"ticket_id": self.registration,
			"registration_id": registration.name,
			"participant_name": self.full_name,
			"participant_email": self.email,
			"parent_email": parent_email or "N/A",
			"event_name": event.title,
			"event_start_date": event_start_date,
			"event_end_date": event_end_date,
			"event_image": event_image_url,
			"schedules": formatted_schedules,
			"has_last_entry_time": has_last_entry_time,
			"qr_code_url": qr_code_url,
			"qr_code_id": self.qr_code_id,
			"terms_text": event.terms_text if hasattr(event, 'terms_text') else None,
			"current_year": frappe.utils.now_datetime().year
		}

	def send_confirmation_email(self):
		"""Send confirmation email with QR code to participant"""
		try:
			context = self.get_email_context()
			
			# Render email template
			import os
			template_path = os.path.join(
				os.path.dirname(__file__), 
				"event_participant_email.html"
			)
			
			with open(template_path, 'r') as f:
				template_content = f.read()
			
			from jinja2 import Template
			template = Template(template_content)
			html_content = template.render(**context)
			
			# Fetch event title for subject
			event_title = context.get("event_name", "Event")

			# Send email - QR code is loaded from external URL, no attachments needed
			frappe.sendmail(
				recipients=[self.email],
				subject=f"Registration Confirmed: {event_title}",
				message=html_content,
				now=True
			)
			
			frappe.logger().info(f"Confirmation email sent to {self.email} for participant {self.name}")
			
		except Exception as e:
			# Log error but don't block participant creation
			frappe.logger().error(f"Failed to send confirmation email to {self.email}: {str(e)}")
			frappe.log_error(f"Email sending failed for participant {self.name}: {str(e)}", "Event Participant Email Error")


