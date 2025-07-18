import frappe


@frappe.whitelist(allow_guest=False)
def get_items_from_pouring_stock_entries(date=None, shift_type=None):
	"""
	Fetch unique item codes from Stock Entry Details linked to Stock Entries of type 'Pouring'
	for a given custom_date and custom_shift_type.

	Args:
	    date (str): The date to filter Stock Entries.
	    shift_type (str): The shift type to filter Stock Entries.

	Returns:
	    dict: Contains status, list of unique item codes, and optional debug log or error message.
	"""
	debug_log = [f"Fetching items for custom_date: {date}, custom_shift_type: {shift_type}"]

	try:
		# Validate inputs
		if not date or not shift_type:
			return {"status": "error", "message": "Date and Shift Type are required"}
		if not frappe.utils.is_valid_date(date):
			return {"status": "error", "message": "Invalid date format"}

		# Check permissions
		if not frappe.has_permission("Stock Entry", "read"):
			frappe.throw("Insufficient permissions", frappe.PermissionError)

		# Fetch Stock Entries
		stock_entries = frappe.get_all(
			"Stock Entry",
			filters={"stock_entry_type": "Pouring", "custom_date": date, "custom_shift_type": shift_type},
			fields=["name"],
		)
		debug_log.append(f"Found Stock Entries: {[se.name for se in stock_entries]}")

		if not stock_entries:
			return {
				"status": "success",
				"items": [],
				"message": "No stock entries found for the specified date and shift type",
				"debug_log": debug_log,
			}

		# Fetch Stock Entry Details in one query
		details = frappe.get_all(
			"Stock Entry Detail",
			filters={"parent": ["in", [se.name for se in stock_entries]]},
			fields=["item_code"],
		)
		item_codes = [d.item_code for d in details]
		debug_log.append(f"Items fetched: {item_codes}")

		# Get unique items
		unique_items = list(set(item_codes))
		debug_log.append(f"Final unique item list: {unique_items}")

		return {
			"status": "success",
			"items": unique_items,
			"debug_log": debug_log,  # Included for debugging, can be removed in production
		}

	except Exception as e:
		frappe.log_error(f"Error in get_items_from_pouring_stock_entries: {str(e)}")
		return {"status": "error", "message": f"Server error: {str(e)}", "items": []}


# Set API response (for direct script execution)
frappe.response["message"] = get_items_from_pouring_stock_entries(
	date=frappe.form_dict.get("date"), shift_type=frappe.form_dict.get("shift_type")
)
