# Copyright (c) 2025, beetashoke.chakraborty@clapgrow.com and contributors
# For license information, please see license.txt

# import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data


import frappe
from frappe import _


def execute(filters=None):
	columns = [
		{"label": _("Item"), "fieldname": "item", "fieldtype": "Link", "options": "Item", "width": 200},
		{"label": _("Total Weight"), "fieldname": "total_weight", "fieldtype": "Float", "width": 150},
		{
			"label": _("Total Valuation"),
			"fieldname": "total_valuation",
			"fieldtype": "Currency",
			"width": 150,
		},
	]

	where_clauses = []
	query_params = {}

	# Handle from_date and to_date
	if filters.get("from_date") and filters.get("to_date"):
		where_clauses.append("h.date BETWEEN %(from_date)s AND %(to_date)s")
		query_params["from_date"] = filters["from_date"]
		query_params["to_date"] = filters["to_date"]

	# Handle item filter
	if filters.get("item"):
		where_clauses.append("cmct.item = %(item)s")
		query_params["item"] = filters["item"]

	# Build the WHERE clause
	where_sql = ""
	if where_clauses:
		where_sql = "WHERE " + " AND ".join(where_clauses)

	query = f"""
		SELECT
			cmct.item AS item,
			SUM(cmct.weight) AS total_weight,
			SUM(IFNULL(it.valuation_rate, 0) * IFNULL(cmct.weight, 0)) AS total_valuation
		FROM
			`tabHeat` AS h
		JOIN
			`tabCharge mix component table` AS cmct
			ON cmct.parent = h.name AND cmct.parenttype = 'Heat'
		LEFT JOIN
			`tabItem` AS it
			ON it.name = cmct.item
		{where_sql}
		GROUP BY
			cmct.item
		ORDER BY
			cmct.item
	"""

	data = frappe.db.sql(query, query_params, as_dict=True)
	return columns, data
