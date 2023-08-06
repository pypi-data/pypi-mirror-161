import uuid
import json
from rest_framework.test import APITestCase, APIClient

from djangoldp_community.models import Community, CommunityMember
from djangoldp_community.tests.models import User


class PermissionsTestCase(APITestCase):
    # Django runs setUp automatically before every test
    def setUp(self):
        # we set up a client, that allows us
        self.client = APIClient()

    # we have custom set up functions for things that we don't want to run before *every* test, e.g. often we want to
    # set up an authenticated user, but sometimes we want to run a test with an anonymous user
    def setUpLoggedInUser(self, is_superuser=False):
        self.user = User(email='test@mactest.co.uk', first_name='Test', last_name='Mactest', username='test',
                         password='glass onion', is_superuser=is_superuser)
        self.user.save()
        # this means that our user is now logged in (as if they had typed username and password)
        self.client.force_authenticate(user=self.user)

    # we write functions like this for convenience - we can reuse between tests
    def _get_random_user(self):
        return User.objects.create(email='{}@test.co.uk'.format(str(uuid.uuid4())), first_name='Test',
                                   last_name='Test',
                                   username=str(uuid.uuid4()))

    def _get_random_community(self):
        return Community.objects.create(name='Test', slug=str(uuid.uuid4()))

    def _get_community_member(self, user, community, is_admin=False):
        return CommunityMember.objects.create(user=user, community=community, is_admin=is_admin)

    '''
    list communities - public
    list community members - public
    create community - authenticated
    update, delete, control community - community admin only
    create, update, delete, control community member - community admin only
    Admins can't remove admins (or themselves if they're the last admin)
    community projects - apply Project permissions (same for JobOffers and Circles)
    '''
    # only authenticated users can create communities
    def test_post_community_anonymous(self):
        response = self.client.post('/communities/', data=json.dumps({}), content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)

    def test_post_community_authenticated(self):
        self.setUpLoggedInUser()
        response = self.client.post('/communities/', data=json.dumps({}), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

    # only community admins can update communities
    def test_update_community_is_admin(self):
        self.setUpLoggedInUser()
        community = self._get_random_community()
        self._get_community_member(user=self.user, community=community, is_admin=True)
        response = self.client.patch('/communities/{}/'.format(community.slug), data=json.dumps({}),
                                     content_type='application/ld+json')
        self.assertEqual(response.status_code, 200)

    def test_update_community_is_member(self):
        self.setUpLoggedInUser(is_superuser=False)
        community = self._get_random_community()
        self._get_community_member(user=self.user, community=community, is_admin=False)
        response = self.client.patch('/communities/{}/'.format(community.slug), data=json.dumps({}),
                                     content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)

    def test_update_community_is_auth_super_user(self):
        self.setUpLoggedInUser(is_superuser=True)
        community = self._get_random_community()
        self._get_community_member(user=self.user, community=community, is_admin=False)
        response = self.client.patch('/communities/{}/'.format(community.slug), data=json.dumps({}),
                                     content_type='application/ld+json')
        self.assertEqual(response.status_code, 403)

    # only community admins can delete communities
    def test_delete_community_is_admin(self):
        self.setUpLoggedInUser(is_superuser=False)
        community = self._get_random_community()
        self._get_community_member(user=self.user, community=community, is_admin=True)
        response = self.client.delete('/communities/{}/'.format(community.slug))
        self.assertEqual(response.status_code, 403)

    def test_delete_community_is_member(self):
        self.setUpLoggedInUser(is_superuser=False)
        community = self._get_random_community()
        self._get_community_member(user=self.user, community=community, is_admin=False)
        response = self.client.delete('/communities/{}/'.format(community.slug))
        self.assertEqual(response.status_code, 403)

    def test_delete_community_is_auth_super_user(self):
        self.setUpLoggedInUser(is_superuser=True)
        community = self._get_random_community()
        self._get_community_member(user=self.user, community=community, is_admin=False)
        response = self.client.delete('/communities/{}/'.format(community.slug))
        self.assertEqual(response.status_code, 403)

    # TODO: https://git.startinblox.com/djangoldp-packages/djangoldp/issues/363
    '''
    def test_get_community_is_member(self):
        self.setUpLoggedInUser(is_superuser=False)
        community = self._get_random_community()
        me = self._get_community_member(user=self.user, community=community, is_admin=False)

        response = self.client.get('/communities/{}/members/'.format(community.slug))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn({'mode': {'@type': 'add'}}, response.data['permissions'])
        self.assertEqual(len(response.data['permissions']), 1)
    '''

    def test_get_communities_is_member(self):
        self.setUpLoggedInUser(is_superuser=False)
        community = self._get_random_community()
        me = self._get_community_member(user=self.user, community=community, is_admin=False)

        response = self.client.get('/communities/')
        self.assertEqual(response.status_code, 200)
        communities = response.data['ldp:contains']
        self.assertEqual(len(communities), 1)
        members_permissions = communities[0]['members']['permissions']
        self.assertNotIn({'mode': {'@type': 'add'}}, members_permissions)
        self.assertEqual(len(members_permissions), 1)

    def test_get_communities_is_admin(self):
        self.setUpLoggedInUser(is_superuser=False)
        community = self._get_random_community()
        me = self._get_community_member(user=self.user, community=community, is_admin=True)

        response = self.client.get('/communities/')
        self.assertEqual(response.status_code, 200)
        communities = response.data['ldp:contains']
        self.assertEqual(len(communities), 1)
        members_permissions = communities[0]['members']['permissions']
        self.assertIn({'mode': {'@type': 'add'}}, members_permissions)
        self.assertIn({'mode': {'@type': 'view'}}, members_permissions)
        self.assertEqual(len(members_permissions), 2)

    # only community admins can do any operation on community members
    def test_add_community_member_is_admin(self):
        self.setUpLoggedInUser(is_superuser=False)
        another_user = self._get_random_user()

        community = self._get_random_community()
        me = self._get_community_member(user=self.user, community=community, is_admin=True)

        body = {
            'http://happy-dev.fr/owl#community': community.urlid,
            'http://happy-dev.fr/owl#user': another_user.urlid
        }

        response = self.client.post('/communities/{}/members/'.format(community.slug),
                                    body=json.dumps(body), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)

    def test_add_community_member_is_member(self):
        self.setUpLoggedInUser(is_superuser=False)
        another_user = self._get_random_user()

        community = self._get_random_community()
        me = self._get_community_member(user=self.user, community=community, is_admin=False)

        body = {
            'http://happy-dev.fr/owl#community': community.urlid,
            'http://happy-dev.fr/owl#user': another_user.urlid
        }

        response = self.client.post('/communities/{}/members/', body=json.dumps(body), content_type='application/ld+json')
        self.assertEqual(response.status_code, 404)

    # TODO: https://git.startinblox.com/djangoldp-packages/djangoldp-community/issues/3
    '''
    def test_add_community_member_is_admin_no_parent(self):
        self.setUpLoggedInUser(is_superuser=False)
        another_user = self._get_random_user()

        community = self._get_random_community()
        me = self._get_community_member(user=self.user, community=community, is_admin=True)

        body = {
            'http://happy-dev.fr/owl#community': community.urlid,
            'http://happy-dev.fr/owl#user': another_user.urlid
        }

        response = self.client.post('/community-members/', body=json.dumps(body), content_type='application/ld+json')
        self.assertEqual(response.status_code, 201)
    '''

    def test_delete_community_member_is_admin(self):
        self.setUpLoggedInUser(is_superuser=False)
        another_user = self._get_random_user()

        community = self._get_random_community()
        me = self._get_community_member(user=self.user, community=community, is_admin=True)
        member = self._get_community_member(user=another_user, community=community, is_admin=False)

        response = self.client.delete('/community-members/{}/'.format(member.pk))
        self.assertEqual(response.status_code, 204)

    def test_delete_community_member_is_member(self):
        self.setUpLoggedInUser(is_superuser=False)
        another_user = self._get_random_user()

        community = self._get_random_community()
        me = self._get_community_member(user=self.user, community=community, is_admin=False)
        member = self._get_community_member(user=another_user, community=community, is_admin=False)

        response = self.client.delete('/community-members/{}/'.format(member.pk))
        self.assertEqual(response.status_code, 403)

    def test_delete_community_member_is_auth_super_user(self):
        self.setUpLoggedInUser(is_superuser=True)
        another_user = self._get_random_user()

        community = self._get_random_community()
        me = self._get_community_member(user=self.user, community=community, is_admin=False)
        member = self._get_community_member(user=another_user, community=community, is_admin=False)

        response = self.client.delete('/community-members/{}/'.format(member.pk))
        self.assertEqual(response.status_code, 403)

    # community admins cannot remove other admins
    def test_delete_community_admin_is_admin(self):
        self.setUpLoggedInUser(is_superuser=False)
        another_user = self._get_random_user()

        community = self._get_random_community()
        me = self._get_community_member(user=self.user, community=community, is_admin=True)
        member = self._get_community_member(user=another_user, community=community, is_admin=True)

        response = self.client.delete('/community-members/{}/'.format(member.pk))
        self.assertEqual(response.status_code, 403)

    # community admins can remove themselves
    def test_delete_self_is_admin(self):
        self.setUpLoggedInUser(is_superuser=False)
        another_user = self._get_random_user()

        community = self._get_random_community()
        me = self._get_community_member(user=self.user, community=community, is_admin=True)
        member = self._get_community_member(user=another_user, community=community, is_admin=True)

        response = self.client.delete('/community-members/{}/'.format(me.pk))
        self.assertEqual(response.status_code, 204)

    # community admins cannot remove themselves if they are the last admin
    def test_delete_self_is_last_admin(self):
        self.setUpLoggedInUser(is_superuser=False)
        another_user = self._get_random_user()

        community = self._get_random_community()
        me = self._get_community_member(user=self.user, community=community, is_admin=True)
        member = self._get_community_member(user=another_user, community=community, is_admin=False)

        response = self.client.delete('/community-members/{}/'.format(me.pk))
        self.assertEqual(response.status_code, 403)

    # regular users can remove themselves
    def test_delete_self(self):
        self.setUpLoggedInUser(is_superuser=True)
        another_user = self._get_random_user()

        community = self._get_random_community()
        me = self._get_community_member(user=self.user, community=community, is_admin=False)
        member = self._get_community_member(user=another_user, community=community, is_admin=True)

        response = self.client.delete('/community-members/{}/'.format(me.pk))
        self.assertEqual(response.status_code, 204)
