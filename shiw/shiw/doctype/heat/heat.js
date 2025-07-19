// Copyright (c) 2025, beetashoke.chakraborty@clapgrow.com and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Heat", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Heat', {
    before_save: function (frm) {
        if (!frm.doc.furnace_holding_time) {
            frm.set_value('furnace_holding_time', '00:00:00');
        }
    },
    heat_start_at: function (frm) {
        calculate_melting_time(frm);
    },
    heat_end_at: function (frm) {
        calculate_melting_time(frm);
    },
    refresh: function (frm) {
        console.log('Form refreshed, calculating totals and consumption valuation');
        calculate_totals(frm);
        calculate_total_consumption(frm);
    },
    onload: function (frm) {
        calculate_totals(frm);
    },
    charge_mix_component_item_add: function (frm) {
        calculate_totals(frm);
    },
    charge_mix_component_item_remove: function (frm) {
        calculate_totals(frm);
    }
});

frappe.ui.form.on('Charge mix component table', {
    weight: function (frm, cdt, cdn) {
        update_row_amount(cdt, cdn);
        calculate_totals(frm);
    },
    rate: function (frm, cdt, cdn) {
        update_row_amount(cdt, cdn);
        calculate_totals(frm);
    }
});

frappe.ui.form.on('Heat-Ladle Consumption Table', {
    quantity: function (frm, cdt, cdn) {
        console.log(`Weight changed for row ${cdn}: ${locals[cdt][cdn].weight_in_kg}`);
        calculate_row_amount(frm, cdt, cdn);
        calculate_total_consumption(frm);
    },
    rate: function (frm, cdt, cdn) {
        console.log(`Rate changed for row ${cdn}: ${locals[cdt][cdn].rate}`);
        calculate_row_amount(frm, cdt, cdn);
        calculate_total_consumption(frm);
    },
    table_vkjb_remove: function (frm, cdt, cdn) {
        console.log(`Row ${cdn} removed from table_mcjm`);
        calculate_total_consumption(frm);
    }
});

function calculate_melting_time(frm) {
    if (frm.doc.heat_start_at && frm.doc.heat_end_at) {
        let start_time = moment(frm.doc.heat_start_at, "HH:mm:ss");
        let end_time = moment(frm.doc.heat_end_at, "HH:mm:ss");

        if (end_time.isBefore(start_time)) {
            end_time.add(1, 'days');
        }

        let duration = moment.duration(end_time.diff(start_time));
        let hours = Math.floor(duration.asHours());
        let minutes = duration.minutes();
        let seconds = duration.seconds();

        let formatted_duration = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

        frm.set_value('melting_time', formatted_duration);
    }
}

function update_row_amount(cdt, cdn) {
    const row = locals[cdt][cdn];
    const wt = parseFloat(row.weight) || 0;
    const rate = parseFloat(row.rate) || 0;
    const value = wt * rate;
    frappe.model.set_value(cdt, cdn, 'amount', value);
}

function calculate_totals(frm) {
    let total_weight = 0;
    let total_valuation = 0;

    (frm.doc.charge_mix_component_item || []).forEach(row => {
        const wt = parseFloat(row.weight) || 0;
        const rate = parseFloat(row.rate) || 0;

        total_weight += wt;
        total_valuation += wt * rate;
    });

    frm.set_value({
        total_charge_mix_in_kg: total_weight,
        total_charge_mix_valuation: total_valuation
    });

    frm.refresh_field(['total_charge_mix_in_kg', 'total_charge_mix_valuation']);
}

function calculate_row_amount(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    if (row.quantity && row.rate) {
        row.amount = flt(row.quantity) * flt(row.rate);
        console.log(`Calculated amount for row ${cdn}: ${row.amount} (weight: ${row.quantity}, rate: ${row.rate})`);
    } else {
        row.amount = 0;
        console.log(`Amount set to 0 for row ${cdn} (weight: ${row.quantity}, rate: ${row.rate})`);
    }
    frm.refresh_field('table_vkjb');
}

function calculate_total_consumption(frm) {
    let total = 0;
    if (frm.doc.table_vkjb && Array.isArray(frm.doc.table_vkjb)) {
        frm.doc.table_vkjb.forEach(function (row) {
            total += flt(row.amount);
            console.log(`Adding amount for row ${row.name}: ${row.amount}, Running total: ${total}`);
        });
    } else {
        console.log('Child table table_vkjb is undefined or empty');
    }
    frm.set_value('total_ladle_consumption_valuation', total);
    console.log(`Total consumption valuation set to: ${total}`);
}

