
$(document).ready(function() {
                                $('#comment_form').submit(function() {
                                    if ($("#id_honeypot").val().length!=0) {
                                                alert("Stop!垃圾评论");
                                                return false;
                                    };
                                    if ($("#id_name").val().length==0) {
                                                alert("Error:请输入您的用户名");
                                                $("#id_name").focus();
                                                return false;
                                    };
                                    if ($("#id_email").val().length==0) {
                                                alert("Error:请输入您的邮箱地址");
                                                $("#id_email").focus();
                                                return false;
                                    };

                                    var email=$("#id_email").val();
                                    if(!email.match(/^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+((\.[a-zA-Z0-9_-]{2,3}){1,2})$/)){
                                        alert("Error:邮箱不正确！请重新输入");
                                        $("#id_email").focus();
                                        return false;
                                    }

                                    if ($("#id_comment").val().length==0){
                                        alert("Error:请输入您的评论");
                                        $("#id_comment").focus();
                                        return false;
                                    };

                                    var pk_id = $("#pk").val();
                                    alert(pk_id);
                                    $("#id_timestamp").value=event.timeStamp;
                                    $.ajax({
                                        type: "POST",
                                        data: $('#comment_form').serialize(),
                                        url: "{% comment_form_target %}",
                                        cache: false,
                                        dataType: "html",
                                        success: function(html, textStatus) {
                                            window.location.reload();
                                        },
                                        error: function (XMLHttpRequest, textStatus, errorThrown) {
                                            alert("评论出错，" + errorThrown);
                                        }
                                    });
                                    return false;
                                    });
                                });