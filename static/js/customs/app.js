document.addEventListener('DOMContentLoaded', function() {

    // Set formset prefixes here
    var product_prefix = 'product';
    var document_prefix = 'document';

    // SetLang
    $('a[data-lang]').click(function(e) {
        e.stopImmediatePropagation();
        e.preventDefault();
        var url = document.URL.replace(/^(?:\/\/|[^/]+)*\/(ja|en)/, '');
      
        $.ajax({
            type: 'POST',
            url: '/i18n/setlang/',
            data: {
                language: $(e.currentTarget).data('lang'),
                next: '/'
            },
            beforeSend: function(request) {
                request.setRequestHeader('X-CSRFToken', csrftoken);
            }
        })
        .done(function(response) {
            window.location.href = url;
        });
    });

    function resetTotalFormNumber(prefix) {
        if ($('table.table-' + prefix + ' .odd').length) {
            $('#id_' + prefix + '-TOTAL_FORMS').val(0);
        }
    }
    // Adding the product to ProductFormSet based table
    $('button[name="add_product_btn"]').click( function (e) {
        // unless product is selected, nothing happens
        var value = $('select.select-product').val();
        if (value == "") return;

        resetTotalFormNumber(product_prefix);
        var data = $('select.select-product').select2('data');
        var product = data[0].name;
        $('select.select-product').val(null).trigger('change');
        
        if ($('table.table-product .odd').length) {
            $('table.table-product .odd').remove();
        }
        var formNum = parseInt($('#id_' + product_prefix + '-TOTAL_FORMS').val());
        var $hiddenTR = $('table.table-product #' + product_prefix + '-formset-row');
        var $newTR = $hiddenTR.clone().removeAttr('style').removeAttr('id').addClass('formset_row-' + product_prefix);
        $('#id_' + product_prefix + '-TOTAL_FORMS').val(formNum + 1);

        $hiddenTR.before($newTR);
        var formRegex = RegExp(`${product_prefix}-xx-`, 'g');
        var html = $newTR.html().replace(formRegex, `${product_prefix}-${formNum}-`);
        $newTR.html(html);

        var productID = `#id_${product_prefix}-${formNum}-id`;
        $(productID).val(value);
        var productName = `#id_${product_prefix}-${formNum}-name`;
        $(productName).val(product);

        $newTR.find(".new-selectbox").selectBoxIt({
            autoWidth: false
        });
    });


    // Adding change event lister to input field inside table-product
    $('table.table-product').on('keyup mousedown', 'input', function (e) {
        $parent = $(this).closest('tr');
    });


    // Form validator function for trader sales contract page
    $('form[name="trader_sales"]').submit( function (e) {
        var $form = $(this);
        var lang = $('input[name="selected-lang"]').val();

        // To prevent the cached total_form_num hidden value from being sent to the server,
        // reset it to zero if no product has been added.
        resetTotalFormNumber(product_prefix);
        
        // if customer is not selected
        // var customer = $form.find('select[name="name"]').val();
        // if (customer == "") {
        //     alert('Customer must be selected.');
        //     return false;
        // }

        // var personInCharge = $form.find('input[name="person_in_charge"]').val().trim();
        // if (personInCharge == "") {
        //     alert('Person in charge should be entered.');
        //     return false;
        // }

        // var formNum = $form.find('table.table-product #id_' + product_prefix + '-TOTAL_FORMS').val();
        // if (formNum == 0) {
        //     alert('At least one product should be added.');
        //     return false;
        // }

        /*
        // In case of Ajax POST request, i18n throws issues (403) because of automatic url pattern resolve.
        // lang prefix should be added to the url.
         */
        $.ajax({
            type: "POST",
            url: '/' + lang + '/contract/validate/trader-sales/',
            data: $(this).serialize(),
            dataType: 'json',
            success: function (result) {
                return true;
            },
            error: function (error) {
                alert('Products or documents should be added properly.');
                return false;
            }
        });
        return false;
    });

    
    // Form validator function for trader purchases contract page
    $('form[name="trader_purchases"]').submit( function (e) {
        return false;
    });


    // Form validator function for hall sales contract page
    $('form[name="hall_sales"]').submit( function (e) {
        return false;
    });


    // Form validator function for hall purchases contract page
    $('form[name="hall_purchases"]').submit( function (e) {
        return false;
    });

});