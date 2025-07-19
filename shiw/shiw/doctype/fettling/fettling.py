# Copyright (c) 2025, beetashoke.chakraborty@clapgrow.com and contributors
# For license information, please see license.txt

# import frappe
# from frappe.model.document import Document


# class Fettling(Document):
# 	pass

import frappe
from frappe import _
from frappe.model.document import Document


class Fettling(Document):
	def on_submit(self):
		"""
		On Submit: Create a Material Transfer Stock Entry based on items in table_tjba.
		"""

		def flt(val):
			try:
				return float(val)
			except:
				return 0.0

		items = []

		for row in self.table_tjba:
			if row.item_name and flt(row.fettling_quantity) > 0:
				fettling_qty = flt(row.fettling_quantity)
				available_qty = flt(row.available_qty)

				if fettling_qty > available_qty:
					frappe.throw(
						_(
							f"❌ Fettling Quantity ({fettling_qty}) for item {row.item_name} exceeds Available Quantity ({available_qty})."
						)
					)

				items.append(
					{
						"item_code": row.item_name,
						"qty": fettling_qty,
						"s_warehouse": "Short Blast - SHIW",
						"t_warehouse": "Fettling - SHIW",
					}
				)

		if not items:
			frappe.msgprint(_("⚠️ No valid items to create Stock Entry."))
			return

		try:
			stock_entry = frappe.get_doc(
				{
					"doctype": "Stock Entry",
					"stock_entry_type": "Material Transfer",
					"items": items,
					"custom_date": self.get("date"),
					"custom_shift_type": self.get("shift_type"),
					"custom_process_type": "Fettling",
					"remarks": f"Auto-created from Fettling: {self.name}",
				}
			)

			stock_entry.insert(ignore_permissions=True)
			stock_entry.submit()

			# 🔗 Link Stock Entry back to Fettling document
			self.db_set("linked_stock_entry", stock_entry.name)

			frappe.msgprint(_(f"✅ Stock Entry Created and Submitted: {stock_entry.name}"))

		except Exception as e:
			frappe.log_error(frappe.get_traceback(), f"Fettling Stock Entry Error - {self.name}")
			frappe.throw(_(f"❌ Failed to create or submit Stock Entry: {str(e)}"))
