$(function () {
    ClassicEditor
        .create(document.querySelector('#transcriptionText'), {
            removePlugins: ['Title', 'Toolbar'],
        })
        .then(editor => {
            console.log(editor);
            editor.isReadOnly = true;
        })
        .catch(error => {
            console.error(error);
        })


});