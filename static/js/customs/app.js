// Reset the form total number in management form
function resetMangementForm(prefix) {
    var numTotalForms = $('table.table-' + prefix + ' tr[class^="formset_row-"]').length;
    $('#id_' + prefix + '-TOTAL_FORMS').val(numTotalForms);
}

document.addEventListener('DOMContentLoaded', function() {

    // Set formset prefixes here
    var product_prefix = 'product';
    var document_prefix = 'document';
    var document_fee_prefix = 'document_fee';
    var lang = $('input[name="selected-lang"]').val();

    // Re-calculation of the price
    function calculateFees() {
        var sub_total = 0;
        var tax_sum = 0;
        var fee_sum = 0;
        $('table.table-formset').each(function () {
            var $table = $(this);
            $table.find('tbody tr[class^="formset_row-"]').each(function () {
                var $tr = $(this);
                var amount = parseInt($tr.find('input[name$="-amount"]').val());
                sub_total += amount;
                var tax = parseInt($tr.find('input[name$="-tax"]').val());
                tax_sum += tax;
                if ($tr.find('input[name$="-fee"]').length) {
                    var fee = parseInt($tr.find('input[name$="-fee"]').val());
                    fee_sum += fee;
                }
            });
        });

        $('#id_sub_total').val(sub_total);
        $('#id_tax').val(tax_sum);
        $('#id_fee').val(fee_sum);
        calculateTotal();
    }

    // Include/exclude insurance fee
    function calculateTotal() {
        var sub_total = parseInt($('#id_sub_total').val());
        var tax = parseInt($('#id_tax').val());
        var fee = parseInt($('#id_fee').val());
        var total = sub_total + tax + fee;
        $('#id_total').val(total);
        if ($('#id_billing_amount').length)
            $('#id_billing_amount').val(total);
    }

    // SetLang
    $('a[data-lang]').click(function(e) {
        e.stopImmediatePropagation();
        e.preventDefault();
        var new_lang = $(e.currentTarget).data('lang');
        if (lang == new_lang) return;

        var url = document.URL.replace(/^(?:\/\/|[^/]+)*\/(ja|en)/, '');
      
        $.ajax({
            type: 'POST',
            url: '/i18n/setlang/',
            data: {
                language: new_lang,
                next: '/'
            },
            beforeSend: function(request) {
                request.setRequestHeader('X-CSRFToken', csrftoken);
            }
        })
        .done(function() {
            // Remove URL parameters to avoid date format inconsistency b/w English and Japanese
            window.location.href = url.split('?')[0];
        });
    });


    // Delete the selected row and update the formset management
    function deleteRow($table) {
        var $inputTotalForm = $table.find('input[name$="-TOTAL_FORMS"]');
        var numOfItems = parseInt($inputTotalForm.val());
        $inputTotalForm.val(numOfItems - 1);
        var index = 0;
        $table.find('tr[class^="formset_row-"]').each(function (e) {
            $tr = $(this);
            $tr.find('input, select').each(function (e) {
                var el_name = $(this).attr('name');
                el_name = el_name.replace(/\d+/, index);
                $(this).attr('name', el_name);
                $(this).attr('id', 'id_' + el_name);
            });
            index++;
            $tr.find('select.product-type-selectbox').selectBoxIt('destroy');
            $tr.find('select.product-type-selectbox').selectBoxIt({
                autoWidth: false
            });
        });
    }

    // Clicking on delete(-) button in each row inside product/document/documentfee tables
    $('table').on('click', 'a[name="delete_data"]', function (e) {
        e.preventDefault();
        $this = $(this);
        $tr = $this.closest('tr');
        $table = $tr.closest('table');
        $tr.remove();
        deleteRow($table);
        calculateFees();
    });

    // Adding the product to ProductFormSet based table
    $('button[name="add_product_btn"]').click( function (e) {
        // unless product is selected, nothing happens
        var value = $('select.select-product').val();
        if (value == "") {
            $('#modal_product_error').modal('toggle');
            return;
        }
        // reset total number of forms in management form section if there is any cached value
        // after adding selected product name, reset the select2 back to empty option
        resetMangementForm(product_prefix);
        var data = $('select.select-product').select2('data');
        var product = data[0].name;
        $('select.select-product').val(null).trigger('change');
        if ($('table.table-product .odd').length) {
            $('table.table-product .odd').remove();
        }

        // Clone the hiddent formset-row and populate the selected product id/name into the cloned td fields
        var formNum = parseInt($('#id_' + product_prefix + '-TOTAL_FORMS').val());
        var $hiddenTR = $('table.table-product #' + product_prefix + '-formset-row');
        var $newTR = $hiddenTR.clone().removeAttr('style').removeAttr('id').addClass('formset_row-' + product_prefix);
        $('#id_' + product_prefix + '-TOTAL_FORMS').val(formNum + 1);
        $hiddenTR.before($newTR);
        var trRegex = RegExp(`${product_prefix}-xx-`, 'g');
        var html = $newTR.html().replace(trRegex, `${product_prefix}-${formNum}-`);
        $newTR.html(html);
        var productID = `#id_${product_prefix}-${formNum}-product_id`;
        $(productID).val(value);
        var productName = `#id_${product_prefix}-${formNum}-name`;
        $(productName).val(product);

        // after population, make the selectbox inside cloned tr work.
        $newTR.find("select").addClass('product-type-selectbox').selectBoxIt({
            autoWidth: false
        });
    });
    
    // When clicking "Add Document" button
    $('button[name="add_document_btn"]').click( function (e) {
        // unless any document is selected, nothing happens
        var value = $('select.select-document').val();
        var document = $('select.select-document').children("option:selected").text();
        if (value == "") {
            $('#modal_document_error').modal('toggle');
            return;
        }

        // reset total number of forms in management form section if there is any cached value
        // after adding selected product name, reset the selectbox
        resetMangementForm(document_prefix);
        if ($('table.table-document .odd').length) {
            $('table.table-document .odd').remove();
        }
        $('select.select-document').val("").trigger('change');

        // Clone the hiddent formset-row and populate the selected document id/name into the cloned td fields
        var formNum = parseInt($('#id_' + document_prefix + '-TOTAL_FORMS').val());
        var $hiddenTR = $('table.table-document #' + document_prefix + '-formset-row');
        var $newTR = $hiddenTR.clone().removeAttr('style').removeAttr('id').addClass('formset_row-' + document_prefix);
        $('#id_' + document_prefix + '-TOTAL_FORMS').val(formNum + 1);
        $hiddenTR.before($newTR);
        var trRegex = RegExp(`${document_prefix}-xx-`, 'g');
        var html = $newTR.html().replace(trRegex, `${document_prefix}-${formNum}-`);
        $newTR.html(html);
        var documentID = `#id_${document_prefix}-${formNum}-document_id`;
        $(documentID).val(value);
        var documentName = `#id_${document_prefix}-${formNum}-name`;
        $(documentName).val(document);
        $.ajax({
            type: 'POST',
            url: `/${lang}/contract/check-taxable/`,
            data: {
                id: value,
            },
            beforeSend: function(request) {
                request.setRequestHeader('X-CSRFToken', csrftoken);
            },
            success: function (result) {
                var taxable = result.taxable;
                $(`#id_${document_prefix}-${formNum}-taxable`).val(taxable);
            }
        });
    });

    // When clicking "Add Document Fee" button
    $('button[name="add_document_fee_btn"]').click( function (e) {
        // unless any document is selected, nothing happens
        var value = $('select.select-document-fee').val();
        var document_fee = $('select.select-document-fee').children("option:selected").text();
        if (value == "") {
            $('#modal_document_fee_error').modal('toggle');
            return;
        }
        $.ajax({
            type: 'POST',
            url: `/${lang}/master/document-fee/`,
            data: {
                id: value,
            },
            beforeSend: function(request) {
                request.setRequestHeader('X-CSRFToken', csrftoken);
            },
            success: function (result) {
                var model_price = result.model_price;
                var unit_price = result.unit_price;
                var application_fee = result.application_fee;

                resetMangementForm(document_fee_prefix);
                if ($('table.table-document_fee .odd').length) {
                    $('table.table-document_fee .odd').remove();
                }
                $('select.select-document-fee').val("").trigger('change');

                // Clone the hiddent formset-row and populate the selected document id/name into the cloned td fields
                var formNum = parseInt($('#id_' + document_fee_prefix + '-TOTAL_FORMS').val());
                var $hiddenTR = $('table.table-document_fee #' + document_fee_prefix + '-formset-row');
                var $newTR = $hiddenTR.clone().removeAttr('style').removeAttr('id').addClass('formset_row-' + document_fee_prefix);
                $newTR.find('input[name="model_price"]').val(model_price);
                $newTR.find('input[name="unit_price"]').val(unit_price);
                $newTR.find('input[name="application_fee"]').val(application_fee);
                $('#id_' + document_fee_prefix + '-TOTAL_FORMS').val(formNum + 1);
                $hiddenTR.before($newTR);
                var trRegex = RegExp(`${document_fee_prefix}-xx-`, 'g');
                var html = $newTR.html().replace(trRegex, `${document_fee_prefix}-${formNum}-`);
                $newTR.html(html);
                var documentFeeID = `#id_${document_fee_prefix}-${formNum}-id`;
                $(documentFeeID).val(value);
                var documentFeeName = `#id_${document_fee_prefix}-${formNum}-name`;
                $(documentFeeName).val(document_fee);
            }
        });
    });

   // Adding change event lister to input field inside table-product
    $('table.table-product').on('input', 'input', function (e) {
        // Calculate quantity * price and set it in id_product-xx-amount td element
        var $self = $(this);
        var $tr = $self.closest('tr');
        var trClassName = $tr.attr('class');
        if (trClassName.startsWith('formset_row-') == false) return;
        var price = $tr.find('input[name$="-price"]').val();
        var quantity = $tr.find('input[name$="-quantity"]').val();
        var amount = parseInt(price) * parseInt(quantity);
        var tax = parseInt(amount * 0.1);
        var fee = 100 * quantity;
        var rounded_price = Math.round(price / 1000) * 1000;
        if (rounded_price > 100000) {
            fee = parseInt(200 * quantity * (rounded_price / 100000));
        }
        $tr.find('input[name$="-amount"]').val(amount);
        $tr.find('input[name$="-tax"]').val(tax);
        $tr.find('input[name$="-fee"]').val(fee);
        calculateFees();
    });

    $('table.table-document').on('input', 'input', function (e) {
        var $self = $(this);
        var $tr = $self.closest('tr');
        var trClassName = $tr.attr('class');
        if (trClassName.startsWith('formset_row-') == false) return;
        var price = $tr.find('input[name$="-price"]').val();
        var quantity = $tr.find('input[name$="-quantity"]').val();
        var amount = parseInt(price) * parseInt(quantity);
        var taxable = parseInt($tr.find('input[name$="-taxable"]').val());
        var tax = 0;
        if (taxable) tax = parseInt(amount * 0.1);
        $tr.find('input[name$="-amount"]').val(amount);
        $tr.find('input[name$="-tax"]').val(tax);
        calculateFees();
    });

    $('table.table-document_fee').on('input', 'input', function (e) {
        var $self = $(this);
        var $tr = $self.closest('tr');
        var trClassName = $tr.attr('class');
        if (trClassName.startsWith('formset_row-') == false) return;
        var modelCount = $tr.find('input[name$="-model_count"]').val();
        var unitCount = $tr.find('input[name$="-unit_count"]').val();
        var applicationFee = $tr.find('input[name$="-application_fee"]').val();
        var modelPrice = $tr.find('input[name$="-model_price"]').val();
        var unitPrice = $tr.find('input[name$="-unit_count"]').val();
        var amount = parseInt(modelCount) * parseInt(modelPrice) + parseInt(unitCount) * parseInt(unitPrice) + parseInt(applicationFee);
        var tax = parseInt(amount * 0.1);
        $tr.find('input[name$="-amount"]').val(amount);
        $tr.find('input[name$="-tax"]').val(tax);
        calculateFees();
    });

    // when insurance fee value changes...
    $('#id_fee').on('input', function () {
        calculateTotal();
    });

    // when fee_fre checkbox is checked/unchecked...
    $('#fee_edit').change(function () {
        if (this.checked) $('#id_fee').prop('readonly', false); else $('#id_fee').prop('readonly', true);
    });

    // Form validator function for trader sales contract page
    $('form[name="trader_sales"] button[type="submit"]').click( function (e) {
        e.preventDefault();
        var $form = $(this).closest('form');
        // To prevent the cached total_form_num hidden value from being sent to the server,
        // reset it to zero if no items has been added.
        resetMangementForm(product_prefix);
        resetMangementForm(document_prefix);
        /*
        // In case of Ajax POST request, i18n throws issues (403) because of automatic url pattern resolve.
        // lang prefix should be added to the url.
         */
        $.ajax({
            type: "POST",
            url: `/${lang}/contract/validate/trader-sales/`,
            data: $form.serialize(),
            dataType: 'json',
            success: function (result) {
                if (('success' in result) && result['success'] == false) {
                    $('#modal_trader_sales_error').modal('toggle');
                    return false;
                }
                $form.attr('action', $(location).attr('href'));
                $form.submit();
            }
        });
    });

    // Form validator function for trader purchases contract page
    $('form[name="trader_purchases"] button[type="submit"]').click( function (e) {
        e.preventDefault();
        var $form = $(this).closest('form');
        $form.attr('action', `/${lang}/contract/trader-purchases/`);
        resetMangementForm(product_prefix);
        resetMangementForm(document_prefix);
        $.ajax({
            type: "POST",
            url: `/${lang}/contract/validate/trader-purchases/`,
            data: $form.serialize(),
            dataType: 'json',
            success: function (result) {
                if (('success' in result) && result['success'] == false) {
                    $('#modal_trader_purchases_error').modal('toggle');
                    return false;
                }
                $form.submit();
            }
        });
    });

    // Form validator function for hall sales contract page
    $('form[name="hall_sales"] button[type="submit"]').click( function (e) {
        e.preventDefault();
        var $form = $(this).closest('form');
        $form.attr('action', `/${lang}/contract/hall-sales/`);
        resetMangementForm(product_prefix);
        resetMangementForm(document_prefix);
        resetMangementForm(document_fee_prefix);
        $.ajax({
            type: "POST",
            url: `/${lang}/contract/validate/hall-sales/`,
            data: $form.serialize(),
            dataType: 'json',
            success: function (result) {
                if (('success' in result) && result['success'] == false) {
                    $('#modal_hall_sales_error').modal('toggle');
                    return false;
                }
                $form.submit();
            }
        });
    });

    // Form validator function for hall purchases contract page
    $('form[name="hall_purchases"] button[type="submit"]').click( function (e) {
        e.preventDefault();
        var $form = $(this).closest('form');
        $form.attr('action', `/${lang}/contract/hall-purchases/`);
        resetMangementForm(product_prefix);
        resetMangementForm(document_prefix);
        resetMangementForm(document_fee_prefix);
        $.ajax({
            type: "POST",
            url: `/${lang}/contract/validate/hall-purchases/`,
            data: $form.serialize(),
            dataType: 'json',
            success: function (result) {
                if (('success' in result) && result['success'] == false) {
                    $('#modal_hall_purchases_error').modal('toggle');
                    return false;
                }
                $form.submit();
            }
        });
    });

});