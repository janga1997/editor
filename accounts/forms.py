from django.conf import settings
from registration.forms import RegistrationForm
from django import forms
from django.forms.widgets import PasswordInput, Textarea
from django.utils.translation import ugettext_lazy as _
from accounts.models import UserProfile
from django.contrib.auth.models import User
from sanitizer.forms import SanitizedCharField
from django import apps

class NumbasRegistrationForm(RegistrationForm):
    first_name = forms.CharField(label=_('First Name(s)'))
    last_name = forms.CharField(label=_('Surname'))
    if apps.registry.apps.is_installed('numbasmailing'):
        subscribe = forms.BooleanField(label=_('Subscribe to the Numbas newsletter'),required=False)

    register_button = _('Register')

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('first_name','last_name','email','bio','language','avatar')

    first_name = forms.CharField(max_length=30,widget=forms.TextInput(attrs={'class':'form-control'}))
    last_name = forms.CharField(max_length=30,widget=forms.TextInput(attrs={'class':'form-control'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'class':'form-control'}))
    language = forms.ChoiceField(choices=[(x,y) for y,x in settings.GLOBAL_SETTINGS['NUMBAS_LOCALES']],widget=forms.Select(attrs={'class':'form-control'}))
    bio = SanitizedCharField(
            widget=Textarea, 
            allowed_tags=settings.SANITIZER_ALLOWED_TAGS, 
            allowed_attributes=settings.SANITIZER_ALLOWED_ATTRIBUTES, 
            required=False
            )

    def __init__(self, *args, **kw):
        super(UserProfileForm, self).__init__(*args, **kw)
        self.profile = self.get_profile()
        self.fields['language'].initial = self.profile.language
        self.fields['bio'].initial = self.profile.bio
    
    def get_profile(self):
        return UserProfile.objects.get(user=self.instance)

    def save(self,*args,**kwargs):
        self.profile.language = self.cleaned_data.get('language')
        self.profile.bio = self.cleaned_data.get('bio')
        if self.cleaned_data.get('avatar'):
            self.profile.avatar = self.cleaned_data.get('avatar')
        self.profile = self.profile.save()
        super(UserProfileForm,self).save(self,*args,**kwargs)

class ChangePasswordForm(forms.ModelForm):
    class Meta:
        model = User
        fields = []
    password1 = forms.CharField(widget=PasswordInput(attrs={'class':'form-control'}),label='New password')
    password2 = forms.CharField(widget=PasswordInput(attrs={'class':'form-control'}),label='Type new password again')

    def clean(self):
        cleaned_data = super(forms.ModelForm,self).clean()

        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if (not password2) or password1 != password2:
            raise forms.ValidationError("You didn't type the same password twice.")

        return cleaned_data


    def save(self,*args,**kwargs):
        print('save!')
        password = self.cleaned_data.get('password1')

        self.instance.set_password(password)
        self.instance.save()
