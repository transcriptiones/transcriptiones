/*
 * 
 * Handlers for buttons
 * 
 */


// Handle documentTitleForm
function submitDocument(event) {
    var form = $(event.target).closest('form')[0];

    document.querySelector('.ck-editor__editable').ckeditorInstance.updateSourceElement();

    if (validateForm(form)) {
        form.submit();
    }
};


/*
 * 
 * Add special Characters to CKedit-configuration
 * 
 */

function SpecialCharactersSuperscript(editor) {
    editor.plugins.get('SpecialCharacters').addItems('Diakritische Zeichen', [
        { title: 'latin capital letter O with combining latin small letter e', character: 'Oͤ'},
        { title: 'latin small letter o with combining latin small letter e', character: 'oͤ' },
        { title: 'latin capital letter U with combining latin small letter e', character: 'Uͤ' },
        { title: 'latin small letter u with combining latin small letter e', character: 'uͤ' },
        { title: 'latin capital letter U with combining latin small letter o', character: 'Uͦ' },
        { title: 'latin small letter u with combining latin small letter o', character: 'uͦ' },

    ]);
}


/*
 * 
 * Handler for DOMContentLoaded
 * 
 */

$(function () {
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
    $('#submitButtonDocument').on('click', null, this, submitDocument);
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