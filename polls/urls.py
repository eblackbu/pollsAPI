from django.urls import path, include


app_name = 'polls'
urlpatterns = [
    path('v1/', include('polls.v1urls', namespace='v1')),
]
