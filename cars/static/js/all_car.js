$(function() {
    $("#addLine").click(function(e) {
        $(".brand-line:first-of-type").clone().insertAfter(".brand-line:last");
    })
    $(document).on('click', ".dellLine",  function(e){
        const line = $(e.target.closest('.brand-line'));
        if (line.prev().length) {
            line.remove();
        }
    })
})
