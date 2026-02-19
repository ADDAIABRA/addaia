from import_export import resources
from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from .models import Visitor

class VisitorResource(resources.ModelResource):
    class Meta:
        model = Visitor
        fields = (
            "id",
            "username",
            "ip_address",
            "machine_key",
            "timestamp",
            "user_agent",
            "referer",
            "page_visited",
        )
        export_order = fields  # mesma ordem acima

@admin.register(Visitor)
class VisitorAdmin(ImportExportModelAdmin):
    resource_class = VisitorResource
    list_display = ('username', 'ip_address', 'machine_key', 'timestamp', 'page_visited')
    list_filter = ('timestamp', 'username')
    search_fields = ('ip_address', 'username', 'machine_key', 'page_visited')
