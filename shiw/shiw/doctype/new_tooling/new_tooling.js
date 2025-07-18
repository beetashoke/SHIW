// Copyright (c) 2025, beetashoke.chakraborty@clapgrow.com and contributors
// For license information, please see license.txt

// frappe.ui.form.on("New Tooling", {
// 	refresh(frm) {

// 	},
// });



frappe.ui.form.on("New Tooling", {
    onload: function (frm) {
        setTimeout(() => {
            const grid = frm.fields_dict["details_table"]?.grid;

            if (grid && grid.wrapper) {
                console.log("✅ Grid ready. Attaching pattern_id focus listener...");

                grid.wrapper.on("focusin", function (e) {
                    const $target = $(e.target);

                    if ($target.attr("data-fieldname") === "pattern_id") {
                        const grid_row_el = $target.closest(".grid-row");
                        const grid_row = $(grid_row_el).data("grid_row");

                        if (grid_row && grid_row.doc) {
                            const item_val = grid_row.doc.item;
                            const cdt = grid_row.doc.doctype;
                            const cdn = grid_row.doc.name;

                            console.log("🟡 pattern_id focused.");
                            console.log("📦 Corresponding item:", item_val);

                            if (item_val) {
                                frappe.call({
                                    method: "frappe.client.get",
                                    args: {
                                        doctype: "New Pattern Manufacturing Details",
                                        name: item_val,
                                    },
                                    callback: function (r) {
                                        if (r.message) {
                                            let table_romr = r.message.table_romr || [];
                                            let pattern_no_ids = table_romr.map(row => row.pattern_no_id);
                                            console.log("✅ Extracted pattern_no_id values:", pattern_no_ids);

                                            // Clear current pattern_id value
                                            frappe.model.set_value(cdt, cdn, "pattern_id", "");

                                            // ✅ Set dropdown options globally (applies to all rows)
                                            frm.fields_dict["details_table"].grid.update_docfield_property(
                                                "pattern_id",
                                                "options",
                                                [""].concat(pattern_no_ids).join("\n")
                                            );

                                            frm.refresh_field("details_table"); // force redraw
                                            console.log("✅ Dropdown updated with new pattern_no_ids");
                                        } else {
                                            console.warn("⚠ No matching document found for:", item_val);
                                        }
                                    }
                                });
                            } else {
                                console.warn("⚠ Item field is empty.");
                            }
                        }
                    }
                });
            }
        }, 500);
    },

    refresh(frm) {
        console.log("🔄 Form Refreshed");
        calculate_yield(frm);
    },

    bunch_weight(frm) {
        console.log("📦 Bunch Weight changed:", frm.doc.bunch_weight);
        calculate_yield(frm);
    }
});

frappe.ui.form.on("Tooling Item Details table", {
    item: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];  // Get the selected row
        console.log("▶ Selected Item:", row.item);

        if (row.item) {
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "New Pattern Manufacturing Details",
                    name: row.item
                },
                callback: function (r) {
                    if (r.message) {
                        console.log("✅ Matching Document Found:", r.message);

                        let table_romr = r.message.table_romr || [];
                        console.log("▶ Child Table Data:", table_romr);

                        if (table_romr.length > 0) {
                            console.log("▶ Available Fields in Child Record:", Object.keys(table_romr[0]));

                            // Extract pattern_no_id values
                            let pattern_no_ids = table_romr.map(row => row.pattern_no_id);
                            console.log("✅ Extracted pattern_no_id values:", pattern_no_ids);

                            // Clear existing value
                            frappe.model.set_value(cdt, cdn, "pattern_id", "");

                            // ✅ Correct way to update dropdown options inside a child table
                            frm.fields_dict["details_table"].grid.update_docfield_property(
                                "pattern_id", "options", [""].concat(pattern_no_ids).join("\n")
                            );

                            frm.refresh_field("details_table");  // Refresh the child table

                            console.log("✅ Updated dropdown options for pattern_id:", pattern_no_ids);

                        } else {
                            console.warn("⚠ No Child Data Found for pattern_no_id.");
                        }
                    } else {
                        console.warn("⚠ No Matching Record Found for:", row.item);
                    }
                }
            });
        }
    },

    casting_weight(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        console.log("✅ Casting Weight Changed in Row:", row.name, "New Value:", row.casting_weight);
        calculate_yield(frm);
    },

    cavity(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        console.log("🟣 Cavity Changed in Row:", row.name, "New Value:", row.cavity);
        calculate_yield(frm);
    },

    details_table_add(frm) {
        console.log("➕ New Row Added.");
        calculate_yield(frm);
    },

    details_table_remove(frm) {
        console.log("❌ Row Removed.");
        calculate_yield(frm);
    }
});

// 🔄 Updated Calculation Logic
function calculate_yield(frm) {
    console.log("🔄 Recalculating Yield...");

    let total_casting_weight = 0;

    if (frm.doc.details_table && Array.isArray(frm.doc.details_table)) {
        frm.doc.details_table.forEach(row => {
            let casting_weight = row.casting_weight || 0;
            let cavity = row.cavity || 1; // 👈 Default to 1 if not given

            let effective_weight = casting_weight * cavity;
            console.log(`🎯 Row: ${row.name} | Casting Weight: ${casting_weight} | Cavity: ${cavity} | Effective Weight: ${effective_weight}`);

            total_casting_weight += effective_weight;
        });
    }

    let bunch_weight = frm.doc.bunch_weight || 0;
    let runner_riser_weight = bunch_weight - total_casting_weight;
    let yield_value = bunch_weight !== 0 ? (total_casting_weight / bunch_weight) * 100 : 0;

    console.log("🔹 Total Casting Weight:", total_casting_weight);
    console.log("🔸 Runner Riser Weight:", runner_riser_weight);
    console.log("✅ Final Yield:", yield_value);

    frm.set_value('total_casting_weight', total_casting_weight);
    frm.set_value('runner_riser_weight', runner_riser_weight);
    frm.set_value('yield', yield_value);

    frm.refresh_field("total_casting_weight");
    frm.refresh_field("runner_riser_weight");
    frm.refresh_field("yield");
}