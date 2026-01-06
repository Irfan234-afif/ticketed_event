
import frappe

def get_context(context):
	if frappe.form_dict.name:
		doc = frappe.get_doc("Event Participant", frappe.form_dict.name)
		email_context = doc.get_email_context()
		context.update(email_context)
