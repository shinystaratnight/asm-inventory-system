document.addEventListener('DOMContentLoaded', function() {

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
        var value = $('select.select-product').val();
        if (value == "") return;

        var data = $('select.select-product').select2('data');
        var product = data[0].name;
        $('select.select-product').val(null).trigger('change');
        
        var formNum = parseInt($('#id_form-TOTAL_FORMS').val());
        if (formNum == 0) $('table.table-product .odd').remove();

        var $hiddenTR = $('table.table-product #non-formset-row');
        var $newTR = $hiddenTR.clone().removeAttr('style').removeAttr('id').addClass('formset_row-form');
        $('#id_form-TOTAL_FORMS').val(formNum + 1);

        $hiddenTR.before($newTR);
        var formRegex = RegExp(`form-xx-`, 'g');
        var html = $newTR.html().replace(formRegex, `form-${formNum}-`);
        $newTR.html(html);

        var productID = `#id_form-${formNum}-id`;
        $(productID).val(value);
        var productName = `#id_form-${formNum}-name`;
        $(productName).val(product);

        $newTR.find(".new-selectbox").selectBoxIt({
            autoWidth: false
        });
    });


    // Adding change event lister to input field inside table-product
    $('table.table-product input[type="number"]').on('change', function (e) {
        alert("Changed");
    });

});