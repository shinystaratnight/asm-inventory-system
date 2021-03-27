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


    // Adding the product to ProductFormSet based table
    $('button[name="add_product_btn"]').click( function (e) {
        var prefix = product_prefix;
        var value = $('select.select-product').val();
        if (value == "") return;

        var data = $('select.select-product').select2('data');
        var product = data[0].name;
        $('select.select-product').val(null).trigger('change');
        
        var formNum = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
        if (formNum == 0) $('table.table-product .odd').remove();

        var $hiddenTR = $('table.table-product #' + prefix + '-formset-row');
        var $newTR = $hiddenTR.clone().removeAttr('style').removeAttr('id').addClass('formset_row-' + prefix);
        $('#id_' + prefix + '-TOTAL_FORMS').val(formNum + 1);

        $hiddenTR.before($newTR);
        var formRegex = RegExp(`${prefix}-xx-`, 'g');
        var html = $newTR.html().replace(formRegex, `${prefix}-${formNum}-`);
        $newTR.html(html);

        var productID = `#id_${prefix}-${formNum}-id`;
        $(productID).val(value);
        var productName = `#id_${prefix}-${formNum}-name`;
        $(productName).val(product);

        $newTR.find(".new-selectbox").selectBoxIt({
            autoWidth: false
        });
    });


    // Adding change event lister to input field inside table-product
    $('table.table-product').on('keyup mousedown', 'input', function (e) {
        console.log($(this));
    });


    // Form validator function for trader sales contract page
    $('form[name="trader_sales"]').submit( function (e) {
        var $form = $(this);
        var lang = $('input[name="selected-lang"]').val();
        
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

        var formNum = $form.find('table.table-product #id_' + product_prefix + '-TOTAL_FORMS').val();
        if (formNum == 0) {
            alert('At least one product should be added.');
            return false;
        }

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