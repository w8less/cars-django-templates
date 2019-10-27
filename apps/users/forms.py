from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from apps.users.models import Profile, UserFilter
from apps.users.utils import normalize_phone, normalize_email, valid_phone


class PhoneRequiredMixin(forms.Form):
    phone = forms.CharField(
        required=True,
        max_length=20
    )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        phone = normalize_phone(phone)

        if not valid_phone(phone):
            error_message = u'Invalid format'
            raise forms.ValidationError(error_message)

        return phone


class EmailRequiredMixin(forms.Form):
    email = forms.EmailField(required=True)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        email = normalize_email(email)
        return email


class ProfileCreationForm(UserCreationForm, PhoneRequiredMixin, EmailRequiredMixin):

    def __init__(self, *args, **kargs):
        super(ProfileCreationForm, self).__init__(*args, **kargs)
        try:
            del self.fields['username']
        except KeyError:
            pass

    class Meta:
        model = Profile
        fields = ('phone', 'name', 'email')


class ProfileChangeForm(UserChangeForm, PhoneRequiredMixin, EmailRequiredMixin):

    def __init__(self, *args, **kargs):
        super(ProfileChangeForm, self).__init__(*args, **kargs)
        try:
            del self.fields['username']
        except KeyError:
            pass

    class Meta:
        model = Profile
        fields = '__all__'


class RegistrationForm(forms.ModelForm, EmailRequiredMixin, PhoneRequiredMixin):

    class Meta:
        model = Profile
        fields = ('name', 'profile_type', 'email', 'phone', 'password')


class ProfileUpdateForm(forms.ModelForm, EmailRequiredMixin, PhoneRequiredMixin):

    class Meta:
        model = Profile
        fields = ('name', 'email', 'phone', 'profile_type', 'plan_type', 'expired', 'comment')


class UserFilterForm(forms.ModelForm):

    class Meta:
        model = UserFilter
        fields = (
            'name', 'description', 'model', 'mark', 'gearbox',
            'location', 'year_start', 'year_end', 'price_start',
            'price_end', 'cleared', 'dtp', 'blocked', 'dealer',
            'fuel', 'body', 'engine', 'mileage_start', 'mileage_end'
        )
