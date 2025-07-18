# import frappe
# from frappe import _


# @frappe.whitelist()
# def get_quantity_for_finishing(item_name, warehouse=None):
# 	# Fallback if no warehouse is provided
# 	if not warehouse:
# 		warehouse = frappe.db.get_single_value("Stock Settings", "default_warehouse")

# 	# Get item_code using item_name
# 	item_code = frappe.db.get_value("Item", {"item_name": item_name}, "name")

# 	if not item_code:
# 		frappe.response["message"] = {
# 			"qty": 0,
# 			"warehouse": warehouse,
# 			"message": f"❌ Item not found for name: {item_name}",
# 		}
# 		return

# 	# Get actual_qty from Bin table
# 	actual_qty = (
# 		frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": warehouse}, "actual_qty") or 0
# 	)

# 	frappe.response["message"] = {
# 		"qty": actual_qty,
# 		"warehouse": warehouse,
# 		"message": f"✅ Current stock: {actual_qty}" if actual_qty > 0 else "⚠️ No quantity found in Bin",
# 	}


import frappe
from frappe import _


@frappe.whitelist()
def get_quantity_for_finishing(item_code, warehouse=None):
	# Fallback if no warehouse provided
	if not warehouse:
		warehouse = frappe.db.get_single_value("Stock Settings", "default_warehouse")

	# Ensure item_code exists
	if not item_code:
		frappe.response["message"] = {
			"qty": 0,
			"warehouse": warehouse,
			"message": "❌ No item_code provided",
		}
		return

	# Get actual stock from Bin table
	actual_qty = (
		frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": warehouse}, "actual_qty") or 0
	)

	frappe.response["message"] = {
		"qty": actual_qty,
		"warehouse": warehouse,
		"message": f"✅ Current stock: {actual_qty}" if actual_qty > 0 else "⚠️ No quantity found in Bin",
	}
