window.onload = function() {
  AOS.init();
  $(function() {
    $(window).on("scroll", function() {
      if($(window).scrollTop() > 0) {
        $(".navbar li").css("color", "white");
        $(".navbar li a").css("color", "white");
        $(".navbar li a:hover").css("color", "#ff7363");
        $(".main-nav").addClass("nav-scroll");
      } else {
        $(".navbar li").css("color", "black");
        $(".navbar li a").css("color", "black");
        $(".navbar li a:hover").css("color", "white");
        $(".main-nav").removeClass("nav-scroll");
      }
    });

    $(window).scroll(function(){
      $(".scroll-indicator").css("opacity", 1 - $(window).scrollTop() / 300);
    });

    $("#navbar-home").click(function(){
      $('html, body').animate({
        scrollTop: 0
      }, 1000);
    });

    $("#navbar-about").click(function(){
      $('html, body').animate({
        scrollTop: $("#aboutheader").offset().top - 210
      }, 1000);
    });

    $("#navbar-contact").click(function(){
      $('html, body').animate({
        scrollTop: $(document).height()-$(window).height() + 1
      }, 1000);
    });

    $("#landingpagecontactbutton").click(function(){
      $('#form-main').toggle();
      $(".overlay").toggle();
    });

    $("#formclose").click(function(){
      $('#form-main').toggle();
      $(".overlay").toggle();
    });

    $.fn.extend({
      rotaterator: function(options) {
        var defaults = {
          fadeSpeed: 500,
          pauseSpeed: 100,
  				child: null
        };

        var options = $.extend(defaults, options);

        return this.each(function() {
          var o = options;
          var obj = $(this);
          var items = $(obj.children(), obj);
  			  items.each(function() {$(this).hide();})
  			  if(!o.child) {
            var next = $(obj).children(':first');
  				} else {
            var next = o.child;
  				}
  				$(next).fadeIn(o.fadeSpeed, function() {
  					$(next).delay(o.pauseSpeed).fadeOut(o.fadeSpeed, function() {
  					  var next = $(this).next();
  						if (next.length == 0) {
  							next = $(obj).children(':first');
  						}
  						$(obj).rotaterator({child : next, fadeSpeed : o.fadeSpeed, pauseSpeed : o.pauseSpeed});
  					})
  				});
        });
      }
    });

    $(document).ready(function() {
      $('.scroller-text').rotaterator ({
        fadeSpeed: 600, pauseSpeed: 1800
      });
    });
  });
}
$.fn.textWidth = function(text, font) {

    if (!$.fn.textWidth.fakeEl) $.fn.textWidth.fakeEl = $('<span>').hide().appendTo(document.body);

    $.fn.textWidth.fakeEl.text(text || this.val() || this.text() || this.attr('placeholder')).css('font', font || this.css('font'));

    return $.fn.textWidth.fakeEl.width();
};

$('.width-dynamic').on('input', function() {
    var inputWidth = $(this).textWidth();
    $(this).css({
        width: inputWidth
    })
}).trigger('input');


function inputWidth(elem, minW, maxW) {
    elem = $(this);
    console.log(elem)
}

var targetElem = $('.width-dynamic');

inputWidth(targetElem);