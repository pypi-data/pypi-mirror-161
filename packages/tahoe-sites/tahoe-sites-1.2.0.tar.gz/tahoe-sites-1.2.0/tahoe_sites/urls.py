"""
v1 URLs
"""
from rest_framework import routers

from tahoe_sites.views import OrganizationViewSet

router = routers.SimpleRouter()
router.register(r'api/v1/organizations', OrganizationViewSet, basename='tahoe_sites_organization')

urlpatterns = router.urls
