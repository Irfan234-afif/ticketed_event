frappe.views.calendar["Event Schedule"] = {
	field_map: {
		start: "start_time",
		end: "end_time",
		id: "name",
		allDay: "all_day",
		title: "event",
		status: "status",
	},
	get_events_method: "ticketed_event.ticketed_event.doctype.event_schedule.event_schedule.get_events",
};
