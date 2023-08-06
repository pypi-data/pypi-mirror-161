if (django) {
    var $ = django.jQuery;
}
function initialiseWYSIWYG(){
    $('.wysiwyg-init.uninitialised').each(function(){
        var id = $(this).attr('id');
        if(id.indexOf('__prefix__') === -1) {
            $("#" + id).summernote(JSON.parse($(this).attr('data-config')));
            $(this).removeClass('uninitialised');
        }
    });
}
$(document).ready(function(){
    // Initialise wysiwyg for initially printed fields
    initialiseWYSIWYG();
    // Bind add click to add new wysiwyg for each addition
    if (django) {
        django.jQuery('.add-row a').on('click', function (e) {
            initialiseWYSIWYG();
        });
    }
});
