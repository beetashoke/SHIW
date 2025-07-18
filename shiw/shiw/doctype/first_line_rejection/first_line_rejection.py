# Copyright (c) 2025, beetashoke.chakraborty@clapgrow.com and contributors
# For license information, please see license.txt

# import frappe
# from frappe.model.document import Document


# class FirstLineRejection(Document):
# 	pass


# import frappe
# from frappe import _


# def on_submit(doc, method=None):
# 	"""
# 	On Submit hook for First Line Rejection doctype.
# 	Creates and submits a Stock Entry for valid items in the table_yncx child table.
# 	"""

# 	# Custom float conversion to avoid import
# 	def flt(val):
# 		try:
# 			return float(val)
# 		except:  # noqa: E722
# 			return 0.0

# 	items = []

# 	# Iterate through child table (table_yncx)
# 	for row in doc.table_yncx:
# 		if not row.item_name or flt(row.quantity_rejected) <= 0:
# 			continue

# 		rejected_qty = flt(row.quantity_rejected)
# 		total_qty = flt(row.quantity)

# 		# Validate rejected quantity
# 		if rejected_qty > total_qty:
# 			frappe.throw(
# 				_(
# 					f"Rejected Quantity ({rejected_qty}) for item {row.item_name} exceeds Total Quantity ({total_qty})."
# 				)
# 			)

# 		# Determine source warehouse based on rejection stage
# 		stage = row.rejection_stage or ""
# 		s_warehouse = ""

# 		if stage == "Pouring":
# 			s_warehouse = "Pouring - SHIW"
# 		elif stage == "Shake Out":
# 			s_warehouse = "Shake Out - SHIW"
# 		elif stage == "Shot Blast":
# 			s_warehouse = "Short Blast - SHIW"
# 		else:
# 			# Default fallback
# 			s_warehouse = "Short Blast - SHIW"

# 		items.append(
# 			{
# 				"item_code": row.item_name,
# 				"qty": rejected_qty,
# 				"s_warehouse": s_warehouse,
# 				"t_warehouse": "First Line Rejection - SHIW",
# 				"custom_pouring_id": row.pouring_id,
# 			}
# 		)

# 	# Check if there are valid items to process
# 	if not items:
# 		frappe.msgprint(_("⚠️ No valid items to create Stock Entry."))
# 		return

# 	try:
# 		# Create new Stock Entry
# 		se = frappe.new_doc("Stock Entry")
# 		se.stock_entry_type = "Material Transfer"
# 		se.custom_date = doc.date
# 		se.custom_shift_type = doc.shift_type
# 		se.custom_process_type = "First Line Rejection"
# 		se.remarks = f"Auto-created from First Line Rejection: {doc.name}"

# 		# Append items to Stock Entry
# 		for item in items:
# 			se.append("items", item)

# 		# Insert and submit Stock Entry
# 		se.insert(ignore_permissions=True)
# 		se.submit()

# 		# Link Stock Entry back to First Line Rejection
# 		frappe.db.set_value(doc.doctype, doc.name, "linked_stock_entry", se.name)

# 		# Notify success
# 		frappe.msgprint(_(f"✅ Stock Entry Created and Submitted: {se.name}"))
# 	except Exception as e:
# 		frappe.log_error(f"First Line Rejection on_submit Error: {e!s}")
# 		frappe.throw(_(f"Failed to create or submit Stock Entry: {e!s}"))


# apps/shiw/shiw/doctype/first_line_rejection/first_line_rejection.py
import frappe
from frappe import _
from frappe.model.document import Document


class FirstLineRejection(Document):
	def on_submit(self):
		def flt(val):
			try:
				return float(val)
			except:
				return 0.0

		items = []
		for row in self.table_yncx:
			if not row.item_name or flt(row.quantity_rejected) <= 0:
				continue
			rejected_qty = flt(row.quantity_rejected)
			total_qty = flt(row.quantity)
			if rejected_qty > total_qty:
				frappe.throw(
					_(
						f"Rejected Quantity ({rejected_qty}) for item {row.item_name} exceeds Total Quantity ({total_qty})."
					)
				)
			stage = row.rejection_stage or ""
			s_warehouse = "Short Blast - SHIW"  # Default
			if stage == "Pouring":
				s_warehouse = "Pouring - SHIW"
			elif stage == "Shake Out":
				s_warehouse = "Shake Out - SHIW"
			elif stage == "Shot Blast":
				s_warehouse = "Short Blast - SHIW"
			items.append(
				{
					"item_code": row.item_name,
					"qty": rejected_qty,
					"s_warehouse": s_warehouse,
					"t_warehouse": "First Line Rejection - SHIW",
					"custom_pouring_id": row.pouring_id,
				}
			)
		if not items:
			frappe.msgprint(_("⚠️ No valid items to create Stock Entry."))
			return
		try:
			se = frappe.new_doc("Stock Entry")
			se.stock_entry_type = "Material Transfer"
			se.custom_date = self.date
			se.custom_shift_type = self.shift_type
			se.custom_process_type = "First Line Rejection"
			se.remarks = f"Auto-created from First Line Rejection: {self.name}"
			for item in items:
				se.append("items", item)
			se.insert(ignore_permissions=True)
			se.submit()
			self.db_set("linked_stock_entry", se.name)
			frappe.msgprint(_(f"✅ Stock Entry Created and Submitted: {se.name}"))
		except Exception as e:
			frappe.log_error(f"First Line Rejection after_submit Error: {e!s}")
			frappe.throw(_(f"Failed to create or submit Stock Entry: {e!s}"))
