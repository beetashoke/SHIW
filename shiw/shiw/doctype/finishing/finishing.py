# Copyright (c) 2025, beetashoke.chakraborty@clapgrow.com and contributors
# For license information, please see license.txt

# import frappe
# from frappe.model.document import Document
# import frappe
# from frappe.model.document import Document


# class Finishing(Document):
# 	pass


from frappe.model.document import Document
import frappe
from frappe import _


class Finishing(Document):
	def on_submit(self):
		"""
		Handle the on_submit event for the Finishing doctype.
		Creates and submits a Stock Entry of type 'Material Transfer' based on items in table_eiko.
		"""

		def flt(val):
			"""Safe float conversion."""
			try:
				return float(val)
			except:
				return 0.0

		try:
			if not frappe.has_permission("Stock Entry", "create"):
				frappe.throw(_("Insufficient permissions to create Stock Entry"), frappe.PermissionError)

			items = []

			for row in self.table_eiko:
				if not row.item_name or flt(row.finishing_quantity) <= 0:
					continue

				finishing_qty = flt(row.finishing_quantity)
				total_qty = flt(row.quantity)

				if finishing_qty > total_qty:
					frappe.throw(
						_(
							f"Finishing Quantity ({finishing_qty}) for item {row.item_name} "
							f"exceeds Total Quantity ({total_qty})."
						)
					)

				items.append(
					{
						"item_code": row.item_name,
						"qty": finishing_qty,
						"s_warehouse": "Fettling - SHIW",
						"t_warehouse": "Finishing - SHIW",
					}
				)

			if not items:
				frappe.msgprint(_("⚠️ No valid items to create Stock Entry."))
				return

			stock_entry = frappe.get_doc(
				{
					"doctype": "Stock Entry",
					"stock_entry_type": "Material Transfer",
					"items": items,
					"custom_date": self.date,
					"custom_shift_type": self.shift_type,
					"custom_process_type": "Finishing",
					"remarks": f"Auto-created from Finishing: {self.name}",
				}
			)

			stock_entry.insert(ignore_permissions=True)
			stock_entry.submit()

			# Link to Finishing
			self.db_set("linked_stock_entry", stock_entry.name)

			frappe.msgprint(_(f"✅ Stock Entry Created and Submitted: {stock_entry.name}"))

		except Exception as e:
			frappe.log_error(f"Error in on_submit for Finishing {self.name}: {e}\n{frappe.get_traceback()}")
			frappe.throw(_(f"Failed to create Stock Entry: {e}"))
