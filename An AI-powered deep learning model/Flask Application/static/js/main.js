$(document).ready(function () {
    // Image preview
    $('#imageUpload').change(function () {
        $('.image-section').show();
        $('#btn-predict').show();
        $('#result').text('');
        readURL(this);
    });

    // Preview image
    function readURL(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                $('#imagePreview').attr('src', e.target.result);
            };
            reader.readAsDataURL(input.files[0]);
        }
    }

    // Predict button click
    $('#btn-predict').click(function () {
        var form_data = new FormData($('#upload-file')[0]);
        $('.loader').show();
        $('#result').text('');

        $.ajax({
            type: 'POST',
            url: '/predict',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            success: function (result) {
                $('.loader').hide();
                $('#result').text('Prediction: ' + result);
            },
            error: function (error) {
                $('.loader').hide();
                $('#result').text('Prediction failed. Please try again.');
            }
        });
    });
});
