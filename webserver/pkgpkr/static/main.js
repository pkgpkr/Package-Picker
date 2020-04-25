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
    var repoTable = $('#repo-table').DataTable({
        "bLengthChange": false,
        dom: 'tip',
        scroller: true
    });

    $('.modal-background').click(function() {
        $('#scoreModal').modal('hide');
    })

    $('#modal-close').click(function() {
        $('#scoreModal').modal('hide');
    })
});

function myFunction() {
  var element = document.getElementsByClassName("pageloader");
  element[0].classList.add("hidden");
}

function categoryClick(value) {
    var categoryName = document.getElementById('category-name');
    categoryName.value = value;
    triggerEvent(categoryName, 'keyup');
    document.getElementById('category-clear').style.visibility = "visible";
}

function triggerEvent(el, type){
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
