from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import View
from .models import Student, ResearchTopic, Milestone, Meeting, ResearchFile
from .forms import StudentForm, ResearchTopicFormSet, RegistrationNumberForm, ResearchFileForm
from django.urls import reverse

class StudentIDInputView(View):
    template_name = 'student_id_input.html'

    def get(self, request):
        # Fetch the last five students who have submitted their research topics
        latest_students = Student.objects.filter(selected_topic__isnull=False).order_by('-selected_topic__id')[:5]
        return render(request, self.template_name, {
            'latest_students': latest_students,
        })

def students_without_topics(request):
    students_without_topics = Student.objects.filter(selected_topic__isnull=True)
    return render(request, 'admin/students_without_topics.html', {
        'students': students_without_topics,
    })

def home(request):
    return render(request, 'home.html')

def all(request):
    template_name = 'all.html'
    return render(request, 'all.html')

class StudentResearchGuideView(View):
    template_name = 'research_guide.html'

    def get(self, request):
        reg_no = request.GET.get('reg_no')
        if not reg_no:
            return redirect('student_id_input')

        student = get_object_or_404(Student, reg_no=reg_no)
        research_project = student.selected_topic
        milestones = Milestone.objects.filter(student=student).order_by('due_date')
        total_milestones = milestones.count()
        completed_milestones = milestones.filter(completion_date__isnull=False).count()
        progress = (completed_milestones / total_milestones) * 100 if total_milestones > 0 else 0
        meetings = Meeting.objects.filter(student=student).order_by('date')
        research_files = ResearchFile.objects.filter(student=student)

        file_form = ResearchFileForm()

        context = {
            'student': student,
            'research_project': research_project,
            'milestones': milestones,
            'progress': progress,
            'meetings': meetings,
            'file_form': file_form,
            'research_files': research_files,  # Add this line
        }
        return render(request, self.template_name, context)

    def post(self, request):
        reg_no = request.GET.get('reg_no')
        student = get_object_or_404(Student, reg_no=reg_no)

        file_form = ResearchFileForm(request.POST, request.FILES)
        if file_form.is_valid():
            research_file = file_form.save(commit=False)
            research_file.student = student
            research_file.save()
            return redirect(reverse('research_guide') + f'?reg_no={student.reg_no}')

        research_project = student.selected_topic
        milestones = Milestone.objects.filter(student=student).order_by('due_date')
        total_milestones = milestones.count()
        completed_milestones = milestones.filter(completion_date__isnull=False).count()
        progress = (completed_milestones / total_milestones) * 100 if total_milestones > 0 else 0
        meetings = Meeting.objects.filter(student=student).order_by('date')
        research_files = ResearchFile.objects.filter(student=student)

        context = {
            'student': student,
            'research_project': research_project,
            'milestones': milestones,
            'progress': progress,
            'meetings': meetings,
            'file_form': file_form,
            'research_files': research_files,  # Add this line
        }
        return render(request, self.template_name, context)
    
def view_research_data(request):
    research_data = None
    form = RegistrationNumberForm()

    if request.method == 'POST':
        form = RegistrationNumberForm(request.POST)
        if form.is_valid():
            reg_no = form.cleaned_data['reg_no']
            try:
                student = Student.objects.get(reg_no=reg_no)
                research_data = {
                    'student': student,
                    'research_topics': student.selected_topic,
                    'milestones': student.milestone_set.all(),
                    'meetings': student.meeting_set.all(),
                }
            except Student.DoesNotExist:
                research_data = 'Student not found.'

    return render(request, 'view_research_data.html', {'form': form, 'research_data': research_data})

def student_list(request):
    students = Student.objects.select_related('supervisor', 'selected_topic')
    return render(request, 'student_list.html', {'students': students})

def register(request):
    if request.method == 'POST':
        student_form = StudentForm(request.POST)
        topic_formset = ResearchTopicFormSet(request.POST)
        if student_form.is_valid() and topic_formset.is_valid():
            student = student_form.save()
            topics = topic_formset.save(commit=False)
            for topic in topics:
                topic.student = student
                topic.save()
            return redirect('success')
    else:
        student_form = StudentForm()
        topic_formset = ResearchTopicFormSet(queryset=ResearchTopic.objects.none())

    return render(request, 'register.html', {
        'student_form': student_form,
        'topic_formset': topic_formset,
    })

def success(request):
    return HttpResponse("Registration successful!")

