# Copyright (c) 2025, beetashoke.chakraborty@clapgrow.com and contributors
# For license information, please see license.txt

import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data


# def execute(filters=None):
# 	from_date = filters.get("from_date")
# 	to_date = filters.get("to_date")

# 	columns = [
# 		{"label": "Id", "fieldname": "id", "fieldtype": "Link", "options": "Heat", "width": 120},
# 		{"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 100},
# 		{"label": "Shift", "fieldname": "shift", "fieldtype": "Data", "width": 100},
# 		{"label": "Power Consumption", "fieldname": "power_consumption", "fieldtype": "Float", "width": 150},
# 		{"label": "Burning Loss", "fieldname": "burning_loss", "fieldtype": "Float", "width": 120},
# 	]

# 	data = frappe.db.get_all(
# 		"Heat",
# 		fields=[
# 			"name as id",
# 			"date",
# 			"shift_timing as shift",
# 			"power_consumptionkwh as power_consumption",
# 			"burning_loss",
# 		],
# 		filters={"date": ["between", [from_date, to_date]]},
# 		order_by="date DESC, shift_timing ASC",
# 	)

# 	return columns, data


def execute(filters=None):
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	furnace_no = filters.get("furnace_no")
	material_grade = filters.get("material_grade")

	columns = [
		{"label": "Id", "fieldname": "id", "fieldtype": "Link", "options": "Heat", "width": 120},
		{"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 100},
		{"label": "Shift", "fieldname": "shift", "fieldtype": "Data", "width": 100},
		{
			"label": "Furnace",
			"fieldname": "furnace_no",
			"fieldtype": "Link",
			"options": "Furnace - Master",
			"width": 140,
		},
		{
			"label": "Grade",
			"fieldname": "material_grade",
			"fieldtype": "Link",
			"options": "Grade Master",
			"width": 120,
		},
		{"label": "Power Consumption", "fieldname": "power_consumption", "fieldtype": "Float", "width": 150},
		{"label": "Burning Loss", "fieldname": "burning_loss", "fieldtype": "Float", "width": 120},
	]

	filters_dict = {"date": ["between", [from_date, to_date]]}

	if furnace_no:
		filters_dict["furnace_no"] = furnace_no

	if material_grade:
		filters_dict["material_grade"] = material_grade

	data = frappe.db.get_all(
		"Heat",
		fields=[
			"name as id",
			"date",
			"shift_timing as shift",
			"furnace_no",
			"material_grade",
			"power_consumptionkwh as power_consumption",
			"burning_loss",
		],
		filters=filters_dict,
		order_by="date DESC, shift_timing ASC",
	)

	return columns, data
