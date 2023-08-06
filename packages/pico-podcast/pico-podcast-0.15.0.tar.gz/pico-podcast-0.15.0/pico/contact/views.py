from django.contrib import messages
from django.views.generic import CreateView
from pico import menu
from pico.seo.mixins import SEOMixin
from .forms import MessageForm
from .models import Message


class CreateMessageView(SEOMixin, CreateView):
    model = Message
    form_class = MessageForm
    seo_title = 'Contact Us'

    def get_context_data(self, **kwargs):
        return {
            'next': self.get_success_url(),
            'podcast': getattr(self.request, 'podcast', None),
            'menu_items': menu.build(self.request),
            **super().get_context_data(**kwargs)
        }

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Thank you for your message.')
        return response

    def get_success_url(self):
        if self.request.method == 'POST' and self.request.POST.get('next'):
            return self.request.POST['next']

        if self.request.method == 'GET' and self.request.GET.get('next'):
            return self.request.GET['next']

        return '/'
