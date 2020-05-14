
$(function () {

    var max_fields = 10;
    var wrapper = $('#wrapper');
    var add_button = $('#addButton');

    var x = 1;


    $(add_button).click(function (e) {
        e.preventDefault();

        if (x < max_fields) {
            x++;

            var field_group = '<div id="g' + x + '"><select name="f' + x + '"><option value="institution">' +
                'Institution</option><option value="refnumber">Signatur</option></select>' +
                '<select name="b' + x + '"><option value="is">ist gleich</option><option value="isnot">' +
                'ist nicht gleich</option><option value="contains">enthält</option></select>' +
                '<input name="q' + x + '" type="text" placeholder="Suchen..." />' +
                '<button type="button" id="delButton">-</button></div>';

            $(wrapper).append(field_group);

        } else {
            alert('Maximale Anzahl Felder erreicht')
        }
    });

    $(wrapper).on('click', '#delButton', function (e) {
        e.preventDefault();
        $(this).parent('div').remove();
        x--;
    });

});