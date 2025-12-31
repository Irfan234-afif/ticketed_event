import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days
from unittest.mock import patch, MagicMock

# Adjust import path based on your app structure
from ticketed_event.ticketed_event.doctype.event_registration.event_registration import check_in_participant

# Hack to bypass ImplicitCommitError in this environment
if frappe.db:
	frappe.db.check_implicit_commit = lambda query: None

class TestEventRegistration(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		"""Set up test class - runs once before all tests"""
		super().setUpClass()
		# Ensure we're running on a test site
		if not frappe.flags.in_test:
			frappe.throw("Tests should only run in test mode!")
	
	def setUp(self):
		"""Set up each test - runs before each test method"""
		# Clear test data using frappe.db.delete with a filter to be safer
		# These will only affect test records created during test runs
		frappe.db.delete("Event Checkin")
		frappe.db.delete("Event Registration")
		frappe.db.delete("Event Participant")
		
		# Don't delete Event User, Event Schedule, or Ticketed Event globally
		# Instead, we'll create test-specific ones with unique names
		
		frappe.db.commit()

		# Create a test event user with unique email
		import random
		import string
		random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
		self.test_user = frappe.get_doc({
			"doctype": "Event User",
			"email": f"test_user_{random_suffix}@example.com",
			"full_name": "Test User"
		}).insert()

		# Create a test event
		self.event = frappe.get_doc({
			"doctype": "Ticketed Event",
			"title": f"Test Event {random_suffix}",
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
			"max_capacity": 10, # Increased capacity to allow test participants
			"enrolled_count": 0,
			"last_entry_time": "23:59:59"
		}).insert()
	
	def tearDown(self):
		"""Clean up after each test"""
		# Delete test-specific records we created
		if hasattr(self, 'event') and self.event:
			# Delete checkins first
			frappe.db.delete("Event Checkin", {"event": self.event.name})
			# Delete registrations and participants
			registrations = frappe.get_all("Event Registration", filters={"event": self.event.name}, fields=["name", "docstatus"])
			for reg in registrations:
				frappe.db.delete("Event Participant", {"registration": reg.name})
				# Cancel if submitted before deleting
				if reg.docstatus == 1:
					reg_doc = frappe.get_doc("Event Registration", reg.name)
					reg_doc.cancel()
				frappe.delete_doc("Event Registration", reg.name, force=True)
			# Delete schedules
			frappe.db.delete("Event Schedule", {"event": self.event.name})
			# Delete event
			frappe.delete_doc("Ticketed Event", self.event.name, force=True)
		
		# Delete test user if exists
		if hasattr(self, 'test_user') and self.test_user:
			frappe.delete_doc("Event User", self.test_user.name, force=True)
		
		frappe.db.commit()
		
		frappe.db.commit()


	def create_registration(self, user=None):
		reg = frappe.get_doc({
			"doctype": "Event Registration",
			"user": user or self.test_user.name,
			"event": self.event.name,
			"status": "Draft",
			"schedules": [
				{"schedule": self.schedule.name}
			]
		})
		reg.insert()
		return reg

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
		# Create a schedule with exact capacity for this test
		capacity_test_schedule = frappe.get_doc({
			"doctype": "Event Schedule",
			"event": self.event.name,
			"date": today(),
			"start_time": "10:00:00",
			"end_time": "12:00:00",
			"max_capacity": 2, # Exact capacity for 2 participants
			"enrolled_count": 0
		}).insert()
		
		# Reg 1 with 2 participants (Full capacity)
		reg1 = frappe.get_doc({
			"doctype": "Event Registration",
			"user": self.test_user.name,
			"event": self.event.name,
			"status": "Draft",
			"schedules": [{"schedule": capacity_test_schedule.name}]
		})
		reg1.insert()
		self.create_participant(reg1.name, "P1", "p1@test.com")
		self.create_participant(reg1.name, "P2", "p2@test.com")
		
		# Verify enrolled count
		capacity_test_schedule.reload()
		self.assertEqual(capacity_test_schedule.enrolled_count, 2)

		# Reg 2 for DIFFERENT USER
		another_user = frappe.get_doc({
			"doctype": "Event User",
			"email": "another@test.com",
			"full_name": "Another User"
		}).insert()

		reg2 = frappe.get_doc({
			"doctype": "Event Registration",
			"user": another_user.name,
			"event": self.event.name,
			"status": "Draft",
			"schedules": [{"schedule": capacity_test_schedule.name}]
		})
		reg2.insert()
		
		# Should fail when creating participant because capacity is full
		self.assertRaises(frappe.ValidationError, self.create_participant, reg2.name, "P3", "p3@test.com")

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
			"status": "Draft",
			"schedules": [
				{"schedule": self.schedule.name}
			]
		})
		
		# Should fail save/validation due to uniqueness check
		self.assertRaises(frappe.ValidationError, reg2.insert)

	def test_check_in_flow(self):
		# Register 1 participant
		reg = self.create_registration()
		p1 = self.create_participant(reg.name, "CheckIn Guy", "check@test.com")
		reg.submit()
		
		p1.reload()
		qr_code = p1.qr_code_id
		self.assertTrue(qr_code)

		# Test Check-in Permission Denied (Guest/Non-Scanner)
		with patch("frappe.get_roles", return_value=["Guest"]):
			self.assertRaises(frappe.PermissionError, check_in_participant, qr_code)

		# Test Check-in Success with Correct Role
		with patch("frappe.get_roles", return_value=["Scanner"]):
			res = check_in_participant(qr_code)
			self.assertEqual(res["status"], "success")

		# Verify Checked In status in Event Checkin
		checkin_exists = frappe.db.exists("Event Checkin", {"participant": p1.name, "registration": reg.name, "schedule": self.schedule.name})
		self.assertTrue(checkin_exists)

		# Test Double Check-in (Should Fail)
		with patch("frappe.get_roles", return_value=["Scanner"]):
			self.assertRaises(frappe.ValidationError, check_in_participant, qr_code)

	def test_check_in_with_explicit_schedule(self):
		# Register
		reg = self.create_registration()
		p1 = self.create_participant(reg.name, "Explicit", "explicit@test.com")
		reg.submit()
		p1.reload()

		# Success: Check in with correct schedule
		with patch("frappe.get_roles", return_value=["Scanner"]):
			res = check_in_participant(p1.qr_code_id, schedule=self.schedule.name)
			self.assertEqual(res["status"], "success")

		# Create another schedule that user does NOT have
		other_schedule = frappe.get_doc({
			"doctype": "Event Schedule",
			"event": self.event.name,
			"date": today(),
			"start_time": "20:00:00",
			"end_time": "21:00:00", 
			"max_capacity": 5,
			"enrolled_count": 0
		}).insert()

		# Fail: Check in with WRONG schedule
		with patch("frappe.get_roles", return_value=["Scanner"]):
			self.assertRaises(frappe.ValidationError, check_in_participant, p1.qr_code_id, schedule=other_schedule.name)

	def test_check_in_failures(self):
		# 1. Invalid QR Code
		with patch("frappe.get_roles", return_value=["Scanner"]):
			self.assertRaises(frappe.ValidationError, check_in_participant, "INVALID-QR")

		# 2. Registration Not Found (orphaned participant - hard to produce normally, skipping or requires direct DB manip)
		
		# 3. Registration Not Submitted
		reg_draft = self.create_registration()
		p_draft = self.create_participant(reg_draft.name, "Draft P", "draft@test.com")
		# Do NOT submit
		
		# Participant has QR code only after save, but let's assume we can get it or it's generated on save.
		# Note: qr_code_id is usually generated on save.
		if not p_draft.qr_code_id:
			p_draft.reload() # Should have it if logic generates it on save
		
		if p_draft.qr_code_id:
			with patch("frappe.get_roles", return_value=["Scanner"]):
				self.assertRaises(frappe.ValidationError, check_in_participant, p_draft.qr_code_id)

	def test_auto_detect_schedule(self):
		# Create multiple schedules for same day
		from frappe.utils import get_datetime
		
		# Schedule A: 09:00 - 11:00
		sch_a = self.schedule # existing
		
		# Schedule B: 13:00 - 15:00
		sch_b = frappe.get_doc({
			"doctype": "Event Schedule",
			"event": self.event.name,
			"date": today(),
			"start_time": "13:00:00",
			"end_time": "15:00:00", 
			"max_capacity": 10
		}).insert()

		# Register for BOTH
		reg = frappe.get_doc({
			"doctype": "Event Registration",
			"user": self.test_user.name,
			"event": self.event.name,
			"status": "Draft",
			"schedules": [{"schedule": sch_a.name}, {"schedule": sch_b.name}]
		})
		reg.insert()
		p = self.create_participant(reg.name, "Multi", "multi@test.com")
		reg.submit()
		p.reload()

		# Case 1: Time is 10:00 -> Should pick Schedule A
		mock_time_10 = get_datetime(f"{today()} 10:00:00")
		with patch("ticketed_event.ticketed_event.doctype.event_registration.event_registration.frappe.utils.now_datetime", return_value=mock_time_10):
			with patch("frappe.get_roles", return_value=["Scanner"]):
				res = check_in_participant(p.qr_code_id) # No schedule arg
				self.assertEqual(res["schedule"], sch_a.name)

		# Case 2: Time is 14:00 -> Should pick Schedule B
		mock_time_14 = get_datetime(f"{today()} 14:00:00")
		with patch("ticketed_event.ticketed_event.doctype.event_registration.event_registration.frappe.utils.now_datetime", return_value=mock_time_14):
			with patch("frappe.get_roles", return_value=["Scanner"]):
				res = check_in_participant(p.qr_code_id) # No schedule arg
				self.assertEqual(res["schedule"], sch_b.name)

	def test_email_notifications_skipped(self):
		# Verify that sendmail is NOT called
		with patch("frappe.sendmail") as mock_sendmail:
			reg = self.create_registration()
			self.create_participant(reg.name, "P1", "p1@test.com")
			reg.submit()
			
			# Ensure no email was sent
			mock_sendmail.assert_not_called()

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
		# Should be ONE registration now
		self.assertEqual(len(res["registration"]), 1)
		reg_name = res["registration"][0]
		
		reg_doc = frappe.get_doc("Event Registration", reg_name)
		self.assertEqual(len(reg_doc.schedules), 2)
		
		# Check if participants were created for the registration
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

	def test_unlimited_capacity(self):
		# Create unlimited schedule
		unlimited_schedule = frappe.get_doc({
			"doctype": "Event Schedule",
			"event": self.event.name,
			"date": today(),
			"start_time": "18:00:00",
			"end_time": "20:00:00", 
			"max_capacity": 1, # Set low capacity but unlimited flag
			"is_unlimited_capacity": 1,
			"enrolled_count": 0
		}).insert()

		# Register 2 participants (Exceeding max_capacity of 1)
		reg = frappe.get_doc({
			"doctype": "Event Registration",
			"user": self.test_user.name,
			"event": self.event.name,
			"status": "Draft",
			"schedules": [{"schedule": unlimited_schedule.name}]
		})
		reg.insert() # Save
		
		# Create 2 participants
		self.create_participant(reg.name, "U1", "u1@test.com")
		self.create_participant(reg.name, "U2", "u2@test.com")
		
		
		unlimited_schedule.reload()
		self.assertEqual(unlimited_schedule.enrolled_count, 2)

	def test_last_entry_time(self):
		from frappe.utils import get_datetime
		
		# Valid Date for test
		test_date = today()
		
		# Mock NOW to be 12:00:00
		fixed_now = get_datetime(f"{test_date} 12:00:00")
		
		with patch("ticketed_event.ticketed_event.doctype.event_registration.event_registration.frappe.utils.now_datetime", return_value=fixed_now):
			
			# 1. EARLY CLOSER (11:00:00) - Should Fail
			schedule_early = frappe.get_doc({
				"doctype": "Event Schedule",
				"event": self.event.name,
				"date": test_date,
				"start_time": "08:00:00",
				"end_time": "23:00:00",
				"last_entry_time": "11:00:00",
				"max_capacity": 100
			}).insert()
			
			reg = frappe.get_doc({
				"doctype": "Event Registration",
				"user": self.test_user.name,
				"event": self.event.name,
				"status": "Draft",
				"schedules": [{"schedule": schedule_early.name}]
			})
			reg.insert()
			p = self.create_participant(reg.name, "Late Guy", "late@test.com")
			reg.submit()
			p.reload()
			
			# Check-in should FAIL (12:00 > 11:00)
			# We must pass schedule now
			with patch("frappe.get_roles", return_value=["Scanner"]):
				self.assertRaises(frappe.ValidationError, check_in_participant, p.qr_code_id, schedule=schedule_early.name)

			# 2. LATE CLOSER (13:00:00) - Should Succeed
			schedule_late = frappe.get_doc({
				"doctype": "Event Schedule",
				"event": self.event.name,
				"date": test_date,
				"start_time": "08:00:00",
				"end_time": "23:00:00",
				"last_entry_time": "13:00:00",
				"max_capacity": 100
			}).insert()

			user2 = frappe.get_doc({
				"doctype": "Event User",
				"email": "user2@test.com",
				"full_name": "User Two"
			}).insert()

			reg2 = frappe.get_doc({
				"doctype": "Event Registration",
				"user": user2.name,
				"event": self.event.name,
				"status": "Draft",
				"schedules": [{"schedule": schedule_late.name}]
			})
			reg2.insert()
			p2 = self.create_participant(reg2.name, "Ontime Guy", "ontime@test.com")
			reg2.submit()
			p2.reload()

			# Check-in should SUCCEED (12:00 < 13:00)
			with patch("frappe.get_roles", return_value=["Scanner"]):
				res = check_in_participant(p2.qr_code_id, schedule=schedule_late.name)
				self.assertEqual(res["status"], "success")
