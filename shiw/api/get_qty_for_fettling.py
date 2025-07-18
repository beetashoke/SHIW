import frappe
from frappe import _


@frappe.whitelist(allow_guest=True)  # Remove `allow_guest=True` if login is required
def get_qty_for_fettling(item_name, warehouse=None):
	# item_name = frappe.form_dict.get("item_code")  # This is item_name
	# warehouse = frappe.form_dict.get("warehouse")

	# Fallback if no warehouse provided
	if not warehouse:
		warehouse = frappe.db.get_single_value("Stock Settings", "default_warehouse")

	# Get item_code from item_name
	item_code = frappe.db.get_value("Item", {"item_name": item_name}, "name")

	if not item_code:
		return {"qty": 0, "warehouse": warehouse, "message": f"❌ Item not found for name: {item_name}"}

	# Get actual stock from Bin table
	actual_qty = (
		frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": warehouse}, "actual_qty") or 0
	)

	return {
		"qty": actual_qty,
		"warehouse": warehouse,
		"message": f"✅ Current stock: {actual_qty}" if actual_qty > 0 else "⚠️ No quantity found in Bin",
	}
