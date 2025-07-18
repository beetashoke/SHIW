# shiw/material/api.py
import frappe


@frappe.whitelist(allow_guest=False)
def get_per_day_consumption(item_code, warehouse):
	"""
	Calculate per-day consumption for the given item and warehouse based on Material Issue entries from the last 7 days.
	"""
	if not item_code or not warehouse:
		return 0

	recent_date = frappe.utils.add_days(frappe.utils.nowdate(), -7)

	stock_entry_names = frappe.get_all(
		"Stock Entry",
		filters={"stock_entry_type": "Material Issue", "posting_date": [">=", recent_date]},
		pluck="name",
	)

	if not stock_entry_names:
		return 0

	stock_details = frappe.get_all(
		"Stock Entry Detail",
		filters={"parent": ["in", stock_entry_names], "item_code": item_code, "s_warehouse": warehouse},
		fields=["qty"],
	)

	total_qty = sum([d.qty for d in stock_details])
	per_day = round(total_qty / 7, 2) if total_qty else 0

	return per_day
