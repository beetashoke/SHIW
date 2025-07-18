import frappe


@frappe.whitelist(allow_guest=False)
def get_recent_pouring_qty(item_code, custom_date, custom_shift_type):
	debug_log = [
		(
			f"Server script called with item_code: {item_code}, "
			f"custom_date: {custom_date}, custom_shift_type: {custom_shift_type}"
		)
	]

	try:
		# ── 1. Get only the Pouring entries that match date + shift ──
		stock_entries = frappe.get_all(
			"Stock Entry",
			filters={
				"stock_entry_type": "Pouring",
				"custom_date": custom_date,
				"custom_shift_type": custom_shift_type,
			},
			fields=["name"],
			order_by="creation desc",
		)
		debug_log.append(f"Filtered Stock Entries: {[se.name for se in stock_entries]}")

		# ── 2. Look inside each entry for the requested item_code ──
		for se in stock_entries:
			details = frappe.get_all(
				"Stock Entry Detail",
				filters={
					"parent": se.name,
					"item_code": item_code,
				},
				fields=["item_code", "qty"],
			)
			debug_log.append(f"Checked {se.name}, Found: {details}")

			if details:
				return {
					"qty": details[0].qty,  # first/most-recent match
					"stock_entries": stock_entries,
					"log": debug_log,
				}

		debug_log.append("No matching record found.")
		return {"qty": 0, "stock_entries": stock_entries, "log": debug_log}

	except Exception as e:
		error_msg = f"Error: {str(e)}\n{frappe.get_traceback()}"
		frappe.log_error("get_recent_pouring_qty Error", error_msg)
		return {"qty": 0, "stock_entries": [], "log": debug_log + [error_msg]}


# ─────────────────────────  API entry point  ────────────────────────── #
required = ("item_code", "custom_date", "custom_shift_type")
missing = [k for k in required if not frappe.form_dict.get(k)]

if missing:
	frappe.throw(f"Missing required parameters: {', '.join(missing)}")

frappe.response["message"] = get_recent_pouring_qty(
	frappe.form_dict.get("item_code"),
	frappe.form_dict.get("custom_date"),
	frappe.form_dict.get("custom_shift_type"),
)
