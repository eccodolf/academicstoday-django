from django.shortcuts import render
from django.core import serializers
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
import json
import datetime
from registrar.models import Course
from registrar.models import Announcement
from registrar.models import Syllabus
from registrar.models import Policy
from registrar.models import Lecture
from registrar.models import Assignment
from registrar.models import Quiz
from registrar.models import Exam
from registrar.models import CourseSubmission

@login_required(login_url='/landpage')
def overview_page(request, course_id):
    course = Course.objects.get(id=course_id)

    try:
        review = CourseSubmission.objects.get(course=course)
    except CourseSubmission.DoesNotExist:
        review = None

    try:
        announcements = Announcement.objects.filter(course=course).order_by('-post_date')
    except Announcement.DoesNotExist:
        announcements = None

    try:
        syllabus = Syllabus.objects.get(course=course)
    except Syllabus.DoesNotExist:
        syllabus = None

    try:
        policy = Policy.objects.get(course=course)
    except Policy.DoesNotExist:
        policy = None

    try:
        lectures = Lecture.objects.filter(course=course).order_by('-lecture_num')
    except Lecture.DoesNotExist:
        lectures = None

    try:
        assignments = Assignment.objects.filter(course=course).order_by('-assignment_num')
    except Assignment.DoesNotExist:
        assignments = None

    try:
        quizzes = Quiz.objects.filter(course=course).order_by('-quiz_num')
    except Quiz.DoesNotExist:
        quizzes = None

    try:
        exams = Exam.objects.filter(course=course).order_by('-exam_num')
    except Exam.DoesNotExist:
        exams = None

    return render(request, 'teacher/overview/view.html',{
        'course': course,
        'review': review,
        'announcements' : announcements,
        'syllabus': syllabus,
        'lectures': lectures,
        'assignments': assignments,
        'quizzes': quizzes,
        'exams': exams,
        'policy': policy,
        'COURSE_SUBMITTED_FOR_REVIEW_STATUS': settings.COURSE_SUBMITTED_FOR_REVIEW_STATUS,
        'COURSE_IN_REVIEW_STATUS': settings.COURSE_IN_REVIEW_STATUS,
        'COURSE_UNAVAILABLE_STATUS': settings.COURSE_UNAVAILABLE_STATUS,
        'COURSE_AVAILABLE_STATUS': settings.COURSE_AVAILABLE_STATUS,
        'COURSE_REJECTED_STATUS': settings.COURSE_REJECTED_STATUS,
        'user': request.user,
        'tab': 'overview',
        'local_css_urls': settings.SB_ADMIN_CSS_LIBRARY_URLS,
        'local_js_urls': settings.SB_ADMIN_JS_LIBRARY_URLS,
    })

@login_required(login_url='/landpage')
def submit_course_for_review(request, course_id):
    course = Course.objects.get(id=course_id)
    response_data = {'status' : 'failed', 'message' : ''}

    # Validate announcements
    try:
        announcements = Announcement.objects.filter(course=course).order_by('-post_date')
        if announcements.count() < 1:
            response_data['message'] = 'zero announcements'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    except Announcement.DoesNotExist:
        response_data['message'] = 'no announcements detected'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    # Validate syllabus
    try:
        Syllabus.objects.get(course=course)
    except Syllabus.DoesNotExist:
        response_data['message'] = 'no syllabus set'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    # Validate policy
    try:
        Policy.objects.get(course=course)
    except Policy.DoesNotExist:
        response_data['message'] = 'no policy set'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    # Validate lectures
    try:
        lectures = Lecture.objects.filter(course=course).order_by('-lecture_num')
        if lectures.count() < 2:
            response_data['message'] = 'minimum 2 lectures required'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    except Lecture.DoesNotExist:
        response_data['message'] = 'no policy set'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    # Validate assignments
    try:
        assignments = Assignment.objects.filter(course=course).order_by('-assignment_num')
        if assignments.count() < 2:
            response_data['message'] = 'minimum 1 assignment required'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    except Assignment.DoesNotExist:
        response_data['message'] = 'no assignment(s)'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    # Validate quizzes
    try:
        quizzes = Quiz.objects.filter(course=course).order_by('-quiz_num')
        if quizzes.count() < 2:
            response_data['message'] = 'minimum 1 quiz required'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    except Quiz.DoesNotExist:
        response_data['message'] = 'no quiz(zes) found'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    # Validate exams
    try:
        exams = Exam.objects.filter(course=course).order_by('-exam_num')
        if exams.count() < 1:
            response_data['message'] = 'minimum 1 exam required'
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    except Exam.DoesNotExist:
        response_data['message'] = 'no exams(s) found'
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    review = CourseSubmission.objects.create(
        course=course,
    )
    review.save()

    response_data = {'status' : 'success', 'message' : 'submitted course review'}
    return HttpResponse(json.dumps(response_data), content_type="application/json")