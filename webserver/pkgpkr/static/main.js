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

$(document).ready( function () {
    var table = $('.display-data-tables').DataTable({
        "bLengthChange": false,
        dom: 'tip',
        scroller: true
    });

    $('#categoryName').keyup( function() {
        table.column(1).search($(this).val()).draw();
    });

    $('#recommendationFilter').keyup( function() {
        table.search($(this).val()).draw();
    });
});

function categoryClick(value) {
    var categoryName = document.getElementById('categoryName');
    categoryName.value = value;
    triggerEvent(categoryName, 'keyup');
    document.getElementById('categoryClear').style.visibility = "visible";
}

function triggerEvent(el, type){
    var e = document.createEvent('HTMLEvents');
    e.initEvent(type, false, true);
    el.dispatchEvent(e);
}

function categoryClear() {
    var categoryName = document.getElementById('categoryName');
    document.getElementById('categoryName').value = '';
    triggerEvent(categoryName, 'keyup');
    document.getElementById('categoryClear').style.visibility = "hidden";
}
