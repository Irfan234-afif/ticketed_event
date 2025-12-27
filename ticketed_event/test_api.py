import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, add_days
from ticketed_event.api import get_scanner_schedules

class TestTicketedEventAPI(FrappeTestCase):
	def setUp(self):
		frappe.db.delete("Event Schedule")
		frappe.db.delete("Ticketed Event")

		self.event = frappe.get_doc({
			"doctype": "Ticketed Event",
			"title": "API Test Event",
			"start_date": today(),
			"end_date": add_days(today(), 5),
			"status": "Published"
		}).insert()

	def test_get_scanner_schedules(self):
		# Create a schedule for TODAY
		schedule_today = frappe.get_doc({
			"doctype": "Event Schedule",
			"event": self.event.name,
			"date": today(),
			"start_time": "10:00:00",
			"end_time": "12:00:00",
			"max_capacity": 50,
			"enrolled_count": 0
		}).insert()

		# Create a schedule for TOMORROW (Should NOT appear)
		schedule_tomorrow = frappe.get_doc({
			"doctype": "Event Schedule",
			"event": self.event.name,
			"date": add_days(today(), 1),
			"start_time": "10:00:00",
			"end_time": "12:00:00",
			"max_capacity": 50,
			"enrolled_count": 0
		}).insert()

		# Call API
		schedules = get_scanner_schedules()
		
		# Verify results
		self.assertTrue(schedules)
		schedule_names = [s.name for s in schedules]
		self.assertIn(schedule_today.name, schedule_names)
		self.assertNotIn(schedule_tomorrow.name, schedule_names)
