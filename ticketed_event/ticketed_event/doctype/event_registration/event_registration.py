# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now

class EventRegistration(Document):
	def validate(self):
		self.validate_participant_limit()
		self.validate_schedule_capacity()
		self.validate_user_schedule_uniqueness()
		self.validate_daily_schedule_limit()

	def get_participant_count(self):
		return frappe.db.count("Event Participant", {"registration": self.name})

	def validate_participant_limit(self):
		# This is trickier since participants are created separately.
		# We might need to check this during submission or when adding participants.
		# For now, let's keep it as a check on the registration level.
		if self.get_participant_count() > 3:
			frappe.throw("You can register a maximum of 3 participants per registration.")

	def validate_schedule_capacity(self):
		if not self.schedule:
			return

		schedule_doc = frappe.get_doc("Event Schedule", self.schedule)
		if schedule_doc.max_capacity == 0:
			return # No limit
		
		# Current enrolled
		current_enrolled = schedule_doc.enrolled_count
		new_count = self.get_participant_count()

		if self.docstatus == 0 or self.docstatus == 1: # Draft or Submitted (pre-update)
			if current_enrolled + new_count > schedule_doc.max_capacity:
				frappe.throw(f"Schedule is full. Available slots: {schedule_doc.max_capacity - current_enrolled}")

	def validate_user_schedule_uniqueness(self):
		if not self.user or not self.schedule:
			return
		
		# Check if this user already has a SUBMITTED registration for this same schedule
		existing = frappe.db.exists("Event Registration", {
			"user": self.user,
			"schedule": self.schedule,
			"docstatus": 1, # Submitted
			"name": ["!=", self.name]
		})
		
		if existing:
			frappe.throw(f"User {self.user} is already registered for this schedule (Registration: {existing}).")
	
	def validate_daily_schedule_limit(self):
		"""Validate that a user (by email) can only register for max 2 schedules per day"""
		if not self.user or not self.schedule:
			return
		
		# Get the date of the current schedule
		current_schedule_date = frappe.db.get_value("Event Schedule", self.schedule, "date")
		if not current_schedule_date:
			return
		
		# Get user's email
		user_email = frappe.db.get_value("Event User", self.user, "email")
		if not user_email:
			return
		
		# Count existing submitted registrations for this user on the same date
		existing_registrations = frappe.db.sql("""
			SELECT er.name, er.schedule
			FROM `tabEvent Registration` er
			INNER JOIN `tabEvent Schedule` es ON er.schedule = es.name
			WHERE er.user = %(user)s
			AND es.date = %(date)s
			AND er.docstatus = 1
			AND er.name != %(current_name)s
		""", {
			"user": self.user,
			"date": current_schedule_date,
			"current_name": self.name or ""
		}, as_dict=True)
		
		if len(existing_registrations) >= 2:
			frappe.throw(f"You can only register for a maximum of 2 schedules per day. You already have {len(existing_registrations)} registrations for {current_schedule_date}.")

	def validate_one_registration_per_event(self):
		"""Validate that a user can only register once per event"""
		if not self.user or not self.event:
			return
		
		# Check if this user already has a SUBMITTED registration for this event
		existing = frappe.db.exists("Event Registration", {
			"user": self.user,
			"event": self.event,
			"docstatus": 1,  # Submitted
			"name": ["!=", self.name]
		})
		
		if existing:
			frappe.throw(f"You have already registered for this event. Each user can only register once per event. {existing}")

	def on_submit(self):
		self.validate_participant_limit() # Re-check on submission
		self.validate_schedule_capacity() # Re-check capacity
		self.update_schedule_count(increment=True)
		self.send_email_notifications()

	def on_cancel(self):
		self.update_schedule_count(increment=False)

	def update_schedule_count(self, increment=True):
		if not self.schedule:
			return
		
		schedule_doc = frappe.get_doc("Event Schedule", self.schedule)
		count = self.get_participant_count()
		
		if increment:
			schedule_doc.enrolled_count += count
		else:
			schedule_doc.enrolled_count = max(0, schedule_doc.enrolled_count - count)
		
		schedule_doc.save(ignore_permissions=True)

	def send_email_notifications(self):
		# Logic to send email to each participant
		participants = frappe.get_all("Event Participant", filters={"registration": self.name}, fields=["name", "email"])
		for p in participants:
			# Placeholder for email logic
			pass


@frappe.whitelist()
def check_in_participant(qr_code_id):
	# Find participant with this qr_code
	participant = frappe.db.get_value("Event Participant", {"qr_code_id": qr_code_id}, ["name", "full_name", "checked_in", "registration"], as_dict=True)
	
	if not participant:
		frappe.throw("Invalid QR Code.")
	
	if participant.checked_in:
		frappe.throw(f"Participant {participant.full_name} is already checked in.")

	# Find the submitted registration this participant belongs to
	if not participant.registration:
		frappe.throw("Registration record not found for this participant.")
	
	registration_status = frappe.db.get_value("Event Registration", participant.registration, "docstatus")
	
	if registration_status != 1:
		frappe.throw("Registration is not submitted.")

	# Update participant check-in status
	p_doc = frappe.get_doc("Event Participant", participant.name)
	p_doc.checked_in = 1
	p_doc.check_in_time = now()
	p_doc.save(ignore_permissions=True)
	
	return {"status": "success", "participant": participant.full_name, "event": frappe.db.get_value("Event Registration", participant.registration, "event")}

@frappe.whitelist(allow_guest=True)
def create_full_registration(event, schedules, user_data, participants, captcha_token=None):
	"""
	Create a complete registration with multiple schedules and participants.
	:param event: Ticketed Event Name
	:param schedules: List of Event Schedule Names
	:param user_data: Dict with full_name, email, phone
	:param participants: List of Dicts with full_name, email, phone, instagram
	:param captcha_token: reCAPTCHA token
	"""
	from ticketed_event.api import verify_recaptcha
	import json
	
	# Verify CAPTCHA
	verify_recaptcha(captcha_token)

	if isinstance(user_data, str):
		user_data = json.loads(user_data)
	if isinstance(participants, str):
		participants = json.loads(participants)
	
	if isinstance(schedules, str):
		try:
			schedules = json.loads(schedules)
		except:
			# If it's a single string (legacy support or single select), make it a list
			schedules = [schedules]
	
	if not isinstance(schedules, list):
		schedules = [schedules]

	# 1. Get or Create Event User
	email = user_data.get("email")
	full_name = user_data.get("full_name")
	phone = user_data.get("phone")
	
	if not email:
		frappe.throw("Email is defined")

	user_name = email
	if not frappe.db.exists("Event User", user_name):
		user_doc = frappe.new_doc("Event User")
		user_doc.email = email
		user_doc.full_name = full_name
		user_doc.phone = phone
		user_doc.insert(ignore_permissions=True)
	else:
		# Update phone/name if missing? Optional. For now just use existing.
		pass

	# Validate one registration per event BEFORE creating any registrations
	existing_event_registration = frappe.db.exists("Event Registration", {
		"user": user_name,
		"event": event,
		"docstatus": 1
	})
	
	if existing_event_registration:
		frappe.throw(f"You have already registered for this event. Each user can only register once per event.")

	# Validate daily schedule limit BEFORE creating any registrations
	# Group schedules by date
	from collections import defaultdict
	schedule_dates = {}
	for schedule_name in schedules:
		schedule_date = frappe.db.get_value("Event Schedule", schedule_name, "date")
		if schedule_date:
			schedule_dates[schedule_name] = schedule_date
	
	# Count schedules per date in the current request
	dates_count = defaultdict(int)
	for schedule_name in schedules:
		if schedule_name in schedule_dates:
			dates_count[schedule_dates[schedule_name]] += 1
	
	# Check existing registrations for each date
	for date, new_count in dates_count.items():
		existing_count = frappe.db.sql("""
			SELECT COUNT(*) as count
			FROM `tabEvent Registration` er
			INNER JOIN `tabEvent Schedule` es ON er.schedule = es.name
			WHERE er.user = %(user)s
			AND es.date = %(date)s
			AND er.docstatus = 1
		""", {
			"user": user_name,
			"date": date
		}, as_dict=True)[0].count
		
		total_count = existing_count + new_count
		if total_count > 2:
			frappe.throw(f"You can only register for a maximum of 2 schedules per day. You already have {existing_count} registration(s) for {date}, and you're trying to add {new_count} more.")

	created_registrations = []

	# Loop through each selected schedule
	for schedule_name in schedules:
		# 2. Create Event Registration
		registration = frappe.new_doc("Event Registration")
		registration.event = event
		registration.schedule = schedule_name
		registration.user = user_name
		registration.save(ignore_permissions=True) # Validates capacity and uniqueness

		# 3. Create Participants
		for p in participants:
			part_doc = frappe.new_doc("Event Participant")
			part_doc.registration = registration.name
			part_doc.full_name = p.get("full_name")
			part_doc.email = p.get("email")
			part_doc.phone = p.get("phone")
			part_doc.instagram = p.get("instagram")
			part_doc.insert(ignore_permissions=True)

		# 4. Submit Registration
		registration.submit()
		created_registrations.append(registration.name)

	return {"registration": created_registrations}
