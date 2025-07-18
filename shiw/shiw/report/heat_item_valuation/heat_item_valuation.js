// Copyright (c) 2025, beetashoke.chakraborty@clapgrow.com and contributors
// For license information, please see license.txt

// frappe.query_reports["Heat Item Valuation"] = {
// 	"filters": [

// 	]
// };


frappe.query_reports["Heat Item Valuation"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_days(frappe.datetime.now_date(), -30),
			reqd: 1
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.now_date(),
			reqd: 1
		},
		{
			fieldname: "item",
			label: __("Item"),
			fieldtype: "Link",
			options: "Item"
		}
	]
};
