# # Copyright (c) 2025, beetashoke.chakraborty@clapgrow.com and contributors
# # For license information, please see license.txt

# # import frappe
# from frappe.model.document import Document  # type: ignore


# class Pouring(Document):
# 	pass


# import frappe  # type: ignore


# def flt(val):
# 	"""Convert value to float, return 0.0 if None or empty."""
# 	return float(val) if val not in [None, ""] else 0.0


# def on_submit(doc, method):
# 	"""Handle on_submit event for Pouring DocType."""
# 	item_map = {}
# 	tooling_qty_map = {}
# 	updated_moulds = []

# 	# Step 1: Calculate total pouring quantity per tooling_id
# 	for row in doc.mould_batch:
# 		tooling_id = row.tooling_id
# 		qty = flt(row.pouring_quantity)
# 		if tooling_id:
# 			tooling_qty_map[tooling_id] = tooling_qty_map.get(tooling_id, 0) + qty

# 	# Step 2: Update mould quantities and validate
# 	for row in doc.mould_batch:
# 		tooling_id = row.tooling_id
# 		moulding_system = row.moulding_system
# 		mould_no = row.mould_no
# 		qty = flt(row.pouring_quantity)

# 		if not (tooling_id and moulding_system and mould_no):
# 			continue

# 		mould_doc = frappe.get_doc(moulding_system, mould_no)

# 		for table_row in mould_doc.mould_table:
# 			if table_row.tooling == tooling_id:
# 				available = flt(table_row.mould_quantity)
# 				if qty > available:
# 					frappe.throw(
# 						f"Pouring quantity ({qty}) exceeds available "
# 						f"mould quantity ({available}) for tooling {tooling_id}"
# 					)

# 				table_row.mould_quantity = available - qty
# 				updated_moulds.append(
# 					f"🛠️ {tooling_id}: {available} → {table_row.mould_quantity} in {mould_no}"
# 				)
# 				break

# 		mould_doc.save(ignore_permissions=True)

# 	if updated_moulds:
# 		frappe.msgprint("\n".join(["✅ Mould Quantities Updated:", *updated_moulds]))

# 	# Step 3: Build item map for stock entry
# 	for row in doc.mould_batch[::-1]:
# 		tooling_id = row.tooling_id
# 		moulding_system = row.moulding_system
# 		mould_no = row.mould_no
# 		if not (tooling_id and moulding_system and mould_no):
# 			continue

# 		qty_total = tooling_qty_map.get(tooling_id, 0)
# 		tooling_doc = frappe.get_doc("New Tooling", tooling_id)

# 		for d in tooling_doc.details_table:
# 			item = d.item or ""
# 			cavity = flt(d.cavity)

# 			if item:
# 				clean_name = item.replace("PTRN - ", "").rsplit("-", 1)[0].strip()
# 				if clean_name not in item_map:
# 					item_map[clean_name] = {"item_code": clean_name, "qty": qty_total * cavity}

# 	# Step 4: Prepare final items for stock entry
# 	final_items = []

# 	for item_code, entry in item_map.items():
# 		# Get basic rate from Item Price
# 		rate = 0.0
# 		price_list = frappe.get_all(
# 			"Item Price", filters={"item_code": item_code}, fields=["price_list_rate"], limit=1
# 		)
# 		if price_list:
# 			rate = flt(price_list[0].price_list_rate)

# 		# Fetch extra fields from Item master
# 		item_doc = frappe.get_doc("Item", item_code)
# 		cast_wt_per_pc = flt(item_doc.custom_cast_weight_per_pc)
# 		bunch_wt_per_md = flt(item_doc.custom_bunch_weight_per_mould)
# 		grade = item_doc.custom_grade_ or "Unknown"

# 		foundry_return = flt(bunch_wt_per_md - cast_wt_per_pc)

# 		final_items.append(
# 			{
# 				"s_warehouse": "",
# 				"t_warehouse": "Pouring - SHIW",
# 				"item_code": entry["item_code"],
# 				"qty": entry["qty"],
# 				"basic_rate": rate,
# 				"custom_pouring_id": doc.name,
# 				"is_finished_item": 1,
# 				"custom_casting_weight_in_kg": cast_wt_per_pc,
# 				"custom_bunch_weight_in_kg": bunch_wt_per_md,
# 				"custom_grade": grade,
# 				"custom_estimated_foundry_return": foundry_return,
# 			}
# 		)

# 	# Step 5: Calculate foundry return by grade
# 	grade_totals = {}  # { grade : total_return_qty }

# 	for row in final_items:
# 		g = row.get("custom_grade") or "Unknown"
# 		per_row = flt(row.get("custom_estimated_foundry_return")) * flt(row.get("qty"))
# 		grade_totals[g] = grade_totals.get(g, 0.0) + per_row

# 	for g, total_qty in grade_totals.items():
# 		if total_qty <= 0:
# 			continue  # Skip zero-qty to avoid validation error

# 		item_code_return = f"{g} Foundry Return"

# 		final_items.append(
# 			{
# 				"s_warehouse": "",
# 				"t_warehouse": "Estimated Foundry Return - SHIW",
# 				"item_code": item_code_return,
# 				"qty": total_qty,
# 				"basic_rate": 0.0,
# 				"custom_pouring_id": doc.name,
# 				"is_finished_item": 1,
# 				"custom_grade": g,
# 			}
# 		)

# 	# Step 6: Create and submit stock entry
# 	if final_items:
# 		se = frappe.get_doc(
# 			{
# 				"doctype": "Stock Entry",
# 				"stock_entry_type": "Pouring",
# 				"custom_process_type": "Pouring",
# 				"items": final_items,
# 				"custom_date": doc.date,
# 				"custom_shift_type": doc.shift_type,
# 			}
# 		)
# 		se.insert()
# 		se.submit()

# 		# Link stock entry to Pouring document
# 		doc.db_set("linked_stock_entry", se.name)
# 		frappe.msgprint(f"✅ Stock Entry {se.name} created and linked.")
# 	else:
# 		frappe.msgprint("⚠️ No valid items found for Stock Entry.")


import frappe
from frappe import _
from frappe.model.document import Document


class Pouring(Document):
	def on_submit(self):
		"""Handle after_submit event for Pouring DocType."""

		def flt(val):
			"""Convert value to float, return 0.0 if None or empty."""
			return float(val) if val not in [None, ""] else 0.0

		item_map = {}
		tooling_qty_map = {}
		updated_moulds = []

		# Step 1: Calculate total pouring quantity per tooling_id
		for row in self.mould_batch:
			tooling_id = row.tooling_id
			qty = flt(row.pouring_quantity)
			if tooling_id:
				tooling_qty_map[tooling_id] = tooling_qty_map.get(tooling_id, 0) + qty

		# Step 2: Update mould quantities and validate
		for row in self.mould_batch:
			tooling_id = row.tooling_id
			moulding_system = row.moulding_system
			mould_no = row.mould_no
			qty = flt(row.pouring_quantity)

			if not (tooling_id and moulding_system and mould_no):
				continue

			mould_doc = frappe.get_doc(moulding_system, mould_no)

			for table_row in mould_doc.mould_table:
				if table_row.tooling == tooling_id:
					available = flt(table_row.mould_quantity)
					if qty > available:
						frappe.throw(
							_(
								f"Pouring quantity ({qty}) exceeds available "
								f"mould quantity ({available}) for tooling {tooling_id}"
							)
						)

					table_row.mould_quantity = available - qty
					updated_moulds.append(
						f"🛠️ {tooling_id}: {available} → {table_row.mould_quantity} in {mould_no}"
					)
					break

			mould_doc.save(ignore_permissions=True)

		if updated_moulds:
			frappe.msgprint(_("\n".join(["✅ Mould Quantities Updated:", *updated_moulds])))

		# Step 3: Build item map for stock entry
		for row in self.mould_batch[::-1]:
			tooling_id = row.tooling_id
			moulding_system = row.moulding_system
			mould_no = row.mould_no
			if not (tooling_id and moulding_system and mould_no):
				continue

			qty_total = tooling_qty_map.get(tooling_id, 0)
			tooling_doc = frappe.get_doc("New Tooling", tooling_id)

			for d in tooling_doc.details_table:
				item = d.item or ""
				cavity = flt(d.cavity)

				if item:
					clean_name = item.replace("PTRN - ", "").rsplit("-", 1)[0].strip()
					if clean_name not in item_map:
						item_map[clean_name] = {"item_code": clean_name, "qty": qty_total * cavity}

		# Step 4: Prepare final items for stock entry
		final_items = []

		for item_code, entry in item_map.items():
			# Get basic rate from Item Price
			rate = 0.0
			price_list = frappe.get_all(
				"Item Price", filters={"item_code": item_code}, fields=["price_list_rate"], limit=1
			)
			if price_list:
				rate = flt(price_list[0].price_list_rate)

			# Fetch extra fields from Item master
			item_doc = frappe.get_doc("Item", item_code)
			cast_wt_per_pc = flt(item_doc.custom_cast_weight_per_pc)
			bunch_wt_per_md = flt(item_doc.custom_bunch_weight_per_mould)
			grade = item_doc.custom_grade_ or "Unknown"

			foundry_return = flt(bunch_wt_per_md - cast_wt_per_pc)

			final_items.append(
				{
					"s_warehouse": "",
					"t_warehouse": "Pouring - SHIW",
					"item_code": entry["item_code"],
					"qty": entry["qty"],
					"basic_rate": rate,
					"custom_pouring_id": self.name,
					"is_finished_item": 1,
					"custom_casting_weight_in_kg": cast_wt_per_pc,
					"custom_bunch_weight_in_kg": bunch_wt_per_md,
					"custom_grade": grade,
					"custom_estimated_foundry_return": foundry_return,
				}
			)

		# Step 5: Calculate foundry return by grade
		grade_totals = {}  # { grade : total_return_qty }

		for row in final_items:
			g = row.get("custom_grade") or "Unknown"
			per_row = flt(row.get("custom_estimated_foundry_return")) * flt(row.get("qty"))
			grade_totals[g] = grade_totals.get(g, 0.0) + per_row

		for g, total_qty in grade_totals.items():
			if total_qty <= 0:
				continue  # Skip zero-qty to avoid validation error

			item_code_return = f"{g} Foundry Return"

			final_items.append(
				{
					"s_warehouse": "",
					"t_warehouse": "Estimated Foundry Return - SHIW",
					"item_code": item_code_return,
					"qty": total_qty,
					"basic_rate": 0.0,
					"custom_pouring_id": self.name,
					"is_finished_item": 1,
					"custom_grade": g,
				}
			)

		# Step 6: Create and submit stock entry
		if final_items:
			se = frappe.get_doc(
				{
					"doctype": "Stock Entry",
					"stock_entry_type": "Pouring",
					"custom_process_type": "Pouring",
					"items": final_items,
					"custom_date": self.date,
					"custom_shift_type": self.shift_type,
				}
			)
			se.insert(ignore_permissions=True)
			se.submit()

			# Link stock entry to Pouring document
			self.db_set("linked_stock_entry", se.name)
			frappe.msgprint(_(f"✅ Stock Entry {se.name} created and linked."))
		else:
			frappe.msgprint(_("⚠️ No valid items found for Stock Entry."))
