// Copyright (c) 2025, beetashoke.chakraborty@clapgrow.com and contributors
// For license information, please see license.txt

// frappe.ui.form.on("First Line Rejection", {
// 	refresh(frm) {

// 	},
// });


frappe.ui.form.on("First Line Rejection", {
    // Utility function to clear row fields
    clear_flr_row_fields: function (cdt, cdn, frm) {
        if (!locals[cdt] || !locals[cdt][cdn]) return;

        let row = locals[cdt][cdn];

        if ("item_name" in row) frappe.model.set_value(cdt, cdn, "item_name", "");
        if ("quantity" in row) frappe.model.set_value(cdt, cdn, "quantity", null);
        if ("quantity_rejected" in row) frappe.model.set_value(cdt, cdn, "quantity_rejected", null);

        let grid_row = frm.fields_dict["table_yncx"].grid.grid_rows_by_docname[cdn];
        if (grid_row) {
            let item_field = grid_row.get_field("item_name");
            if (item_field) {
                item_field.df.options = "";
                item_field.refresh();
            }
        }
    },

    // Utility function to enable/disable item_name field in a specific row
    toggle_flr_item_name_field: function (frm, cdt, cdn, enabled) {
        if (!locals[cdt] || !locals[cdt][cdn]) return;

        let grid_row = frm.fields_dict["table_yncx"].grid.grid_rows_by_docname[cdn];
        if (grid_row) {
            let item_field = grid_row.get_field("item_name");
            if (item_field) {
                item_field.$input.prop("disabled", !enabled);
                if (!enabled) {
                    frappe.model.set_value(cdt, cdn, "item_name", "");
                    item_field.df.options = "";
                    item_field.refresh();
                }
            }
        }
    },

    // Utility function to fetch available item_name options based on pouring_id
    fetch_flr_items: function (frm, cdt, cdn) {
        if (!locals[cdt] || !locals[cdt][cdn]) return;

        let row = locals[cdt][cdn];
        const pouring_id = row.pouring_id;

        if (pouring_id && pouring_id.includes(" - ")) {
            this.toggle_flr_item_name_field(frm, cdt, cdn, true);

            const parts = pouring_id.split(" - ");
            if (parts.length < 4) {
                frappe.msgprint("⚠️ Invalid Pouring ID format.");
                return;
            }

            const custom_date = parts[1];
            const custom_shift_type = parts[2];

            frappe.call({
                method: "shiw.api.get_items_by_pouring_id_for_flrj.get_items_by_pouring_id_for_flrj",
                args: {
                    date: custom_date,
                    shift_type: custom_shift_type,
                    pouring_id: pouring_id
                },
                callback: function (r) {
                    if (r.message && Array.isArray(r.message)) {
                        let grid_row = frm.fields_dict["table_yncx"].grid.grid_rows_by_docname[cdn];
                        if (grid_row) {
                            let item_field = grid_row.get_field("item_name");
                            if (item_field) {
                                item_field.df.options = r.message.join("\n");
                                item_field.refresh();
                                frappe.model.set_value(cdt, cdn, "item_name", "");
                            }
                        }
                    } else {
                        frappe.msgprint("⚠️ No items returned for this Pouring ID.");
                    }
                }
            });
        } else {
            this.toggle_flr_item_name_field(frm, cdt, cdn, false);
        }
    },

    // Utility function to calculate total rejected quantity across child rows
    calculate_total_qty_rejected: function (frm) {
        let total = 0;

        if (frm.doc.table_yncx) {
            frm.doc.table_yncx.forEach(row => {
                total += parseFloat(row.quantity_rejected) || 0;
            });
        }

        frm.set_value('total_qty_rejected', total);
        frm.refresh_field('total_qty_rejected');
    },

    // Event handlers
    refresh: function (frm) {
        // Enable/disable item_name per row and calculate total
        frm.fields_dict["table_yncx"].grid.grid_rows.forEach(row => {
            const cdt = row.doc.doctype;
            const cdn = row.doc.name;
            if (!locals[cdt] || !locals[cdt][cdn]) return;
            const row_doc = locals[cdt][cdn];
            this.toggle_flr_item_name_field(frm, cdt, cdn, !!row_doc.pouring_id);
        });

        this.calculate_total_qty_rejected(frm);
    },

    onload: function (frm) {
        this.calculate_total_qty_rejected(frm);

        // Setup item_name focus listener
        setTimeout(() => {
            const grid = frm.fields_dict["table_yncx"]?.grid;

            if (!grid || !grid.wrapper) {
                console.warn("⛔ table_yncx grid not found");
                return;
            }

            console.log("✅ Setting up item_name focus listener for FLR");

            grid.wrapper.on("focusin", (e) => {
                const $target = $(e.target);

                if ($target.attr("data-fieldname") === "item_name") {
                    const grid_row_el = $target.closest(".grid-row");
                    const grid_row = $(grid_row_el).data("grid_row");

                    if (grid_row) {
                        const cdt = grid_row.doc.doctype;
                        const cdn = grid_row.doc.name;
                        this.fetch_flr_items(frm, cdt, cdn); // Reuse fetch_flr_items
                    }
                }
            });
        }, 300);
    },

    pouring_id: function (frm, cdt, cdn) {
        this.clear_flr_row_fields(cdt, cdn, frm);
        this.fetch_flr_items(frm, cdt, cdn);
        this.calculate_total_qty_rejected(frm);
    },

    item_name: function (frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        const item_code = row.item_name;
        const pouring_id = row.pouring_id;

        if (!item_code) {
            frappe.model.set_value(cdt, cdn, "quantity", null);
            this.calculate_total_qty_rejected(frm);
            return;
        }

        if (pouring_id && pouring_id.includes(" - ")) {
            const parts = pouring_id.split(" - ");
            if (parts.length < 4) {
                frappe.msgprint("⚠️ Invalid Pouring ID format.");
                frappe.model.set_value(cdt, cdn, "quantity", null);
                this.calculate_total_qty_rejected(frm);
                return;
            }

            const custom_date = parts[1];
            const custom_shift_type = parts[2];

            frappe.call({
                method: "shiw.api.get_qty_by_item_for_pouring_id.get_qty_by_item_for_pouring_id",
                args: {
                    item_code: item_code,
                    date: custom_date,
                    shift_type: custom_shift_type
                },
                callback: function (r) {
                    if (r.message && r.message.qty != null) {
                        frappe.model.set_value(cdt, cdn, "quantity", r.message.qty);
                    } else {
                        frappe.msgprint("⚠️ Quantity not found for this item in selected Pouring batch.");
                        frappe.model.set_value(cdt, cdn, "quantity", null);
                    }
                    frm.script_manager.trigger("calculate_total_qty_rejected");
                }
            });
        } else {
            frappe.msgprint("⚠️ Invalid Pouring ID format.");
            frappe.model.set_value(cdt, cdn, "quantity", null);
            this.calculate_total_qty_rejected(frm);
        }
    },

    quantity_rejected: function (frm) {
        this.calculate_total_qty_rejected(frm);
    },

    table_yncx_add: function (frm, cdt, cdn) {
        this.clear_flr_row_fields(cdt, cdn, frm);
        this.toggle_flr_item_name_field(frm, cdt, cdn, false);
        this.calculate_total_qty_rejected(frm);
    },

    table_yncx_remove: function (frm) {
        this.calculate_total_qty_rejected(frm);
    }
});