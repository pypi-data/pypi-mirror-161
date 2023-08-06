from captcha.fields import ReCaptchaField
from django import forms
from .models import Message


class MessageForm(forms.ModelForm):
    name = forms.CharField(
        label='Your name',
        max_length=100
    )

    email = forms.EmailField(
        label='Your email address',
        max_length=255
    )

    body = forms.CharField(
        label='Your message',
        widget=forms.Textarea
    )

    captcha = ReCaptchaField()

    class Meta:
        model = Message
        fields = (
            'name',
            'email',
            'subject',
            'body'
        )
