// Copyright (c) 2025, beetashoke.chakraborty@clapgrow.com and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Fettling", {
// 	refresh(frm) {

// 	},
// });



frappe.ui.form.on('Fettling', {
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
    table_pnnt_remove: function (frm, cdt, cdn) {
        console.log(`Row ${cdn} removed from consumption`);
        calculate_total_consumption(frm);
    }
});

frappe.ui.form.on("Fettling Table", {
    item_name(frm, cdt, cdn) {
        const row = locals[cdt][cdn];
        const item_code = row.item_name;

        if (!item_code) {
            frappe.model.set_value(cdt, cdn, "available_qty", null);
            return;
        }

        frappe.call({
            method: "shiw.api.get_qty_for_fettling.get_qty_for_fettling",
            args: {
                item_code: item_code,
                warehouse: "Short Blast - SHIW"
            },
            callback(r) {
                const qty = r.message?.qty ?? null;
                frappe.model.set_value(cdt, cdn, "available_qty", qty);
            }
        });
    },
    fettling_quantity(frm) {
        calculate_total_fettling_quantity(frm);
        calculate_total_fettling_weight(frm);
    },
    cast_weight_in_kg(frm) {
        calculate_total_fettling_weight(frm);
    },
    table_tjba_add(frm, cdt, cdn) {
        clear_row_fields(cdt, cdn, frm);
        calculate_total_fettling_quantity(frm);
        calculate_total_fettling_weight(frm);
    },
    table_tjba_remove(frm) {
        calculate_total_fettling_quantity(frm);
        calculate_total_fettling_weight(frm);
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
    frm.refresh_field('table_pnnt');
}

// Function to calculate total_consumption_valuation
function calculate_total_consumption(frm) {
    let total = 0;
    if (frm.doc.table_pnnt && Array.isArray(frm.doc.table_pnnt)) {
        frm.doc.table_pnnt.forEach(function (row) {
            total += flt(row.amount);
            console.log(`Adding amount for row ${row.name}: ${row.amount}, Running total: ${total}`);
        });
    } else {
        console.log('Child table table_pnnt is undefined or empty');
    }
    frm.set_value('total_consumption_valuation', total);
    console.log(`Total consumption valuation set to: ${total}`);
}

function clear_row_fields(cdt, cdn, frm) {
    frappe.model.set_value(cdt, cdn, "item_name", "");
    frappe.model.set_value(cdt, cdn, "available_qty", null);

    const grid_row = frm.fields_dict["table_tjba"].grid.grid_rows_by_docname[cdn];
    if (grid_row) {
        const item_field = grid_row.get_field("item_name");
        if (item_field) {
            item_field.df.options = "";
            item_field.refresh();
        }
    }
    console.log("🧹 Cleared row fields for:", cdn);
}

function calculate_total_fettling_quantity(frm) {
    const total_qty = (frm.doc.table_tjba || []).reduce((acc, row) => {
        return acc + (parseFloat(row.fettling_quantity) || 0);
    }, 0);

    console.log("📊 total_fettling_quantity:", total_qty);
    frm.set_value("total_fettling_quantity", total_qty);
    frm.refresh_field("total_fettling_quantity");
}

function calculate_total_fettling_weight(frm) {
    const total_wt = (frm.doc.table_tjba || []).reduce((acc, row) => {
        const qty = parseFloat(row.fettling_quantity) || 0;
        const cwtkg = parseFloat(row.cast_weight_in_kg) || 0;
        return acc + qty * cwtkg;
    }, 0);

    console.log("📏 total_fettling_weight:", total_wt);
    frm.set_value("total_fettling_weight", total_wt);
    frm.refresh_field("total_fettling_weight");
}