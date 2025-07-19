// Copyright (c) 2025, beetashoke.chakraborty@clapgrow.com and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Second Line Rejection", {
// 	refresh(frm) {

// 	},
// });


// SECOND LINE REJECTION FORM LOGIC
frappe.ui.form.on('Second Line Rejection', {
    refresh(frm) {
        console.log('🔄 Form refreshed');
    },

    table_scpn_add(frm, cdt, cdn) {
        console.log(`➕ Row added: ${cdn}`);
        clear_row_fields(cdt, cdn, frm);
    },

    table_scpn_remove(frm, cdt, cdn) {
        console.log(`❌ Row removed: ${cdn}`);
        update_total_rejected_quantity(frm);
        update_rejected_quantity_weight(frm);
    },

    validate(frm) {
        console.log('✅ Validating form, recalculating totals');
        update_total_rejected_quantity(frm);
        update_rejected_quantity_weight(frm);
    }
});

// SECOND LINE REJECTION TABLE CHILD EVENTS
frappe.ui.form.on('Second Line Rejection Table', {
    item_name(frm, cdt, cdn) {
        console.log(`📦 Item changed for row ${cdn}`);
        fetch_available_quantity(frm, cdt, cdn);
    },

    rejection_stage(frm, cdt, cdn) {
        console.log(`🏗️ Stage changed for row ${cdn}`);
        fetch_available_quantity(frm, cdt, cdn);
    },

    rejected_qty(frm, cdt, cdn) {
        console.log(`🔢 Rejected qty changed for row ${cdn}`);
        update_total_rejected_quantity(frm);
        update_rejected_quantity_weight(frm);
    },

    cast_weight_in_kg(frm, cdt, cdn) {
        console.log(`⚖️ Cast weight changed for row ${cdn}`);
        update_rejected_quantity_weight(frm);
    }
});

// ───── HELPER FUNCTIONS ───────────────────────────────

function flt(val) {
    return parseFloat(val) || 0;
}

// Clear fields when a new row is added
function clear_row_fields(cdt, cdn, frm) {
    frappe.model.set_value(cdt, cdn, 'item_name', '');
    frappe.model.set_value(cdt, cdn, 'rejection_stage', '');
    frappe.model.set_value(cdt, cdn, 'available_quantity', null);
    frappe.model.set_value(cdt, cdn, 'rejected_qty', null);

    console.log(`🧹 Cleared row fields for: ${cdn}`);
}

// Fetch available quantity from warehouse based on stage
function fetch_available_quantity(frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    const item_code = row.item_name;
    const stage = row.rejection_stage;

    if (!item_code || !stage) {
        console.log(`⏳ Waiting for both item and stage for row ${cdn}`);
        return;
    }

    let warehouse = null;
    if (stage === 'Finishing') {
        warehouse = 'Finishing - SHIW';
    } else if (stage === 'Fettling') {
        warehouse = 'Fettling - SHIW';
    }

    if (!warehouse) {
        frappe.model.set_value(cdt, cdn, 'available_quantity', null);
        return;
    }

    frappe.call({
        method: 'shiw.api.get_qty_for_fettling.get_qty_for_fettling',
        args: { item_code, warehouse },
        callback(r) {
            const qty = r.message?.qty ?? null;
            frappe.model.set_value(cdt, cdn, 'available_quantity', qty);
            console.log(`📦 Available quantity for row ${cdn}: ${qty}`);
        }
    });
}

// Total of rejected_qty field
function update_total_rejected_quantity(frm) {
    const total = (frm.doc.table_scpn || []).reduce((acc, row) => {
        return acc + flt(row.rejected_qty);
    }, 0);

    frm.set_value('total_rejected_quantity', total);
    frm.refresh_field('total_rejected_quantity');
    console.log(`📊 Total rejected quantity: ${total}`);
}

// Total of rejected_qty * cast_weight_in_kg
function update_rejected_quantity_weight(frm) {
    const total = (frm.doc.table_scpn || []).reduce((acc, row) => {
        const qty = flt(row.rejected_qty);
        const wt = flt(row.cast_weight_in_kg);
        return acc + qty * wt;
    }, 0);

    frm.set_value('rejected_quantity', total);
    frm.refresh_field('rejected_quantity');
    console.log(`⚖️ Total rejected weight (kg): ${total}`);
}
