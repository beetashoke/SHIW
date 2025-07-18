import frappe


@frappe.whitelist(allow_guest=False)
def get_pouring_id_by_item(item_code=None, custom_date=None, custom_shift_type=None):
	"""
	Fetch the custom_pouring_id for a given item_code, custom_date, and custom_shift_type
	from Stock Entry Detail and Stock Entry, ensuring the stock_entry_type is 'Pouring'.

	Args:
	    item_code (str): The item code to filter Stock Entry Detail.
	    custom_date (str): The date to match in Stock Entry.
	    custom_shift_type (str): The shift type to match in Stock Entry.

	Returns:
	    dict: Contains custom_pouring_id if found, or an error message.
	"""
	try:
		# Validate inputs
		if not item_code:
			return {"status": "error", "message": "Missing item_code"}
		if not custom_date or not custom_shift_type:
			return {"status": "error", "message": "Missing custom_date or custom_shift_type"}
		if not frappe.utils.is_valid_date(custom_date):
			return {"status": "error", "message": "Invalid date format"}

		# Check permissions
		if not frappe.has_permission("Stock Entry", "read"):
			frappe.throw("Insufficient permissions", frappe.PermissionError)

		# Fetch Stock Entry Details
		stock_details = frappe.get_all(
			"Stock Entry Detail", filters={"item_code": item_code}, fields=["custom_pouring_id", "parent"]
		)

		if not stock_details:
			return {"status": "error", "message": "No stock details found for the item_code"}

		# Check each Stock Entry Detail
		for detail in stock_details:
			if not detail.custom_pouring_id:
				continue

			# Fetch Stock Entry details
			entry = frappe.db.get_value(
				"Stock Entry",
				detail.parent,
				["stock_entry_type", "custom_date", "custom_shift_type"],
				as_dict=True,
			)

			if not entry:
				continue

			# Match conditions
			if (
				entry.stock_entry_type == "Pouring"
				and str(entry.custom_date) == str(custom_date)
				and entry.custom_shift_type == custom_shift_type
			):
				return {"status": "success", "custom_pouring_id": detail.custom_pouring_id}

		return {"status": "error", "message": "No pouring ID found matching all conditions"}

	except Exception as e:
		frappe.log_error(f"Error in get_pouring_id: {str(e)}")
		return {"status": "error", "message": f"Server error: {str(e)}"}


# Set API response (for direct script execution)
frappe.response["message"] = get_pouring_id_by_item(
	item_code=frappe.form_dict.get("item_code"),
	custom_date=frappe.form_dict.get("custom_date"),
	custom_shift_type=frappe.form_dict.get("custom_shift_type"),
)
