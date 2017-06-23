from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
from django.core.exceptions import ValidationError
from .models import UserProfile
import pdb

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('nickname', 'user', 'sex','phone')


class ChangeNickForm(forms.Form):
    """change the nick name form"""
    # 旧昵称，hidden类型，用于判断是否有修改
    old_nickname = forms.CharField(widget=forms.HiddenInput(attrs={'id': 'old_nickname'}))
    # 新昵称
    nickname = forms.CharField(label=u'新的昵称', max_length=20,
                               widget=forms.TextInput(
                                   attrs={'class': 'form-control', 'id': 'nickname', 'placeholder': u"请输入您的昵称"}),
                               error_messages={'required': u'昵称不能为空'})

    # nickname验证方法
    def clean_nickname(self):
        pdb.set_trace()
        old_nickname = self.cleaned_data.get('old_nickname')
        nickname = self.cleaned_data.get('nickname')
        #is_exist = User.objects.filter(first_name=nickname).count() > 0
        is_exist = UserProfile.objects.filter(nickname=nickname).count() > 0

        if is_exist:
            # 用事先写入hidden的昵称判断是否是自己的昵称
            if old_nickname == nickname:
                raise ValidationError(u'您当前的昵称就是“%s”，写一个新的吧' % nickname)
            else:
                raise ValidationError(u'“%s”已被使用，请重新输入' % nickname)
        else:
            return nickname