# Copyright (c) 2013, Web Notes Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt


from __future__ import unicode_literals
import frappe
from frappe import session, msgprint
from frappe.utils import today

	

from erpnext.utilities.transaction_base import TransactionBase

class CustomerIssue(TransactionBase):
	
	def validate(self):
		if session['user'] != 'Guest' and not self.customer:
			msgprint("Please select Customer from whom issue is raised",
				raise_exception=True)
				
		if self.status=="Closed" and \
			frappe.db.get_value("Customer Issue", self.name, "status")!="Closed":
			self.resolution_date = today()
			self.resolved_by = frappe.session.user
	
	def on_cancel(self):
		lst = frappe.db.sql("""select t1.name 
			from `tabMaintenance Visit` t1, `tabMaintenance Visit Purpose` t2 
			where t2.parent = t1.name and t2.prevdoc_docname = %s and	t1.docstatus!=2""", 
			(self.name))
		if lst:
			lst1 = ','.join([x[0] for x in lst])
			msgprint("Maintenance Visit No. "+lst1+" already created against this customer issue. So can not be Cancelled")
			raise Exception
		else:
			frappe.db.set(self, 'status', 'Cancelled')

	def on_update(self):
		pass

@frappe.whitelist()
def make_maintenance_visit(source_name, target_doc=None):
	from frappe.model.mapper import get_mapped_doc
	
	visit = frappe.db.sql("""select t1.name 
		from `tabMaintenance Visit` t1, `tabMaintenance Visit Purpose` t2 
		where t2.parent=t1.name and t2.prevdoc_docname=%s 
		and t1.docstatus=1 and t1.completion_status='Fully Completed'""", source_name)
		
	if not visit:
		doclist = get_mapped_doc("Customer Issue", source_name, {
			"Customer Issue": {
				"doctype": "Maintenance Visit", 
				"field_map": {
					"complaint": "description", 
					"doctype": "prevdoc_doctype", 
					"name": "prevdoc_docname"
				}
			}
		}, target_doc)
	
		return doclist