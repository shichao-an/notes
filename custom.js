$(window).load(function() {
  $('body').each(function () {
    var $spy = $(this).scrollspy('refresh')
  })
  $('table.js-file-line-container').removeClass('table table-striped table-hover');
});
