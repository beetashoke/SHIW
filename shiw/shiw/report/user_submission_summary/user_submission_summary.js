// Copyright (c) 2025, beetashoke.chakraborty@clapgrow.com and contributors
// For license information, please see license.txt

// frappe.query_reports["User Submission Summary"] = {
// 	"filters": [

// 	]
// };



frappe.query_reports["User Submission Summary"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": "From Date",
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.add_days(frappe.datetime.get_today(), -30)
		},
		{
			"fieldname": "to_date",
			"label": "To Date",
			"fieldtype": "Date",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		}
	]
};
