/**
* This JS file is for additional new JS built over the existing theme
* ...so as to avoid breaking anything unexpectedly
*/
(function($) {

  var $body = $('body');

  $(document).ready(function() {
    alert('community js page');

    // icon
    $(".icon-telegram-developer").hover(function () {
      $(this).html('').html('<svg class="icon" aria-hidden="true"><use xlink:href="#iconicon_telegram_h"></use></svg>');
    }, function () {
      $(this).html('').html('<svg class="icon" aria-hidden="true"><use xlink:href="#iconicon_telegram"></use></svg>');
    });
    $(".icon-telegram-validator").hover(function () {
      $(this).html('').html('<svg class="icon" aria-hidden="true"><use xlink:href="#iconicon_telegram_h"></use></svg>');
    }, function () {
      $(this).html('').html('<svg class="icon" aria-hidden="true"><use xlink:href="#iconicon_telegram"></use></svg>');
    });

    $(".icon-twitter-community").hover(function () {
      $(this).html('').html('<svg class="icon" aria-hidden="true"><use xlink:href="#iconicon_twitter_h"></use></svg>');
    }, function () {
      $(this).html('').html('<svg class="icon" aria-hidden="true"><use xlink:href="#iconicon_twitter"></use></svg>');
    });
    $(".icon-email-community").hover(function () {
      $(this).html('').html('<svg class="icon" aria-hidden="true"><use xlink:href="#iconicon_email_h"></use></svg>');
    }, function () {
      $(this).html('').html('<svg class="icon" aria-hidden="true"><use xlink:href="#iconicon_email"></use></svg>');
    });

  });

})(jQuery);
