/* ------------------------------------------------------------------------------
*
*  # Date and time pickers
*
*  Demo JS code for picker_date.html page
*
* ---------------------------------------------------------------------------- */

document.addEventListener('DOMContentLoaded', function() {

    var lang = $('input[name="selected-lang"]').val();
    moment.locale(lang);
    
    // Date ranger picker with single date
    $('.daterange-single').daterangepicker({ 
        singleDatePicker: true
    });

    // Single picker
    $('.datepicker-milestone').datepicker({
        'defaultDate': null
    });
    
});
