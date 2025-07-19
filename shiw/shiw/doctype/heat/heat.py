# Copyright (c) 2025, beetashoke.chakraborty@clapgrow.com and contributors
# For license information, please see license.txt

# import frappe
# from frappe.model.document import Document


# class Heat(Document):
# 	pass


import frappe
from frappe.model.document import Document


class Heat(Document):
	def on_submit(self):
		"""
		On Submit: Create a Material Issue Stock Entry for items in charge_mix_component_item
		where 'is_stock_entry' is checked.
		"""

		company_name = "Shree Hanuman Iron Works"
		warehouse_label = "Estimated Foundry Return"

		# 1. Resolve source warehouse
		SOURCE_WH = frappe.db.get_value(
			"Warehouse", {"warehouse_name": warehouse_label, "company": company_name}, "name"
		)

		if not SOURCE_WH:
			frappe.throw(f"❌ Could not find warehouse '{warehouse_label}' for company '{company_name}'.")

		# 2. Float utility
		def flt(val):
			try:
				return float(val) if val not in [None, ""] else 0.0
			except Exception:
				return 0.0

		# 3. Build stock entry items
		items = []

		for row in self.charge_mix_component_item:
			if row.is_stock_entry:
				qty = flt(row.weight)

				if qty <= 0:
					frappe.throw(f"Row {row.idx}: Weight must be > 0.")

				item_code = row.item
				if not frappe.db.exists("Item", item_code):
					frappe.throw(f"Row {row.idx}: Item '{item_code}' not found.")

				items.append(
					{
						"item_code": item_code,
						"qty": qty,
						"s_warehouse": SOURCE_WH,
					}
				)

		# 4. Create and submit Stock Entry if items exist
		if items:
			try:
				stock_entry = frappe.get_doc(
					{
						"doctype": "Stock Entry",
						"stock_entry_type": "Material Issue",
						"items": items,
						"remarks": f"Auto Material Issue from Heat {self.name}",
					}
				)

				stock_entry.insert(ignore_permissions=True)
				stock_entry.submit()

				# 5. Link back to Heat
				self.db_set("linked_stock_entry", stock_entry.name)
				frappe.msgprint(f"✅ Stock Entry Created: {stock_entry.name}")

			except Exception as e:
				frappe.log_error(frappe.get_traceback(), f"Heat Stock Entry Error - {self.name}")
				frappe.throw(f"❌ Failed to create Stock Entry: {e!s}")

		else:
			frappe.msgprint("✅ No rows marked for stock entry – skipping creation.")
