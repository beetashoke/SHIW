// Copyright (c) 2025, beetashoke.chakraborty@clapgrow.com and contributors
// For license information, please see license.txt

// frappe.ui.form.on("No-Bake Mould Batch", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('New Mould Table', {
    start_no: function (frm, cdt, cdn) {
        console.log("Start No changed for row:", cdn);
        calculate_mould_quantity(cdt, cdn);
    },
    end_no: function (frm, cdt, cdn) {
        console.log("End No changed for row:", cdn);
        calculate_mould_quantity(cdt, cdn);
    }
});

frappe.ui.form.on('No-Bake Mould Batch', {
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
    table_pzkg_remove: function (frm, cdt, cdn) {
        console.log(`Row ${cdn} removed from table_pzkg`);
        calculate_total_consumption(frm);
    }
});

function calculate_mould_quantity(cdt, cdn) {
    let row = locals[cdt][cdn];
    console.log("Row data:", row);

    if (row.start_no && row.end_no) {
        if (row.end_no >= row.start_no) {
            let quantity = (row.end_no - row.start_no) + 1;
            console.log(`Calculated mould_quantity: ${quantity} (end_no: ${row.end_no} - start_no: ${row.start_no})`);
            frappe.model.set_value(cdt, cdn, 'mould_quantity', quantity);
            frappe.model.set_value(cdt, cdn, 'remaining_mould', quantity);
        } else {
            console.log(`Error: end_no (${row.end_no}) is less than start_no (${row.start_no})`);
            frappe.model.set_value(cdt, cdn, 'mould_quantity', 0);
            frappe.model.set_value(cdt, cdn, 'remaining_mould', 0);
            frappe.msgprint({
                title: "Invalid Input",
                message: "End No cannot be smaller than Start No.",
                indicator: "red"
            });
        }
    }
}

function calculate_row_amount(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    if (row.weight_in_kg && row.rate) {
        row.amount = flt(row.weight_in_kg) * flt(row.rate);
        console.log(`Calculated amount for row ${cdn}: ${row.amount} (weight: ${row.weight_in_kg}, rate: ${row.rate})`);
    } else {
        row.amount = 0;
        console.log(`Amount set to 0 for row ${cdn} (weight: ${row.weight_in_kg}, rate: ${row.rate})`);
    }
    frm.refresh_field('table_pzkg');
}

function calculate_total_consumption(frm) {
    let total = 0;
    if (frm.doc.table_pzkg && Array.isArray(frm.doc.table_pzkg)) {
        frm.doc.table_pzkg.forEach(function (row) {
            total += flt(row.amount);
            console.log(`Adding amount for row ${row.name}: ${row.amount}, Running total: ${total}`);
        });
    } else {
        console.log('Child table table_pzkg is undefined or empty');
    }
    frm.set_value('total_consumption_valuation', total);
    console.log(`Total consumption valuation set to: ${total}`);
}