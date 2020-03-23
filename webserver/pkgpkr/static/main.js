$(document).ready( function () {
    var table = $('.display-data-tables').DataTable({
        "bLengthChange": false,
        dom: 'itp'
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
    document.getElementById('categoryName').value = value;
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
