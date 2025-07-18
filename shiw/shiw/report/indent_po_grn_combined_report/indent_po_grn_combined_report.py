# Copyright (c) 2025, beetashoke.chakraborty@clapgrow.com and contributors
# For license information, please see license.txt

import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data


# # Defining the server-side logic for the Material Request Report
# def execute(filters=None):
# 	columns, data = [], []

# 	# Define report columns
# 	columns = [
# 		{
# 			"label": "Material Request",
# 			"fieldname": "material_request",
# 			"fieldtype": "Link",
# 			"options": "Material Request",
# 			"width": 150,
# 		},
# 		{"label": "Indent Date", "fieldname": "indent_date", "fieldtype": "Date", "width": 100},
# 		{"label": "MR Status", "fieldname": "mr_status", "fieldtype": "Data", "width": 100},
# 		{
# 			"label": "Item Code",
# 			"fieldname": "item_code",
# 			"fieldtype": "Link",
# 			"options": "Item",
# 			"width": 120,
# 		},
# 		{"label": "Requested Qty", "fieldname": "requested_qty", "fieldtype": "Float", "width": 100},
# 		{"label": "UOM", "fieldname": "uom", "fieldtype": "Link", "options": "UOM", "width": 80},
# 		{
# 			"label": "Purchase Order",
# 			"fieldname": "purchase_order",
# 			"fieldtype": "Link",
# 			"options": "Purchase Order",
# 			"width": 150,
# 		},
# 		{"label": "PO Status", "fieldname": "po_status", "fieldtype": "Data", "width": 100},
# 		{"label": "Ordered Qty", "fieldname": "ordered_qty", "fieldtype": "Float", "width": 100},
# 		{"label": "PO UOM", "fieldname": "po_uom", "fieldtype": "Link", "options": "UOM", "width": 80},
# 		{"label": "PO Rate", "fieldname": "po_rate", "fieldtype": "Currency", "width": 100},
# 		{"label": "Discount", "fieldname": "discount", "fieldtype": "Currency", "width": 100},
# 		{"label": "Item Amount", "fieldname": "item_amount", "fieldtype": "Currency", "width": 120},
# 		{
# 			"label": "Supplier",
# 			"fieldname": "supplier",
# 			"fieldtype": "Link",
# 			"options": "Supplier",
# 			"width": 150,
# 		},
# 		{"label": "PO Date", "fieldname": "po_date", "fieldtype": "Date", "width": 100},
# 		{"label": "Required By", "fieldname": "required_by", "fieldtype": "Date", "width": 100},
# 		{"label": "PO Grand Total", "fieldname": "po_grand_total", "fieldtype": "Currency", "width": 120},
# 		{
# 			"label": "Purchase Receipt",
# 			"fieldname": "purchase_receipt",
# 			"fieldtype": "Link",
# 			"options": "Purchase Receipt",
# 			"width": 150,
# 		},
# 		{"label": "Received Qty", "fieldname": "received_qty", "fieldtype": "Float", "width": 100},
# 		{"label": "Receipt Date", "fieldname": "receipt_date", "fieldtype": "Date", "width": 100},
# 		{
# 			"label": "Purchase Invoice",
# 			"fieldname": "purchase_invoice",
# 			"fieldtype": "Link",
# 			"options": "Purchase Invoice",
# 			"width": 150,
# 		},
# 		{"label": "Invoiced Qty", "fieldname": "invoiced_qty", "fieldtype": "Float", "width": 100},
# 		{"label": "Invoice Date", "fieldname": "invoice_date", "fieldtype": "Date", "width": 100},
# 	]

# 	# Get filters
# 	from_date = filters.get("from_date")
# 	to_date = filters.get("to_date")

# 	# SQL query to fetch data
# 	query = """
#         SELECT
#             mr.name AS material_request,
#             mr.transaction_date AS indent_date,
#             mr.workflow_state AS mr_status,
#             mri.item_code AS item_code,
#             mri.qty AS requested_qty,
#             mri.uom AS uom,
#             po.name AS purchase_order,
#             po.workflow_state AS po_status,
#             poi.qty AS ordered_qty,
#             poi.uom AS po_uom,
#             poi.rate AS po_rate,
#             poi.discount_amount AS discount,
#             poi.amount AS item_amount,
#             po.supplier AS supplier,
#             po.transaction_date AS po_date,
#             po.schedule_date AS required_by,
#             po.grand_total AS po_grand_total,
#             pr.name AS purchase_receipt,
#             pri.qty AS received_qty,
#             pr.posting_date AS receipt_date,
#             pi.name AS purchase_invoice,
#             pii.qty AS invoiced_qty,
#             pi.posting_date AS invoice_date
#         FROM
#             `tabMaterial Request` mr
#         LEFT JOIN
#             `tabMaterial Request Item` mri ON mri.parent = mr.name
#         LEFT JOIN
#             `tabPurchase Order Item` poi
#                 ON poi.material_request_item = mri.name
#                 AND (
#                     EXISTS (
#                         SELECT 1
#                         FROM `tabPurchase Order` po_sub
#                         WHERE po_sub.name = poi.parent
#                         AND po_sub.docstatus = 1
#                         AND po_sub.workflow_state != 'Cancelled'
#                     )
#                 )
#         LEFT JOIN
#             `tabPurchase Order` po
#                 ON po.name = poi.parent
#                 AND po.docstatus = 1
#                 AND po.workflow_state != 'Cancelled'
#         LEFT JOIN
#             `tabPurchase Receipt Item` pri ON pri.purchase_order_item = poi.name
#         LEFT JOIN
#             `tabPurchase Receipt` pr ON pr.name = pri.parent AND pr.docstatus = 1
#         LEFT JOIN
#             `tabPurchase Invoice Item` pii
#                 ON pii.purchase_receipt = pr.name
#                 AND pii.purchase_order = po.name
#                 AND pii.item_code = mri.item_code
#         LEFT JOIN
#             `tabPurchase Invoice` pi ON pi.name = pii.parent AND pi.docstatus = 1
#         WHERE
#             mr.docstatus = 1
#             AND mr.transaction_date BETWEEN %(from_date)s AND %(to_date)s
#         ORDER BY
#             mr.name, mri.item_code
#     """

# 	# Execute the query with filters
# 	data = frappe.db.sql(query, {"from_date": from_date, "to_date": to_date}, as_dict=True)

# 	return columns, data


# Defining the server-side logic for the Material Request Report with additional filters
# def execute(filters=None):
# 	columns, data = [], []

# 	# Define report columns
# 	columns = [
# 		{
# 			"label": "Material Request",
# 			"fieldname": "material_request",
# 			"fieldtype": "Link",
# 			"options": "Material Request",
# 			"width": 150,
# 		},
# 		{"label": "Indent Date", "fieldname": "indent_date", "fieldtype": "Date", "width": 100},
# 		{"label": "MR Status", "fieldname": "mr_status", "fieldtype": "Data", "width": 100},
# 		{
# 			"label": "Item Code",
# 			"fieldname": "item_code",
# 			"fieldtype": "Link",
# 			"options": "Item",
# 			"width": 120,
# 		},
# 		{"label": "Requested Qty", "fieldname": "requested_qty", "fieldtype": "Float", "width": 100},
# 		{"label": "UOM", "fieldname": "uom", "fieldtype": "Link", "options": "UOM", "width": 80},
# 		{
# 			"label": "Purchase Order",
# 			"fieldname": "purchase_order",
# 			"fieldtype": "Link",
# 			"options": "Purchase Order",
# 			"width": 150,
# 		},
# 		{"label": "PO Status", "fieldname": "po_status", "fieldtype": "Data", "width": 100},
# 		{"label": "Ordered Qty", "fieldname": "ordered_qty", "fieldtype": "Float", "width": 100},
# 		{"label": "PO UOM", "fieldname": "po_uom", "fieldtype": "Link", "options": "UOM", "width": 80},
# 		{"label": "PO Rate", "fieldname": "po_rate", "fieldtype": "Currency", "width": 100},
# 		{"label": "Discount", "fieldname": "discount", "fieldtype": "Currency", "width": 100},
# 		{"label": "Item Amount", "fieldname": "item_amount", "fieldtype": "Currency", "width": 120},
# 		{
# 			"label": "Supplier",
# 			"fieldname": "supplier",
# 			"fieldtype": "Link",
# 			"options": "Supplier",
# 			"width": 150,
# 		},
# 		{"label": "PO Date", "fieldname": "po_date", "fieldtype": "Date", "width": 100},
# 		{"label": "Required By", "fieldname": "required_by", "fieldtype": "Date", "width": 100},
# 		{"label": "PO Grand Total", "fieldname": "po_grand_total", "fieldtype": "Currency", "width": 120},
# 		{
# 			"label": "Purchase Receipt",
# 			"fieldname": "purchase_receipt",
# 			"fieldtype": "Link",
# 			"options": "Purchase Receipt",
# 			"width": 150,
# 		},
# 		{"label": "Received Qty", "fieldname": "received_qty", "fieldtype": "Float", "width": 100},
# 		{"label": "Receipt Date", "fieldname": "receipt_date", "fieldtype": "Date", "width": 100},
# 		{
# 			"label": "Purchase Invoice",
# 			"fieldname": "purchase_invoice",
# 			"fieldtype": "Link",
# 			"options": "Purchase Invoice",
# 			"width": 150,
# 		},
# 		{"label": "Invoiced Qty", "fieldname": "invoiced_qty", "fieldtype": "Float", "width": 100},
# 		{"label": "Invoice Date", "fieldname": "invoice_date", "fieldtype": "Date", "width": 100},
# 	]

# 	# Get filters
# 	from_date = filters.get("from_date")
# 	to_date = filters.get("to_date")
# 	material_request = filters.get("material_request")
# 	purchase_order = filters.get("purchase_order")
# 	purchase_receipt = filters.get("purchase_receipt")
# 	item_code = filters.get("item_code")

# 	# SQL query with additional filter conditions
# 	query = """
#         SELECT
#             mr.name AS material_request,
#             mr.transaction_date AS indent_date,
#             mr.workflow_state AS mr_status,
#             mri.item_code AS item_code,
#             mri.qty AS requested_qty,
#             mri.uom AS uom,
#             po.name AS purchase_order,
#             po.workflow_state AS po_status,
#             poi.qty AS ordered_qty,
#             poi.uom AS po_uom,
#             poi.rate AS po_rate,
#             poi.discount_amount AS discount,
#             poi.amount AS item_amount,
#             po.supplier AS supplier,
#             po.transaction_date AS po_date,
#             po.schedule_date AS required_by,
#             po.grand_total AS po_grand_total,
#             pr.name AS purchase_receipt,
#             pri.qty AS received_qty,
#             pr.posting_date AS receipt_date,
#             pi.name AS purchase_invoice,
#             pii.qty AS invoiced_qty,
#             pi.posting_date AS invoice_date
#         FROM
#             `tabMaterial Request` mr
#         LEFT JOIN
#             `tabMaterial Request Item` mri ON mri.parent = mr.name
#         LEFT JOIN
#             `tabPurchase Order Item` poi
#                 ON poi.material_request_item = mri.name
#                 AND (
#                     EXISTS (
#                         SELECT 1
#                         FROM `tabPurchase Order` po_sub
#                         WHERE po_sub.name = poi.parent
#                         AND po_sub.docstatus = 1
#                         AND po_sub.workflow_state != 'Cancelled'
#                     )
#                 )
#         LEFT JOIN
#             `tabPurchase Order` po
#                 ON po.name = poi.parent
#                 AND po.docstatus = 1
#                 AND po.workflow_state != 'Cancelled'
#         LEFT JOIN
#             `tabPurchase Receipt Item` pri ON pri.purchase_order_item = poi.name
#         LEFT JOIN
#             `tabPurchase Receipt` pr ON pr.name = pri.parent AND pr.docstatus = 1
#         LEFT JOIN
#             `tabPurchase Invoice Item` pii
#                 ON pii.purchase_receipt = pr.name
#                 AND pii.purchase_order = po.name
#                 AND pii.item_code = mri.item_code
#         LEFT JOIN
#             `tabPurchase Invoice` pi ON pi.name = pii.parent AND pi.docstatus = 1
#         WHERE
#             mr.docstatus = 1
#             AND mr.transaction_date BETWEEN %(from_date)s AND %(to_date)s
#             {material_request_condition}
#             {purchase_order_condition}
#             {purchase_receipt_condition}
#             {item_code_condition}
#         ORDER BY
#             mr.name, mri.item_code
#     """

# 	# Add filter conditions dynamically
# 	conditions = []
# 	params = {"from_date": from_date, "to_date": to_date}

# 	if material_request:
# 		conditions.append("mr.name = %(material_request)s")
# 		params["material_request"] = material_request

# 	if purchase_order:
# 		conditions.append("po.name = %(purchase_order)s")
# 		params["purchase_order"] = purchase_order

# 	if purchase_receipt:
# 		conditions.append("pr.name = %(purchase_receipt)s")
# 		params["purchase_receipt"] = purchase_receipt

# 	if item_code:
# 		conditions.append("mri.item_code = %(item_code)s")
# 		params["item_code"] = item_code

# 	# Format conditions into the query
# 	condition_str = " AND ".join(conditions)
# 	if condition_str:
# 		condition_str = f" AND {condition_str}"

# 	query = query.format(
# 		material_request_condition=condition_str if material_request else "",
# 		purchase_order_condition="",
# 		purchase_receipt_condition="",
# 		item_code_condition="",
# 	)

# 	# Execute the query with filters
# 	data = frappe.db.sql(query, params, as_dict=True)

# 	return columns, data


# Defining the server-side logic for the Material Request Report with fixed item_code filter
def execute(filters=None):
	columns, data = [], []

	# Define report columns
	columns = [
		{
			"label": "Material Request",
			"fieldname": "material_request",
			"fieldtype": "Link",
			"options": "Material Request",
			"width": 150,
		},
		{"label": "Indent Date", "fieldname": "indent_date", "fieldtype": "Date", "width": 100},
		{"label": "MR Status", "fieldname": "mr_status", "fieldtype": "Data", "width": 100},
		{
			"label": "Item Code",
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 120,
		},
		{"label": "Requested Qty", "fieldname": "requested_qty", "fieldtype": "Float", "width": 100},
		{"label": "UOM", "fieldname": "uom", "fieldtype": "Link", "options": "UOM", "width": 80},
		{
			"label": "Purchase Order",
			"fieldname": "purchase_order",
			"fieldtype": "Link",
			"options": "Purchase Order",
			"width": 150,
		},
		{"label": "PO Status", "fieldname": "po_status", "fieldtype": "Data", "width": 100},
		{"label": "Ordered Qty", "fieldname": "ordered_qty", "fieldtype": "Float", "width": 100},
		{"label": "PO UOM", "fieldname": "po_uom", "fieldtype": "Link", "options": "UOM", "width": 80},
		{"label": "PO Rate", "fieldname": "po_rate", "fieldtype": "Currency", "width": 100},
		{"label": "Discount", "fieldname": "discount", "fieldtype": "Currency", "width": 100},
		{"label": "Item Amount", "fieldname": "item_amount", "fieldtype": "Currency", "width": 120},
		{
			"label": "Supplier",
			"fieldname": "supplier",
			"fieldtype": "Link",
			"options": "Supplier",
			"width": 150,
		},
		{"label": "PO Date", "fieldname": "po_date", "fieldtype": "Date", "width": 100},
		{"label": "Required By", "fieldname": "required_by", "fieldtype": "Date", "width": 100},
		{"label": "PO Grand Total", "fieldname": "po_grand_total", "fieldtype": "Currency", "width": 120},
		{
			"label": "Purchase Receipt",
			"fieldname": "purchase_receipt",
			"fieldtype": "Link",
			"options": "Purchase Receipt",
			"width": 150,
		},
		{"label": "Received Qty", "fieldname": "received_qty", "fieldtype": "Float", "width": 100},
		{"label": "Receipt Date", "fieldname": "receipt_date", "fieldtype": "Date", "width": 100},
		{
			"label": "Purchase Invoice",
			"fieldname": "purchase_invoice",
			"fieldtype": "Link",
			"options": "Purchase Invoice",
			"width": 150,
		},
		{"label": "Invoiced Qty", "fieldname": "invoiced_qty", "fieldtype": "Float", "width": 100},
		{"label": "Invoice Date", "fieldname": "invoice_date", "fieldtype": "Date", "width": 100},
	]

	# Get filters
	from_date = filters.get("from_date")
	to_date = filters.get("to_date")
	material_request = filters.get("material_request")
	purchase_order = filters.get("purchase_order")
	purchase_receipt = filters.get("purchase_receipt")
	item_code = filters.get("item_code")

	# SQL query with additional filter conditions
	query = """
        SELECT
            mr.name AS material_request,
            mr.transaction_date AS indent_date,
            mr.workflow_state AS mr_status,
            mri.item_code AS item_code,
            mri.qty AS requested_qty,
            mri.uom AS uom,
            po.name AS purchase_order,
            po.workflow_state AS po_status,
            poi.qty AS ordered_qty,
            poi.uom AS po_uom,
            poi.rate AS po_rate,
            poi.discount_amount AS discount,
            poi.amount AS item_amount,
            po.supplier AS supplier,
            po.transaction_date AS po_date,
            po.schedule_date AS required_by,
            po.grand_total AS po_grand_total,
            pr.name AS purchase_receipt,
            pri.qty AS received_qty,
            pr.posting_date AS receipt_date,
            pi.name AS purchase_invoice,
            pii.qty AS invoiced_qty,
            pi.posting_date AS invoice_date
        FROM
            `tabMaterial Request` mr
        LEFT JOIN
            `tabMaterial Request Item` mri ON mri.parent = mr.name
        LEFT JOIN
            `tabPurchase Order Item` poi 
                ON poi.material_request_item = mri.name
                AND (
                    EXISTS (
                        SELECT 1 
                        FROM `tabPurchase Order` po_sub 
                        WHERE po_sub.name = poi.parent 
                        AND po_sub.docstatus = 1 
                        AND po_sub.workflow_state != 'Cancelled'
                    )
                )
        LEFT JOIN
            `tabPurchase Order` po 
                ON po.name = poi.parent 
                AND po.docstatus = 1 
                AND po.workflow_state != 'Cancelled'
        LEFT JOIN
            `tabPurchase Receipt Item` pri ON pri.purchase_order_item = poi.name
        LEFT JOIN
            `tabPurchase Receipt` pr ON pr.name = pri.parent AND pr.docstatus = 1
        LEFT JOIN
            `tabPurchase Invoice Item` pii 
                ON pii.purchase_receipt = pr.name 
                AND pii.purchase_order = po.name 
                AND pii.item_code = mri.item_code
        LEFT JOIN
            `tabPurchase Invoice` pi ON pi.name = pii.parent AND pi.docstatus = 1
        WHERE
            mr.docstatus = 1
            AND mr.transaction_date BETWEEN %(from_date)s AND %(to_date)s
    """

	# Add filter conditions dynamically
	conditions = []
	params = {"from_date": from_date, "to_date": to_date}

	if material_request:
		conditions.append("mr.name = %(material_request)s")
		params["material_request"] = material_request

	if purchase_order:
		conditions.append("po.name = %(purchase_order)s")
		params["purchase_order"] = purchase_order

	if purchase_receipt:
		conditions.append("pr.name = %(purchase_receipt)s")
		params["purchase_receipt"] = purchase_receipt

	if item_code:
		conditions.append("mri.item_code = %(item_code)s")
		params["item_code"] = item_code

	# Append conditions to the query
	if conditions:
		query += " AND " + " AND ".join(conditions)

	# Execute the query with filters
	data = frappe.db.sql(query, params, as_dict=True)

	return columns, data
