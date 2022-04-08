(function() {
    var editor_instance, numbers, doc, iframe,
    e, top, numbers_top = 0, min_top, rows;

    var setNumberBar = function(elem, number) {
        top = $(elem).offset().top + numbers_top;
        if(number === 1) {
            // if all text has been deleted and there is the only paragraph,
            // editor itself changes the paragraph's height with notice
            // and first difit appears higher that it's supposed to be
            if(typeof min_top === 'undefined') {
                min_top = top;
            }
            else if(top < min_top) {
                top = min_top;
            }
        }
        e = $('<pre>'+number+'</pre>').css('top', top);
        var coef = ((""+number).length - 1)*5;
        numbers.width(20+coef).append(e);
    };

    var enumerate = function(i, elem) {
        if($(elem).is('ol,ul')) {
            $(elem).children('li').each(enumerate);
        }
        else if(elem.tagName || elem.textContent.trim()) {
            rows.push(elem);
        }
    };

    var setNumbers = function(e) {
        var text = $(editor_instance.document.getBody().$), i;

        rows = [];
        text.contents().filter('p,br,ol,ul').each(enumerate);

        if((e && e.currentTarget && e.currentTarget.tagName === 'A')
            || numbers.children().length !== rows.length || rows.length === 1) {

            numbers.children().remove();
            for(i = 0; i < rows.length; i++) {
                setNumberBar(rows[i], i+1);
            }
        }
    };

    CKEDITOR.plugins.add('linenumbers', {
        requires: ['autogrow'],
        init: function(editor) {
            editor_instance = editor;
            editor.on('instanceReady', function(e) {
                var container = $(editor.container.$);
                numbers = $('<div id="numbers"></div>');
                doc = $(editor.document.$);
                iframe = $('iframe', container);
                $('td.cke_contents', container).prepend(numbers);
                editor.document.on('keydown', setNumbers);
                editor.document.on('keyup', setNumbers);

                editor.on('resize', function(e) {
                    var last = numbers.find('pre:last');
                    var minHeight = parseInt(last.css('top')) + last.height() + 13; // to not show a scrollbar
                    iframe.height() < minHeight && iframe.height(minHeight);
                    numbers.height() > minHeight && iframe.height(numbers.height());
                    iframe.width($('table', container).width() - numbers.width());
                });

                iframe.width($('table', container).width() - numbers.width());
                $('span.cke_button a', container).click(setNumbers).keypress(setNumbers);
                setNumbers();
            });
        }
    });
})();