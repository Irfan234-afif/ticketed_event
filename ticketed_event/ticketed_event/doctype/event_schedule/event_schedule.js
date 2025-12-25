frappe.ui.form.on("Event Schedule", {
	onload: function(frm) {
		if (frm.is_new()) {
			// Calendar view sets start_time and end_time directly on the doc as datetime strings
			// But the DocType expects Date for 'date' and Time for 'start_time'/'end_time'
			// So we need to parse the datetime string in 'start_time' (which is technically invalid for a Time field)
			// and distribute it to the correct fields.
			
			const start_val = frm.doc.start_time;
			const end_val = frm.doc.end_time;

			// Check if start_time looks like a full datetime string
			if (start_val && (start_val.includes(" ") || start_val.includes("T"))) {
				
				const process_datetime = (dt_val) => {
					if (!dt_val) return { date: null, time: null };

					// Issue: Calendar JS converts "Browser Time" to "System Time" but drifts if Browser TZ != User TZ
					// Example: User picks 16:00. Browser (+7). User (+5.5). Result 17:30 (+1.5h).
					// Fix: We need to subtract the drift: (BrowserOffset - UserOffset)
					
					const user_tz = frappe.boot.user.time_zone || frappe.boot.sysdefaults.time_zone;
					const user_offset = moment.tz(user_tz).utcOffset(); // e.g. +330
					const browser_offset = moment().utcOffset(); // e.g. +420
					
					// Drift = Browser - User
					// We want to subtract Drift to cancel out the calendar's conversion
					// Correction = -(Browser - User) = User - Browser
					const correction_minutes = user_offset - browser_offset;

					// Create moment object, treating raw string as local, then add correction
					let dt_moment = moment(dt_val).add(correction_minutes, 'minutes');

					if (!dt_moment.isValid()) {
						return { date: null, time: null };
					}

					return { 
						date: dt_moment.format("YYYY-MM-DD"), 
						time: dt_moment.format("HH:mm:ss")
					};
				};

				const start = process_datetime(start_val);
				const end = process_datetime(end_val);

				if (start.date) {
					frm.set_value("date", start.date);
					frm.set_value("start_time", start.time);
				}
				
				if (end.time) {
					frm.set_value("end_time", end.time);
				}
			}
		}
	},
});
