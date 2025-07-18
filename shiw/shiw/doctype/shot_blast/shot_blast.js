// Copyright (c) 2025, beetashoke.chakraborty@clapgrow.com and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Shot Blast", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("Shot Blast", {
    onload: function (frm) {
        setTimeout(() => {
            const grid = frm.fields_dict["table_short"]?.grid;
            if (!grid || !grid.wrapper) {
                console.warn("⛔ table_short grid not found");
                return;
            }

            console.log("✅ Setting up item_name focus listener");
            grid.wrapper.on("focusin", function (e) {
                const $target = $(e.target);
                if ($target.attr("data-fieldname") !== "item_name") return;

                const grid_row_el = $target.closest(".grid-row");
                const grid_row = $(grid_row_el).data("grid_row");
                if (!grid_row) return;

                // Get fresh values from fields
                const row_date = grid_row.get_field("date")?.value || frm.doc.date;
                const row_shift = grid_row.get_field("shift_type")?.value || frm.doc.shift_type;
                console.log("🕵️‍♂️ item_name clicked", "📅 Date:", row_date, "🌙 Shift Type:", row_shift);

                if (!row_date || !row_shift) {
                    console.warn("⚠️ Missing date or shift_type");
                    return;
                }

                // Fetch item options from backend
                frappe.call({
                    method: "shiw.api.get_items_from_shakeout_stock_entries.get_items_from_shakeout_stock_entries",
                    args: { date: row_date, shift_type: row_shift },
                    callback: function (r) {
                        if (r.message && Array.isArray(r.message)) {
                            const field = grid_row.get_field("item_name");
                            if (field) {
                                field.df.options = r.message.join("\n");
                                field.refresh();
                                frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, "item_name", "");
                            }
                        } else {
                            console.error("❌ Failed to get item list");
                            frappe.msgprint("⚠️ No items returned from server.");
                        }
                    }
                });
            });
        }, 300);
    }
});

frappe.ui.form.on("Shakeout Table", {
    date: function (frm, cdt, cdn) {
        clear_row_fields(frm, cdt, cdn);
        fetch_available_items(frm, cdt, cdn);
    },

    shift_type: function (frm, cdt, cdn) {
        clear_row_fields(frm, cdt, cdn);
        fetch_available_items(frm, cdt, cdn);
    },

    item_name: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (!row || !row.item_name || !row.date || !row.shift_type) {
            frappe.model.set_value(cdt, cdn, "item_name", "");
            return;
        }

        // Fetch shakeout quantity
        frappe.call({
            method: "shiw.api.get_recent_shakeout_qty.get_recent_shakeout_qty",
            args: {
                item_code: row.item_name,
                custom_date: row.date,
                custom_shift_type: row.shift_type
            },
            callback: function (r) {
                if (r.message && r.message.qty != null) {
                    frappe.model.set_value(cdt, cdn, "shakeout_quantity", r.message.qty);
                } else {
                    frappe.msgprint("⚠️ No quantity found for this item.");
                    frappe.model.set_value(cdt, cdn, "shakeout_quantity", null);
                }
            }
        });

        // Fetch pouring ID
        frappe.call({
            method: "shiw.api.get_pouring_id_for_shotbrust.get_pouring_id_for_shotbrust",
            args: {
                item_code: row.item_name,
                custom_date: row.date,
                custom_shift_type: row.shift_type
            },
            callback: function (r) {
                if (r.message && r.message.custom_pouring_id) {
                    frappe.model.set_value(cdt, cdn, "pouring_id", r.message.custom_pouring_id);
                } else {
                    frappe.msgprint(r.message?.error || "No pouring ID found.");
                    frappe.model.set_value(cdt, cdn, "pouring_id", "");
                }
            }
        });
    },

    table_short_add: function (frm, cdt, cdn) {
        clear_row_fields(frm, cdt, cdn);
        toggle_item_name_field(frm, cdt, cdn, false);
    },

    refresh: function (frm) {
        frm.fields_dict["table_short"].grid.grid_rows.forEach(row => {
            let cdt = row.doc.doctype;
            let cdn = row.doc.name;
            if (!locals[cdt] || !locals[cdt][cdn]) return;
            let row_doc = locals[cdt][cdn];
            toggle_item_name_field(frm, cdt, cdn, row_doc.date && row_doc.shift_type);
        });
    }
});

function clear_row_fields(frm, cdt, cdn) {
    if (!locals[cdt] || !locals[cdt][cdn]) return;
    let row = locals[cdt][cdn];

    // Clear fields
    ["item_name", "shakeout_quantity", "short_blast_quantity", "pouring_id"].forEach(field => {
        if (field in row) frappe.model.set_value(cdt, cdn, field, "");
    });

    // Reset item_name field options
    let grid_row = frm.fields_dict["table_short"].grid.grid_rows_by_docname[cdn];
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

    let grid_row = frm.fields_dict["table_short"].grid.grid_rows_by_docname[cdn];
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
            method: "shiw.api.get_items_from_shakeout_stock_entries.get_items_from_shakeout_stock_entries",
            args: { date: row.date, shift_type: row.shift_type },
            callback: function (r) {
                if (r.message && Array.isArray(r.message)) {
                    let grid_row = frm.fields_dict["table_short"].grid.grid_rows_by_docname[cdn];
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