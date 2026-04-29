$(function ($) {
  "use strict";

  jQuery(document).ready(function () {

    // preloader
    $("#preloader").delay(300).animate({
      "opacity": "0"
    }, 500, function () {
      $("#preloader").css("display", "none");
    });

    // Scroll Top
    var ScrollTop = $(".scrollToTop");
    $(window).on('scroll', function () {
      if ($(this).scrollTop() < 500) {
        ScrollTop.removeClass("active");
      } else {
        ScrollTop.addClass("active");
      }
    });
    $('.scrollToTop').on('click', function () {
      $('html, body').animate({
        scrollTop: 0
      }, 500);
      return false;
    });

    // Navbar Dropdown
    $(window).resize(function () {
      if ($(window).width() < 992) {
        $(".dropdown-menu").removeClass('show');
      }
      else {
        $(".dropdown-menu").addClass('show');
      }
    });
    if ($(window).width() < 992) {
      $(".dropdown-menu").removeClass('show');
    }
    else {
      $(".dropdown-menu").addClass('show');
    }

    // Sticky Header
    var fixed_top = $(".header-section");
    $(window).on("scroll", function () {
      if ($(window).scrollTop() > 50) {
        fixed_top.addClass("animated fadeInDown header-fixed");
      }
      else {
        fixed_top.removeClass("animated fadeInDown header-fixed");
      }
    });

    // Remittance active
    var remittance = $(".remittance .single-box");
    $(remittance).on('mouseover', function () {
        $(remittance).removeClass('active');
        $(this).addClass('active');
    });

    // social link active
    var socialLink = $(".social-link a");
    $(socialLink).on('mouseover', function () {
        $(socialLink).removeClass('active');
        $(this).addClass('active');
    });


    // Function to calculate monthly payment
    function calculateMonthlyPayment(loanAmount, interestRate, tenure) {
      var monthlyInterestRate = (interestRate / 100) / 12;
      var numberOfPayments = tenure * 12;
      var monthlyPayment = loanAmount * monthlyInterestRate / (1 - Math.pow(1 + monthlyInterestRate, -numberOfPayments));
      return monthlyPayment.toFixed(2);
    }

    // Function to calculate total payment
    function calculateTotalPayment(monthlyPayment, numberOfPayments) {
        return (monthlyPayment * numberOfPayments).toFixed(2);
    }

    // Update results when input changes
    $('input').on('input', function(){
        var loanAmount = parseFloat($('.loan-amount input').val());
        var interestRate = parseFloat($('.interest-rate input').val());
        var tenure = parseFloat($('.tenure input').val());
        var mainAmount = parseFloat($('.home-amount input').val());

        var monthlyPayment = calculateMonthlyPayment(loanAmount, interestRate, tenure);
        var numberOfPayments = tenure * 12;
        var totalPayment = calculateTotalPayment(monthlyPayment, numberOfPayments);

        $('#ratioInterest').text(totalPayment-loanAmount);

        $('.interestRate').text(interestRate+'%');
        $('.totalPayment').text('$'+totalPayment);
        $('.monthlyPayment').text(monthlyPayment);
        $('.mainAmountShow').text(mainAmount);
    });
    
    $('input').trigger('input');

    if (document.querySelector('#chart') !== null) {

      function renderChart(mainAmount, ratioInterest) {

          var mainAmount = parseFloat($('.home-amount input').val());
          
          var ratioInterest = $('#ratioInterest')[0].innerHTML;
          
          function roundToNearest(number) {
            return Math.round(number);
          }
          var ratioInterest = roundToNearest(ratioInterest);
          
          var options = {
            series: [mainAmount, ratioInterest],
            chart: {
              width: 380,
              type: 'pie',
          },
          labels: ['Main Amount', 'Ratio Interest'],
          legend: {
            position: 'top',
            horizontalAlign: 'left',
          },
          colors:['#1A4DBE', '#055C2D'],
          dataLabels: {
            style: {
              colors: ['#fff', '#fff']
            }
          },
          
          responsive: [{
            breakpoint: 480,
            options: {
              chart: {
                width: 250
              },
            }
          }]

        };

        var chart = new ApexCharts(document.querySelector("#chart"), options);
        chart.render();

      }

      var mainAmount = parseFloat($('.home-amount input').val());
      var ratioInterest = parseFloat($('.interest-rate input').text());
      renderChart(mainAmount, ratioInterest);

      $('input').on('input', function(){
        var mainAmount = parseFloat($('.home-amount input').val());
        var ratioInterest = parseFloat($('.interest-rate input').text());
        renderChart(mainAmount, ratioInterest);
      });
    
    }

    $('.range-slider').each(function(index) {
      var $input = $(this);
      var $valueSpan = $('.range-value').eq(index);
      
      $input.css('--min', $input.attr('min'));
      $input.css('--max', $input.attr('max'));
      $input.css('--value', $input.val());

      $valueSpan.text($(this).val());

      var $homeInput = $('.home-amount input');

      var $downInput = $('.down-payment input');
      var $downValueSpan = $('.down-payment .range-value');
      var $downCaption = $('.down-payment .caption-bottom p:last-child');

      var $loanInput = $('.loan-amount input');
      var $loanValueSpan = $('.loan-amount .range-value');
      var $loanCaption = $('.loan-amount .caption-bottom p:last-child');

      $downValueSpan.text($homeInput.val());
      $downCaption.text('$' + $homeInput.val());

      $downInput.css('--max', $homeInput.val());
      $downInput.css('--value', $homeInput.val());

      $downInput.attr('max', $homeInput.val());
      $downInput.attr('value', $homeInput.val());

      var $loanValueSpanVal = $homeInput.val() - $downInput.val();
      
      $loanInput.css('--max', $homeInput.val());
      $loanInput.css('--value', $loanValueSpanVal);

      $loanInput.attr('max', $homeInput.val());
      $loanInput.attr('value', $loanValueSpanVal);

      $loanCaption.text('$' + $homeInput.val());

      $input.on('input', function() {
        $valueSpan.text($(this).val());
        $(this).css('--value', $(this).val());

        if (index === 0) {

          $downInput.attr('max', $(this).val());
          $downCaption.text('$' + $(this).val());
          $downValueSpan.text($(this).val());

          var $downValueSpanVal = $homeInput.val() - $loanInput.val();
          $downValueSpan.text($downInput.val());        

          $downInput.css('--max', $downInput.attr('max'));
          $downInput.css('--value', $downInput.val());

          var $loanValueSpanVal = $homeInput.val() - $downInput.val();
          $loanValueSpan.text($loanValueSpanVal);

          $loanInput.attr('max', $(this).val());
          $loanInput.attr('value', $loanValueSpanVal);
          $loanCaption.text('$' + $(this).val());

          $loanInput.css('--min', '0');
          $loanInput.css('--max', $loanInput.attr('max'));
          $loanInput.css('--value', $loanValueSpanVal);

        }

        if (index === 1) {

          var $loanValueSpanVal = $homeInput.val() - $downInput.val();
          $loanValueSpan.text($loanValueSpanVal);

          $loanInput.attr('max', $homeInput.val());
          $loanInput.attr('value', $loanValueSpanVal);
          
          $loanInput.css('--max', $loanInput.attr('max'));
          $loanInput.css('--value', $loanValueSpanVal);

          var $downValueSpanVal = $homeInput.val() - $loanInput.attr('value');
          $downInput.css('--value', $downValueSpanVal);

        }

      });

    });

    // stylesheet disabled enabled
    function toggleStylesheet(stylesheet) {
      if (stylesheet === 'rtl') {
        $('#rtl-stylesheet').prop('disabled', false);
        $('#ltr-stylesheet').prop('disabled', true);
        localStorage.setItem('selectedStylesheet', 'rtl');
        $('html, body').addClass('rtl-active');
      } else {
        $('#ltr-stylesheet').prop('disabled', false);
        $('#rtl-stylesheet').prop('disabled', true);
        localStorage.setItem('selectedStylesheet', 'ltr');
        $('html, body').removeClass('rtl-active');
      }
    }
  
    // Check local storage for selected stylesheet
    var selectedStylesheet = localStorage.getItem('selectedStylesheet');
    if (selectedStylesheet) {
      toggleStylesheet(selectedStylesheet);
    }
  
    // Button click event handlers
    $('#btn-ltr').on('click', function(){
      toggleStylesheet('ltr');
      $('html, body').removeClass('rtl-active');
    });
  
    $('#btn-rtl').on('click', function(){
      toggleStylesheet('rtl');
      $('html, body').addClass('rtl-active');
    });

    // Navbar Auto Active Class 
    var curUrl = $(location).attr('href');
    var terSegments = curUrl.split("/");
    var desired_segment = terSegments[terSegments.length - 1];
    var removeGarbage = desired_segment.split(".html")[0] + ".html";
    var checkLink = $('.navbar-nav a[href="' + removeGarbage + '"]');
    var targetClass = checkLink.addClass('active');
    targetClass.parents('.sub-navbar').addClass('active-parents');
    targetClass.parents('.main-navbar').addClass('active-parents');
    $('.active-parents > a').addClass('active');

    // Dragging 
    var isDragging = false;
    var startX, initialLeft;

    // When mouse or touch starts on draggable div
    $('#draggableDiv').on('mousedown touchstart', function(e) {
        isDragging = true;
        if (e.type === 'mousedown') {
            startX = e.pageX;
        } else if (e.type === 'touchstart') {
            var touch = e.originalEvent.touches[0];
            startX = touch.pageX;
        }
        initialLeft = parseFloat($(this).css('left'));
    });

    // When mouse or touch moves while dragging
    $(document).on('mousemove touchmove', function(e) {
        if(isDragging) {
            var moveX;
            if (e.type === 'mousemove') {
                moveX = e.pageX;
            } else if (e.type === 'touchmove') {
                var touch = e.originalEvent.touches[0];
                moveX = touch.pageX;
            }
            var deltaX = moveX - startX;
            var newX = initialLeft + deltaX;
            
            // Calculate main screen boundaries
            var mainScreenWidth = $(window).width();
            
            // Constrain movement within main screen boundaries
            newX = Math.min(Math.max(newX, 0), mainScreenWidth - $('#draggableDiv').outerWidth());
            
            $('#draggableDiv').css({
                left: newX
            });
            
            // Prevent default touchmove behavior (e.g., page scrolling)
            e.preventDefault();
        }
    });

    // When mouse or touch ends
    $(document).on('mouseup touchend', function() {
        isDragging = false;
    });

    // Password Show Hide
    $('.showPass').on('click', function(){
        var passInput=$(".passInput");
        if(passInput.attr('type')==='password'){
          passInput.attr('type','text');
        }else{
          passInput.attr('type','password');
        }
    });
    
  });
});