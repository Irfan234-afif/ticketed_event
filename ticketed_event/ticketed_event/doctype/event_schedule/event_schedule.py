import json
from datetime import datetime, timedelta
import frappe
from frappe.model.document import Document

class EventSchedule(Document):
	pass

@frappe.whitelist()
def get_events(start, end, filters=None):
	"""
	Returns events for the calendar view.
	Combines 'date' and 'start_time'/'end_time' into single datetime strings.
	"""
	from frappe.desk.reportview import get_filters_cond

	if isinstance(filters, str):
		filters = json.loads(filters)

	filter_cond = get_filters_cond("Event Schedule", filters, [])

	events = frappe.db.sql(f"""
		SELECT 
			name, event, date, start_time, end_time
		FROM 
			`tabEvent Schedule`
		WHERE 
			date >= %(start)s AND date <= %(end)s
			{filter_cond}
	""", {
		"start": start,
		"end": end
	}, as_dict=True)

	for ev in events:
		# Format the combined datetime strings
		# start_time and end_time are usually timedelta or strings in Frappe
		
		date_str = str(ev.date)
		
		# Helper to combine date and time
		def combine_date_time(d_str, t):
			if not t:
				return None
			# if t is timedelta (typical for Time fields)
			if isinstance(t, timedelta):
				# It might be more than 24h if not careful, but usually it's time of day
				seconds = t.total_seconds()
				hours = int(seconds // 3600)
				minutes = int((seconds % 3600) // 60)
				return f"{d_str} {hours:02d}:{minutes:02d}:00"
			return f"{d_str} {t}"

		ev.start_time = combine_date_time(date_str, ev.start_time)
		ev.end_time = combine_date_time(date_str, ev.end_time)
		ev.all_day = 0
		ev.title = ev.event

	return events
