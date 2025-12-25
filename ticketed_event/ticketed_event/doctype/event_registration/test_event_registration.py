import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days
from unittest.mock import patch, MagicMock

# Adjust import path based on your app structure
from ticketed_event.ticketed_event.doctype.event_registration.event_registration import check_in_participant

class TestEventRegistration(FrappeTestCase):
	def setUp(self):
		# Cleanup
		frappe.db.sql("DELETE FROM `tabEvent Registration`")
		frappe.db.sql("DELETE FROM `tabEvent Participant`")
		frappe.db.sql("DELETE FROM `tabEvent User`")
		frappe.db.sql("DELETE FROM `tabEvent Schedule`")
		frappe.db.sql("DELETE FROM `tabTicketed Event`")

		# Create a test event user
		self.test_user = frappe.get_doc({
			"doctype": "Event User",
			"email": "test_user@example.com",
			"full_name": "Test User"
		}).insert()

		# Create a test event and schedule
		self.event = frappe.get_doc({
			"doctype": "Ticketed Event",
			"title": "Test Event",
			"start_date": today(),
			"end_date": add_days(today(), 2),
			"status": "Published"
		}).insert()

		self.schedule = frappe.get_doc({
			"doctype": "Event Schedule",
			"event": self.event.name,
			"date": today(),
			"start_time": "09:00:00",
			"end_time": "17:00:00",
			"max_capacity": 2, # Small capacity for testing
			"enrolled_count": 0
		}).insert()

	def create_registration(self, user=None):
		return frappe.get_doc({
			"doctype": "Event Registration",
			"user": user or self.test_user.name,
			"event": self.event.name,
			"schedule": self.schedule.name,
			"status": "Draft"
		}).insert()

	def create_participant(self, registration_name, name, email):
		return frappe.get_doc({
			"doctype": "Event Participant",
			"registration": registration_name,
			"full_name": name,
			"email": email
		}).insert()

	def test_participant_limit(self):
		reg = self.create_registration()
		# Create 4 participants
		for i in range(4):
			self.create_participant(reg.name, f"P{i}", f"p{i}@test.com")
		
		# Should fail validation on submit (Max 3)
		self.assertRaises(frappe.ValidationError, reg.submit)

	def test_capacity_limit(self):
		# Reg 1 with 2 participants (Full capacity)
		reg1 = self.create_registration()
		self.create_participant(reg1.name, "P1", "p1@test.com")
		self.create_participant(reg1.name, "P2", "p2@test.com")
		reg1.submit() # Should update enrolled count to 2
		
		# Verify enrolled count
		self.schedule.reload()
		self.assertEqual(self.schedule.enrolled_count, 2)

		# Reg 2 for DIFFERENT USER
		another_user = frappe.get_doc({
			"doctype": "Event User",
			"email": "another@test.com",
			"full_name": "Another User"
		}).insert()

		reg2 = self.create_registration(user=another_user.name)
		self.create_participant(reg2.name, "P3", "p3@test.com")
		
		# Should fail submission because capacity is full
		self.assertRaises(frappe.ValidationError, reg2.submit)

	def test_unique_schedule_per_user(self):
		# Register first time
		reg1 = self.create_registration()
		self.create_participant(reg1.name, "P1", "p1@test.com")
		reg1.submit()

		# Try to register for SAME schedule again
		reg2 = frappe.get_doc({
			"doctype": "Event Registration",
			"user": self.test_user.name,
			"event": self.event.name,
			"schedule": self.schedule.name,
			"status": "Draft"
		})
		
		# Should fail save/validation due to uniqueness check
		self.assertRaises(frappe.ValidationError, reg2.insert)

	def test_check_in_flow(self):
		# Register 1 participant
		reg = self.create_registration()
		p1 = self.create_participant(reg.name, "CheckIn Guy", "check@test.com")
		reg.submit()
		
		# Get generated QR code
		p1.reload()
		qr_code = p1.qr_code_id
		self.assertTrue(qr_code)

		# Test Check-in Success
		res = check_in_participant(qr_code)
		self.assertEqual(res["status"], "success")

		# Verify Checked In status in DB
		p1.reload()
		self.assertEqual(p1.checked_in, 1)
		self.assertTrue(p1.check_in_time)

		# Test Double Check-in (Should Fail)
		self.assertRaises(frappe.ValidationError, check_in_participant, qr_code)

	def test_create_full_registration_multiple_schedules(self):
		from ticketed_event.ticketed_event.doctype.event_registration.event_registration import create_full_registration

		# Create another schedule for the same day
		schedule2 = frappe.get_doc({
			"doctype": "Event Schedule",
			"event": self.event.name,
			"date": today(),
			"start_time": "13:00:00",
			"end_time": "15:00:00", 
			"max_capacity": 5,
			"enrolled_count": 0
		}).insert()

		participants = [{"full_name": "P1", "email": "p1@test.com", "phone": "123", "instagram": "ig"}]
		user_data = {"email": "test_user@example.com", "full_name": "Test User", "phone": "123"}
		
		# Pass list of schedules
		schedules = [self.schedule.name, schedule2.name]
		
		# Mock verify_recaptcha to pass
		with patch("ticketed_event.api.verify_recaptcha", return_value=True):
			res = create_full_registration(
				event=self.event.name,
				schedules=schedules, 
				user_data=user_data,
				participants=participants,
				captcha_token="dummy-token"
			)

		self.assertTrue(res.get("registration"))
		self.assertEqual(len(res["registration"]), 2)
			
		# Verify both registrations exist
		for reg_name in res["registration"]:
			self.assertTrue(frappe.db.exists("Event Registration", reg_name))
			# Check if participants were created for each
			self.assertEqual(frappe.db.count("Event Participant", {"registration": reg_name}), 1)

	def test_recaptcha_verification_success(self):
		from ticketed_event.api import verify_recaptcha
		
		with patch("requests.post") as mock_post:
			mock_response = MagicMock()
			mock_response.json.return_value = {"success": True}
			mock_post.return_value = mock_response
			
			# Should not raise exception
			res = verify_recaptcha("valid-token")
			self.assertTrue(res)

	def test_recaptcha_verification_failure(self):
		from ticketed_event.api import verify_recaptcha
		
		with patch("requests.post") as mock_post:
			mock_response = MagicMock()
			mock_response.json.return_value = {"success": False}
			mock_post.return_value = mock_response
			
			# Should raise validation error
			self.assertRaises(frappe.ValidationError, verify_recaptcha, "invalid-token")

	def test_create_full_registration_captcha_integration(self):
		from ticketed_event.ticketed_event.doctype.event_registration.event_registration import create_full_registration
		
		participants = [{"full_name": "P1", "email": "p1@test.com", "phone": "123", "instagram": "ig"}]
		user_data = {"email": "test_user_new@example.com", "full_name": "New User", "phone": "123"}
		schedules = [self.schedule.name]
		
		with patch("ticketed_event.api.verify_recaptcha") as mock_verify:
			create_full_registration(
				event=self.event.name,
				schedules=schedules, 
				user_data=user_data,
				participants=participants,
				captcha_token="integration-token"
			)
			mock_verify.assert_called_once_with("integration-token")
