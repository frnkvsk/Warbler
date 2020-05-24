
/**
 * Handles likes for likes.html
 */
function doLike(args) {
    let [id, message_id] = args.split(',')
    let count = parseInt($(".likes").text())
    if($(id).hasClass("not-liked")) {
        ++count
        $(".likes").text(count.toString())
        $(id).removeClass("not-liked").addClass("liked")
    } else {
        --count   
        $(".likes").text(count.toString())
        $(id).removeClass("liked").addClass("not-liked")
    }
    $.ajax({
        data : {
            message_id : message_id
        },
        type : 'post',
        url : '/do_like'
    });
}
