from django.conf.urls import url
from .views import OpenCommunitiesViewset
from .models import Community
from djangoldp.models import Model

urlpatterns = [
    url(r'^open-communities/', OpenCommunitiesViewset.urls(model_prefix="open-communities",
        model=Community,
        lookup_field=Model.get_meta(Community, 'lookup_field', 'pk'),
        permission_classes=Model.get_meta(Community, 'permission_classes', []),
        fields=Model.get_meta(Community, 'serializer_fields', []),
        nested_fields=Model.get_meta(Community, 'nested_fields', [])))
]
