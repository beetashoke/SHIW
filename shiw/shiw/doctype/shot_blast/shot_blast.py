# Copyright (c) 2025, beetashoke.chakraborty@clapgrow.com and contributors
# For license information, please see license.txt

# import frappe
# from frappe.model.document import Document


# class ShotBlast(Document):
# 	pass


# import frappe


# def flt(val):
# 	"""Convert value to float, return 0.0 if conversion fails."""
# 	try:
# 		return float(val)
# 	except:
# 		return 0.0


# def on_submit(doc, method):
# 	"""Handle after_submit event for Shot Blast doctype to create and submit a Stock Entry."""
# 	items = []

# 	# Iterate through table_short child table
# 	for row in doc.table_short:
# 		if not row.item_name:
# 			continue

# 		s_warehouse = "Shake Out - SHIW"
# 		short_qty = flt(row.short_blast_quantity)
# 		shakeout_qty = flt(row.shakeout_quantity)

# 		# Validate quantities
# 		if short_qty > 0:
# 			if short_qty > shakeout_qty:
# 				frappe.throw(
# 					f"Error: Shot Blast Quantity ({short_qty}) for item {row.item_name} exceeds Shakeout Quantity ({shakeout_qty})."
# 				)

# 			items.append(
# 				{
# 					"item_code": row.item_name,
# 					"qty": short_qty,
# 					"s_warehouse": s_warehouse,
# 					"t_warehouseresenter": "Short Blast - SHIW",
# 					"custom_pouring_id": row.pouring_id,
# 				}
# 			)

# 	# Create Stock Entry if valid items exist
# 	if items:
# 		try:
# 			se = frappe.new_doc("Stock Entry")
# 			se.stock_entry_type = "Material Transfer"
# 			se.custom_date = doc.date
# 			se.custom_shift_type = doc.shift_type
# 			se.custom_process_type = "Short Blast"
# 			se.remarks = f"Auto-created from Shot Blast: {doc.name}"

# 			for item in items:
# 				se.append("items", item)

# 			se.insert(ignore_permissions=True)
# 			se.submit()

# 			# Link Stock Entry to Shot Blast document
# 			frappe.db.set_value(doc.doctype, doc.name, "linked_stock_entry", se.name)

# 			# Success Message
# 			frappe.msgprint(f"✅ Stock Entry Created and Submitted: {se.name}")
# 		except Exception as e:
# 			frappe.log_error(
# 				f"Failed to create or submit Stock Entry for Shot Blast {doc.name}: {e!s}\n{frappe.get_traceback()}"
# 			)
# 			frappe.throw(f"Failed to create or submit Stock Entry: {e!s}")
# 	else:
# 		frappe.msgprint("⚠️ No valid quantities to create Stock Entry.")


# apps/shiw/shiw/doctype/shot_blast/shot_blast.py
import frappe
from frappe import _
from frappe.model.document import Document


class ShotBlast(Document):
	def on_submit(self):
		"""Handle after_submit event for Shot Blast doctype to create and submit a Stock Entry."""

		def flt(val):
			"""Convert value to float, return 0.0 if conversion fails."""
			try:
				return float(val)
			except:
				return 0.0

		items = []

		# Iterate through table_short child table
		for row in self.table_short:
			if not row.item_name:
				continue

			s_warehouse = "Shake Out - SHIW"
			short_qty = flt(row.short_blast_quantity)
			shakeout_qty = flt(row.shakeout_quantity)

			# Validate quantities
			if short_qty > 0:
				if short_qty > shakeout_qty:
					frappe.throw(
						_(
							f"Shot Blast Quantity ({short_qty}) for item {row.item_name} exceeds Shakeout Quantity ({shakeout_qty})."
						)
					)

				items.append(
					{
						"item_code": row.item_name,
						"qty": short_qty,
						"s_warehouse": s_warehouse,
						"t_warehouse": "Short Blast - SHIW",  # Fixed typo: 't_warehouseresenter' to 't_warehouse'
						"custom_pouring_id": row.pouring_id,
					}
				)

		# Create Stock Entry if valid items exist
		if items:
			try:
				se = frappe.new_doc("Stock Entry")
				se.stock_entry_type = "Material Transfer"
				se.custom_date = self.date
				se.custom_shift_type = self.shift_type
				se.custom_process_type = "Short Blast"
				se.remarks = f"Auto-created from Shot Blast: {self.name}"

				for item in items:
					se.append("items", item)

				se.insert(ignore_permissions=True)
				se.submit()

				# Link Stock Entry to Shot Blast document
				self.db_set("linked_stock_entry", se.name)

				# Success Message
				frappe.msgprint(_(f"✅ Stock Entry Created and Submitted: {se.name}"))
			except Exception as e:
				frappe.log_error(
					f"Failed to create or submit Stock Entry for Shot Blast {self.name}: {e!s}\n{frappe.get_traceback()}"
				)
				frappe.throw(_(f"Failed to create or submit Stock Entry: {e!s}"))
		else:
			frappe.msgprint(_("⚠️ No valid quantities to create Stock Entry."))
