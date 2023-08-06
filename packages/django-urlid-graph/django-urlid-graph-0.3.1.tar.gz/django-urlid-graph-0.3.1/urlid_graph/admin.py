from django.contrib import admin

from urlid_graph.models import ElementConfig, Entity, JobLog, LogStep, ObjectRepository, SavedGraph


class JobLogAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description", "progress", "eta", "current_step", "last_updated_at")
    search_fields = ("id", "name", "description")
    readonly_fields = ("progress", "eta", "current_step", "last_updated_at")


class LogStepAdmin(admin.ModelAdmin):
    list_display = ("id", "job_id", "created_at", "action", "step", "message", "done", "total")
    search_fields = ("job__id", "action", "step", "message")

    def job_id(self, instance):
        if instance.id:
            return instance.job.id
        return "-"

    job_id.short_description = "Job ID"


class EntityAdmin(admin.ModelAdmin):
    pass


class ElementConfigAdmin(admin.ModelAdmin):
    pass


class ObjectRepositoryAdmin(admin.ModelAdmin):
    pass


class SavedGraphAdmin(admin.ModelAdmin):
    pass


admin.site.register(JobLog, JobLogAdmin)
admin.site.register(LogStep, LogStepAdmin)
admin.site.register(Entity, EntityAdmin)
admin.site.register(ElementConfig, ElementConfigAdmin)
admin.site.register(ObjectRepository, ObjectRepositoryAdmin)
admin.site.register(SavedGraph, SavedGraphAdmin)
