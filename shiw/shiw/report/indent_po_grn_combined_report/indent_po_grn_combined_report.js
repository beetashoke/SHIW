// Copyright (c) 2025, beetashoke.chakraborty@clapgrow.com and contributors
// For license information, please see license.txt

// frappe.query_reports["Indent Po Grn combined report"] = {
// 	"filters": [

// 	]
// };

// frappe.query_reports["Indent Po Grn combined report"] = {
// 	"filters": [
// 		{
// 			"fieldname": "from_date",
// 			"label": __("From Date"),
// 			"fieldtype": "Date",
// 			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
// 			"reqd": 1
// 		},
// 		{
// 			"fieldname": "to_date",
// 			"label": __("To Date"),
// 			"fieldtype": "Date",
// 			"default": frappe.datetime.get_today(),
// 			"reqd": 1
// 		}
// 	]
// };


// Defining the client-side configuration for the Material Request Report with additional filters
frappe.query_reports["Indent Po Grn combined report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			"reqd": 1
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			"reqd": 1
		},
		{
			"fieldname": "material_request",
			"label": __("Material Request ID"),
			"fieldtype": "Link",
			"options": "Material Request",
			"reqd": 0
		},
		{
			"fieldname": "purchase_order",
			"label": __("Purchase Order ID"),
			"fieldtype": "Link",
			"options": "Purchase Order",
			"reqd": 0
		},
		{
			"fieldname": "purchase_receipt",
			"label": __("Goods Received Note ID"),
			"fieldtype": "Link",
			"options": "Purchase Receipt",
			"reqd": 0
		},
		{
			"fieldname": "item_code",
			"label": __("Item Code"),
			"fieldtype": "Link",
			"options": "Item",
			"reqd": 0
		}
	]
};