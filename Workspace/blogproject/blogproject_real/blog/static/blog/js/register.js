
$(document).ready(function(){
            //检查登录状态
            $.ajax({
                type:"GET",
                url:"{% url 'check_is_login' %}",
                cache:false,
                dataType:'text',
                success:function(result){
                    $("#user_part").html(result);
                },
                error:function(XMLHttpRequest, textStatus, errorThrown){
                    //alert(textStatus);
                    $("#user_part").html('<li><a href="#" data-toggle="modal" data-target="#LoginModal">登录</a></li><li><a href="#" data-toggle="modal" data-target="#RegModal">注册</a></li>');
                }
            });
            //登录
            $('#user_form').submit(function(){
                //验证
                var tip=$('#tip_text');
                tip.text('');

                if($('#user_name').val()==''){
                    tip.text('请输入邮箱');
                    return false;
                };
                if($('#user_pwd').val()==''){
                    tip.text('请输入密码');
                    return false;
                };

                //登录
                $.ajax({
                    type: "POST",
                    data: $('#user_form').serialize(),
                    url: "/blog/loging",
                    cache: false,
                    dataType: "json",
                    success: function(json, textStatus){
                        var is_success = json['success'];
                        if(is_success){
                            tip.text('登录成功，页面处理中...');

                            //跳转回原来的页面
                            var reback_url = $('#reback_url').val();
                            if(!reback_url){reback_url='/';}
                            window.location.href = reback_url;
                        }else{
                            tip.text('邮箱或者密码错误，请重试');
                        };
                    },
                    error: function (XMLHttpRequest, textStatus, errorThrown) {
                        tip.text("登录出错，请重试 "+errorThrown);
                    }
                });
                return false;
            });

            //注册
            $('#user_reg').click(function(){
                //验证
                var tip=$('#tip_text');
                tip.text('');

                var reg_name=$('#user_name').val();
                var reg_pwd=$('#user_pwd').val();

                if(reg_name==''){
                    tip.text('邮箱不能为空');
                    return false;
                };
                if(!reg_name.match(/^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+((\.[a-zA-Z0-9_-]{2,3}){1,2})$/)){
                    tip.text('请输入正确的邮箱格式');
                    return false;
                }

                if(reg_pwd==''){
                    tip.text('密码不能为空');
                    return false    ;
                };
                if(reg_pwd.length<6){
                    tip.text('密码不能少于6位');
                }

                //注册
                tip.text('注册中，请稍后...');
                $.ajax({
                    type: "POST",
                    data: $('#user_form').serialize(),
                    url: "/blog/register",
                    cache: false,
                    dataType: "json",
                    success: function(json, textStatus){
                        var is_success = json['success'];
                        if(is_success){
                            tip.text('注册成功，页面处理中...');
                            $('#user_control').text(json['message']);

                            window.setTimeout(function(){
                                var reback_url = $('#reback_url').val();
                                if(!reback_url){reback_url='/';}
                                window.location.href = reback_url;
                            },3000);
                        }else{
                            tip.text(json['message']);
                        };
                    },
                    error: function (XMLHttpRequest, textStatus, errorThrown) {
                        tip.text("注册出错，请重试 "+errorThrown);
                    }
                });
                return false;
            });
        });