import frappe


@frappe.whitelist(allow_guest=False)
def get_recent_shakeout_qty(item_code, custom_date=None, custom_shift_type=None):
	"""
	Whitelisted function to fetch the most recent shakeout quantity for a given item code, date, and shift type.

	Args:
	    item_code (str): Item code to search for
	    custom_date (str, optional): Custom date filter for Stock Entries
	    custom_shift_type (str, optional): Custom shift type filter for Stock Entries

	Returns:
	    dict: Dictionary containing the quantity, stock entries, and debug log
	"""
	debug_log = [
		f"Server script called with item_code: {item_code}, date: {custom_date}, shift: {custom_shift_type}"
	]

	try:
		filters = {"stock_entry_type": "Material Transfer", "custom_process_type": "Shake Out"}

		# Apply additional filters if provided
		if custom_date:
			filters["custom_date"] = custom_date
		if custom_shift_type:
			filters["custom_shift_type"] = custom_shift_type

		stock_entries = frappe.get_all(
			"Stock Entry", filters=filters, fields=["name"], order_by="creation desc"
		)
		debug_log.append(f"Found Stock Entries: {[se.name for se in stock_entries]}")

		for se in stock_entries:
			details = frappe.get_all(
				"Stock Entry Detail",
				filters={"parent": se.name, "item_code": item_code},
				fields=["item_code", "qty"],
			)
			debug_log.append(f"Checked {se.name}, Found: {details}")

			if details:
				return {"qty": details[0].qty, "stock_entries": stock_entries, "log": debug_log}

		debug_log.append("No matching item_code found in recent stock entries.")
		return {"qty": 0, "stock_entries": stock_entries, "log": debug_log}

	except Exception as e:
		error_msg = f"Error: {e!s}\n{frappe.get_traceback()}"
		frappe.log_error("get_recent_shakeout_qty Error", error_msg)
		return {"qty": 0, "stock_entries": [], "log": [*debug_log, error_msg]}
