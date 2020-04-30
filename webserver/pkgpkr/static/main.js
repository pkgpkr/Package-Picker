const SAMPLE_JS_INPUTS = '"lodash": "v4.17.15",\n"react": "16.13.1",\n"express": "4.17.1",\n"moment": "2.24.0"';
const SAMPLE_PYTHON_INPUTS = "Django==2.1.2\nrequests>=2.23.0\ntensorflow==2.1.0";

document.addEventListener('DOMContentLoaded', () => {
    const $navbarBurgers = Array.prototype.slice.call(document.querySelectorAll('.navbar-burger'), 0);

    if ($navbarBurgers.length > 0) {
        $navbarBurgers.forEach(el => {
            el.addEventListener('click', () => {
                const target = el.dataset.target;
                const $target = document.getElementById(target);

                el.classList.toggle('is-active');
                $target.classList.toggle('is-active');
            });
        });
    }
});

$(document).ready(function () {
    var repoTable = $('#repo-table').DataTable({
        "bLengthChange": false,
        dom: 'tip',
        scroller: true
    });

    $('.modal-background').click(function () {
        $('#scoreModal').modal('hide');
    })

    $('#modal-close').click(function () {
        $('#scoreModal').modal('hide');
    })

    var page_title = window.document.title;

    if (page_title.match("My Repositories") || page_title.match("Recommendations")) {
        $('#title-text-parent').addClass('smaller-banner-z-index');
        $('#title-text').addClass('smaller-banner');
        $('#subtitle-text').addClass('hidden-banner');
    }

    // Set sample demo input to JS
    $('#manual-input').val(SAMPLE_JS_INPUTS);
    document.getElementById('lang-select').selectedIndex=0;
});

function hideLoadingAnimation() {
    var element = document.getElementsByClassName("pageloader");
    element[0].classList.add("hidden");
}

function categoryClick(value) {
    var categoryName = document.getElementById('category-name');
    categoryName.value = value;
    var categoryLength = 'width: ' + (value.length + 1) * 10 + 'px;'
    categoryName.setAttribute("style", categoryLength);
    triggerEvent(categoryName, 'keyup');
    document.getElementById('category-clear').style.visibility = "visible";
}

function triggerEvent(el, type) {
    var e = document.createEvent('HTMLEvents');
    e.initEvent(type, false, true);
    el.dispatchEvent(e);
}

function categoryClear() {
    var categoryName = document.getElementById('category-name');
    document.getElementById('category-name').value = '';
    triggerEvent(categoryName, 'keyup');
    document.getElementById('category-clear').style.visibility = "hidden";
}

function loadDemoLanguage(language) {
    const area = document.getElementById('manual-input');

    if (language === 'Javascript') {
        area.value = SAMPLE_JS_INPUTS;
    } else if (language === 'Python')
        area.value = SAMPLE_PYTHON_INPUTS;

}
