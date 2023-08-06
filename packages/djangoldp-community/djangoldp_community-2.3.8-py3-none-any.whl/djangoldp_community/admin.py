from django.conf import settings
from django.contrib import admin
from djangoldp.admin import DjangoLDPAdmin
from djangoldp.models import Model
from djangoldp_community.models import Community, CommunityMember, CommunityCircle,\
    CommunityProject, CommunityJobOffer, CommunityProfile, CommunityAddress
from importlib import import_module


class EmptyAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        return {}


class MemberInline(admin.TabularInline):
    model = CommunityMember
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink')
    extra = 0


class CircleInline(admin.TabularInline):
    model = CommunityCircle
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink')
    extra = 0


class ProjectInline(admin.TabularInline):
    model = CommunityProject
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink')
    extra = 0


class JobOfferInline(admin.TabularInline):
    model = CommunityJobOffer
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink')
    extra = 0


class ProfileInline(admin.StackedInline):
    model = CommunityProfile
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink')
    extra = 0


class AddressInline(admin.TabularInline):
    model = CommunityAddress
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink')
    extra = 0


djangoldp_modules = list(settings.DJANGOLDP_PACKAGES)
community_inlines = [ProfileInline, AddressInline,
                     MemberInline, CircleInline, ProjectInline, JobOfferInline]

for dldp_module in djangoldp_modules:
    try:
        module_settings = import_module(dldp_module + '.settings')
        module_community_inlines = module_settings.COMMUNITY_ADMIN_INLINES
        for module in module_community_inlines:
            module_admin = import_module(module[0])
            community_inlines += [getattr(module_admin, module[1])]
    except:
        pass


class CommunityAdmin(DjangoLDPAdmin):
    list_display = ('urlid', 'name', 'allow_self_registration')
    exclude = ('urlid', 'slug', 'is_backlink', 'allow_create_backlink')
    inlines = community_inlines
    search_fields = ['urlid', 'name',
                     'members__user__urlid', 'circles__circle__name']
    ordering = ['urlid']

    def get_queryset(self, request):
        # Hide distant communities
        queryset = super(CommunityAdmin, self).get_queryset(request)
        internal_ids = [x.pk for x in queryset if not Model.is_external(x)]
        return queryset.filter(pk__in=internal_ids)


admin.site.register(Community, CommunityAdmin)
admin.site.register(CommunityMember, EmptyAdmin)
admin.site.register(CommunityCircle, EmptyAdmin)
admin.site.register(CommunityProject, EmptyAdmin)
admin.site.register(CommunityJobOffer, EmptyAdmin)
admin.site.register(CommunityProfile, EmptyAdmin)
admin.site.register(CommunityAddress, EmptyAdmin)
