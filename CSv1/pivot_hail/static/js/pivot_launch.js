$(document).ready(function () {
    $('#btn-launch-pivot').on('click', function(e) {
        setupAjax();
        var num_insts = parseInt($('#txtInstance').val());
        var num_cpus = parseInt($('#txtCPU').val());
        var num_mems = parseInt($('#txtMEM').val());
        var def_num_insts = parseInt($('#default_num_insts').val());
        var def_num_cpus = parseInt($('#default_num_cpus').val());
        var def_num_mems = parseInt($('#default_num_mems').val());
        var opt_cloud = $('#optCloud').val();
        var error_field_msg = '';
        $('#pivot-error').text('');
        $('#pivot-error').hide();

        if (num_insts > def_num_insts) {
            error_field_msg = 'number of instances';
        }

        if (num_cpus > def_num_cpus) {
            if(error_field_msg == '')
                error_field_msg = 'number of CPUs';
            else
                error_field_msg += ', number of CPUs';
        }

        if (num_mems > def_num_mems) {
            if(error_field_msg == '')
                error_field_msg = 'memory';
            else
                error_field_msg += ', memory';
        }

        if (error_field_msg != '') {
            $('#pivot-error').text('The entered value for ' + error_field_msg + ' cannot be greater than the default');
            $('#pivot-error').show();
        }
        else {
            $.ajax({
                type: "POST",
                url: "/pivot_hail/deploy/",
                dataType: "json",
                data: {
                    'num_instances': num_insts,
                    'num_cpus': num_cpus,
                    'mem_size': num_mems,
                    'opt_cloud': opt_cloud,
                    'token': $('#txtToken').val()
                },
                success: function(result) {
                    window.location.href = result.url
                },
                error: function (xhr, errmsg, err) {
                    $('#pivot-error').html(xhr.responseText);
                    $('#pivot-error').show();
                }
            });
        }
    });
});