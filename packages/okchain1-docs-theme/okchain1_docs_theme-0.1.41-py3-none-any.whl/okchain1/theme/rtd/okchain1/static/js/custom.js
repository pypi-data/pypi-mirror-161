/**
* This JS file is for additional new JS built over the existing theme
* ...so as to avoid breaking anything unexpectedly
*/
(function($) {

  var $body = $('body');

  $(document).ready(function() {
  //web jumb
    var hostname = window.location.hostname;
    var href = window.location.href;
    if ( hostname.includes("okexchain-docs") ) {
      window.location.href = href.replace("okexchain-docs","okc-docs");
    }
    if ( hostname.includes("oec-docs") ) {
      window.location.href = href.replace("oec-docs","okc-docs");
    }

    /**
    * Dropdown menu
    */
    var triggers = document.querySelectorAll(
      '.main-nav li.menu-item-has-children'
    );
    var background = document.querySelector('.dropdownBackground');
    var nav = document.querySelector('.main-nav');

    function handleEnter() {
      this.classList.add('trigger-enter');
      setTimeout(
        () =>
        this.classList.contains('trigger-enter') &&
        this.classList.add('trigger-enter-active'),
        150
      );
      background.classList.add('open');

      var dropdown = this.querySelector('.main-nav .sub-menu');
      var dropdownCoords = dropdown.getBoundingClientRect();
      var navCoords = nav.getBoundingClientRect();

      var coords = {
        height: dropdownCoords.height,
        width: dropdownCoords.width,
        top: dropdownCoords.top - navCoords.top + 5,
        left: dropdownCoords.left - navCoords.left
      };

      background.style.setProperty('width', `${coords.width}px`);
      background.style.setProperty('height', `${coords.height}px`);
      background.style.setProperty(
        'transform',
        `translate(${coords.left}px, ${coords.top}px)`
      );
    }

    function handleLeave() {
      this.classList.remove('trigger-enter', 'trigger-enter-active');
      background.classList.remove('open');
    }

    triggers.forEach(trigger =>
      trigger.addEventListener('mouseenter', handleEnter)
    );
    triggers.forEach(trigger =>
      trigger.addEventListener('mouseleave', handleLeave)
    );

    /**
    * Set height on sidebar
    */
    var viewportHeight = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);
    var $sidebar = $('.bs-docs-sidebar');
    $sidebar.css('max-height', `${viewportHeight - 40}px`);




    // sidebar open / close
    $(".bs-docs-sidenav .caption-text").click(function () {
      $(this).toggleClass('close');
      $(this).parent().next().slideToggle();
    });





    // footer icon
    $(".footer-icon-twitter").hover(function () {
      $(this).html('').html('<svg class="icon" aria-hidden="true"><use xlink:href="#iconicon_twitter_h"></use></svg>');
    }, function () {
      $(this).html('').html('<svg class="icon" aria-hidden="true"><use xlink:href="#iconicon_twitter"></use></svg>');
    });
    $(".footer-icon-telegram").hover(function () {
      $(this).html('').html('<svg class="icon" aria-hidden="true"><use xlink:href="#iconicon_telegram_h"></use></svg>');
    }, function () {
      $(this).html('').html('<svg class="icon" aria-hidden="true"><use xlink:href="#iconicon_telegram"></use></svg>');
    });
    $(".footer-icon-email").hover(function () {
      $(this).html('').html('<svg class="icon" aria-hidden="true"><use xlink:href="#iconicon_email_h"></use></svg>');
    }, function () {
      $(this).html('').html('<svg class="icon" aria-hidden="true"><use xlink:href="#iconicon_email"></use></svg>');
    });
    $(".footer-icon-facebook").hover(function () {
      $(this).html('').html('<svg class="icon" aria-hidden="true"><use xlink:href="#iconicon_facebook_h"></use></svg>');
    }, function () {
      $(this).html('').html('<svg class="icon" aria-hidden="true"><use xlink:href="#iconicon_facebook"></use></svg>');
    });
    $(".footer-icon-Weibo").hover(function () {
      $(this).html('').html('<svg class="icon" aria-hidden="true"><use xlink:href="#iconicon_Weibo_h"></use></svg>');
    }, function () {
      $(this).html('').html('<svg class="icon" aria-hidden="true"><use xlink:href="#iconicon_Weibo"></use></svg>');
    });
    $(".footer-icon-WeChat").hover(function () {
      $(this).html('').html('<svg class="icon" aria-hidden="true"><use xlink:href="#iconicon_WeChat_h"></use></svg>');
    }, function () {
      $(this).html('').html('<svg class="icon" aria-hidden="true"><use xlink:href="#iconicon_WeChat"></use></svg>');
    });
    $(".footer-icon-QQ").hover(function () {
      $(this).html('').html('<svg class="icon" aria-hidden="true"><use xlink:href="#iconicon_QQ_h"></use></svg>');
    }, function () {
      $(this).html('').html('<svg class="icon" aria-hidden="true"><use xlink:href="#iconicon_QQ"></use></svg>');
    });
    $(".footer-icon-reddit").hover(function () {
      $(this).html('').html('<svg class="icon" aria-hidden="true"><use xlink:href="#iconicon_reddit_h"></use></svg>');
    }, function () {
      $(this).html('').html('<svg class="icon" aria-hidden="true"><use xlink:href="#iconicon_reddit"></use></svg>');
    });
  });

})(jQuery);
