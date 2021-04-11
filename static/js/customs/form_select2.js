/* ------------------------------------------------------------------------------
*
*  # Select2 selects
*
*  Demo JS code for form_select2.html page
*
* ---------------------------------------------------------------------------- */

document.addEventListener('DOMContentLoaded', function() {

    // Select customer select2 initialization and formatting
    function formatCustomer (customer) {
        if (customer.loading) return customer.text;

        var markup = "<div class='select2-result-customer clearfix'>" +
            "<div class='select2-result-customer__name'><b>" + customer.name + "</b></div>" +
            "<div class='select2-result-customer__frigana'>【" + customer.frigana + "】</div>";
            if (customer.tel) {
                markup += "<div class='select2-result-customer__tel'>TEL : <b>" + customer.tel + "</b></div>";
            }
            if (customer.fax) {
                markup += "<div class='select2-result-customer__fax'>FAX : <b>" + customer.fax + "</b></div>";
            }
            markup += "</div>";
        return markup;
    }

    function formatCustomerSelection (customer) {
        return customer.name || customer.text;
    }

    $(".select-customer").select2({
        ajax: {
            url: "/master/search-customer/",
            dataType: 'json',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term,
                    page: params.page
                };
            },
            processResults: function (data, params) {
                params.page = params.page || 1;
                return {
                    results: data.customers,
                    pagination: {
                        more: (params.page * 30) < data.total_count
                    }
                };
            },
            cache: true
        },
        escapeMarkup: function (markup) { return markup; },
        // allowClear: true,
        minimumInputLength: 1,
        templateResult: formatCustomer,
        templateSelection: formatCustomerSelection
    });
    
    // customer-search select2 changed event
    $('.select-customer').on('select2:select', function(e) {
        var customer = e.params.data;
        var frigana = customer.frigana;
        var postal_code = customer.postal_code;
        var address = customer.address;
        var tel = customer.tel;
        var fax = customer.fax;

        if (frigana) {
            // updates the values only when admin selects the customer manually
            $('input[name="frigana"]').val(frigana);
            $('input[name="postal_code"]').val(postal_code);
            $('input[name="address"]').val(address);
            $('input[name="tel"]').val(tel);
            $('input[name="fax"]').val(fax);
    
            $('span.buyer-postal-code').text(postal_code);
            $('span.buyer-address').text(address);
            $('h4.buyer-company').text(customer.name);
            $('span.buyer-tel').text(tel);
            $('span.buyer-fax').text(fax);
        }
        
    });
    // End of select customer select2 initialization and formatting


    // Select hall select2 initialization and formatting
    function formatHall (hall) {
        if (hall.loading) return hall.text;

        var markup = "<div class='select2-result-hall clearfix'>" +
            "<div class='select2-result-hall__name'><b>" + hall.name + "</b></div>" +
            "<div class='select2-result-hall__frigana'>【" + hall.frigana + "】</div>";
            if (hall.tel) {
                markup += "<div class='select2-result-hallr__tel'>TEL : <b>" + hall.tel + "</b></div>";
            }
            if (hall.fax) {
                markup += "<div class='select2-result-hall__fax'>FAX : <b>" + hall.fax + "</b></div>";
            }
            markup += "</div>";
        return markup;
    }

    function formatHallSelection (hall) {
        return hall.name || hall.text;
    }

    $(".select-hall").select2({
        ajax: {
            url: "/master/search-hall/",
            dataType: 'json',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term,
                    page: params.page
                };
            },
            processResults: function (data, params) {
                params.page = params.page || 1;
                return {
                    results: data.halls,
                    pagination: {
                        more: (params.page * 30) < data.total_count
                    }
                };
            },
            cache: true
        },
        escapeMarkup: function (markup) { return markup; },
        // allowClear: true,
        minimumInputLength: 1,
        templateResult: formatHall,
        templateSelection: formatHallSelection
    });
    // End of select hall select2 initialization and formatting
    
    // hall-search select2 changed event
    $('.select-hall').on('select2:select', function(e) {
        var hall = e.params.data;
        var address = hall.address;
        var tel = hall.tel;

        $('input[name="address"]').val(address);
        $('input[name="tel"]').val(tel);
    });


    // Select product select2 initialization and formatting
    function formatProduct (product) {
        if (product.loading) return product.text;

        var markup = "<div class='select2-result-product clearfix'>" +
            "<div class='select2-result-product__name'><b>" + product.name + "</b></div></div>";
        return markup;
    }

    function formatProductSelection (product) {
        return product.name || product.text;
    }

    $('.select-product').select2({
        ajax: {
            url: "/master/search-product/",
            dataType: 'json',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term,
                    page: params.page
                };
            },
            processResults: function (data, params) {
                params.page = params.page || 1;
                return {
                    results: data.products,
                    pagination: {
                        more: (params.page * 30) < data.total_count
                    }
                };
            },
            cache: true
        },
        escapeMarkup: function (markup) { return markup; },
        // allowClear: true,
        minimumInputLength: 1,
        templateResult: formatProduct,
        templateSelection: formatProductSelection
    });
    // End of select hall select2 initialization and formatting

});
