from django.urls import path
from .views import SubscriptionCallbackView


urlpatterns = (
    path(
        '<uuid:pk>/',
        SubscriptionCallbackView.as_view(),
        name='websub_callback'
    ),
)
