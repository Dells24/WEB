from django.contrib import admin
from .models import Student, Position, Candidate, Vote

class CandidateInline(admin.TabularInline):
    model = Candidate
    extra = 1  # Number of empty forms to display

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'reg_no', 'email', 'is_active', 'has_voted')
    list_filter = ('is_active', 'has_voted')
    search_fields = ('name', 'reg_no', 'email')
    ordering = ('name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related()  # Use select_related for performance optimization

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)

from django.contrib import admin
from django.utils.html import mark_safe
from .models import Candidate  # Adjust the import based on your project structure

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'position', 'votes_count', 'image_preview')
    list_filter = ('position',)
    search_fields = ('name', 'position__title')

    def votes_count(self, obj):
        return obj.get_vote_count()  # Using the method from the Candidate model
    votes_count.short_description = 'Votes Count'  # Custom label for the votes column

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="width: 50px; height: 50px;" />')
        return 'No image'
    image_preview.short_description = 'Image'  # Custom label for the image column


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('student', 'candidate', 'timestamp')
    list_filter = ('candidate',)
    search_fields = ('student__name', 'candidate__name', 'candidate__position__title')
    readonly_fields = ('timestamp',)  # Make timestamp read-only

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('student', 'candidate')  # Optimize related lookups

# Optionally, you can register your models without decorators
# admin.site.register(Student, StudentAdmin)
# admin.site.register(Position, PositionAdmin)
# admin.site.register(Candidate, CandidateAdmin)
# admin.site.register(Vote, VoteAdmin)
