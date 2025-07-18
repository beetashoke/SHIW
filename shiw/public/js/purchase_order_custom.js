// frappe.ui.form.on('Purchase Order', {
//     onload: function (frm) {
//         console.log("🔄 Form loaded: Checking taxes table...");
//         frm.trigger("calculate_taxes_on_load");
//     },

//     refresh: function (frm) {
//         console.log("🔄 Form refreshed: Checking taxes table...");
//         frm.trigger("calculate_taxes_on_load");

//         // Detect item_code in child table and set custom_hsn
//         frm.doc.items.forEach(row => {
//             if (row.item_code && !row._item_code_logged) {
//                 row._item_code_logged = true;
//                 console.log("📦 Detected item_code:", row.item_code);

//                 // Fetch Item doc and set custom_hsn in the child row
//                 frappe.db.get_doc('Item', row.item_code).then(item_doc => {
//                     const hsn = item_doc.custom_hsn || '';
//                     console.log(`🔢 Fetched HSN for ${row.item_code}:`, hsn);
//                     frappe.model.set_value(row.doctype, row.name, 'custom_hsn', hsn);
//                 }).catch(err => {
//                     console.error(`❌ Failed to fetch Item doc for ${row.item_code}`, err);
//                     frappe.model.set_value(row.doctype, row.name, 'custom_hsn', '');
//                 });
//             }
//         });

//         // Fetch supplier data
//         if (frm.doc.supplier) {
//             frappe.db.get_doc('Supplier', frm.doc.supplier).then(supplier_doc => {
//                 console.log("✅ Supplier matched:", supplier_doc.name);
//                 console.log("🏷️ Tax Category from Supplier:", supplier_doc.tax_category);

//                 // For each item, fetch Item doc and inspect taxes table
//                 frm.doc.items.forEach((row, idx) => {
//                     if (row.item_code) {
//                         frappe.db.get_doc('Item', row.item_code).then(item_doc => {
//                             const taxes = item_doc.taxes || [];
//                             taxes.forEach(tax_row => {
//                                 if (tax_row.tax_category === supplier_doc.tax_category) {
//                                     console.log(`✅ Match found for ${row.item_code} → Item Tax Template: ${tax_row.item_tax_template}`);
//                                     frappe.model.set_value(row.doctype, row.name, 'item_tax_template', tax_row.item_tax_template);
//                                 }
//                             });
//                         }).catch(err => {
//                             console.error(`❌ Failed to fetch Item doc for ${row.item_code}`, err);
//                         });
//                     }
//                 });
//             }).catch(err => {
//                 console.error("❌ Failed to fetch Supplier doc:", err);
//             });
//         }
//     },

//     calculate_taxes_on_load: function (frm) {
//         // Ensure latest taxes are fetched
//         frm.refresh_field("taxes");

//         if (frm.doc.taxes && frm.doc.taxes.length > 0) {
//             console.log("📥 Taxes found in table, running calculations...");
//             calculate_taxes(frm);
//         } else {
//             console.log("⚠ No taxes found, skipping calculation.");
//         }
//     }
// });

// frappe.ui.form.on('Purchase Order Item', {
//     item_tax_template: function (frm, cdt, cdn) {
//         let row = locals[cdt][cdn];
//         console.log(`🏷 'item_tax_template' selected: ${row.item_tax_template}, recalculating taxes...`);
//         frm.refresh_field("taxes");
//         frappe.run_serially([
//             () => frappe.timeout(0.5),
//             () => calculate_taxes(frm)
//         ]);
//     },

//     price_list_rate: function (frm, cdt, cdn) {
//         console.log("💰 Price changed: Recalculating taxes...");
//         update_taxes_on_item_change(frm);
//     },

//     discount_percentage: function (frm, cdt, cdn) {
//         console.log("🎯 Discount changed: Recalculating taxes...");
//         update_taxes_on_item_change(frm);
//     },

//     custom_uom_conversion_: function (frm, cdt, cdn) {
//         let row = locals[cdt][cdn];
//         console.log("🟡 Button clicked in row:", row);

//         if (!row.qty || !row.conversion_factor) {
//             frappe.show_alert({
//                 message: "⚠️ Please ensure both 'Qty' and 'Conversion Factor' are filled.",
//                 indicator: 'orange'
//             });
//             console.warn("❌ Missing values. Qty:", row.qty, "Conversion Factor:", row.conversion_factor);
//             return;
//         }

//         row._is_converted = !row._is_converted;
//         console.log(`🔁 Toggled state for row ${cdn}: Converted =`, row._is_converted);

//         let new_stock_qty;
//         if (row._is_converted) {
//             new_stock_qty = row.qty / row.conversion_factor;
//             frappe.show_alert({
//                 message: `✅ Converted: Stock Qty = ${new_stock_qty.toFixed(2)}`,
//                 indicator: 'green'
//             });
//             console.log(`🧮 Converted: ${row.qty} / ${row.conversion_factor} = ${new_stock_qty}`);
//         } else {
//             new_stock_qty = row.qty * row.conversion_factor;
//             frappe.show_alert({
//                 message: `↩️ Reverted: Stock Qty = ${new_stock_qty.toFixed(2)}`,
//                 indicator: 'blue'
//             });
//             console.log(`🔄 Reverted: ${row.qty} * ${row.conversion_factor} = ${new_stock_qty}`);
//         }

//         frappe.model.set_value(cdt, cdn, 'stock_qty', new_stock_qty)
//             .then(() => {
//                 console.log(`✅ Updated stock_qty for row ${cdn}:`, new_stock_qty);
//             })
//             .catch(err => {
//                 console.error("❌ Failed to update stock_qty:", err);
//             });
//     }
// });

// frappe.ui.form.on('Purchase Taxes and Charges', {
//     taxes_add: function (frm) {
//         console.log("➕ Tax row added: Running calculations...");
//         frm.refresh_field("taxes");
//         calculate_taxes(frm);
//     },
//     taxes_remove: function (frm) {
//         console.log("❌ Tax row removed: Running calculations...");
//         frm.refresh_field("taxes");
//         calculate_taxes(frm);
//     },
//     tax_amount: function (frm) {
//         console.log("💰 Tax amount changed: Running calculations...");
//         frm.refresh_field("taxes");
//         calculate_taxes(frm);
//     },
//     account_head: function (frm) {
//         console.log("🔄 Account Head changed: Running calculations...");
//         frm.refresh_field("taxes");
//         calculate_taxes(frm);
//     }
// });

// function update_taxes_on_item_change(frm) {
//     console.log("🔄 Price or Discount Changed! Recalculating Taxes...");
//     frappe.timeout(0.5).then(() => {
//         frm.trigger("calculate_taxes_on_load");
//     });
// }

// function calculate_taxes(frm) {
//     console.log("🔄 Running tax calculation...");
//     frm.refresh_field("taxes");

//     if (!frm.doc.taxes || frm.doc.taxes.length === 0) {
//         console.log("⚠ No taxes found in the table.");
//         return;
//     }

//     console.log("🔍 Tax Table:", frm.doc.taxes);

//     let total_cgst = 0, total_sgst = 0, total_igst = 0;

//     $.each(frm.doc.taxes, function (index, tax) {
//         console.log(`Looping through taxes: ${tax.account_head}, Amount: ${tax.tax_amount}`);
//         if (tax.account_head.includes("CGST")) {
//             total_cgst += tax.tax_amount || 0;
//         } else if (tax.account_head.includes("SGST")) {
//             total_sgst += tax.tax_amount || 0;
//         } else if (tax.account_head.includes("IGST")) {
//             total_igst += tax.tax_amount || 0;
//         }
//     });

//     console.log("✅ Final Tax Totals:");
//     console.log("CGST:", total_cgst);
//     console.log("SGST:", total_sgst);
//     console.log("IGST:", total_igst);

//     frm.set_value("custom_cgst_total", total_cgst);
//     frm.set_value("custom_sgst_total", total_sgst);
//     frm.set_value("custom_igst_total", total_igst);

//     console.log("✅ Tax values updated in the form!");
// }