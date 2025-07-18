import frappe
from frappe import _


@frappe.whitelist()
def get_qty_by_item_for_pouring_id(item_code, date=None, shift_type=None):
	"""
	Whitelisted function to fetch the quantity for a given item_code, date, and shift_type from Stock Entry.

	Args:
	    item_code (str): The item code to search for.
	    date (str, optional): The date in DD-MM-YYYY or YYYY-MM-DD format.
	    shift_type (str, optional): The shift type to filter Stock Entries.

	Returns:
	    dict: Contains 'qty' (quantity found or 0), 'stock_entries' (list of stock entries), and 'log' (debug messages).
	"""
	debug_log = [f"Server script called with item_code: {item_code}, date: {date}, shift_type: {shift_type}"]

	try:
		# Build filters for Stock Entry
		filters = {"stock_entry_type": "Pouring", "docstatus": 1}

		# Handle date filter
		if date:
			try:
				# Parse date to YYYY-MM-DD (handles DD-MM-YYYY or YYYY-MM-DD)
				if "-" in date:
					parts = date.split("-")
					if len(parts) == 3:
						if len(parts[0]) == 4:  # YYYY-MM-DD
							formatted_date = date
						else:  # DD-MM-YYYY
							formatted_date = f"{parts[2]}-{parts[1]}-{parts[0]}"
						filters["custom_date"] = formatted_date
						debug_log.append(f"Formatted date: {formatted_date}")
					else:
						debug_log.append(f"Invalid date format for: {date}")
						return {
							"qty": 0,
							"stock_entries": [],
							"log": [*debug_log, "Invalid date format provided."],
						}
				else:
					debug_log.append(f"Invalid date format for: {date}")
					return {
						"qty": 0,
						"stock_entries": [],
						"log": [*debug_log, "Invalid date format provided."],
					}
			except Exception as e:
				debug_log.append(f"Date parsing error for: {date}")
				frappe.log_error(f"get_qty_by_item_for_pouring_id Date Parsing Error: {e!s}")
				return {"qty": 0, "stock_entries": [], "log": [*debug_log, "Date parsing error."]}

		# Handle shift filter
		if shift_type:
			filters["custom_shift_type"] = shift_type
			debug_log.append(f"Shift type filter: {shift_type}")

		# Fetch Stock Entries
		stock_entries = frappe.get_all(
			"Stock Entry",
			filters=filters,
			fields=["name", "custom_date", "custom_shift_type"],
			order_by="creation desc",
			limit=5,
		)
		stock_entry_logs = [
			f"{se.name} (Date: {se.custom_date}, Shift: {se.custom_shift_type})" for se in stock_entries
		]
		debug_log.append(f"Found Stock Entries: [{', '.join(stock_entry_logs)}]")

		# Check Stock Entry Details
		for se in stock_entries:
			details = frappe.get_all(
				"Stock Entry Detail",
				filters={"parent": se.name, "item_code": item_code},
				fields=["item_code", "qty"],
			)
			debug_log.append(f"Checked Stock Entry {se.name}: {details}")

			if details:
				return {"qty": details[0].qty, "stock_entries": stock_entries, "log": debug_log}

		debug_log.append(
			f"No matching item_code '{item_code}' found in recent stock entries for the given date and shift."
		)
		return {"qty": 0, "stock_entries": stock_entries, "log": debug_log}

	except Exception as e:
		error_msg = f"Error occurred: {e!s}"
		debug_log.append(error_msg)
		frappe.log_error(f"get_qty_by_item_for_pouring_id Error: {error_msg}")
		return {"qty": 0, "stock_entries": [], "log": [*debug_log, error_msg]}
