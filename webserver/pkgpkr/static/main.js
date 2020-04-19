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
    var repoTable = $('#repoTable').DataTable({
        "bLengthChange": false,
        dom: 'tip',
        scroller: true
    });

    var table = $('#recommendTable').DataTable({
        "bLengthChange": false,
        dom: 'tip',
        scroller: true,
        order: [[2, "desc"]],
        columnDefs : [{
            "targets": [3, 4, 5, 6],
            "visible": false
        }]
    });

    $('#recommendTable tbody ').on('click', 'img', function() {
        var data = table.row($(this).parents('tr')).data();
        $('.insertHere').html(
             '<table class="table dtr-details" width="100%"><tbody><tr><td>PkgPkr Score<td><td>' + data[2] +
             '</td></tr><tr><td>Absolute Trend Score<td><td>' + data[3] +
             '</td></tr><tr><td>Relative Trend Score<td><td>' + data[4] +
             '</td></tr><tr><td>Popularity Score<td><td>' + data[5] +
             '</td></tr><tr><td>Similarity Score<td><td>' + data[6] +
             '</td></tr></tbody></table>'
        );
        $('#scoreModal').modal('show');
    });

    $('#categoryName').keyup(function() {
        table.column(7).search($(this).val()).draw();
    });

    $('#recommendationFilter').keyup(function() {
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
