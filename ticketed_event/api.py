import frappe
import requests

@frappe.whitelist(allow_guest=True)
def get_registration_details(name):
    """
    Fetch registration details and participants for a given registration ID (name).
    Allowed for guests.
    """
    if not name:
        frappe.throw("Registration ID is required", frappe.DoesNotExistError)

    try:
        registration = frappe.get_doc("Event Registration", name)
    except frappe.DoesNotExistError:
        frappe.throw("Registration not found", frappe.DoesNotExistError)

    participants = frappe.get_all(
        "Event Participant",
        filters={"registration": name},
        fields=["name", "full_name", "email", "qr_code_id", "checked_in"]
    )

    schedule_details = None
    if registration.schedule:
        schedule_details = frappe.db.get_value(
            "Event Schedule", 
            registration.schedule, 
            ["title", "date", "start_time", "end_time"], 
            as_dict=True
        )

    return {
        "registration": registration,
        "participants": participants,
        "schedule": schedule_details
    }

@frappe.whitelist(allow_guest=True)
def get_published_events():
    """
    Fetch all published ticketed events.
    """
    return frappe.get_all(
        "Ticketed Event",
        filters={"status": "Published"},
        fields=["name", "title", "image", "start_date", "end_date"]
    )

@frappe.whitelist(allow_guest=True)
def get_event_details(name):
    """
    Fetch details for a specific event.
    """
    try:
        return frappe.get_doc("Ticketed Event", name)
    except frappe.DoesNotExistError:
        frappe.throw("Event not found", frappe.DoesNotExistError)

@frappe.whitelist(allow_guest=True)
def get_event_schedules(event):
    """
    Fetch available schedules for an event from today onwards.
    """
    from frappe.utils import today
    
    return frappe.get_all(
        "Event Schedule",
        filters={
            "event": event,
            "date": [">=", today()]
        },
        fields=["name", "date", "start_time", "end_time", "max_capacity", "enrolled_count", "title"],
        order_by="date asc, start_time asc"
    )

@frappe.whitelist(allow_guest=True)
def get_settings():
    """
    Fetch public settings.
    """
    return {
        "google_recaptcha_site_key": frappe.conf.get("google_recaptcha_site_key")
    }

def verify_recaptcha(token):
    """
    Verify Google reCAPTCHA token.
    """
    secret_key = frappe.conf.get("google_recaptcha_secret_key")
    if not secret_key:
        # If no secret key is configured, we might be in a dev environment
        # or it's intentionally disabled. In production, this should be mandatory.
        if frappe.conf.developer_mode:
            return True
        frappe.throw("reCAPTCHA secret key not configured")

    if not token:
        frappe.throw("CAPTCHA token is required")

    response = requests.post(
        "https://www.google.com/recaptcha/api/siteverify",
        data={
            "secret": secret_key,
            "response": token,
            "remoteip": frappe.local.request_ip
        }
    )
    
    result = response.json()
    if not result.get("success"):
        frappe.throw("CAPTCHA verification failed. Please try again.")
    
    return True
