from django.urls import path
from .views import StudentResearchGuideView, StudentIDInputView,student_list, register, success,view_research_data, students_without_topics
urlpatterns = [
    path('', StudentIDInputView.as_view(), name='student_id_input'),
    path('research-guide/', StudentResearchGuideView.as_view(), name='research_guide'),
    path('students/', student_list, name='student_list'),
    path('all/', all, name='all'),
    path('register/', register, name='register'),
    path('success/', success, name='success'),
    path('view-research-data/', view_research_data, name='view_research_data'),
    path('students_without_topics/',students_without_topics, name='students_without_topics'),
]