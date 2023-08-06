from django.contrib import admin
from djangoldp.admin import DjangoLDPAdmin
from djangoldp.models import Model
from .models import Circle, CircleMember, CircleAccessRequest


class EmptyAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        return {}


class TeamInline(admin.TabularInline):
    model = CircleMember
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink')
    extra = 0


class CircleAccessRequestAdmin(DjangoLDPAdmin):
    list_display = ('urlid', 'user', 'circle', 'status')
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink')
    search_fields = ['urlid', 'user__urlid', 'circle__urlid', 'circle__name']
    ordering = ['urlid']


class CircleAccessRequestInline(admin.TabularInline):
    model = CircleAccessRequest
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink')
    extra = 0


class CircleAdmin(DjangoLDPAdmin):
    list_display = ('urlid', 'name', 'owner', 'status', 'jabberID')
    exclude = ('urlid', 'is_backlink', 'allow_create_backlink', 'jabberID', 'jabberRoom')
    search_fields = ['urlid', 'name', 'members__user__urlid', 'subtitle', 'description', 'status', 'owner__urlid']
    ordering = ['urlid']
    inlines = [TeamInline, CircleAccessRequestInline]

    def get_queryset(self, request):
        # Hide distant circles
        queryset = super(CircleAdmin, self).get_queryset(request)
        internal_ids = [x.pk for x in queryset if not Model.is_external(x)]
        return queryset.filter(pk__in=internal_ids)


admin.site.register(CircleMember, EmptyAdmin)
admin.site.register(Circle, CircleAdmin)
admin.site.register(CircleAccessRequest, CircleAccessRequestAdmin)
