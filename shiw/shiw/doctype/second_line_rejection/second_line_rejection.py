# Copyright (c) 2025, beetashoke.chakraborty@clapgrow.com and contributors
# For license information, please see license.txt

# import frappe
# from frappe.model.document import Document


# class SecondLineRejection(Document):
# 	pass


import frappe
from frappe import _
from frappe.model.document import Document


class SecondLineRejection(Document):
	def on_submit(self):
		"""
		On Submit: Create a Material Transfer Stock Entry based on rejected items in table_scpn.
		"""

		def flt(val):
			try:
				return float(val)
			except:
				return 0.0

		items = []

		for row in self.table_scpn:
			if row.item_name and flt(row.rejected_qty) > 0:
				rejected_qty = flt(row.rejected_qty)
				available_qty = flt(row.available_quantity)

				if rejected_qty > available_qty:
					frappe.throw(
						_(
							f"❌ Rejected Quantity ({rejected_qty}) for item {row.item_name} exceeds Available Quantity ({available_qty})."
						)
					)

				# Determine source warehouse based on rejection stage
				if row.rejection_stage == "Fettling":
					source_warehouse = "Fettling - SHIW"
				elif row.rejection_stage == "Finishing":
					source_warehouse = "Finishing - SHIW"
				else:
					frappe.msgprint(_(f"⚠️ Unknown rejection stage: {row.rejection_stage}"))
					continue

				items.append(
					{
						"item_code": row.item_name,
						"qty": rejected_qty,
						"s_warehouse": source_warehouse,
						"t_warehouse": "Second Line Rejected - SHIW",
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
					"custom_process_type": "Second Line Rejection",
					"remarks": f"Auto-created from Second Line Rejection: {self.name}",
				}
			)

			stock_entry.insert(ignore_permissions=True)
			stock_entry.submit()

			# 🔗 Link Stock Entry back to Second Line Rejection document
			self.db_set("linked_stock_entry", stock_entry.name)

			frappe.msgprint(_(f"✅ Stock Entry Created and Submitted: {stock_entry.name}"))

		except Exception as e:
			frappe.log_error(frappe.get_traceback(), f"Second Line Rejection Error - {self.name}")
			frappe.throw(_(f"❌ Failed to create or submit Stock Entry: {e!s}"))
