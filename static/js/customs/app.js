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

});