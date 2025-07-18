# Copyright (c) 2025, beetashoke.chakraborty@clapgrow.com and contributors
# For license information, please see license.txt

# import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data


import frappe
from frappe.utils import getdate


def execute(filters=None):
	if not filters:
		return [], []

	from_date = getdate(filters.get("from_date"))
	to_date = getdate(filters.get("to_date"))

	# Manually include these doctypes
	include_doctypes = {"Material Request", "Purchase Order", "Purchase Receipt"}

	# Fetch all SHIW module doctypes that are not child tables
	shiw_doctypes = frappe.get_all("DocType", filters={"module": "SHIW", "istable": 0}, fields=["name"])

	for d in shiw_doctypes:
		include_doctypes.add(d.name)

	# Final result storage
	result = []

	for doctype in sorted(include_doctypes):
		try:
			data = frappe.db.sql(
				f"""
                SELECT 
                    %(doctype)s AS doctype,
                    u.full_name AS owner,
                    COUNT(*) AS raw_count
                FROM `tab{doctype}` d
                JOIN `tabUser` u ON u.name = d.owner
                WHERE DATE(d.creation) BETWEEN %(from_date)s AND %(to_date)s
                GROUP BY u.full_name
            """,
				{"doctype": doctype, "from_date": from_date, "to_date": to_date},
				as_dict=True,
			)

			for row in data:
				count = row["raw_count"]

				# Determine color
				if count < 20:
					color = "red"
				elif count < 50:
					color = "orange"
				else:
					color = "green"

				# Apply styled HTML
				row["count"] = f'<span style="color:{color}; font-weight:bold">{count}</span>'

				# Clean up
				del row["raw_count"]

				result.append(row)

		except Exception as e:
			frappe.log_error(f"Error processing doctype {doctype}: {e!s}")

	# Define columns
	columns = [
		{"label": "Doctype", "fieldname": "doctype", "fieldtype": "Data", "width": 200},
		{"label": "Owner", "fieldname": "owner", "fieldtype": "Data", "width": 200},
		{"label": "Count", "fieldname": "count", "fieldtype": "HTML", "width": 100},
	]

	return columns, result


# import frappe
# from frappe.utils import getdate


# def execute(filters=None):
# 	if not filters:
# 		return [], []

# 	from_date = getdate(filters.get("from_date"))
# 	to_date = getdate(filters.get("to_date"))

# 	# Manually include these doctypes
# 	include_doctypes = {"Material Request", "Purchase Order", "Purchase Receipt"}

# 	# Fetch all SHIW module doctypes that are not child tables
# 	shiw_doctypes = frappe.get_all(
# 		"DocType", filters={"module": "SHIW", "istable": 0}, fields=["name"]
# 	)

# 	for d in shiw_doctypes:
# 		include_doctypes.add(d.name)

# 	# Final result storage
# 	result = []

# 	for doctype in sorted(include_doctypes):
# 		try:
# 			data = frappe.db.sql(
# 				f"""
#                 SELECT
#                     %(doctype)s AS doctype,
#                     u.full_name AS owner,
#                     COUNT(*) AS count
#                 FROM `tab{doctype}` d
#                 JOIN `tabUser` u ON u.name = d.owner
#                 WHERE DATE(d.creation) BETWEEN %(from_date)s AND %(to_date)s
#                 GROUP BY u.full_name
#             """,
# 				{"doctype": doctype, "from_date": from_date, "to_date": to_date},
# 				as_dict=True,
# 			)

# 			result.extend(data)

# 		except Exception as e:
# 			frappe.log_error(f"Error processing doctype {doctype}: {str(e)}")

# 	columns = [
# 		{"label": "Doctype", "fieldname": "doctype", "fieldtype": "Data", "width": 200},
# 		{"label": "Owner", "fieldname": "owner", "fieldtype": "Data", "width": 200},
# 		{"label": "Count", "fieldname": "count", "fieldtype": "Int", "width": 100},
# 	]

# 	return columns, result
