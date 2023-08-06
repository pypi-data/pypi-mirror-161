from django.urls import path
from .views import CreateMessageView


urlpatterns = (
    path('', CreateMessageView.as_view(), name='create_message'),
)
