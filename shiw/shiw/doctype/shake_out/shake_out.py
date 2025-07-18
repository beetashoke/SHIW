# # # Copyright (c) 2025, beetashoke.chakraborty@clapgrow.com and contributors
# # # For license information, please see license.txt

# # # import frappe
# # from frappe.model.document import Document  # type: ignore


# # class ShakeOut(Document):
# # 	pass


# # import frappe  # type: ignore


# # def flt(val):
# # 	"""Custom float conversion to avoid import."""
# # 	try:
# # 		return float(val)
# # 	except:  # noqa: E722
# # 		return 0.0


# # def on_submit(doc, method):
# # 	"""
# # 	Handle the after_submit event for the Shake Out doctype.
# # 	Creates and submits a Stock Entry of type 'Material Transfer' based on items in table_abc.

# # 	Args:
# # 	    doc (frappe.Document): The submitted Shake Out document.
# # 	    method (str): The event method (after_submit).
# # 	"""
# # 	try:
# # 		# Check permissions
# # 		if not frappe.has_permission("Stock Entry", "create"):
# # 			frappe.throw("Insufficient permissions to create Stock Entry", frappe.PermissionError)

# # 		stock_items = []
# # 		for row in doc.table_abc:
# # 			if not row.item_name or flt(row.shake_out_qty) <= 0:
# # 				continue

# # 			shake_out_qty = flt(row.shake_out_qty)
# # 			prod_cast_qty = flt(row.prod_cast)

# # 			# Validate quantities
# # 			if shake_out_qty > prod_cast_qty:
# # 				frappe.throw(
# # 					f"Error: Shake Out Quantity ({shake_out_qty}) for item {row.item_name} "
# # 					f"exceeds Production Cast Quantity ({prod_cast_qty})."
# # 				)

# # 			stock_items.append(
# # 				{
# # 					"item_code": row.item_name,
# # 					"qty": shake_out_qty,
# # 					"custom_pouring_id": row.pouring_id,
# # 					"s_warehouse": "Pouring - SHIW",
# # 					"t_warehouse": "Shake Out - SHIW",
# # 				}
# # 			)

# # 		if not stock_items:
# # 			frappe.msgprint("⚠️ No valid items to create Stock Entry.")
# # 			return

# # 		# Create Stock Entry
# # 		se_doc = frappe.get_doc(
# # 			{
# # 				"doctype": "Stock Entry",
# # 				"stock_entry_type": "Material Transfer",
# # 				"items": stock_items,
# # 				"custom_date": doc.date,
# # 				"custom_shift_type": doc.shift_type,
# # 				"custom_process_type": "Shake Out",
# # 				"remarks": f"Auto-created from Shake Out: {doc.name}",
# # 			}
# # 		)

# # 		# Insert and submit Stock Entry
# # 		se_doc.insert(ignore_permissions=True)
# # 		se_doc.submit()

# # 		# Link Stock Entry to Shake Out
# # 		frappe.db.set_value("Shake Out", doc.name, "linked_stock_entry", se_doc.name)
# # 		frappe.msgprint(f"✅ Stock Entry Created and Submitted: {se_doc.name}")

# # 	except Exception as e:
# # 		frappe.log_error(f"Error in on_shake_out_submit for Shake Out {doc.name}: {e!s}")
# # 		frappe.throw(f"Failed to create Stock Entry: {e!s}")


# # apps/shiw/shiw/doctype/shake_out/shake_out.py
# # Copyright (c) 2025, beetashoke.chakraborty@clapgrow.com and contributors
# # For license information, please see license.txt

# import frappe
# from frappe import _
# from frappe.model.document import Document


# class ShakeOut(Document):
# 	def after_submit(self):
# 		"""
# 		Handle the after_submit event for the Shake Out doctype.
# 		Creates and submits a Stock Entry of type 'Material Transfer' based on items in table_abc.
# 		"""

# 		def flt(val):
# 			"""Custom float conversion to avoid import."""
# 			try:
# 				return float(val)
# 			except:
# 				return 0.0

# 		try:
# 			# Check permissions
# 			if not frappe.has_permission("Stock Entry", "create"):
# 				frappe.throw(_("Insufficient permissions to create Stock Entry"), frappe.PermissionError)

# 			stock_items = []
# 			for row in self.table_abc:
# 				if not row.item_name or flt(row.shake_out_qty) <= 0:
# 					continue

# 				shake_out_qty = flt(row.shake_out_qty)
# 				prod_cast_qty = flt(row.prod_cast)

# 				# Validate quantities
# 				if shake_out_qty > prod_cast_qty:
# 					frappe.throw(
# 						_(
# 							f"Shake Out Quantity ({shake_out_qty}) for item {row.item_name} "
# 							f"exceeds Production Cast Quantity ({prod_cast_qty})."
# 						)
# 					)

# 				stock_items.append(
# 					{
# 						"item_code": row.item_name,
# 						"qty": shake_out_qty,
# 						"custom_pouring_id": row.pouring_id,
# 						"s_warehouse": "Pouring - SHIW",
# 						"t_warehouse": "Shake Out - SHIW",
# 					}
# 				)

# 			if not stock_items:
# 				frappe.msgprint(_("⚠️ No valid items to create Stock Entry."))
# 				return

# 			# Create Stock Entry
# 			se_doc = frappe.get_doc(
# 				{
# 					"doctype": "Stock Entry",
# 					"stock_entry_type": "Material Transfer",
# 					"items": stock_items,
# 					"custom_date": self.date,
# 					"custom_shift_type": self.shift_type,
# 					"custom_process_type": "Shake Out",
# 					"remarks": f"Auto-created from Shake Out: {self.name}",
# 				}
# 			)

# 			# Insert and submit Stock Entry
# 			se_doc.insert(ignore_permissions=True)
# 			se_doc.submit()

# 			# Link Stock Entry to Shake Out
# 			self.db_set("linked_stock_entry", se_doc.name)

# 			# Success Message
# 			frappe.msgprint(_(f"✅ Stock Entry Created and Submitted: {se_doc.name}"))

# 		except Exception as e:
# 			frappe.log_error(
# 				f"Error in after_submit for Shake Out {self.name}: {e!s}\n{frappe.get_traceback()}"
# 			)
# 			frappe.throw(_(f"Failed to create Stock Entry: {e!s}"))


# apps/shiw/shiw/doctype/shake_out/shake_out.py
# Copyright (c) 2025, beetashoke.chakraborty@clapgrow.com and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class ShakeOut(Document):
	def on_submit(self):
		"""
		Handle the after_submit event for the Shake Out doctype.
		Creates and submits a Stock Entry of type 'Material Transfer' based on items in table_abc.
		"""

		def flt(val):
			"""Custom float conversion to avoid import."""
			try:
				return float(val)
			except:
				return 0.0

		try:
			# Check permissions
			if not frappe.has_permission("Stock Entry", "create"):
				frappe.throw(_("Insufficient permissions to create Stock Entry"), frappe.PermissionError)

			stock_items = []
			for row in self.table_abc:
				if not row.item_name or flt(row.shake_out_qty) <= 0:
					continue

				shake_out_qty = flt(row.shake_out_qty)
				prod_cast_qty = flt(row.prod_cast)

				# Validate quantities
				if shake_out_qty > prod_cast_qty:
					frappe.throw(
						_(
							f"Shake Out Quantity ({shake_out_qty}) for item {row.item_name} "
							f"exceeds Production Cast Quantity ({prod_cast_qty})."
						)
					)

				stock_items.append(
					{
						"item_code": row.item_name,
						"qty": shake_out_qty,
						"custom_pouring_id": row.pouring_id,
						"s_warehouse": "Pouring - SHIW",
						"t_warehouse": "Shake Out - SHIW",
					}
				)

			if not stock_items:
				frappe.msgprint(_("⚠️ No valid items to create Stock Entry."))
				return

			# Create Stock Entry
			se_doc = frappe.get_doc(
				{
					"doctype": "Stock Entry",
					"stock_entry_type": "Material Transfer",
					"items": stock_items,
					"custom_date": self.shake_out_date,
					"custom_shift_type": self.shift_type,
					"custom_process_type": "Shake Out",
					"remarks": f"Auto-created from Shake Out: {self.name}",
				}
			)

			# Insert and submit Stock Entry
			se_doc.insert(ignore_permissions=True)
			se_doc.submit()

			# Link Stock Entry to Shake Out
			self.db_set("linked_stock_entry", se_doc.name)

			# Success Message
			frappe.msgprint(_(f"✅ Stock Entry Created and Submitted: {se_doc.name}"))

		except Exception as e:
			frappe.log_error(
				f"Error in after_submit for Shake Out {self.name}: {e!s}\n{frappe.get_traceback()}"
			)
			frappe.throw(_(f"Failed to create Stock Entry: {e!s}"))
