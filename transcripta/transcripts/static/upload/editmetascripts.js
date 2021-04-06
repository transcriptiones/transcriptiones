/*
 * 
 * Handlers for buttons
 * 
 */


// Handle confirmation of newly created Authors
function confirmAuthor() {
    $('#confirmationModal').modal('hide');
    $('#authorList').empty();
    $('#editMetaForm').submit();
};

function closeAuthor() {
    $('#confirmationModal').modal('hide');
    $('#authorList').empty();
    $('#id_author').focus();
};


// Handle editMetaForm
function submitDocument(event) {
    var form = $(event.target).closest('form')[0];
    var authorData = $(form).find('#id_author').val();

    if (validateForm(form)) {
        var cleanAuthor = true

        // check if in the array there is an Author not yet in the DB
        if (authorData && authorData.length != 0) {

            authorData.forEach(function (author) {
                if (Number.isNaN(Number(author))) {
                    $('#authorList').append('<li>' + author + '</li>');
                    cleanAuthor = false;
                }
            });

        }

        // ask for confirmation if necessary, else submit form
        if (cleanAuthor) {
            form.submit();
        } else {
            $('#confirmationModal').modal('show');
        }
    }
};


/*
 * Show and hide EndDate. Maybe make a toggle-function?
 */


function showEndDate() {
    $('#endDate').show();
    $('#labelStartDate').html("Datierung von");
    $('#buttonEndDate').on('click', hideEndDate).html("Zeitpunkt");
}

function hideEndDate() {
    $('#endDate').hide();
    $('#labelStartDate').html("Datierung");
    $('#endDate').find('input[type="number"]').val('');
    $('#buttonEndDate').on('click', showEndDate).html("Zeitspanne");
}



/*
 * 
 * Handler for DOMContentLoaded
 * 
 */

$(function () {
    // Turn select fields into Select2 fields and pass additional information.
    $('#id_author').each(function () {
        var element = $(this);
        element.select2({
            theme: 'bootstrap4',
            tags: true,
            placeholder: element.attr('placeholder'),
        });
    });
    $('#id_language, #id_source_type_parent, #id_source_type_child, #id_material, #id_start_month, #id_start_day, #id_end_month, #id_end_day').each(function () {
        var element = $(this);
        element.select2({
            theme: 'bootstrap4',
            placeholder: element.attr('placeholder'),
            allowClear: true,
        });
    });
    $('#id_paging_system').select2({
        theme: 'bootstrap4',
        tags: true,
        placeholder: $('#id_paging_system').attr('placeholder'),
        minimumResultsForSearch: Infinity,
        allowClear: true,
    });
    $('#id_illuminated, #id_seal').each(function () {
        var element = $(this);
        element.select2({
            theme: 'bootstrap4',
            tags: true,
            placeholder: element.attr('placeholder'),
            minimumResultsForSearch: Infinity,
        });
    });

    // add label to required fields
    $('[required]').parents('.form-group').find('.control-label').addClass('label-required');

    // add various handlers to events
    $('#id_start_month, #id_start_day, #id_end_month, #id_end_day').each(function () {
        if (!$(this).val() || $(this).val() == '') {
            $(this).prop('disabled', true);
        }
    });
    $('#id_start_year, #id_start_month, #id_end_year, #id_end_month').on('input', null, this, enableDate);
    // trigger change event on source_type_parent in order to update source_type_child
    $('#id_source_type_parent').change();
    $('#submitButtonDocument').on('click', null, this, submitDocument);
    $('#submitButtonAuthor').on('click', confirmAuthor);
    $('#closeButtonAuthor').on('click', closeAuthor);
    $('#buttonEndDate').on('click', showEndDate);

    // initialize tooltips
    $('.tooltipster').tooltipster({
        maxWidth: 300,
        theme: ['tooltipster-punk', 'tooltipster-transcriptiones']
    });
});


/*
 * 
 * Functions and handlers for dynamic form (opening modals, dependent dropdowns, etc)
 * 
 */

//enable month field if year is set, enable day field if month is set, disable if not set

function enableDate(event) {
    if ($(event.target).val() && $(event.target).val() != '') {
        $(event.target).closest('.fieldWrapper').next('.fieldWrapper').find('select').prop('disabled', false);
    } else if ($(event.target).val('')) {
        $(event.target).closest('.fieldWrapper').nextAll('.fieldWrapper').find('select').prop('disabled', true).val('');
    }
}

//change number of possible days based on selection of month

$('#id_start_month, #id_end_month').on('change', function (event) {
    if (['4', '6', '9', '11'].includes($(event.target).val())) {
        $(event.target).closest('.fieldWrapper').next('.fieldWrapper').find('option[value="30"]').show();
        $(event.target).closest('.fieldWrapper').next('.fieldWrapper').find('option[value="31"]').hide();
    } else if ($(event.target).val() == '2') {
        $(event.target).closest('.fieldWrapper').next('.fieldWrapper').find('option[value="30"], option[value="31"]').hide();
    } else {
        $(event.target).closest('.fieldWrapper').next('.fieldWrapper').find('option:hidden').show();
    }
});


// show/hide source_type_child options based on selection of source_type_parent
$('#id_source_type_parent').on('change', function (event) {
    var parent = $(event.target).val()
    if (parent && parent != '') {
        $('#id_source_type_child').find('option').prop('disabled', true);
        $('#id_source_type_child').prop('disabled', false).find('option[data-parent=' + parent + ']').prop('disabled', false);
    } else {
        $('#id_source_type_child').prop('selectedIndex', -1).change().prop('disabled', true).find('option').prop('disabled', true);
    }
});

/*
 * 
 * Functions used in client-side form validation
 * 
 */

function validateForm (form) {

    // get different types of inputs or selects
    const textInputs = form.querySelectorAll('input[type=text]');
    const numberInputs = form.querySelectorAll('input[type=number');
    const selectInputs = form.querySelectorAll('select');
    const urlInputs = form.querySelectorAll('input[type=url');
    const textareaInputs = form.querySelectorAll('textarea');

    var formValid = true;

    textInputs.forEach(function (textInput) {

        if (textInput.validity.valid) {
            $(textInput).siblings('.error').html('');
            $(textInput).siblings('.error').removeClass('active');
        } else {
            showTextError(textInput);
            formValid = false;
        }

    });

    numberInputs.forEach(function (numberInput) {

        if (numberInput.validity.valid) {
            $(numberInput).siblings('.error').html('');
            $(numberInput).siblings('.error').removeClass('active');
        } else {
            showNumberError(numberInput);
            formValid = false;
        }

    });

    urlInputs.forEach(function (urlInput) {

        if (urlInput.validity.valid) {
            $(urlInput).siblings('.error').html('');
            $(urlInput).siblings('.error').removeClass('active');
        } else {
            showUrlError(urlInput);
            formValid = false;
        }

    });

    selectInputs.forEach(function (selectInput) {
        if (selectInput.validity.valid) {
            $(selectInput).siblings('.error').html('');
            $(selectInput).siblings('.error').removeClass('active');
        } else {
            showSelectError(selectInput);
            formValid = false;
        }

    });

    textareaInputs.forEach(function (textareaInput) {

        if (textareaInput.validity.valid) {
            $(textareaInput).siblings('.error').html('');
            $(textareaInput).siblings('.error').removeClass('active');
        } else {
            showTextareaError(textareaInput);
            formValid = false;
        }

    });

    // set focus on first erroneous form field
    if (formValid === false) {
        $('.error.active').first().siblings().first().focus();
    }

    return formValid;
};

function showTextError(textInput) {
    if (textInput.validity.valueMissing) {
        $(textInput).siblings('.error').text('Dies ist ein Pflichtfeld');
    } else if (textInput.validity.tooLong) {
        $(textInput).siblings('.error').text('Maximale Anzahl Zeichen: ' + textInput.maxLength);
    }

    $(textInput).siblings('.error').addClass('active');
};

function showNumberError(numberInput) {
    if (numberInput.validity.valueMissing) {
        $(numberInput).siblings('.error').text('Dies ist ein Pflichtfeld');
    } else if (numberInput.validity.rangeUnderflow) {
        $(numberInput).siblings('.error').text('Minimalwert: ' + numberInput.min);
    } else if (numberInput.validity.rangeOverflow) {
        $(numberInput).siblings('.error').text('Maximalwert: ' + numberInput.max);
    } 

    $(numberInput).siblings('.error').addClass('active');
};

function showUrlError(urlInput) {
    if (urlInput.validity.valueMissing) {
        $(urlInput).siblings('.error').text('Dies ist ein Pflichtfeld');
    } else if (urlInput.validity.tooLong) {
        $(urlInput).siblings('.error').text('Maximale Anzahl Zeichen: ' + urlInput.maxLength);
    } else if (urlInput.validity.typeMismatch) {
        $(urlInput).siblings('.error').text('Der eingegebene Wert muss eine URL sein (inklusive https://)');
    }

    $(urlInput).siblings('.error').addClass('active');
};

function showSelectError(selectInput) {
    if (selectInput.validity.valueMissing) {
        $(selectInput).siblings('.error').text('Dies ist ein Pflichtfeld');
    }

    $(selectInput).siblings('.error').addClass('active');
};


/*
 * TODO: Proper validation specifications, maybe html-escaping?
 */

function showTextareaError(textareaInput) {
    if (textareaInput.validity.valueMissing) {
        $(textareaInput).siblings('.error').text('Dies ist ein Pflichtfeld');
    } else if (textareaInput.validity.tooLong) {
        $(textareaInput).siblings('.error').text('Maximale Anzahl Zeichen: ' + textareaInput.maxLength);
    }

    $(textareaInput).siblings('.error').addClass('active');
};