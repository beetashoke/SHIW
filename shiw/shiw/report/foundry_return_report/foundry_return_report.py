# Copyright (c) 2025, beetashoke.chakraborty@clapgrow.com and contributors
# For license information, please see license.txt

# import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data


import frappe
from frappe import _


def execute(filters=None):
	columns, data = [], []

	# Define columns
	columns = [
		{"label": _("Id"), "fieldname": "id", "fieldtype": "Link", "options": "Heat", "width": 100},
		{"label": _("Date"), "fieldname": "date", "fieldtype": "Date", "width": 100},
		{"label": _("Shift"), "fieldname": "shift_timing", "fieldtype": "Data", "width": 80},
		{"label": _("Item Name"), "fieldname": "item", "fieldtype": "Link", "options": "Item", "width": 150},
		{"label": _("Weight"), "fieldname": "weight", "fieldtype": "Float", "width": 100},
		{"label": _("Rate"), "fieldname": "rate", "fieldtype": "Currency", "width": 100},
		{"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 120},
	]

	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	item = filters.get("item")

	item_condition = ""
	if item:
		item_condition = "AND cmc.item = %(item)s"
	else:
		item_condition = "AND cmc.item LIKE %(like_pattern)s"

	query = f"""
		SELECT
			h.name AS id,
			h.date AS date,
			h.shift_timing AS shift_timing,
			cmc.item AS item,
			cmc.weight AS weight,
			cmc.rate AS rate,
			cmc.amount AS amount
		FROM
			`tabHeat` h
		JOIN
			`tabCharge mix component table` cmc ON cmc.parent = h.name
		WHERE
			h.date BETWEEN %(from_date)s AND %(to_date)s
			{item_condition}
		ORDER BY
			h.date DESC, h.shift_timing ASC
	"""

	# Set parameters
	query_params = {"from_date": from_date, "to_date": to_date}
	if item:
		query_params["item"] = item
	else:
		query_params["like_pattern"] = "%Foundry Return"

	data = frappe.db.sql(query, query_params, as_dict=True)
	return columns, data
