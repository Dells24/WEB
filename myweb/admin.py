from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from .models import Faculty, Supervisor, Student, ResearchTopic, Milestone, Meeting, Course, ResearchFile
# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_code')
    search_fields = ('name', 'short_code')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'faculty')
    search_fields = ('name', 'faculty__name')

@admin.register(Supervisor)
class SupervisorAdmin(admin.ModelAdmin):
    list_display = ('name', 'faculty', 'email', 'contact')
    search_fields = ('name', 'faculty__name', 'email', 'contact')
    list_filter = ('faculty',)

class ResearchTopicInline(admin.TabularInline):
    model = ResearchTopic
    extra = 1

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'reg_no', 'faculty_name', 'course', 'level', 'selected_topic', 'supervisor', 'profile_image_tag')
    search_fields = ('name', 'reg_no')
    list_filter = ('faculty', 'course', 'supervisor', 'level')
    inlines = [ResearchTopicInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            form.base_fields['selected_topic'].queryset = ResearchTopic.objects.filter(student=obj)
        return form

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('notifications/', self.admin_site.admin_view(self.notifications_view), name='notifications'),
            path('students_without_topics/', self.admin_site.admin_view(self.display_students_without_topics), name='students_without_topics')
        ]
        return custom_urls + urls

    def notifications_view(self, request):
        log_entries = LogEntry.objects.filter(content_type_id=ContentType.objects.get_for_model(Student).pk)
        return render(request, 'admin/notifications.html', {'log_entries': log_entries})

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Remove WebSocket notification code
        # channel_layer = get_channel_layer()
        # if channel_layer:
        #     async_to_sync(channel_layer.group_send)(
        #         "admin_notifications", 
        #         {
        #             "type": "send_notification",
        #             "message": f"New student registered: {obj.name} - {obj.reg_no}"
        #         }
        #     )

    def faculty_name(self, obj):
        return obj.faculty.name
    faculty_name.short_description = 'Faculty'

    def profile_image_tag(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" style="width: 45px; height: 45px;" />'.format(obj.profile_image.url))
        return "-"
    profile_image_tag.short_description = 'Profile Image'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs

    def display_students_without_topics(self, request):
        students_without_topics = Student.objects.filter(selected_topic__isnull=True)
        return render(request, 'admin/students_without_topics.html', {
            'students': students_without_topics,
        })

    def student_without_topics_count(self):
        return Student.objects.filter(selected_topic__isnull=True).count()
    
    student_without_topics_count.short_description = "Students Without Selected Topics"

    actions = ['view_students_without_topics']

    def view_students_without_topics(self, request, queryset):
        return redirect('students_without_topics')  # Redirect to your custom view
    view_students_without_topics.short_description = "View Students Without Selected Topics"

@admin.register(ResearchTopic)
class ResearchTopicAdmin(admin.ModelAdmin):
    list_display = ('topic', 'student', 'district_of_study', 'case_study_area')
    search_fields = ('topic', 'district_of_study', 'case_study_area')
    list_filter = ('district_of_study', 'case_study_area')

@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('milestone_name', 'student', 'due_date', 'completion_date')
    search_fields = ('milestone_name', 'student__name', 'student__reg_no')
    list_filter = ('due_date', 'completion_date')

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('student', 'date')
    search_fields = ('student__name', 'student__reg_no', 'discussion_points')
    list_filter = ('date',)

@admin.register(ResearchFile)
class ResearchFileAdmin(admin.ModelAdmin):
    list_display = ('file', 'description', 'student')
    search_fields = ('student__name', 'description')
    list_filter = ('student',)
