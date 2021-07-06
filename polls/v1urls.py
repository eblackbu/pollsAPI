from django.urls import path, include
from rest_framework.routers import SimpleRouter

from polls.viewsets import PollViewSet, PollUserViewSet, QuestionViewSet

app_name = 'polls'

router = SimpleRouter()
router.register(r'polls', PollViewSet)
router.register(r'users', PollUserViewSet)
router.register(r'questions', QuestionViewSet)

urlpatterns = router.urls
