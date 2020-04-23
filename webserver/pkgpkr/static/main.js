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
        order: [[2, "desc"]]
    });

    $('#recommendTable tbody').on('click', 'img', function() {
        var data = table.row($(this).parents('tr')).data();
        $('.insertHere').html(
             '<table class="table dtr-details" width="100%"><tbody><tr>' +
             '<th class="pkgpkr_score_td">PkgPkr<br>Score© <div class="tooltip"><i class="fas fa-question-circle" style="opacity:0.5;"></i>' +
             '<span class="tooltiptext">A score of 10 indicates that the packages are always used together. ' +
             '<a target="_blank" href="/about">See more details</a></span></div></th>' +

             '<th class="other_score_td">Used-Together<br>Score <div class="tooltip"><i class="fas fa-question-circle" style="opacity:0.5;"></i>' +
             '<span class="tooltiptext">A score of 10 indicates that the packages are always used together. ' +
             '<a target="_blank" href="/about">See more details</a></span></div></th>' +

             '<th class="other_score_td">Collaborative Filtering<br>Score <div class="tooltip"><i class="fas fa-question-circle" style="opacity:0.5;"></i>' +
             '<span class="tooltiptext">A score of 10 indicates that the packages are always used together A score of 10 indicates that the packages are always used together. ' +
             '<a target="_blank" href="/about">See more details</a></span></div></th>' +

             '<th class="other_score_td">Absolute Trend<br>Score <div class="tooltip"><i class="fas fa-question-circle" style="opacity:0.5;"></i>' +
             '<span class="tooltiptext">A score of 10 indicates that the packages are always used together. ' +
             '<a target="_blank" href="/about">See more details</a></span></div></th>' +

             '<th class="other_score_td">Relative Trend<br>Score <div class="tooltip-left"><i class="fas fa-question-circle" style="opacity:0.5;"></i>' +
             '<span class="tooltiptext-left">A score of 10 indicates that the packages are always used together. ' +
             '<a target="_blank" href="/about">See more details</a></span></div></th><tr>' +
             '<td>' + data[2] + '</td>' +
             '<td>' + data[3] + '</td>' +
             '<td>' + data[4] + '</td>' +
             '<td>' + data[5] + '</td>' +
             '<td>' + data[6] + '</td>' +
             '</tr></tbody></table>'
        );
        $('#scoreModal').modal('show');
    });

    $('.modal-background').click(function() {
        $('#scoreModal').modal('hide');
    })

    $('#modal-close').click(function() {
        $('#scoreModal').modal('hide');
    })

    $('#categoryName').keyup(function() {
        table.column(7).search($(this).val()).draw();
    });

    $('#recommendationFilter').keyup(function() {
        table.search($(this).val()).draw();
    });
});

function myFunction() {
  var element = document.getElementsByClassName("pageloader");
  element[0].classList.add("hidden");
}

window.addEventListener("load", function() {
    const loader = document.querySelector(".pageloader");

    setTimeout(function() {
      myFunction()
    }, 2000);
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
