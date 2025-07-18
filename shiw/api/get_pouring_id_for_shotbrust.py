import frappe


@frappe.whitelist(allow_guest=False)
def get_pouring_id_for_shotblast(item_code, custom_date=None, custom_shift_type=None):
	"""
	Whitelisted function to fetch the pouring ID for a given item code, date, and shift type from Stock Entry Details.

	Args:
	    item_code (str): Item code to search for
	    custom_date (str, optional): Custom date filter for Stock Entries
	    custom_shift_type (str, optional): Custom shift type filter for Stock Entries

	Returns:
	    dict: Dictionary containing either the custom_pouring_id or an error message
	"""
	if not item_code:
		return {"error": "Missing item_code"}

	try:
		stock_details = frappe.get_all(
			"Stock Entry Detail", filters={"item_code": item_code}, fields=["custom_pouring_id", "parent"]
		)

		for detail in stock_details:
			entry = frappe.db.get_value(
				"Stock Entry",
				detail.parent,
				["stock_entry_type", "custom_date", "custom_shift_type", "custom_process_type"],
				as_dict=True,
			)

			if (
				entry
				and entry.stock_entry_type == "Material Transfer"
				and str(entry.custom_date) == str(custom_date)
				and entry.custom_shift_type == custom_shift_type
				and entry.custom_process_type == "Shake Out"
				and detail.custom_pouring_id
			):
				return {"custom_pouring_id": detail.custom_pouring_id}

		return {"error": "No pouring ID found matching all conditions"}

	except Exception as e:
		error_msg = f"Error in get_pouring_id_for_shotblast: {e!s}\n{frappe.get_traceback()}"
		frappe.log_error("get_pouring_id_for_shotblast Error", error_msg)
		return {"error": f"Server error: {e!s}"}
