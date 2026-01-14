
import frappe

def execute():
    # 1. Reset all to 0 first (optional, but safer to start clean if we want to catch 0s)
    # OR better: Calculate correct counts for all, then update.
    
    # Get all schedule names
    schedules = frappe.get_all("Event Schedule", pluck="name")
    
    print(f"Checking {len(schedules)} schedules...")
    
    updated_count = 0
    
    for schedule_name in schedules:
        actual_count = frappe.db.sql("""
            SELECT COUNT(ep.name)
            FROM `tabEvent Participant` ep
            JOIN `tabEvent Registration` er ON ep.registration = er.name
            JOIN `tabEvent Registration Schedule` ers ON ers.parent = er.name
            WHERE ers.schedule = %s
            AND er.docstatus = 1
        """, (schedule_name))[0][0]
        
        # Get current
        current_count = frappe.db.get_value("Event Schedule", schedule_name, "enrolled_count")
        
        if current_count != actual_count:
            print(f"Fixing {schedule_name}: {current_count} -> {actual_count}")
            frappe.db.set_value("Event Schedule", schedule_name, "enrolled_count", actual_count)
            updated_count += 1
            
    print(f"Repaired {updated_count} schedules.")
    frappe.db.commit()

execute()
