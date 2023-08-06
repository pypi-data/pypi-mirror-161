from django.http import Http404
from djangoldp.views import LDPViewSet
from djangoldp.utils import is_authenticated_user


class CommunityMembersViewset(LDPViewSet):

    def get_parent(self):
        raise NotImplementedError("get_parent not implemented in CommunityMembersViewSet")

    def is_safe_create(self, user, validated_data, *args, **kwargs):
        from djangoldp_community.models import Community

        try:
            if 'community' in validated_data.keys():
                community = Community.objects.get(urlid=validated_data['community']['urlid'])
            else:
                community = self.get_parent()

            if community.allow_self_registration or \
                    (is_authenticated_user(user) and community.members.filter(user=user, is_admin=True).exists()):
                return True
        except Community.DoesNotExist:
            return True
        except (KeyError, AttributeError):
            raise Http404('community not specified with urlid')

        return False


class OpenCommunitiesViewset(LDPViewSet):
  def get_queryset(self):
    queryset = super().get_queryset().exclude(allow_self_registration=False)

    # invalidate cache for every open communities
    # unless /open-communities/ is loaded before /communities/xyz/, the last one will get wrong permission nodes
    from djangoldp.models import invalidate_model_cache_if_has_entry
    invalidate_model_cache_if_has_entry(self.model)

    return queryset
