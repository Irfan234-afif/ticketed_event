
import frappe

def execute():
    discrepancies = []
    
    schedules = frappe.get_all("Event Schedule", fields=["name", "title", "enrolled_count"])
    
    print(f"{'Schedule':<40} | {'Stored':<10} | {'Actual':<10} | {'Diff':<10}")
    print("-" * 80)
    
    for s in schedules:
        # Calculate actual count
        # Participants that belong to SUBMITTED registrations that include this schedule
        
        actual_count = frappe.db.sql("""
            SELECT count(ep.name)
            FROM `tabEvent Participant` ep
            JOIN `tabEvent Registration` er ON ep.registration = er.name
            JOIN `tabEvent Registration Schedule` ers ON ers.parent = er.name
            WHERE ers.schedule = %s
            AND er.docstatus = 1
        """, (s.name))[0][0]
        
        if s.enrolled_count != actual_count:
            discrepancies.append({
                "name": s.name,
                "title": s.title,
                "stored": s.enrolled_count,
                "actual": actual_count
            })
            print(f"{s.title[:40]:<40} | {s.enrolled_count:<10} | {actual_count:<10} | {s.enrolled_count - actual_count:<10}")

    if not discrepancies:
        print("\nNo discrepancies found!")
    else:
        print(f"\nFound {len(discrepancies)} schedules with discrepancies.")

execute()
