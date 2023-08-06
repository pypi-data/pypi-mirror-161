function update_page(item) {
    let per_page = document.getElementById("select_per_page").value;
    document.location.href = document.location.href + "&per_page=" + per_page;
}

$('a[data-toggle="pill"]').on('shown.bs.tab', function (e) {
    console.log("tab shown...");
    localStorage.setItem('activeTab', $(e.target).attr('href'));
});

// read hash from page load and change tab
var activeTab = localStorage.getItem('activeTab');
if (activeTab) {
    $('.nav-pills a[href="' + activeTab + '"]').tab('show');
}
