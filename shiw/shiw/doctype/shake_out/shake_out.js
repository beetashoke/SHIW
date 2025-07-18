// Copyright (c) 2025, beetashoke.chakraborty@clapgrow.com and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Shake Out", {
// 	refresh(frm) {

// 	},
// });


frappe.ui.form.on('Shake Out', {
    onload: function (frm) {
        setTimeout(() => {
            const grid = frm.fields_dict["table_abc"]?.grid;
            if (!grid || !grid.wrapper) {
                console.warn("⛔ table_abc grid not found");
                return;
            }

            console.log("✅ Setting up item_name focus listener");
            grid.wrapper.on("focusin", function (e) {
                const $target = $(e.target);
                if ($target.attr("data-fieldname") === "item_name") {
                    const grid_row_el = $target.closest(".grid-row");
                    const grid_row = $(grid_row_el).data("grid_row");

                    if (grid_row) {
                        const row_date = grid_row.get_field("date")?.value || frm.doc.date;
                        const row_shift = grid_row.get_field("shift_type")?.value || frm.doc.shift_type;
                        console.log("🕵️‍♂️ item_name clicked, Date:", row_date, "Shift Type:", row_shift);

                        if (!row_date || !row_shift) {
                            console.warn("⚠️ Missing date or shift_type");
                            return;
                        }

                        frappe.call({
                            method: "shiw.api.get_items_from_pouring_stock_entries.get_items_from_pouring_stock_entries",
                            args: {
                                date: row_date,
                                shift_type: row_shift_type
                            },
                            callback: function (r) {
                                if (r.message && Array.isArray(r.message)) {
                                    const item_options = r.message;
                                    console.log("📦 Got item options:", item_options);

                                    const field = grid_row.get_field('item_name');
                                    if (field) {
                                        field.df.options = item_options.join('\n');
                                        field.refresh();
                                        frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, 'item_name', '');
                                    }
                                } else {
                                    console.error("❌ Failed to get item list");
                                    frappe.msgprint("⚠️ No items returned from server.");
                                }
                            }
                        });
                    }
                }
            });
        }, 300);

        frm.fields_dict["table_abc"].grid.grid_rows.forEach(row => {
            toggle_item_name_field(frm, row.doc.doctype, row.doc.name, row.doc.date && row.doc.shift_type);
        });
    },

    on_submit: function (frm) {
        console.log(`🔵 Shake Out Document Submitted: ${frm.doc.name}`);
        // ✅ Stock Entry will be handled by server script now.
    }
});

frappe.ui.form.on('Treatment Table', {
    date: function (frm, cdt, cdn) {
        clear_row_fields(cdt, cdn);
        fetch_available_items(frm, cdt, cdn);
    },

    shift_type: function (frm, cdt, cdn) {
        clear_row_fields(cdt, cdn);
        fetch_available_items(frm, cdt, cdn);
    },

    item_name: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (!row.date || !row.shift_type) {
            frappe.model.set_value(cdt, cdn, "item_name", "");
            return;
        }

        if (row.item_name) {
            frappe.call({
                method: "shiw.api.get_recent_pouring_qty.get_recent_pouring_qty",
                args: {
                    item_code: row.item_name,
                    custom_date: row.date,
                    custom_shift_type: row.shift_type
                    // warehouse: "Pouring - SHIW"
                },
                callback: function (r) {
                    if (r.message && r.message.qty != null) {
                        frappe.model.set_value(cdt, cdn, "prod_cast", r.message.qty);
                    } else {
                        frappe.msgprint("⚠️ No quantity found for this item.");
                        frappe.model.set_value(cdt, cdn, "prod_cast", null);
                    }
                }
            });

            frappe.call({
                method: "shiw.api.get_pouring_id_by_item.get_pouring_id_by_item",
                args: {
                    item_code: row.item_name,
                    custom_date: row.date,
                    custom_shift_type: row.shift_type
                },
                callback: function (r) {
                    if (r.message.custom_pouring_id) {
                        frappe.model.set_value(cdt, cdn, "pouring_id", r.message.custom_pouring_id);
                    } else {
                        frappe.msgprint(r.message.error || "No pouring ID found.");
                        frappe.model.set_value(cdt, cdn, "pouring_id", "");
                    }
                }
            });
        }
    },

    table_abc_add: function (frm, cdt, cdn) {
        clear_row_fields(cdt, cdn);
        toggle_item_name_field(frm, cdt, cdn, false);
    },

    refresh: function (frm) {
        frm.fields_dict["table_abc"].grid.grid_rows.forEach(row => {
            let cdt = row.doc.doctype;
            let cdn = row.doc.name;
            if (!locals[cdt] || !locals[cdt][cdn]) return;
            toggle_item_name_field(frm, cdt, cdn, row.doc.date && row.doc.shift_type);
        });
    }
});

function clear_row_fields(cdt, cdn) {
    if (!locals[cdt] || !locals[cdt][cdn]) return;

    let row = locals[cdt][cdn];
    if ("item_name" in row) frappe.model.set_value(cdt, cdn, "item_name", "");
    if ("prod_cast" in row) frappe.model.set_value(cdt, cdn, "prod_cast", "");
    if ("shake_out_qty" in row) frappe.model.set_value(cdt, cdn, "shake_out_qty", "");
    if ("pouring_id" in row) frappe.model.set_value(cdt, cdn, "pouring_id", "");

    let grid_row = cur_frm.fields_dict["table_abc"].grid.grid_rows_by_docname[cdn];
    if (grid_row) {
        let item_field = grid_row.get_field("item_name");
        if (item_field) {
            item_field.df.options = "";
            item_field.refresh();
        }
    }
}

function toggle_item_name_field(frm, cdt, cdn, enabled) {
    if (!locals[cdt] || !locals[cdt][cdn]) return;

    let grid_row = frm.fields_dict["table_abc"].grid.grid_rows_by_docname[cdn];
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
}

function fetch_available_items(frm, cdt, cdn) {
    if (!locals[cdt] || !locals[cdt][cdn]) return;

    let row = locals[cdt][cdn];
    toggle_item_name_field(frm, cdt, cdn, !!(row.date && row.shift_type));

    if (row.date && row.shift_type) {
        frappe.call({
            method: "shiw.api.get_items_from_pouring_stock_entries.get_items_from_pouring_stock_entries",
            args: {
                date: row.date,
                shift_type: row.shift_type
            },
            callback: function (r) {
                if (r.message && Array.isArray(r.message)) {
                    let grid_row = frm.fields_dict["table_abc"].grid.grid_rows_by_docname[cdn];
                    if (grid_row) {
                        let item_field = grid_row.get_field("item_name");
                        if (item_field) {
                            item_field.df.options = r.message.join("\n");
                            item_field.refresh();
                        }
                    }
                } else {
                    frappe.msgprint("⚠️ No items returned from server.");
                }
            }
        });
    }
}
