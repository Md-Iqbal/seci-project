(function ($) {
    "use strict";

    jQuery(document).ready(function ($) {
        $(document).on('submit', '#contact_form_submit', function (e) {
            e.preventDefault();
            // var name = $('#name').val();
            var surename = $('#surename').val();
            var phone = $('#phone').val();
            var email = $('#email').val();
            var subject = $('#subject').val();
            var message = $('#message').val();

            if (email && message && surename) {
                $.ajax({
                    type: "POST",
                    url: 'contact.php',
                    data: {
                        // 'name': name,
                        'surename': surename,
                        'phone': phone,
                        'email': email,
                        'subject': subject,
                        'message': message,
                    },
                    success: function (data) {
                        $('#contact_form_submit').children('.email-success').remove();
                        $('#contact_form_submit').prepend('<span class="alert alert-success email-success">' + data + '</span>');
                        // $('#name').val('');
                        $('#surename').val('');
                        $('#phone').val('');
                        $('#email').val('');
                        $('#subject').val('');
                        $('#message').val('');
                        // $('#map').height('576px');
                        $('.email-success').fadeOut(3000);
                    },
                    error: function (res) {

                    }
                });
            } else {
                $('#contact_form_submit').children('.email-success').remove();
                $('#contact_form_submit').prepend('<span class="alert alert-danger email-success">All Fields are Required.</span>');
                // $('#map').height('576px');
                $('.email-success').fadeOut(3000);
            }

        });
    })

}(jQuery));