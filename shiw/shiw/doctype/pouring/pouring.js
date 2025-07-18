// Copyright (c) 2025, beetashoke.chakraborty@clapgrow.com and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Pouring", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Pouring', {
    onload: function (frm) {
        setTimeout(() => {
            const grid = frm.fields_dict["mould_batch"]?.grid;
            if (!grid || !grid.wrapper) return;

            grid.wrapper.on("focusin", function (e) {
                const $target = $(e.target);
                const grid_row_el = $target.closest(".grid-row");
                const grid_row = $(grid_row_el).data("grid_row");

                if (!grid_row || !grid_row.doc) return;

                // Handle mould_no focus
                if ($target.attr("data-fieldname") === "mould_no") {
                    const doctype_name = grid_row.get_field("moulding_system")?.value;
                    if (!doctype_name) return;

                    frappe.call({
                        method: "frappe.client.get_list",
                        args: {
                            doctype: doctype_name,
                            fields: ["name"],
                            limit_page_length: 1000
                        },
                        callback: function (r) {
                            if (r.message) {
                                const mould_names = r.message.map(d => d.name);
                                const mould_field = grid_row.get_field("mould_no");
                                if (mould_field) {
                                    mould_field.df.options = mould_names.join("\n");
                                    mould_field.refresh();
                                }

                                frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, "mould_no", "");
                                frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, "tooling_id", "");
                            }
                        }
                    });
                }

                // Handle tooling_id focus
                if ($target.attr("data-fieldname") === "tooling_id") {
                    const moulding_system = grid_row.get_field("moulding_system")?.value;
                    const mould_no = grid_row.get_field("mould_no")?.value;
                    if (!moulding_system || !mould_no) return;

                    frappe.call({
                        method: "frappe.client.get",
                        args: {
                            doctype: moulding_system,
                            name: mould_no
                        },
                        callback: function (r) {
                            if (r.message) {
                                let tooling_options = (r.message.mould_table || [])
                                    .map(item => item.tooling)
                                    .filter(Boolean);

                                const field = grid_row.get_field('tooling_id');
                                if (field) {
                                    field.df.options = tooling_options.join('\n');
                                    field.refresh();
                                    frappe.model.set_value(grid_row.doc.doctype, grid_row.doc.name, 'tooling_id', '');
                                }
                            }
                        }
                    });
                }
            });
        }, 300);
    }
});

frappe.ui.form.on('Mould Batch', {
    mould_batch_add: function (frm, cdt, cdn) {
        frappe.model.set_value(cdt, cdn, 'mould_no', '');
        frappe.model.set_value(cdt, cdn, 'tooling_id', '');
    },

    moulding_system: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (!row.moulding_system) {
            frappe.model.set_value(cdt, cdn, 'mould_no', '');
            frappe.model.set_value(cdt, cdn, 'tooling_id', '');
            frappe.model.set_value(cdt, cdn, 'quantity_available', '');
            return;
        }

        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: row.moulding_system,
                fields: ["name"],
                limit: 1000
            },
            callback: function (r) {
                if (r.message) {
                    let mould_names = r.message.map(d => d.name);
                    frm.fields_dict['mould_batch'].grid.update_docfield_property(
                        'mould_no',
                        'options',
                        mould_names.join('\n')
                    );

                    frappe.model.set_value(cdt, cdn, 'mould_no', '');
                    frappe.model.set_value(cdt, cdn, 'tooling_id', '');
                    frappe.model.set_value(cdt, cdn, 'quantity_available', '');
                }
            }
        });
    },

    mould_no: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let doctype_name = row.moulding_system;
        let mould_doc_name = row.mould_no;
        if (!doctype_name || !mould_doc_name) return;

        frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: doctype_name,
                name: mould_doc_name
            },
            callback: function (r) {
                if (r.message) {
                    let tooling_options = (r.message.mould_table || [])
                        .map(item => item.tooling)
                        .filter(Boolean);

                    let grid_row = frm.fields_dict['mould_batch'].grid.grid_rows_by_docname[cdn];
                    let tooling_field = grid_row?.get_field('tooling_id');

                    if (tooling_field) {
                        tooling_field.df.options = tooling_options.join('\n');
                        tooling_field.refresh();
                    }

                    frappe.model.set_value(cdt, cdn, 'tooling_id', '');
                    frappe.model.set_value(cdt, cdn, 'quantity_available', '');
                }
            }
        });
    },

    tooling_id: function (frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let doctype_name = row.moulding_system;
        let mould_doc_name = row.mould_no;
        let selected_tooling = row.tooling_id;

        if (!doctype_name || !mould_doc_name || !selected_tooling) return;

        frappe.call({
            method: "frappe.client.get",
            args: {
                doctype: doctype_name,
                name: mould_doc_name
            },
            callback: function (r) {
                if (r.message) {
                    let matched_row = (r.message.mould_table || [])
                        .find(item => item.tooling === selected_tooling);

                    if (matched_row) {
                        let qty = matched_row.mould_quantity || 0;
                        if (qty <= 0) {
                            frappe.msgprint({
                                title: "Invalid Tooling Selection",
                                message: `❌ You can't select "${selected_tooling}" because quantity is 0.`,
                                indicator: 'red'
                            });

                            frappe.model.set_value(cdt, cdn, 'tooling_id', '');
                            frappe.model.set_value(cdt, cdn, 'quantity_available', 0);
                        } else {
                            frappe.model.set_value(cdt, cdn, 'quantity_available', qty);
                        }
                    } else {
                        frappe.model.set_value(cdt, cdn, 'quantity_available', 0);
                    }
                }
            }
        });
    }
});
















