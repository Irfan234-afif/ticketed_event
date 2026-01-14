# Copyright (c) 2024, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class EventRegistration(Document):
	def autoname(self):
		import string
		import random

		# Structure: LFY-{RANDOM_SUFFIX}
		# Random suffix: 6 uppercase characters/digits
		
		chars = string.ascii_uppercase + string.digits
		random_suffix = ''.join(random.choices(chars, k=6))
		
		self.name = f"LFY-{random_suffix}"

	def validate(self):
		self.validate_participant_limit()
		self.validate_schedules_capacity()
		self.validate_user_schedule_uniqueness()
		self.validate_daily_schedule_limit()
		self.validate_one_registration_per_event()



	def get_participant_count(self):
		return frappe.db.count("Event Participant", {"registration": self.name})

	def validate_participant_limit(self):
		# This is trickier since participants are created separately.
		# We might need to check this during submission or when adding participants.
		# For now, let's keep it as a check on the registration level.
		if self.get_participant_count() > 3:
			frappe.throw("You can register a maximum of 3 participants per registration.")

	def validate_schedules_capacity(self):
		if not self.schedules:
			return

		for row in self.schedules:
			schedule_doc = frappe.get_doc("Event Schedule", row.schedule)
			if schedule_doc.is_unlimited_capacity:
				continue
				
			if schedule_doc.max_capacity == 0:
				continue # No limit (Legacy behavior or explicit 0)
			
			# Current enrolled
			current_enrolled = schedule_doc.enrolled_count
			new_count = self.get_participant_count()

			if self.docstatus == 0 or self.docstatus == 1: # Draft or Submitted (pre-update)
				if current_enrolled + new_count > schedule_doc.max_capacity:
					frappe.throw(f"Schedule {row.schedule} is full. Available slots: {schedule_doc.max_capacity - current_enrolled}")

	def validate_user_schedule_uniqueness(self):
		if not self.user or not self.schedules:
			return
		
		for row in self.schedules:
			# Check if this user already has a SUBMITTED registration for this same schedule
			# Joining with child table to find if user has registered for this schedule
			existing = frappe.db.sql("""
				SELECT er.name 
				FROM `tabEvent Registration` er
				JOIN `tabEvent Registration Schedule` ers ON ers.parent = er.name
				WHERE er.user = %(user)s
				AND ers.schedule = %(schedule)s
				AND er.docstatus = 1
				AND er.name != %(current_name)s
			""", {
				"user": self.user,
				"schedule": row.schedule,
				"current_name": self.name
			})
			
			if existing:
				frappe.throw(f"User {self.user} is already registered for schedule {row.schedule} (Registration: {existing[0][0]}).")

	def validate_daily_schedule_limit(self):
		"""Validate that a user (by email) can only register for 1 schedule per day (and in total per event for now based on 'only 1 schedule')"""
		if not self.user or not self.schedules:
			return
		
		# Validasi 1 schedule per registration transaction
		if len(self.schedules) > 1:
			frappe.throw("Mohon maaf, setiap registrasi hanya boleh memilih 1 jadwal.")

		# Get the date of the current schedule
		# Collect all unique dates from selected schedules
		current_dates = set()
		for row in self.schedules:
			date = frappe.db.get_value("Event Schedule", row.schedule, "date")
			if date:
				current_dates.add(date)
		
		for date in current_dates:
			# Count schedules the user is already registered for on this date
			existing_count = frappe.db.sql("""
				SELECT COUNT(ers.schedule)
				FROM `tabEvent Registration` er
				JOIN `tabEvent Registration Schedule` ers ON ers.parent = er.name
				JOIN `tabEvent Schedule` es ON ers.schedule = es.name
				WHERE er.user = %(user)s
				AND es.date = %(date)s
				AND er.docstatus = 1
				AND er.name != %(current_name)s
			""", {
				"user": self.user,
				"date": date,
				"current_name": self.name
			})[0][0]
			
			if existing_count >= 1:
				frappe.throw(f"Setiap akun hanya boleh mendaftar 1 jadwal saja. Anda sudah terdaftar untuk tanggal {date}.")


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
		self.validate_schedules_capacity() # Re-check capacity
		self.update_schedule_count(increment=True)

	def on_cancel(self):
		self.update_schedule_count(increment=False)

	def update_schedule_count(self, increment=True):
		if not self.schedules:
			return
		
		count = self.get_participant_count()
		
		for row in self.schedules:
			# Use atomic SQL UPDATE to prevent race conditions and deadlocks
			# This directly updates the database without loading the document
			if increment:
				frappe.db.sql("""
					UPDATE `tabEvent Schedule`
					SET enrolled_count = enrolled_count + %s,
						modified = NOW(),
						modified_by = %s
					WHERE name = %s
				""", (count, frappe.session.user, row.schedule))
			else:
				# For decrement, ensure we don't go below 0
				frappe.db.sql("""
					UPDATE `tabEvent Schedule`
					SET enrolled_count = GREATEST(0, enrolled_count - %s),
						modified = NOW(),
						modified_by = %s
					WHERE name = %s
				""", (count, frappe.session.user, row.schedule))
			
			# Clear cache for this schedule to ensure fresh data is loaded next time
			frappe.clear_cache(doctype="Event Schedule", name=row.schedule)


@frappe.whitelist()
def check_in_participant(qr_code_id, schedule=None):
	# Role Check
	roles = frappe.get_roles()
	allowed_roles = ["Scanner", "System Manager", "Administrator"]
	if not any(role in roles for role in allowed_roles):
		frappe.throw("You do not have permission to perform this action.", frappe.PermissionError)

	# Find participant with this qr_code
	participant = frappe.db.get_value("Event Participant", {"qr_code_id": qr_code_id}, ["name", "full_name", "registration"], as_dict=True)
	
	if not participant:
		frappe.throw("Invalid QR Code.")
	
	# Find the submitted registration this participant belongs to
	if not participant.registration:
		frappe.throw("Registration record not found for this participant.")
	
	registration = frappe.get_doc("Event Registration", participant.registration)
	
	if registration.docstatus != 1:
		frappe.throw("Registration is not submitted.")

	# Find valid schedules in registration
	registered_schedules = [row.schedule for row in registration.schedules]
	if not registered_schedules:
		frappe.throw("No schedule found in registration.")

	target_schedule = None

	if schedule:
		# EXPLICIT SCHEDULE CHECK
		if schedule not in registered_schedules:
			frappe.throw(f"Participant is not registered for this schedule.")
		
		target_schedule = frappe.get_doc("Event Schedule", schedule)
	else:
		# AUTO-DETECT (Legacy/Fallback)
		# Find closest schedule based on current time
		
		# Get all schedules details
		schedule_details = frappe.get_all("Event Schedule", 
			filters={"name": ["in", registered_schedules]}, 
			fields=["name", "date", "start_time", "end_time", "last_entry_time"])

		import datetime
		now = frappe.utils.now_datetime()
		
		min_diff = None
		
		for s in schedule_details:
			s_start = frappe.utils.get_datetime(f"{s.date} {s.start_time}")
			diff = abs((s_start - now).total_seconds())

			if min_diff is None or diff < min_diff:
				min_diff = diff
				target_schedule = s
		
		if not target_schedule:
			frappe.throw("Could not determine closest schedule.")


	# Check Last Entry Time (Strict Check)
	if target_schedule.last_entry_time:
		import datetime
		now = frappe.utils.now_datetime()
		# Combine date and last_entry_time
		entry_cutoff = frappe.utils.get_datetime(f"{target_schedule.date} {target_schedule.last_entry_time}")
		if now > entry_cutoff:
			frappe.throw(f"Check-in for this schedule closed at {target_schedule.last_entry_time}.")

	# Check if already checked in for this specific schedule (and participant)
	existing_checkin = frappe.db.exists("Event Checkin", {
		"registration": registration.name,
		"participant": participant.name,
		"schedule": target_schedule.name
	})

	if existing_checkin:
		frappe.throw(f"Participant {participant.full_name} is already checked in for schedule {target_schedule.name}.")

	# Create Event Checkin
	checkin = frappe.new_doc("Event Checkin")
	checkin.registration = registration.name
	checkin.participant = participant.name
	checkin.event = registration.event
	checkin.schedule = target_schedule.name
	checkin.check_in_time = frappe.utils.now() 
	checkin.save(ignore_permissions=True)
	
	return {
		"status": "success", 
		"participant": participant.full_name, 
		"event": registration.event,
		"schedule": target_schedule.name,
		"check_in_time": checkin.check_in_time
	}

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

	try:
		# Pre-check capacity for ALL schedules involved
		# Each participant will need 1 spot in EACH schedule
		num_participants = len(participants) if participants else 0
		
		if num_participants > 0:
			from frappe import _
			for schedule_name in schedules:
				# Lock and check
				capacity_data = frappe.db.sql("""
					SELECT max_capacity, enrolled_count, is_unlimited_capacity, title, name
					FROM `tabEvent Schedule` 
					WHERE name = %s 
					FOR UPDATE
					""", (schedule_name), as_dict=True)

				if capacity_data:
					pd = capacity_data[0]
					if not pd.is_unlimited_capacity:
						available = pd.max_capacity - pd.enrolled_count
						if num_participants > available:
							frappe.throw(_("Not enough seats available for Schedule {0}. Requested: {1}, Available: {2}").format(pd.title or pd.name, num_participants, available))


		# 1. Get or Create Event User
		email = user_data.get("email")
		full_name = user_data.get("full_name")
		phone = user_data.get("phone")
		instagram = user_data.get("instagram")
		user_type = user_data.get("type", "Personal")
		
		if not email:
			frappe.throw("Email is defined")

		user_name = email
		if not frappe.db.exists("Event User", user_name):
			user_doc = frappe.new_doc("Event User")
			user_doc.email = email
			user_doc.full_name = full_name
			user_doc.phone = phone
			user_doc.instagram = instagram
			user_doc.type = user_type
			user_doc.insert(ignore_permissions=True)
		else:
			# Update existing user info if needed, or at least type/instagram if missing?
			# For now, let's update if provided
			user_doc = frappe.get_doc("Event User", user_name)
			if instagram:
				user_doc.instagram = instagram
			if user_type:
				user_doc.type = user_type
			user_doc.save(ignore_permissions=True)

		# One Request = One Registration with multiple schedules
		
		# 2. Create Event Registration (ONE DOC)
		registration = frappe.new_doc("Event Registration")
		registration.event = event
		registration.user = user_name
		
		# Add schedules to child table
		for schedule_name in schedules:
			registration.append("schedules", {"schedule": schedule_name})
		
		registration.save(ignore_permissions=True) # Validates capacity and uniqueness

		# 3. Create Participants
		for p in participants:
			# Retry logic for Naming Series Deadlock (Optimistic Locking)
			# Try 5 times before giving up
			for i in range(5):
				try:
					part_doc = frappe.new_doc("Event Participant")
					part_doc.registration = registration.name
					part_doc.full_name = p.get("full_name")
					part_doc.email = p.get("email")
					part_doc.phone = p.get("phone")
					part_doc.instagram = p.get("instagram")
					part_doc.type = p.get("type", "Personal")
					part_doc.insert(ignore_permissions=True)
					break # Success
				except frappe.QueryDeadlockError:
					if i == 4: raise
					import time, random
					time.sleep(random.random() * 0.2) # Wait 0-200ms

		# 4. Submit Registration
		registration.submit()

		# Commit transaction on success
		frappe.db.commit()

		return {"registration": [registration.name]}
	
	except Exception as e:
		# Rollback on any error
		frappe.db.rollback()
		raise
