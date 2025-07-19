# Copyright (c) 2025, beetashoke.chakraborty@clapgrow.com and contributors
# For license information, please see license.txt

# import frappe
# from frappe.model.document import Document


# class FinalInspection(Document):
# 	pass


import frappe
from frappe import _
from frappe.model.document import Document


class FinalInspection(Document):
	def on_submit(self):
		"""
		On Submit: Create a Material Transfer Stock Entry based on items in table_jikz.
		Validates that GN Quantity does not exceed Finished Quantity.
		"""

		def flt(val):
			try:
				return float(val)
			except:
				return 0.0

		items = []

		for row in self.table_jikz:
			if row.item_name and flt(row.gn_qty) > 0:
				gn_qty = flt(row.gn_qty)
				finished_qty = flt(row.finished_qty)

				if gn_qty > finished_qty:
					frappe.throw(
						_(
							f"❌ Gauging Quantity ({gn_qty}) for item {row.item_name} exceeds Finished Quantity ({finished_qty})."
						)
					)

				items.append(
					{
						"item_code": row.item_name,
						"qty": gn_qty,
						"s_warehouse": "Finishing - SHIW",
						"t_warehouse": "Finished Good - SHIW",
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
					"custom_date": self.date,
					"custom_shift_type": self.shift_type,
					"custom_process_type": "Gauging - Inspection",
					"remarks": f"Auto-created from Gauging - Inspection: {self.name}",
				}
			)

			stock_entry.insert(ignore_permissions=True)
			stock_entry.submit()

			self.db_set("linked_stock_entry", stock_entry.name)

			frappe.msgprint(_(f"✅ Stock Entry Created and Submitted: {stock_entry.name}"))

		except Exception as e:
			frappe.log_error(frappe.get_traceback(), f"Final Inspection Stock Entry Error - {self.name}")
			frappe.throw(_(f"❌ Failed to create or submit Stock Entry: {e!s}"))
