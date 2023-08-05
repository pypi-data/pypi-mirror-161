"""
Helper factories for tests
"""
import factory
from django.contrib.auth import get_user_model


class UserFactory(factory.django.DjangoModelFactory):
    """
    Factory helper for tests
    """
    email = factory.Sequence('robot{}@example.com'.format)
    username = factory.Sequence('robot{}'.format)

    class Meta:
        model = get_user_model()
