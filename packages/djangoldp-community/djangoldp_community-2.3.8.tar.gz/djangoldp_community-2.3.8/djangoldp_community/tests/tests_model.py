from djangoldp.serializers import LDListMixin, LDPSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase, APIClient

from djangoldp_community.models import Community


class ModelTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

    # I should not be able to create duplicate names in local communities
    def test_cant_create_duplicate_local_communities(self):
        def create_community():
            Community.objects.create(name='Test')

        create_community()
        try:
            create_community()
            self.fail('Was able to create a local community with a duplicate name!')
        except ValidationError:
            pass

    # I should be able to create multiple backlinked communities without a name
    def test_can_create_duplicate_external_communities(self):
        Community.objects.create(urlid="https://example.com/external/1/")
        try:
            Community.objects.create(urlid="https://example.com/external/2/")
        except ValidationError as e:
            self.fail('Creating duplicate external Community raised exception ' + str(e))
