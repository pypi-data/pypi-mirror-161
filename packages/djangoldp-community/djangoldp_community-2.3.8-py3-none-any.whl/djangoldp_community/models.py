import uuid
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from djangoldp.models import Model
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from importlib import import_module

from djangoldp_community.permissions import CommunityPermissions, CommunityCirclePermissions, \
    CommunityProjectPermissions, CommunityJobPermissions, CommunityMembersPermissions, \
    CommunityProfilePermissions
from djangoldp_community.views import CommunityMembersViewset

from djangoldp_circle.models import Circle
from djangoldp_project.models import Project
from djangoldp_joboffer.models import JobOffer
from rest_framework.exceptions import ValidationError

djangoldp_modules = list(settings.DJANGOLDP_PACKAGES)
community_fields = ['@id', 'name', 'profile', 'addresses', 'logo', 'allow_self_registration',\
                             'projects', 'circles', 'members', 'joboffers']

for dldp_module in djangoldp_modules:
    try:
        module_settings = import_module(dldp_module + '.settings')
        module_community_nested_fields = module_settings.COMMUNITY_NESTED_FIELDS
        community_fields += module_community_nested_fields
    except:
        pass


class Community(Model):
    name = models.CharField(max_length=255, blank=True, null=True, help_text="Changing a community's name is highly discouraged")
    logo = models.URLField(blank=True, null=True)
    allow_self_registration = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def __str__(self):
        try:
            return '{} ({})'.format(self.name, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('community')
        verbose_name_plural = _("communities")
        permission_classes = [CommunityPermissions]
        anonymous_perms = ['view']
        authenticated_perms = ['inherit', 'add']
        superuser_perms = ['view']
        lookup_field = 'slug'
        container_path = "/communities/"
        ordering = ['slug']
        serializer_fields = community_fields
        rdf_type = "sib:Community"
        depth = 1

class CommunityProfile(Model):
    community = models.OneToOneField(Community, on_delete=models.CASCADE, related_name='profile', null=True, blank=True)
    shortDescription = models.CharField(max_length=254, blank=True, null=True, default='')
    description = models.TextField(blank=True, null=True, default='')
    phone = models.CharField(max_length=254, blank=True, null=True, default='')
    email = models.EmailField(max_length=254, blank=True, null=True, default='')
    website = models.URLField(blank=True, null=True, default='')
    tweeter = models.URLField(blank=True, null=True, default='')
    facebook = models.URLField(blank=True, null=True, default='')
    linkedin = models.URLField(blank=True, null=True, default='')
    instagram = models.URLField(blank=True, null=True, default='')
    picture1 = models.URLField(blank=True, null=True, default='')
    picture2 = models.URLField(blank=True, null=True, default='')
    picture3 = models.URLField(blank=True, null=True, default='')

    def __str__(self):
        try:
            return '{} ({})'.format(self.community.urlid, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('community profile')
        verbose_name_plural = _("community profiles")
        permission_classes = [CommunityProfilePermissions]
        anonymous_perms = ['view']
        authenticated_perms = ['inherit']
        superuser_perms = ['view']
        container_path = "community-profiles/"
        serializer_fields = ['@id', 'community', 'shortDescription', 'description', 'phone', 'email', 'website', 'tweeter',\
                             'facebook', 'linkedin', 'instagram', 'picture1', 'picture2', 'picture3']
        rdf_type = "sib:CommunityProfile"

class CommunityAddress(Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='addresses', null=True, blank=True)
    address_line1 = models.CharField(max_length=254, blank=True, null=True, default='')
    address_line2 = models.CharField(max_length=254, blank=True, null=True, default='')
    lat = models.DecimalField(max_digits=15, decimal_places=12, blank=True, null=True, verbose_name=_("Latitude"))
    lng = models.DecimalField(max_digits=15, decimal_places=12, blank=True, null=True, verbose_name=_("Longitude"))

    def __str__(self):
        try:
            return '{} ({})'.format(self.community.urlid, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('community address')
        verbose_name_plural = _("community addresses")
        permission_classes = [CommunityProfilePermissions]
        anonymous_perms = ['view']
        authenticated_perms = ['inherit']
        superuser_perms = ['view']
        container_path = "community-addresses/"
        serializer_fields = ['@id', 'community', 'address_line1', 'address_line2', 'lat', 'lng']
        rdf_type = "sib:CommunityAddress"

class CommunityMember(Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='members', null=True, blank=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="communities", null=True, blank=True)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        try:
            return '{} -> {} ({})'.format(self.user.urlid, self.community.urlid, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('community member')
        verbose_name_plural = _("community members")
        view_set = CommunityMembersViewset
        permission_classes = [CommunityMembersPermissions]
        anonymous_perms = ['view']
        authenticated_perms = ['inherit']
        superuser_perms = ['inherit']
        # unique_together = ['user', 'community']
        container_path = "community-members/"
        serializer_fields = ['@id', 'community', 'user', 'is_admin']
        rdf_type = "as:items"

    def save(self, *args, **kwargs):
        if not self.pk and CommunityMember.objects.filter(community=self.community, user=self.user).exists():
            return

        super(CommunityMember, self).save(*args, **kwargs)

class CommunityCircle(Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='circles', null=True, blank=True)
    circle = models.OneToOneField(Circle, on_delete=models.CASCADE, related_name="community", null=True, blank=True)

    def __str__(self):
        try:
            return '{} -> {} ({})'.format(self.circle.urlid, self.community.urlid, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('community circle')
        verbose_name_plural = _("community circles")
        permission_classes = [CommunityPermissions, CommunityCirclePermissions]
        anonymous_perms = ['view']
        authenticated_perms = ['inherit']
        superuser_perms = ['inherit']
        # unique_together = ['circle', 'community']
        container_path = "community-circles/"
        serializer_fields = ['@id', 'community', 'circle']
        rdf_type = "as:items"

    def save(self, *args, **kwargs):
        if not self.pk and CommunityCircle.objects.filter(community=self.community, circle=self.circle).exists():
            return

        super(CommunityCircle, self).save(*args, **kwargs)

class CommunityProject(Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='projects', null=True, blank=True)
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name="community", null=True, blank=True)

    def __str__(self):
        try:
            return '{} -> {} ({})'.format(self.project.urlid, self.community.urlid, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('community project')
        verbose_name_plural = _("community projects")
        permission_classes = [CommunityPermissions, CommunityProjectPermissions]
        anonymous_perms = ['view']
        authenticated_perms = ['inherit']
        superuser_perms = ['inherit']
        # unique_together = ['project', 'community']
        container_path = "community-projects/"
        serializer_fields = ['@id', 'community', 'project']
        rdf_type = "as:items"

    def save(self, *args, **kwargs):
        if not self.pk and CommunityProject.objects.filter(community=self.community, project=self.project).exists():
            return

        super(CommunityProject, self).save(*args, **kwargs)

class CommunityJobOffer(Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='joboffers', null=True, blank=True)
    joboffer = models.OneToOneField(JobOffer, on_delete=models.CASCADE, related_name="community", null=True, blank=True)

    def __str__(self):
        try:
            return '{} -> {} ({})'.format(self.joboffer.urlid, self.community.urlid, self.urlid)
        except:
            return self.urlid

    class Meta(Model.Meta):
        verbose_name = _('community job offer')
        verbose_name_plural = _("community job offers")
        permission_classes = [CommunityPermissions, CommunityJobPermissions]
        anonymous_perms = ['view']
        authenticated_perms = ['inherit']
        superuser_perms = ['inherit']
        # unique_together = ['joboffer', 'community']
        container_path = "community-joboffers/"
        serializer_fields = ['@id', 'community', 'joboffer']
        rdf_type = "as:items"

    def save(self, *args, **kwargs):
        if not self.pk and CommunityJobOffer.objects.filter(community=self.community, joboffer=self.joboffer).exists():
            return

        super(CommunityJobOffer, self).save(*args, **kwargs)

@receiver(pre_save, sender=Community)
def pre_create_account(sender, instance, **kwargs):
    if not instance.urlid or instance.urlid.startswith(settings.SITE_URL):
        if getattr(instance, Model.slug_field(instance)) != slugify(instance.name):
            if Community.objects.local().filter(slug=slugify(instance.name)).count() > 0:
                raise ValidationError(_("Community name must be unique"))
            setattr(instance, Model.slug_field(instance), slugify(instance.name))
            setattr(instance, "urlid", "")
    else:
        # Is a distant object, generate a random slug
        setattr(instance, Model.slug_field(instance), uuid.uuid4().hex.upper()[0:8])

@receiver(post_save, sender=Circle)
def pre_save_circle_relation(sender, instance, **kwargs):
    try:
        if instance.community:
            if instance.community.community:
                instance.community.circle = instance
                instance.community.save()
    except (Community.DoesNotExist, CommunityCircle.DoesNotExist):
        pass

@receiver(post_save, sender=Community)
def create_community_profile(instance, created, **kwargs):
    if not Model.is_external(instance):
        CommunityProfile.objects.get_or_create(community=instance)

@receiver(post_save, sender=Community)
def create_community_member_admin(instance, created, **kwargs):
    if not Model.is_external(instance):
        if created:
            CommunityMember.objects.get_or_create(community=instance, user=getattr(instance, "modification_user", None), is_admin=True)
        else:
            if instance.members.count() == 1 and not instance.members.first().is_admin:
                CommunityMember.objects.filter(community=instance).update(is_admin=True)
            # Community must have an admin. It'll be you so.
            if instance.members.count() == 0:
                CommunityMember.objects.get_or_create(community=instance, user=getattr(instance, "modification_user", None), is_admin=True)

@receiver(post_save, sender=CommunityMember)
def admin_if_last_member(instance, **kwargs):
    if not Model.is_external(instance.community):
        if instance.community.members.count() < 2 and not instance.is_admin:
            instance.is_admin = True
            instance.save()

@receiver(post_delete, sender=CommunityMember)
def admin_if_last_member(instance, **kwargs):
    if not Model.is_external(instance.community):
        if instance.community.members.count() == 1 and not instance.community.members.first().is_admin:
            CommunityMember.objects.filter(community=instance.community).update(is_admin=True)
        # Community must have an admin. It'll be you so.
        if instance.community.members.count() == 0:
            CommunityMember.objects.get_or_create(community=instance.community, user=getattr(instance, "modification_user", None), is_admin=True)
