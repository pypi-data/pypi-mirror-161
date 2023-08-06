"""
Views for organizations end points.
"""
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet
from organizations.models import Organization
from organizations.serializers import OrganizationSerializer

from tahoe_sites.permissions import IsStaffOrSuperuser


class OrganizationViewSet(ReadOnlyModelViewSet):  # pylint: disable=too-many-ancestors
    """
    Organization details using Token Authentication
    """
    queryset = Organization.objects.filter(active=True)
    serializer_class = OrganizationSerializer
    lookup_field = 'short_name'
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, IsStaffOrSuperuser)
