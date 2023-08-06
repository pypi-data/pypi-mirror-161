from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from djangoldp.models import Model
from djangoldp_circle.models import Circle
from djangoldp_community.models import Community, CommunityMember, CommunityCircle

class Command(BaseCommand):
  help = 'Create a community and append all local users to it'

  def add_arguments(self, parser):
    parser.add_argument('--name', type=str, default="Community", help='Name of your community')

  def handle(self, *args, **options):
    community = Community.objects.get_or_create(name=options['name'])
    for user in get_user_model().objects.all():
      if(not Model.is_external(user)):
        CommunityMember.objects.get_or_create(community=community[0], user=user)
    for circle in Circle.objects.all():
      if(not Model.is_external(circle)) and not hasattr(circle, 'community'):
        CommunityCircle.objects.get_or_create(community=community[0], circle=circle)

    self.stdout.write(self.style.SUCCESS('Successful created community'))
