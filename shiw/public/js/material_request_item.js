frappe.ui.form.on('Material Request Item', {
    item_code: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        // Clear dependent fields if no item code is selected
        if (!row.item_code) {
            console.log("No item code found. Clearing dependent fields.");
            frappe.model.set_value(cdt, cdn, 'custom_last_supplier_name', null);
            frappe.model.set_value(cdt, cdn, 'custom_previous_request_date', null);
            frappe.model.set_value(cdt, cdn, 'custom_store_stock', null);
            frappe.model.set_value(cdt, cdn, 'custom_previous_purchase_rate', null);
            frappe.model.set_value(cdt, cdn, 'custom_per_day_consumption', null);
            frm.refresh_field('items');
            return;
        }

        console.log("Item code selected:", row.item_code);

        // Fetch details from Purchase Order
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Purchase Order",
                filters: {
                    docstatus: 1
                },
                fields: ["name"],
                limit_page_length: 1000
            },
            callback: function (response) {
                console.log("Purchase Orders fetched:", response.message);

                let purchase_orders = response.message;
                if (purchase_orders.length === 0) {
                    console.log("No Purchase Orders found.");
                    frappe.msgprint(__('No matching Purchase Order found for Item Code: ' + row.item_code));
                }

                let latest_supplier = null;
                let latest_date = null;
                let completedRequests = 0;

                // Iterate through each Purchase Order
                purchase_orders.forEach(po => {
                    console.log("Checking Purchase Order:", po.name);

                    frappe.call({
                        method: "frappe.client.get",
                        args: {
                            doctype: "Purchase Order",
                            name: po.name
                        },
                        callback: function (po_data) {
                            console.log("Purchase Order Data:", po_data);

                            let items = po_data.message.items;
                            items.forEach(item => {
                                console.log("Comparing Item Code:", item.item_code, "with", row.item_code);

                                if (item.item_code === row.item_code) {
                                    console.log("Item Matched. Evaluating Supplier and Transaction Date.");
                                    let current_date = new Date(po_data.message.transaction_date);

                                    if (!latest_date || current_date > new Date(latest_date)) {
                                        latest_supplier = po_data.message.supplier;
                                        latest_date = po_data.message.transaction_date;
                                        console.log("Updated Latest Supplier:", latest_supplier);
                                        console.log("Updated Latest Date:", latest_date);
                                    }
                                }
                            });

                            // Track completion of requests
                            completedRequests++;
                            if (completedRequests === purchase_orders.length) {
                                if (latest_supplier && latest_date) {
                                    console.log("Final Supplier Set:", latest_supplier);
                                    console.log("Final Transaction Date Set:", latest_date);
                                    frappe.model.set_value(cdt, cdn, 'custom_last_supplier_name', latest_supplier);
                                    frappe.model.set_value(cdt, cdn, 'custom_previous_request_date', latest_date);
                                    frm.refresh_field('items');
                                } else {
                                    console.log("No matching item found across all Purchase Orders.");
                                }
                            }
                        }
                    });
                });
            }
        });

        // Fetch recent Stock Ledger Entry data
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Stock Ledger Entry",
                filters: {
                    item_code: row.item_code
                },
                fields: ["voucher_type", "qty_after_transaction", "incoming_rate", "item_code", "name"],
                order_by: "creation desc",
                limit_page_length: 5000
            },
            callback: function (response) {
                console.log("Stock Ledger Entries fetched:", response.message);

                if (!response.message || response.message.length === 0) {
                    console.log("No Stock Ledger Entry found for this item.");
                    return;
                }

                let store_stock_value = null;
                let previous_purchase_rate = null;

                for (let sle of response.message) {
                    console.log("Checking Stock Ledger Entry:", sle);

                    if ((sle.voucher_type === "Goods Received Note" || sle.voucher_type === "Stock Entry") && store_stock_value === null) {
                        store_stock_value = sle.qty_after_transaction;
                        console.log("Store Stock Value Found:", store_stock_value);
                    }
                    if ((sle.voucher_type === "Goods Received Note" || sle.voucher_type === "Purchase Receipt") && previous_purchase_rate === null) {
                        previous_purchase_rate = sle.incoming_rate;
                        console.log("Previous Purchase Rate Found:", previous_purchase_rate);
                        break;
                    }
                }

                if (store_stock_value !== null) {
                    frappe.model.set_value(cdt, cdn, 'custom_store_stock', store_stock_value);
                    console.log("Updated Store Stock in Child Table:", store_stock_value);
                } else {
                    console.log("No Store Stock Value Found.");
                }

                if (previous_purchase_rate !== null) {
                    frappe.model.set_value(cdt, cdn, 'custom_previous_purchase_rate', previous_purchase_rate);
                    console.log("Updated Previous Purchase Rate in Child Table:", previous_purchase_rate);
                } else {
                    console.log("No Previous Purchase Rate Found.");
                }

                frm.refresh_field('items');
            }
        });

        // Fetch per day consumption if warehouse is specified
        if (row.warehouse) {
            frappe.call({
                method: "shiw.api.get_per_day_consumption.get_per_day_consumption",
                args: {
                    item_code: row.item_code,
                    warehouse: "Stores - SHIW"
                },
                callback: function (r) {
                    if (r.message !== undefined) {
                        frappe.model.set_value(cdt, cdn, 'custom_per_day_consumption', r.message);
                        console.log("Updated Per Day Consumption in Child Table:", r.message);
                        frm.refresh_field('items');
                    }
                }
            });
        }
    }
});