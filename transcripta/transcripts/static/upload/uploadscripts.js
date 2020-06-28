/*
 * 
 * Handlers for buttons
 * 
 */

// Show entered values in ModalForm and ask for confirmation
// Client-side validation happens here. Do we still need server-side validation?
function submitModalForm(event) {
    var form = $(event.target).closest('form')[0];
    if (validateForm(form)) {
        $(form).find('.form-control').prop('disabled', true);

        $(form).find('#modalIntro').html('Bitte überprüfen Sie Ihre Angaben.');

        if ($(form).attr('id') == 'refNumberForm') {
            $(form).find('#submitButtonModal').off().on('click', confirmRefNumber).html('Bestätigen');
        } else if ($(form).attr('id') == 'institutionForm') {
            $(form).find('#submitButtonModal').off().on('click', confirmInstitution).html('Bestätigen');
        }
        
        $(form).find('#backButtonModal').show();
    }
};

// Go back to RefNumberForm
function backModalForm() {
    $(event.target).closest('form').find('.form-control').prop('disabled', false);
    $(event.target).hide();
    $(event.target).siblings('#submitButtonModal').off().on('click', null, this, submitModalForm).html('Absenden');
};

// Handle RefNumberForm
function confirmRefNumber() {
    $.ajax({
        type: 'POST',
        url: $('#documentTitleForm').attr('modal-ref-url'),
        data: {
            new_holding_institution: $('#id_holding_institution').val(),
            new_refnumber_name: $('#id_refnumber_name').val(),
            new_refnumber_title: $('#id_refnumber_title').val(),
            new_collection_link: $('#id_collection_link').val(),
            csrfmiddlewaretoken: $('#refNumberForm input[name=csrfmiddlewaretoken]').val(),
        },
    })
        .done(function (data) {
            var new_ref_name = $('#id_refnumber_name').val();
            $('#refNumberModal').modal('hide');
            $('#id_parent_refnumber').html(data).prop("disabled", false);
            $('#id_parent_refnumber option:contains(' + new_ref_name + ')').prop("selected", true);
        });
};

// Handle InstitutionForm
function confirmInstitution() {
    $.ajax({
        type: 'POST',
        url: $('#documentTitleForm').attr('modal-inst-url'),
        data: {
            new_institution_name: $('#id_institution_name').val(),
            new_street: $('#id_street').val(),
            new_zip_code: $('#id_zip_code').val(),
            new_city: $('#id_city').val(),
            new_country: $('#id_country').val(),
            new_site_url: $('#id_site_url').val(),
            csrfmiddlewaretoken: $('#institutionForm input[name=csrfmiddlewaretoken]').val(),
        },
    })
        .done(function (data) {
            var new_inst_name = $('#id_institution_name').val();
            $('#institutionModal').modal('hide');
            $('#id_parent_institution').html(data);
            $('#id_parent_institution option:contains(' + new_inst_name + ')').prop("selected", true);
            $('#id_holding_institution').html(data);
            //fires the function to update refnumbers in case institution has been chosen before
            $('#id_parent_institution').change();
            $('#id_parent_institution').prop("disabled", false);
        });
};


// Handle confirmation of newly created Authors
function confirmAuthor() {
    $('#confirmationModal').modal('hide');
    $('#authorList').empty();
    $('#documentTitleForm').submit();
};

function closeAuthor() {
    $('#confirmationModal').modal('hide');
    $('#authorList').empty();
    $('#id_author').focus();
};


// Handle documentTitleForm
function submitDocument(event) {
    var form = $(event.target).closest('form')[0];
    var authorData = $(form).find('#id_author').val();

    document.querySelector('.ck-editor__editable').ckeditorInstance.updateSourceElement();

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
 * AJAX success callbacks after modals loaded
 * 
 */

function institutionLoaded() {
    $('#institutionForm').find('#submitButtonModal').on('click', null, this, submitModalForm);
    $('#institutionForm').find('#backButtonModal').on('click', null, this, backModalForm);
    // add label to required fields
    $('[required]').parents('.form-group').find('.control-label').addClass('label-required');
    // initialize tooltips
    $('.tooltipster').tooltipster({
        maxWidth: 300,
        theme: ['tooltipster-punk', 'tooltipster-transcriptiones']
    });
};

function refNumberLoaded() {
    $('#id_holding_institution').select2({
        theme: 'bootstrap4',
        placeholder: $('#id_holding_institution').attr('placeholder'),
    });
    $('#refNumberForm').find('#submitButtonModal').on('click', null, this, submitModalForm);
    $('#refNumberForm').find('#backButtonModal').on('click', null, this, backModalForm);
    // add label to required fields
    $('[required]').parents('.form-group').find('.control-label').addClass('label-required');
    // initialize tooltips
    $('.tooltipster').tooltipster({
        maxWidth: 300,
        theme: ['tooltipster-punk', 'tooltipster-transcriptiones']
    });
};


/*
 * 
 * Handlers for show.bs.modal events
 * 
 */

// Append entered institution name to intro and first field of institutionForm
$(document).on('show.bs.modal', '#institutionModal', function () {
    var instValue = $('#id_parent_institution').val();
    var txt = "Die Institution " + instValue + " ist noch nicht Teil der Datenbank.";
    $('#institutionModal').find('#modalIntro').html(txt);
    $('#id_institution_name').val(instValue);
});


//append selected values to intro and refNumberForm
$(document).on('show.bs.modal', '#refNumberModal', function () {
    var instValue = $('#id_parent_institution').val();
    var refValue = $('#id_parent_refnumber').val();
    var txt = "Die Signatur " + refValue + " ist noch nicht Teil der Datenbank.";
    $('#refNumberModal').find('#modalIntro').html(txt);
    $('#id_holding_institution option[value="' + instValue + '"]').prop("selected", true).change();
    $('#id_refnumber_name').val(refValue);
});


/*
 * 
 * Handlers for hide.bs.modal events
 * 
 */

// clear the form field which opened institutionModal and disable parent_refnumber
$(document).on('hide.bs.modal', '#institutionModal', function () {
    $('#id_parent_institution').prop('selectedIndex', -1).change();
    $('#id_parent_refnumber').prop("disabled", true);
    $('#institutionForm').find('#submitButtonModal').off().on('click', null, this, submitModalForm).html('Absenden');
    $('#institutionForm').find('#backButtonModal').hide();
    $('#institutionForm').find('.form-control').prop('disabled', false);
    document.getElementById('institutionForm').reset();
});

// clear the form field which opened refNumberModal
$(document).on('hide.bs.modal', '#refNumberModal', function () {
    $('#id_parent_refnumber').prop('selectedIndex', -1).change();
    $('#refNumberForm').find('#submitButtonModal').off().on('click', null, this, submitModalForm).html('Absenden');
    $('#refNumberForm').find('#backButtonModal').hide();
    $('#refNumberForm').find('.form-control').prop('disabled', false);
    document.getElementById('refNumberForm').reset();
});

/*
 * 
 * Add special Characters to CKedit-configuration
 * 
 */

function SpecialCharactersSuperscript(editor) {
    editor.plugins.get('SpecialCharacters').addItems('Diakritische Zeichen', [
        { title: 'latin capital letter O with combining latin small letter e', character: '\u004F\u034F\u0364' },
        { title: 'latin small letter o with combining latin small letter e', character: '\u006F\u034F\u0364' },
        { title: 'latin capital letter U with combining latin small letter e', character: '\u0055\u034F\u0364' },
        { title: 'latin small letter u with combining latin small letter e', character: '\u0075\u034F\u0364' },
        { title: 'latin capital letter U with combining latin small letter o', character: '\u0055\u034F\u0366' },
        { title: 'latin small letter u with combining latin small letter o', character: '\u0075\u034F\u0366' },

    ]);
}


/*
 * 
 * Handler for DOMContentLoaded
 * 
 */

$(function () {
    // load modal-contents of instutionModal and refNumberModal
    $('#institutionModal').find('.modal-content').load($('#documentTitleForm').attr('modal-inst-url'), institutionLoaded);
    $('#refNumberModal').find('.modal-content').load($('#documentTitleForm').attr('modal-ref-url'), refNumberLoaded);

    // Turn select fields into Select2 fields and pass additional information.
    $('#id_parent_institution, #id_author').each(function () {
        var element = $(this);
        element.select2({
            theme: 'bootstrap4',
            tags: true,
            placeholder: element.attr('placeholder'),
        });
    });
    $('#id_parent_refnumber').select2({
        theme: 'bootstrap4',
        tags: true,
        placeholder: $('#id_parent_refnumber').attr('placeholder'),
        disabled: true,
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


    // initialize ckedit

    ClassicEditor
        .create(document.querySelector('#id_transcription_text'), {
            removePlugins: ['Title'],
            extraPlugins: [SpecialCharactersSuperscript],
            toolbar: ['heading', 'fontsize', 'fontcolor', 'fontbackgroundcolor', '|',
                'bold', 'italic', 'underline', 'strikethrough', '|',
                'subscript', 'superscript', 'specialcharacters', 'link', '|',
                'horizontalline', 'pagebreak', '|',
                'indent', 'outdent', '|',
                'blockquote', 'inserttable', 'bulletedlist', 'numberedlist', '|',
                'removeformat', 'undo', 'redo', '|'
            ],
        })
        .then(editor => {
            console.log(editor);
        })
        .catch(error => {
            console.error(error);
        })


    // add label to required fields
    $('[required]').parents('.form-group').find('.control-label').addClass('label-required');

    // add various handlers to events
    $('#id_start_month, #id_start_day, #id_end_month, #id_end_day').prop('disabled', true);
    $('#id_start_year, #id_start_month, #id_end_year, #id_end_month').on('input', null, this, enableDate);
    $('#submitButtonDocument').on('click', null, this, submitDocument);
    $('#id_source_type_child').prop('disabled', true).find('option').prop('disabled', true);
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

// Make Refnumber depend on Institution. Open InstitutionForm if Institution is not part of selection
$(document).on('change', '#id_parent_institution', function () {
    var urldepend = $('#documentTitleForm').attr('dep-ref-url');
    var instId = $(this).val();

    if (Number.isInteger(Number(instId)) && instId != null) {
        $.ajax({
            url: urldepend,
            data: {
                'institution': instId
            },
        })
            .done(function (data) {
                $('#id_parent_refnumber').html(data);
                $('#id_parent_refnumber').prop("disabled", false);
            });
    } else {
        $('#institutionModal').modal('show');
    }
});


// Open RefNuberForm if Refnumber is not Part of the Database
$(document).on('change', '#id_parent_refnumber', function () {
    var refId = Number($(this).val());

    if (Number.isNaN(refId)) {
        $('#refNumberModal').modal('show');
    }
});

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
        $(event.target).closest('.fieldWrapper').next('.fieldWrapper').find('option[value="30"]').prop('disabled', false);
        $(event.target).closest('.fieldWrapper').next('.fieldWrapper').find('option[value="31"]').prop('disabled', true);
    } else if ($(event.target).val() == '2') {
        $(event.target).closest('.fieldWrapper').next('.fieldWrapper').find('option[value="30"], option[value="31"]').prop('disabled', true);
    } else {
        $(event.target).closest('.fieldWrapper').next('.fieldWrapper').find('option:hidden').prop('disabled', false);
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