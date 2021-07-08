from django.urls import path, include
from rest_framework.routers import SimpleRouter

from polls.viewsets import PollViewSet, PollUserViewSet, QuestionViewSet, CompletedPollViewSet

app_name = 'polls'

router = SimpleRouter()
router.register(r'polls', PollViewSet)
router.register(r'users', PollUserViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'completed_polls', CompletedPollViewSet)

urlpatterns = router.urls
