// Copyright (c) 2025, beetashoke.chakraborty@clapgrow.com and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Finishing", {
// 	refresh(frm) {

// 	},
// });


frappe.ui.form.on('Finishing', {
    refresh: function (frm) {
        console.log('Form refreshed, calculating total consumption valuation');
        calculate_total_consumption(frm);
    }
});

frappe.ui.form.on('Consumption-Mould', {
    weight_in_kg: function (frm, cdt, cdn) {
        console.log(`Weight changed for row ${cdn}: ${locals[cdt][cdn].weight_in_kg}`);
        calculate_row_amount(frm, cdt, cdn);
        calculate_total_consumption(frm);
    },
    rate: function (frm, cdt, cdn) {
        console.log(`Rate changed for row ${cdn}: ${locals[cdt][cdn].rate}`);
        calculate_row_amount(frm, cdt, cdn);
        calculate_total_consumption(frm);
    },
    table_xylo_remove: function (frm, cdt, cdn) {
        console.log(`Row ${cdn} removed from consumption`);
        calculate_total_consumption(frm);
    }
});

frappe.ui.form.on("Finishing Table", {
    item_name(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        const item_name = row.item_name;

        console.log("🟡 Item Name changed:", item_name);

        if (!item_name) {
            console.warn("⚠️ No item name provided, clearing quantity");
            frappe.model.set_value(cdt, cdn, "quantity", null);
            return;
        }

        console.log("📡 Calling server script get_quantity_for_finishing with:", {
            item_code: item_name,
            warehouse: "Fettling - SHIW"
        });

        frappe.call({
            method: "shiw.api.get_quantity_for_finishing.get_quantity_for_finishing",
            args: {
                item_code: item_name,
                warehouse: "Fettling - SHIW"
            },
            callback(r) {
                console.log("📥 Server response:", r.message);

                if (r.message && r.message.qty != null) {
                    console.log("✅ Setting quantity to:", r.message.qty);
                    frappe.model.set_value(cdt, cdn, "quantity", r.message.qty);
                } else {
                    console.warn("❌ No quantity returned from server. Message:", r.message?.message);
                    frappe.msgprint(r.message?.message || "⚠️ Could not fetch quantity.");
                    frappe.model.set_value(cdt, cdn, "quantity", null);
                }
            }
        });
    },
    finishing_quantity(frm, cdt, cdn) {
        calculate_total_finishing_quantity(frm);
        calculate_total_finishing_weight(frm);
    },
    casting_weight(frm, cdt, cdn) {
        calculate_total_finishing_weight(frm);
    },
    table_eiko_add(frm, cdt, cdn) {
        console.log("➕ New row added to Finishing Table:", cdn);
        clear_row_fields(cdt, cdn, frm);
        calculate_total_finishing_quantity(frm);
        calculate_total_finishing_weight(frm);
    },
    table_eiko_remove(frm) {
        console.log("➖ Row removed from Finishing Table");
        calculate_total_finishing_quantity(frm);
        calculate_total_finishing_weight(frm);
    }
});

// Function to calculate amount for a single row
function calculate_row_amount(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    if (row.weight_in_kg && row.rate) {
        row.amount = flt(row.weight_in_kg) * flt(row.rate);
        console.log(`Calculated amount for row ${cdn}: ${row.amount} (weight: ${row.weight_in_kg}, rate: ${row.rate})`);
    } else {
        row.amount = 0;
        console.log(`Amount set to 0 for row ${cdn} (weight: ${row.weight_in_kg}, rate: ${row.rate})`);
    }
    frm.refresh_field('table_xylo');
}

// Function to calculate total_consumption_valuation
function calculate_total_consumption(frm) {
    let total = 0;
    if (frm.doc.table_xylo && Array.isArray(frm.doc.table_xylo)) {
        frm.doc.table_xylo.forEach(function (row) {
            total += flt(row.amount);
            console.log(`Adding amount for row ${row.name}: ${row.amount}, Running total: ${total}`);
        });
    } else {
        console.log('Child table table_xylo is undefined or empty');
    }
    frm.set_value('total_consumption_valuation', total);
    console.log(`Total consumption valuation set to: ${total}`);
}

function clear_row_fields(cdt, cdn, frm) {
    const row = locals[cdt][cdn];
    if (!row) return;

    console.log("🧹 Clearing row fields for:", cdn);

    frappe.model.set_value(cdt, cdn, "item_name", "");
    frappe.model.set_value(cdt, cdn, "quantity", null);

    const grid_row = frm.fields_dict["table_eiko"].grid.grid_rows_by_docname[cdn];
    if (grid_row) {
        const item_field = grid_row.get_field("item_name");
        if (item_field) {
            item_field.df.options = "";
            item_field.refresh();
        }
    }
}

function calculate_total_finishing_quantity(frm) {
    let total = 0;
    (frm.doc.table_eiko || []).forEach(row => {
        total += parseFloat(row.finishing_quantity) || 0;
    });
    console.log("📊 Total Finishing Quantity:", total);
    frm.set_value("total_finished_weight", total);
    frm.refresh_field("total_finished_weight");
}

function calculate_total_finishing_weight(frm) {
    let total = 0;
    (frm.doc.table_eiko || []).forEach(row => {
        const qty = parseFloat(row.finishing_quantity) || 0;
        const weight = parseFloat(row.casting_weight) || 0;
        total += qty * weight;
    });
    console.log("📏 Total Finishing Weight (qty × weight):", total);
    frm.set_value("total_finishing_weight", total);
    frm.refresh_field("total_finishing_weight");
}