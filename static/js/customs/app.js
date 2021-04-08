document.addEventListener('DOMContentLoaded', function() {

    // Set formset prefixes here
    var product_prefix = 'product';
    var document_prefix = 'document';
    var document_fee_prefix = 'document_fee';
    var lang = $('input[name="selected-lang"]').val();

    // Reset the form total number in management form
    function resetTotalFormNumber(prefix) {
        if ($('table.table-' + prefix + ' .odd').length) {
            $('#id_' + prefix + '-TOTAL_FORMS').val(0);
        }
    }

    // Re-calculation of the price
    function calculateTotal() {
        var sub_total = 0;
        var insurance_fee = 0;
        $('table.table-product').each(function () {
            var $table = $(this);
            $table.find('tbody tr').each(function () {
                var $tr = $(this);
                var classname = $tr.attr('class');
                var rowRegex = RegExp(`formset_row-${product_prefix}`, 'g');
                if (rowRegex.test(classname)) {
                    var prefix = null;
                    var prefixRegex = RegExp(`${product_prefix}-\\d+-`, 'g');
                    var $amount = $tr.find('td').last().find('input');
                    var id = $amount.attr('id');
                    var m = id.match(prefixRegex);
                    if (m) prefix = m[0];
                    if (prefix) {
                        var amount = parseInt($amount.val());
                        var price = $('#id_' + prefix + 'price').val();
                        var quantity = $('#id_' + prefix + 'quantity').val();
                        var rounded_price = Math.round(price / 1000) * 1000;
                        var unit_fee = 0;
                        if (prefix.indexOf('product') !== -1) {
                            unit_fee = 100 * quantity;
                            if (rounded_price > 100000) {
                                // when rounded price is larger than 101,000
                                unit_fee = parseInt(200 * quantity * (rounded_price / 100000));
                            }
                        }
                        insurance_fee += unit_fee;
                        sub_total += amount;
                    }
                }
            });
        });

        $('table.table-document').each(function () {
            var $table = $(this);
            $table.find('tbody tr').each(function () {
                var $tr = $(this);
                var classname = $tr.attr('class');
                var rowRegex = RegExp(`formset_row-${document_prefix}`, 'g');
                if (rowRegex.test(classname)) {
                    var amount = parseInt($tr.find('td').last().find('input').val());
                    sub_total += amount;
                }
            });
        });

        $('table.table-document_fee').each(function () {
            var $table = $(this);
            $table.find('tbody tr').each(function () {
                var $tr = $(this);
                var classname = $tr.attr('class');
                var rowRegex = RegExp(`formset_row-${document_fee_prefix}`, 'g');
                if (rowRegex.test(classname)) {
                    var amount = parseInt($tr.find('td').last().find('input').val());
                    sub_total += amount;
                }
            });
        });

        $('td.sub_total').text(sub_total);
        var consumption_tax = parseInt(sub_total / 10);
        $('td.consumption_tax').text(consumption_tax);
        $('#insurance_fee').val(insurance_fee);
        var feeIncluded = true;
        if ($('#fee_free').length)
            feeIncluded = $('#fee_free').prop("checked");
        insuranceFeeCalculation(feeIncluded);
    }

    // Include/exclude insurance fee
    function insuranceFeeCalculation(included) {
        var sub_total = parseInt($('td.sub_total').text());
        var consumption_tax = parseInt($('td.consumption_tax').text());
        var insurance_tax = parseInt($('#insurance_fee').val());
        var total = sub_total + consumption_tax;
        if (included) {
            total += insurance_tax;
        }
        $('td.total').text(total);
        if ($('#billing_amount').length)
            $('#billing_amount').val(total);
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
            window.location.href = url;
        });
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
        resetTotalFormNumber(product_prefix);
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
        var productID = `#id_${product_prefix}-${formNum}-id`;
        $(productID).val(value);
        var productName = `#id_${product_prefix}-${formNum}-name`;
        $(productName).val(product);

        // after population, make the selectbox inside cloned tr work.
        $newTR.find(".new-selectbox").selectBoxIt({
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
        resetTotalFormNumber(document_prefix);
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
        var documentID = `#id_${document_prefix}-${formNum}-id`;
        $(documentID).val(value);
        var documentName = `#id_${document_prefix}-${formNum}-name`;
        $(documentName).val(document);
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

                resetTotalFormNumber(document_fee_prefix);
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
        var $parent = $self.closest('tr');
        var regex = RegExp(`${product_prefix}-\\d+-`, 'g');
        var prefix = null;
        var name = $self.attr('name');
        var m = name.match(regex);
        if (m) prefix = m[0];
        if (prefix) {
            var quantity = $parent.find('#id_' + prefix + 'quantity').val();
            var price = $parent.find('#id_' + prefix + 'price').val();
            var $amount = $parent.find('#id_' + prefix + 'amount');
            $amount.val(parseInt(quantity) * parseInt(price));
            calculateTotal();
        }
    });

    $('table.table-document').on('input', 'input', function (e) {
        var $self = $(this);
        var $parent = $self.closest('tr');
        var regex = RegExp(`${document_prefix}-\\d+-`, 'g');
        var prefix = null;
        var name = $self.attr('name');
        var m = name.match(regex);
        if (m) prefix = m[0];
        if (prefix) {
            var quantity = $parent.find('#id_' + prefix + 'quantity').val();
            var price = $parent.find('#id_' + prefix + 'price').val();
            var $amount = $parent.find('#id_' + prefix + 'amount');
            $amount.val(parseInt(quantity) * parseInt(price));
            calculateTotal();
        }
    });

    $('table.table-document_fee').on('input', 'input', function (e) {
        var $self = $(this);
        var $parent = $self.closest('tr');
        var regex = RegExp(`${document_fee_prefix}-\\d+-`, 'g');
        var prefix = null;
        var name = $self.attr('name');
        var m = name.match(regex);
        if (m) prefix = m[0];
        if (prefix) {
            var numOfModels = $parent.find('#id_' + prefix + 'number_of_models').val();
            var numOfUnits = $parent.find('#id_' + prefix + 'number_of_units').val();
            var applicationFee = $parent.find('input[name="application_fee"]').val();
            var modelPrice = $parent.find('input[name="model_price"]').val();
            var unitPrice = $parent.find('input[name="unit_price"]').val();
            var $amount = $parent.find('#id_' + prefix + 'amount');
            var amount = parseInt(numOfModels) * parseInt(modelPrice) + parseInt(numOfUnits) * parseInt(unitPrice) + parseInt(applicationFee);
            $amount.val(amount);
            calculateTotal();
        }
    });

    // when insurance fee value changes...
    $('#insurance_fee').on('input', function () {
        if ($('#fee_free').length) {
            insuranceFeeCalculation($('#fee_free').prop("checked"));
        } else
            insuranceFeeCalculation(true);
    });

    // when fee_fre checkbox is checked/unchecked...
    $('#fee_free').change(function () {
        insuranceFeeCalculation(this.checked);
    });

    $('select.select-sender').change(function (e) {
        var id = $(this).val();
        var $self = $(this);
        var $fs = $self.closest('fieldset');

        if (id == "") {
            $fs.find('textarea.address').val(null);
            $fs.find('input.tel').val(null);
            $fs.find('input.fax').val(null);
            return;
        }
        
        $.ajax({
            type: 'POST',
            url: `/${lang}/master/sender/`,
            data: {
                id: id,
            },
            beforeSend: function(request) {
                request.setRequestHeader('X-CSRFToken', csrftoken);
            },
            success: function (result) {
                $fs.find('textarea.address').val(result.address);
                $fs.find('input.tel').val(result.tel);
                $fs.find('input.fax').val(result.fax);
            }
        });
    });

    // Form validator function for trader sales contract page
    $('form[name="trader_sales"] button[type="submit"]').click( function (e) {
        e.preventDefault();
        var $form = $(this).closest('form');
        $form.attr('action', `/${lang}/contract/trader-sales/`);
        // To prevent the cached total_form_num hidden value from being sent to the server,
        // reset it to zero if no items has been added.
        resetTotalFormNumber(product_prefix);
        resetTotalFormNumber(document_prefix);
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
                $form.submit();
            }
        });
    });

    // Form validator function for trader purchases contract page
    $('form[name="trader_purchases"] button[type="submit"]').click( function (e) {
        e.preventDefault();
        var $form = $(this).closest('form');
        $form.attr('action', `/${lang}/contract/trader-purchases/`);
        resetTotalFormNumber(product_prefix);
        resetTotalFormNumber(document_prefix);
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
        resetTotalFormNumber(product_prefix);
        resetTotalFormNumber(document_prefix);
        resetTotalFormNumber(document_fee_prefix);
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
        resetTotalFormNumber(product_prefix);
        resetTotalFormNumber(document_prefix);
        resetTotalFormNumber(document_fee_prefix);
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