from django.shortcuts import render
import time, re
from .models import UserProfile
from .models import User_forgetpassword
from django.contrib.auth import authenticate, login,logout
import json,datetime,random,string
from django.contrib.auth.models import User
from django.http import HttpResponse,HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMultiAlternatives   #发送邮件
from django.template import RequestContext
from django.shortcuts import render_to_response
import django.utils.timezone
from django.forms.models import model_to_dict
from helper import comments_count
from .forms import ChangeNickForm
import pdb

def register(request):
    response_data = {}
    reg_name = ''


    try:
        reg_name = request.POST.get('user_name')
        reg_pwd = request.POST.get('user_pwd')

        if len(reg_name) * len(reg_pwd) == 0:
            raise Exception(u"邮箱或密码为空")

        # 匹配邮箱格式
        pattern = re.compile(r'^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+((\.[a-zA-Z0-9_-]{2,3}){1,2})$')
        match = pattern.match(reg_name)
        if not match:
            raise Exception(u"邮箱格式不正确")

        # 验证密码长度
        if len(reg_pwd) < 6:
            raise Exception(u"密码不能少于6位")
        pdb.set_trace()
        # 判断用户是否存在
        user = User.objects.filter(username=reg_name)
        if len(user) > 0:
            raise Exception(u"该邮箱已经被注册")



        # 创建新用户
        user = User()
        user.username = reg_name
        user.email = reg_name
        user.set_password(reg_pwd)   # 这样才会对密码加密加盐处理
        user.is_active = False
        user.save()
        #根据user模型找到user的id，就可通过profile模型操作对应的profile信息
        profile = UserProfile()
        profile.user_id = user.id
        profile.nickname = reg_name
        profile.save()




        response_data['success'] = True
        response_data['message'] = u'注册成功，并发送激活邮件到您的邮箱。'
    except Exception as e:
        response_data['success'] = False
        response_data['message'] = str(e)

    finally:
        if response_data['success']:
            try:
                # 发送激活邮件
                # 不想用uuid模块生成唯一ID保存到数据库中，也不想用django-registration
                # 安全级别要求不高，所以简单写个加密解密的方法来处理
                active_code = get_active_code(reg_name)
                send_active_email(reg_name, active_code)
            except Exception as e:
                response_data['message'] = u'注册成功，激活邮件发送失败。请稍后重试 ' + str(e)
            # 注册成功，django1.10之前可以调用以下方法登录用户，1.10(包括)之后的要求激活才能登录,没激活的话user返回的都是none
            #user = authenticate(username=reg_name, password=reg_pwd)
            #if user is not None:
            #    login(request, user)

        return HttpResponse(json.dumps(response_data), content_type="application/json")

def get_active_code(email):
    """get active code by email and current date"""
    key=9
    encry_str='%s|%s' % (email,time.strftime('%Y-%m-%d',time.localtime(time.time())))
    active_code=encrypt(key,encry_str)
    return active_code


def send_active_email(email, active_code):
    """send the active email"""

    url = 'http://www.wuzihan.top%s' % (reverse('users:user_active', args=(active_code,)))

    subject = u'[wuzihan.top]激活您的帐号'
    message = u'''
        <h2>近涛的博客(<a href="http://www.wuzihan.top/" target=_blank>wuzihan.top</a>)<h2><br />
        <p>欢迎注册，请点击下面链接进行激活操作(7天后过期)：<a href="%s" target=_balnk>%s</a></p>
        ''' % (url, url)

    send_to = [email]
    fail_silently = False  # 发送异常不报错

    msg = EmailMultiAlternatives(subject=subject, body=message, to=send_to)
    msg.attach_alternative(message, "text/html")
    msg.send(fail_silently)

def goLogin(request):
    referrer = request.META.get('HTTP_REFERER','/')
    content = {'ref':referrer}

    #判断下多次点击登录/注册按钮或者先点击忘记密码再点击登录，会出现没跳转或还在修改密码页面的问题
    if content['ref'].find("blog/login/") != -1 or content['ref'].find("blog/goPasswordLost/")!=-1:
        return render(request, 'blog/userlogin.html', context={'ref':''})
    else:
        return render(request, 'blog/userlogin.html', context=content)

def goPasswordLost(request):
    return  render(request,'blog/passwordlost.html')

def check_is_login(request):
    """check the user is logined"""
    if request.user.is_authenticated():
        #这里换成nickname,之前是没扩展用户信息，直接用了邮箱为用户名
        #username = request.user.first_name
        nickname = UserProfile.objects.get(id=request.user.id)
        #if not username:
        #username = request.user.username
        if request.user.is_active:
            active_state = ''
        else:
            active_state = u'(未激活)'

        returnText = u'''
            <li role="presentation" class="dropdown">
                <a class="dropdown-toggle" data-toggle="dropdown" href="#" role="button" aria-haspopup="true" aria-expanded="false">
                    您好，%s%s <span class="caret"></span>
                </a>

                <ul class="dropdown-menu">
                    <li><a href="%s">用户中心</a></li>
                    <li><a href="%s">退出</a></li>
                </ul>
            </li>''' % (nickname,active_state,"/blog/gousercenter","/blog/user_logout")
    else:
        # 登录不成功就返回“登录”、“注册”的菜单
        returnText = u'''<li><a href="/blog/login">登录/注册</a></li>'''
    return HttpResponse(returnText, content_type='application/javascript')

def user_logout(request):
    """logout"""
    logout(request)
    #记住来源的url，如果没有则设置为首页('/')
    returnPath=request.META.get('HTTP_REFERER', '/')
    content = {'ref': returnPath}
    data = {}
    data['goto_url'] = '/'
    data['goto_time'] = 2000
    data['goto_page'] = True
    data['message'] = u'登出成功！欢迎您再次登录！！！'
    # 判断点击退出登录，如之前的页面在用户中心
    if content['ref'].find("blog/gousercenter/") != -1 or content['ref'].find("blog/goPasswordLost/") != -1 or content['ref'].find("blog/gonickname_change/") != -1:
        return render(request, 'blog/message.html', data)
    else:
        # 重定向到原来的页面，相当于刷新
        return HttpResponseRedirect(returnPath)

@csrf_exempt
def user_login(request):
    """login"""
    response_data = {}
    #pdb.set_trace()
    try:
        login_name = request.POST.get('user_name')
        login_pwd = request.POST.get('user_pwd')

        pdb.set_trace()
        if len(login_name) * len(login_pwd) == 0:
            raise Exception(u"邮箱或密码为空")

        # django1.10后登陆，不是活跃的账户将不能登陆，之前的版本是可以的。这里使用1.10的所以加上没有激活提示
        #先判断是否邮箱激活了，没有激活提示激活，如果已经激活了，判断账号密码是否正确
        user = User.objects.filter(username=login_name).filter(is_active=0)
        #pdb.set_trace()
        if user:
            raise Exception(u"请先激活邮箱")
        else:
            user = authenticate(username=login_name, password=login_pwd)

            if user is not None:
                login(request, user)  # 登录
                # request.session['user'] = login_name  # 将 session 信息记录到浏览器
            else:
                raise Exception(u"邮箱或密码不正确")
            response_data['success'] = True
            response_data['message'] = 'ok'


    except Exception as e:
        response_data['success'] = False
        response_data['message'] = str(e)
    finally:
        # 返回json数据
        return HttpResponse(json.dumps(response_data), content_type="application/json")

def changepassword(request):
    response_data = {}
    reg_name = ''

    try:
        reg_name = request.POST.get('email')
        reg_pwd = request.POST.get('pwd_1')
        validcode = request.POST.get('validcode')
        #pdb.set_trace()
        if len(reg_name) * len(reg_pwd) == 0:
            raise Exception(u"邮箱或密码为空")

        # 匹配邮箱格式
        pattern = re.compile(r'^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+((\.[a-zA-Z0-9_-]{2,3}){1,2})$')
        match = pattern.match(reg_name)
        if not match:
            raise Exception(u"邮箱格式不正确")

        # 验证密码长度
        if len(reg_pwd) < 6:
            raise Exception(u"密码不能少于6位")

        #验证验证码长度
        if len(validcode) < 4:
            raise Exception(u"验证码不能少于4位")

         # 判断用户是否存在
        user = User.objects.filter(username=reg_name)
        if len(user) <= 0:
            raise Exception(u"该邮箱尚未注册过，直接去注册即可")
        #pdb.set_trace()
        acca = User_forgetpassword.objects.filter(user_fp_id= User.objects.get(username=reg_name).id)
        last_validcode = acca[len(acca)-1].valid_code

        last_validtime = acca[len(acca) - 1].valid_time
        td = django.utils.timezone.now() - last_validtime
        if td.seconds/60 >= 10:
            raise Exception(u"验证码超过10分钟，已失效")

        #if User.objects.filter(user_forgetpassword__valid_code__contains=validcode).filter(username=reg_name):
        if last_validcode ==validcode:
            if user:
                # 修改数据库
                user = User.objects.get(username=reg_name)
                user.set_password(reg_pwd)  # 这样才会对密码加密加盐处理
                user.save()
                response_data['success'] = True
                response_data['message'] = u'重置密码成功,请牢记新密码'
                # 删除验证码
                #User_forgetpassword.objects.get(user_fp_id=User.objects.get(username=reg_name).id).delete()

        else:
            response_data['success'] = False
            response_data['message'] = u'验证码错误或失效，请检查'

    except Exception as e:
        response_data['success'] = False
        response_data['message'] = str(e)
    finally:
        if response_data['success']:
            # 重置密码成功，登录用户
            user = authenticate(username=reg_name, password=reg_pwd)

            if user is not None:
                login(request, user)

        return HttpResponse(json.dumps(response_data), content_type="application/json")


def encrypt(key, s):
    """encrypt string(key is a number)"""
    b = bytearray(str(s).encode('utf-8'))
    n = len(b)  # 求出 b 的字节数
    c = bytearray(n * 2)
    j = 0
    for i in range(0, n):
        b1 = b[i]
        b2 = b1 ^ key  # b1 = b2^ key
        c1 = b2 % 16
        c2 = b2 // 16  # b2 = c2*16 + c1
        c1 = c1 + 65
        c2 = c2 + 65  # c1,c2都是0~15之间的数,加上65就变成了A-P 的字符的编码
        c[j] = c1
        c[j + 1] = c2
        j = j + 2
    return c.decode('utf-8').lower()


def decrypt(key, s):
    """decrypt string(key is a number)"""
    c = bytearray(str(s).upper().encode('utf-8'))
    n = len(c)  # 计算 b 的字节数
    if n % 2 != 0:
        return ""
    n = n // 2
    b = bytearray(n)
    j = 0
    for i in range(0, n):
        c1 = c[j]
        c2 = c[j + 1]
        j = j + 2
        c1 = c1 - 65
        c2 = c2 - 65
        b2 = c2 * 16 + c1
        b1 = b2 ^ key
        b[i] = b1
    try:
        return b.decode('utf-8')
    except:
        return ""


def user_active(request, active_code):
    """user active from the code"""
    # 加错误处理，避免出错。出错认为激活链接失效
    # 解密激活链接
    key = 9
    data = {}
    try:
        decrypt_str = decrypt(key, active_code)

        decrypt_data = decrypt_str.split('|')
        email = decrypt_data[0]  # 邮箱
        create_date = time.strptime(decrypt_data[1], "%Y-%m-%d")  # 激活链接创建日期
        create_date = time.mktime(create_date)  # struct_time 转成浮点型的时间戳

        day = int((time.time() - create_date) / (24 * 60 * 60))  # 得到日期差
        #pdb.set_trace()
        if day > 7:
            raise Exception(u'激活链接过期')

        # 激活
        user = User.objects.filter(username=email)
        if len(user) == 0:
            raise Exception(u'激活链接无效')
        else:
            user = User.objects.get(username=email)

        if user.is_active:
            raise Exception(u'该帐号已激活过了')
        else:
            user.is_active = True
            user.save()

        data['goto_page'] = True
        data['message'] = u'激活成功，欢迎访问！博主会陆续发表高质量的原创博文。'
    except IndexError as e:
        data['goto_page'] = False
        data['message'] = u'激活链接无效'
    except Exception as e:
        data['goto_page'] = False
        data['message'] = e
    finally:
        # 激活成功就跳转到首页(message页面有自动跳转功能)
        data['goto_url'] = '/'
        data['goto_time'] = 5000
        return render_to_response('blog/message.html', data)


def get_email_code(request):
    """get email code"""
    reg_name = request.POST.get('email')

    code = ''.join(random.sample(string.digits + string.ascii_letters, 6))

    data = {}
    data['success'] = False
    data['message'] = ''
    #pdb.set_trace()
    try:
        # 检查邮箱
        users = User.objects.filter(email=reg_name)
        if len(users) == 0:
            data['success'] = False
            data['message'] = u'此邮箱未注册'
            raise Exception(u"此邮箱未注册")
        # 检查短时间内是否有生成过验证码
        #pdb.set_trace()
        acc = User_forgetpassword.objects.filter(user_fp_id= User.objects.get(username=reg_name).id)

        #如果存在验证码就判断是否一分钟内发过验证码，否则就新建一个
        if len(acc) > 0:
            #create_time = User_forgetpassword.objects.get(user_fp_id=User.objects.get(username=reg_name).id).valid_time

            # 两个datetime相减，得到datetime.timedelta类型
            td = django.utils.timezone.now() - acc[len(acc)-1].valid_time
            if td.seconds < 60:
                data['message'] = u'1分钟内发送过一次验证码'
                raise Exception(u"1分钟内发送过一次验证码")
            else:
                # 写入数据库
                user_forgetpassword = User_forgetpassword()
                user_forgetpassword.user_fp_id = User.objects.get(username=reg_name).id  # 跟用户关联起来
                user_forgetpassword.valid_code = code
                user_forgetpassword.valid_time = django.utils.timezone.now()
                user_forgetpassword.save()
        else:
            # 写入数据库
            user_forgetpassword = User_forgetpassword()
            user_forgetpassword.user_fp_id = User.objects.get(username=reg_name).id #跟用户关联起来
            user_forgetpassword.valid_code = code
            user_forgetpassword.valid_time = django.utils.timezone.now()
            user_forgetpassword.save()

            # 发送邮件
        subject = u'[wuzihan.top]重置您的密码'
        message = u"""
            <h2>近涛的博客(<a href='http://www.wuzihan.top/' target=_blank>www.wuzihan.top</a>)<h2><br />
            <p>重置密码的验证码(有效期10分钟)：%s</p>
            <p><br/>(请保管好您的验证码)</p>
            """ % code

        send_to = [reg_name]
        fail_silently = False  # 发送异常报错

        msg = EmailMultiAlternatives(subject=subject, body=message, to=send_to)
        msg.attach_alternative(message, "text/html")
        msg.send(fail_silently)

        data['success'] = True
        data['message'] = 'OK'
    except Exception as e:
        str(e)
    finally:
        return HttpResponse(json.dumps(data), content_type="application/json")
#装饰器，登录判断
def check_login(func):
    def wrapper(request):
        #登录判断，若没登录则跳转到前面写的信息提示页面
        #pdb.set_trace()
        if not request.user.is_authenticated():
            data = {}
            data['goto_url'] = '/blog/login'
            data['goto_time'] = 2000
            data['goto_page'] = True
            data['message'] = u'您尚未登录，请先登录'
            return render_to_response('blog/message.html',data)
        else:
            return func(request)
    return wrapper

@check_login
def gousercenter(request):
    data = {}
    # 判断是否登陆了,这里加了登陆装饰器就不需要判断了
    #if request.user.is_authenticated():

    data['user'] = request.user
    #nickname = UserProfile.objects.get(id=request.user.id)
    data['nickname'] = UserProfile.objects.get(id=request.user.id)
    data['comments_count'] = comments_count.get_comments_count(request.user.id)
    data['replies_count'] = comments_count.get_replies_count(request.user.id)
    data['replyed_count'] = comments_count.get_to_reply_count(request.user.id)
    data['last_talk_about'] = comments_count.last_talk_about(request.user.id)
    data['all_talk_about'] = comments_count.all_talk_about(request.user.id)
    return render_to_response('blog/usercenter.html', data)
'''def gousercenter(request):
    data={}
    user = request.user

    #判断是否登陆了
    if request.user.is_authenticated():
        pdb.set_trace()
        data['user'] = user
        data['comments_count'] = comments_count.get_comments_count(user.id)
        return render_to_response('blog/usercenter.html', data)
    else:
        data['message'] = u'您尚未登录，请先登录'
        data['goto_page'] = True
        data['goto_url'] = '/blog/login/'
        data['goto_time'] = 2000'''
@check_login
def gonickname_change(request):
    data = {}
    data['form_title'] = u'修改昵称'
    data['submit_name'] = u'　确定　'

    if request.method == 'POST':
        # 表单提交
        form = ChangeNickForm(request.POST)

        # 验证是否合法
        if form.is_valid():
            # 修改数据库
            nickname = form.cleaned_data['nickname']
            profile = UserProfile()
            profile.user_id = request.user.id
            profile.nickname = nickname
            profile.save()

            # 页面提示
            data['goto_url'] = reverse('users:gousercenter')
            data['goto_time'] = 3000
            data['goto_page'] = True
            data['message'] = u'修改昵称成功，修改为“%s”' % nickname
            return render_to_response('blog/message.html', data)
    else:
        # 正常加载
        #这个是取userprofile扩展下的昵称
        nickname1=UserProfile.objects.filter(id=request.user.id)
        # 用initial给表单填写初始值
        form = ChangeNickForm(initial={
            'old_nickname': nickname1[0],
            'nickname': nickname1[0],
        })
    data['form'] = form
    return render(request, 'blog/nickname_change.html', data)




