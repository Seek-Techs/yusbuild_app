from rest_framework.routers import DefaultRouter
from .views import PileViewSet

router = DefaultRouter()
router.register("piles", PileViewSet)

urlpatterns = router.urls