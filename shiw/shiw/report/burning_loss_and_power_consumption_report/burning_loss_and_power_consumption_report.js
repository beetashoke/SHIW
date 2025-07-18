// Copyright (c) 2025, beetashoke.chakraborty@clapgrow.com and contributors
// For license information, please see license.txt

// frappe.query_reports["Burning Loss And Power Consumption report"] = {
// 	"filters": [

// 	]
// };


// frappe.query_reports["Burning Loss And Power Consumption report"] = {
// 	filters: [
// 		{
// 			fieldname: "from_date",
// 			label: "From Date",
// 			fieldtype: "Date",
// 			default: frappe.datetime.month_start()
// 		},
// 		{
// 			fieldname: "to_date",
// 			label: "To Date",
// 			fieldtype: "Date",
// 			default: frappe.datetime.month_end()
// 		}
// 	]
// };



frappe.query_reports["Burning Loss And Power Consumption report"] = {
	filters: [
		{
			fieldname: "from_date",
			label: "From Date",
			fieldtype: "Date",
			default: frappe.datetime.month_start(),
			reqd: 1
		},
		{
			fieldname: "to_date",
			label: "To Date",
			fieldtype: "Date",
			default: frappe.datetime.month_end(),
			reqd: 1
		},
		{
			fieldname: "furnace_no",
			label: "Furnace",
			fieldtype: "Link",
			options: "Furnace - Master"
		},
		{
			fieldname: "material_grade",
			label: "Grade",
			fieldtype: "Link",
			options: "Grade Master"
		}
	]
};
