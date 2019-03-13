$(document).ready(function () {
    $('#btn-launch-pivot').on('click', function(e) {
        e.stopImmediatePropagation();
        setupAjax();
        var opt_cloud = $('#optCloud').val();
        $('#pivot-error').text('');
        $('#pivot-error').hide();

        $.ajax({
            type: "POST",
            url: "/pivot_i2b2_transmart_hcm/deploy/",
            dataType: "json",
            data: {
                'opt_cloud': opt_cloud
            },
            success: function(result) {
                window.location.href = result.url
            },
            error: function (xhr, errmsg, err) {
                $('#pivot-error').html(xhr.responseText);
                $('#pivot-error').show();
            }
        });
    });
});
