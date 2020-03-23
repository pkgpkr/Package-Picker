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
 if ('createEvent' in document) {
      // modern browsers, IE9+
      var e = document.createEvent('HTMLEvents');
      e.initEvent(type, false, true);
      el.dispatchEvent(e);
  } else {
      // IE 8
      var e = document.createEventObject();
      e.eventType = type;
      el.fireEvent('on'+e.eventType, e);
  }
}

function categoryClear() {
    var categoryName = document.getElementById('categoryName');
    document.getElementById('categoryName').value = '';
    triggerEvent(categoryName, 'keyup');
    document.getElementById('categoryClear').style.visibility = "hidden";
}
