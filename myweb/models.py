from django.db import models

class Faculty(models.Model):
    name = models.CharField(max_length=100)
    short_code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name

class Supervisor(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    contact = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=100)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Student(models.Model):
    LEVEL_CHOICES = [
        ('DEGREE', 'Degree'),
        ('DIPLOMA', 'Diploma'),
        ('NATIONAL_CERTIFICATE', 'National Certificate'),
    ]
    
    profile_image = models.ImageField(upload_to='student_images/', blank=True, null=True)
    name = models.CharField(max_length=100)
    reg_no = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='DEGREE')
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE, blank=True, null=True)
    selected_topic = models.ForeignKey('ResearchTopic', null=True, blank=True, on_delete=models.SET_NULL, related_name='selected_for')
    start_date = models.DateField(blank=True, null=True)
    graduation_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.reg_no}"

class ResearchTopic(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    topic = models.CharField(max_length=200)
    district_of_study = models.CharField(max_length=100)
    case_study_area = models.CharField(max_length=100)

    def __str__(self):
        return self.topic

class Milestone(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    milestone_name = models.CharField(max_length=100)
    due_date = models.DateField()
    completion_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.selected_topic.topic} - {self.milestone_name}"

class Meeting(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    discussion_points = models.TextField()
    action_items = models.TextField()

    def __str__(self):
        return f"{self.student.selected_topic.topic} {self.date} {self.discussion_points}"

class ResearchFile(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    file = models.FileField(upload_to='research_files/')
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.description if self.description else str(self.file)
