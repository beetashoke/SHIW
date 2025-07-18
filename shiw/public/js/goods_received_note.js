frappe.ui.form.on('Purchase Receipt', {
    onload: function (frm) {
        console.log("🔄 Form loaded: Checking taxes table...");
        frm.trigger("calculate_taxes_on_load");
    },

    refresh: function (frm) {
        console.log("🔄 Form refreshed: Checking taxes table...");
        frm.trigger("calculate_taxes_on_load");
    },

    supplier: function (frm) {
        if (frm.doc.supplier) {
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'Supplier',
                    fieldname: 'custom_gst_no',
                    filters: {
                        supplier_name: frm.doc.supplier
                    }
                },
                callback: function (r) {
                    if (r.message) {
                        frm.set_value('custom_gst_number', r.message.custom_gst_no);
                    } else {
                        frappe.msgprint('No matching supplier found or GST Number not available.');
                        frm.set_value('custom_gst_number', '');
                    }
                }
            });
        } else {
            frm.set_value('custom_gst_number', '');
        }
    },

    calculate_taxes_on_load: function (frm) {
        // Ensure latest taxes are fetched
        frm.refresh_field("taxes");

        if (frm.doc.taxes && frm.doc.taxes.length > 0) {
            console.log("📥 Taxes found in table, running calculations...");
            calculate_taxes(frm);
        } else {
            console.log("⚠ No taxes found, skipping calculation.");
        }
    }
});

// 🔹 Trigger tax calculation when `item_tax_template` is selected
frappe.ui.form.on('Purchase Order Item', {
    item_tax_template: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        console.log(`🏷 'item_tax_template' selected: ${row.item_tax_template}, recalculating taxes...`);

        // Ensure taxes table is refreshed before calculation
        frm.refresh_field("taxes");
        frappe.run_serially([
            () => frappe.timeout(0.5), // Delay to allow taxes table to update
            () => calculate_taxes(frm)
        ]);
    },

    // 🔹 Trigger tax recalculation when price or discount changes
    price_list_rate: function (frm, cdt, cdn) {
        console.log("💰 Price changed: Recalculating taxes...");
        update_taxes_on_item_change(frm);
    },

    discount_percentage: function (frm, cdt, cdn) {
        console.log("🎯 Discount changed: Recalculating taxes...");
        update_taxes_on_item_change(frm);
    }
});

// 🔹 Listen for changes in the Taxes table
frappe.ui.form.on('Purchase Taxes and Charges', {
    taxes_add: function (frm) {
        console.log("➕ Tax row added: Running calculations...");
        frm.refresh_field("taxes");
        calculate_taxes(frm);
    },
    taxes_remove: function (frm) {
        console.log("❌ Tax row removed: Running calculations...");
        frm.refresh_field("taxes");
        calculate_taxes(frm);
    },
    tax_amount: function (frm) {
        console.log("💰 Tax amount changed: Running calculations...");
        frm.refresh_field("taxes");
        calculate_taxes(frm);
    },
    account_head: function (frm) {
        console.log("🔄 Account Head changed: Running calculations...");
        frm.refresh_field("taxes");
        calculate_taxes(frm);
    }
});

// 🔹 Function to recalculate taxes dynamically when an item changes
function update_taxes_on_item_change(frm) {
    console.log("🔄 Price or Discount Changed! Recalculating Taxes...");

    frappe.timeout(0.5).then(() => {
        frm.trigger("calculate_taxes_on_load");  // Call tax calculation function
    });
}

// 🔹 Main tax calculation function
function calculate_taxes(frm) {
    console.log("🔄 Running tax calculation...");

    // Ensure taxes table is loaded
    frm.refresh_field("taxes");

    if (!frm.doc.taxes || frm.doc.taxes.length === 0) {
        console.log("⚠ No taxes found in the table.");
        return;
    }

    console.log("🔍 Tax Table:", frm.doc.taxes);

    let total_cgst = 0, total_sgst = 0, total_igst = 0;

    $.each(frm.doc.taxes, function (index, tax) {
        console.log(`Looping through taxes: ${tax.account_head}, Amount: ${tax.tax_amount}`);

        if (tax.account_head.includes("CGST")) {
            total_cgst += tax.tax_amount || 0;
        } else if (tax.account_head.includes("SGST")) {
            total_sgst += tax.tax_amount || 0;
        } else if (tax.account_head.includes("IGST")) {
            total_igst += tax.tax_amount || 0;
        }
    });

    console.log("✅ Final Tax Totals:");
    console.log("CGST:", total_cgst);
    console.log("SGST:", total_sgst);
    console.log("IGST:", total_igst);

    frm.set_value("custom_cgst_total", total_cgst);
    frm.set_value("custom_sgst_total", total_sgst);
    frm.set_value("custom_igst_total", total_igst);

    console.log("✅ Tax values updated in the form!");
}