import re
from django.shortcuts import HttpResponse, redirect, render,get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.template import context
from .models import *
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.http import Http404


def is_college_admin(user):
    '''checks if authenticated and is a college admin'''
    if user.is_authenticated:
        return user.userType == '1'
    else:
        return False

@user_passes_test(is_college_admin, login_url='/')
def Home(request):
    return render(request, "college/college_dashboard.html")

@user_passes_test(is_college_admin, login_url='/')
def Course_list(request):
    courses = Course.objects.filter(college=request.user.college)
    return render(request, "college/courses_list.html", {'courses': courses})

@user_passes_test(is_college_admin, login_url='/')
def subjects_list(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if(request.user.college != course.college):  # check college admin related college
        raise PermissionDenied
    subjects_list = []
    semesters_list = Semester.objects.filter(course=pk)

    for semester in semesters_list:
        subjects = Subject.objects.filter(semester=semester)
        if subjects.exists():
            for subject in subjects:
                subjects_list.append(subject)
    context = {
        'subjects_list': subjects_list,
        'course': course
    }
    return render(request, "college/subjects_list.html", context)

@user_passes_test(is_college_admin, login_url='/')
def add_subject(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if(request.user.college != course.college):  # check college admin related college
        raise PermissionDenied
    semesters_list = Semester.objects.filter(course=pk)
    subject_type = SubjectType.objects.all()

    if request.method == "POST":
        subject_code = request.POST.get('subject_code')
        subject_name = request.POST.get('subject_name')
        sub_type = SubjectType.objects.get(
            id=request.POST.get('subject_types'))
        semester = Semester.objects.get(id=request.POST.get('semester'))
        subject = Subject(
            code=subject_code,
            name=subject_name,
            sub_type=sub_type,
            semester=semester
        )
        subject.save()
        messages.success(request, "Subject added successfully")
        return redirect('subjects-list', pk)

    context = {
        'subject_type': subject_type,
        'semesters_list': semesters_list
    }

    return render(request, "college/add_subject.html", context)

@user_passes_test(is_college_admin, login_url='/')
def add_course(request):
    if request.method == 'POST':
        course_name = request.POST.get('course_name')
        college = request.user.college
        semester = request.POST.get('NoOfSem')
        if int(semester) > 10 or int(semester) <= 0:
            messages.error(
                request, f"cannot enter insert {semester}. semester must be >0 and <=10")
            return redirect('college-add-course')
        course = Course(
            name=course_name,
            college=college
        )
        course.save()
        for i in range(1, int(semester)+1):
            semester = Semester(
                number=i,
                course=course
            )
            semester.save()
        messages.success(request, f"{course_name} has been added to {college}")
        return redirect('college-course-list')
    return render(request, "college/add_course.html")

@user_passes_test(is_college_admin, login_url='/')
def add_student(request):
    session_year_list = SessionYear.objects.all()
    if request.method == "POST":
        username = request.POST.get('user_name')
        firstname = request.POST.get('first_name')
        lastname = request.POST.get('last_name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        profile_pic = request.FILES.get('profile_pic')
        session_year = SessionYear.objects.get(
            id=request.POST.get('session_year'))
        if CustomUser.objects.filter(email=email).exists():
            messages.info(request, "email is already taken")
            return redirect('college-add-student')
        elif CustomUser.objects.filter(username=username).exists():
            messages.info(request, "username is already taken")
            return redirect('college-add-student')
        else:
            user = CustomUser(
                first_name=firstname,
                last_name=lastname,
                username=username,
                email=email,
                profile_pic=profile_pic,
                userType=3,
                college=request.user.college
            )
            user.set_password(f"{username}123")
            user.save()
            student = Student(
                user=user,
                address=address,
                gender=gender,
                session_year=session_year,
            )
            student.save()
            messages.success(request, "student added successfully")
            return redirect('college-students-list')
    context = {
        'session_year_list': session_year_list,
    }
    return render(request, "college/add_student.html", context)

@user_passes_test(is_college_admin, login_url='/')
def students_list(request):
    students_list = Student.objects.filter(user__college=request.user.college)
    context = {
        'students_list': students_list
    }
    return render(request, 'college/college_students_list.html', context)

@user_passes_test(is_college_admin, login_url='/')
def faculties_list(request):

    faculties_list = Faculty.objects.filter(user__college=request.user.college)
    context = {
        'faculties_list': faculties_list
    }
    return render(request, 'college/college_faculties_list.html', context)

@user_passes_test(is_college_admin, login_url='/')
def add_faculty(request):
    if request.method == "POST":
        username = request.POST.get('user_name')
        firstname = request.POST.get('first_name')
        lastname = request.POST.get('last_name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        profile_pic = request.FILES.get('profile_pic')
        if CustomUser.objects.filter(email=email).exists():
            messages.info(request, "email is already taken")
            return redirect('college-add-student')
        if CustomUser.objects.filter(username=username).exists():
            messages.info(request, "username is already taken")
            return redirect('college-add-student')
        else:
            user = CustomUser(
                first_name=firstname,
                last_name=lastname,
                username=username,
                email=email,
                profile_pic=profile_pic,
                userType=2,
                college=request.user.college
            )
            user.set_password(f"{username}123")
            user.save()
            faculty = Faculty(
                user=user,
                address=address,
                gender=gender,
            )
            faculty.save()
            messages.success(request, "faculty added successfully")
            return redirect('college-faculties-list')

    return render(request, 'college/add_faculty.html')

@user_passes_test(is_college_admin, login_url='/')
def user_profile(request):
    # check if fields are not empty
    if(request.method == "POST"):
        profile = request.FILES.get("profile_pic")
        if profile == None:
            profile = request.user.profile_pic
        username = request.POST.get("username")
        fname = request.POST.get("first_name")
        lname = request.POST.get("last_name")
        user = CustomUser.objects.get(id=request.user.id)
        user.username=username
        user.first_name =fname
        user.last_name = lname
        user.profile_pic=profile
        user.save()
        messages.success(request, "Profile Updated Successfully")
        return redirect('college-admin-profile')
    return render(request, 'college/user_profile.html')

@user_passes_test(is_college_admin, login_url='/')
def update_course(request,pk):
    course = get_object_or_404(Course, pk=pk)
    if(request.user.college != course.college):  # check college admin related college
        raise PermissionDenied
    else:
        semesters_list = Semester.objects.filter(course=course)
        context = {
            'course': course,
            'semesters_list': semesters_list 
            }
        if request.method == 'POST':
            course.name = request.POST.get('course_name')           
            course.save()
            messages.success(request, f"{course.name} is saved!")
            return redirect('college-course-list')
    return render(request, "college/update_course.html",context)

@user_passes_test(is_college_admin, login_url='/')
def update_subject(request,pk):
    subject = get_object_or_404(Subject,pk=pk)
    subject_types = SubjectType.objects.all()
    semesters = Semester.objects.filter(course=subject.semester.course)
    if (subject.semester.course.college != request.user.college):
        raise PermissionDenied
    if request.method == "POST":
        code = request.POST.get('subject_code')
        name = request.POST.get('subject_name')
        subtype = request.POST.get('subject_type')
        semester = request.POST.get('semester')
        subject.code = code
        subject.name = name
        subject.sub_type = SubjectType.objects.get(pk=subtype)
        subject.semester = Semester.objects.get(pk=semester)
        subject.save()
        messages.success(request,f"{subject.name} has been updated!")
        return redirect('college-update-subject',pk)

    context = {
        'subject':subject,
        'subject_types':subject_types,
        'semesters_list':semesters
    }
    return render(request,'college/update_subject.html',context)

@user_passes_test(is_college_admin, login_url='/')
def update_faculty(request,pk):
    faculty = get_object_or_404(Faculty,pk=pk)
    if (faculty.user.college != request.user.college):
        raise PermissionDenied
    if request.method == "POST":
        profile = request.FILES.get("profile_pic")
        if profile == None:
            profile = faculty.user.profile_pic
        faculty.user.username = request.POST.get('username')
        faculty.user.first_name = request.POST.get('first_name')
        faculty.user.last_name = request.POST.get('last_name')
        faculty.gender = request.POST.get('gender')
        faculty.address = request.POST.get('address')
        faculty.user.profile_pic = profile
        faculty.save()
        faculty.user.save()
        messages.success(request,'Faculty Profile Updated Successfully!')
        return redirect('college-update-faculty',faculty.id)
    context = {
        'faculty':faculty,
    }
    return render(request,'college/update_faculty.html',context)

@user_passes_test(is_college_admin, login_url='/')
def update_student(request,pk):
    student = get_object_or_404(Student,pk=pk)
    session_years = SessionYear.objects.all()
    if (student.user.college != request.user.college):
        raise PermissionDenied
    if request.method == "POST":
        profile = request.FILES.get("profile_pic")
        if profile == None:
            profile = student.user.profile_pic
        student.user.username = request.POST.get('username')
        student.user.first_name = request.POST.get('first_name')
        student.user.last_name = request.POST.get('last_name')
        student.address = request.POST.get('address')
        student.gender = request.POST.get('gender')
        student.user.profile_pic = profile
        student.session_year = SessionYear.objects.get(pk=request.POST.get('session_year'))
        student.save()
        student.user.save()
        messages.success(request,'Student Profile Updated Successfully!')
        return redirect('college-update-student',student.id)
    context = {
        'student':student,
        'session_year_list':session_years
    }
    return render(request,'college/update_student.html',context)
@user_passes_test(is_college_admin, login_url='/')
def delete_subject(request,pk):
    subject = get_object_or_404(Subject, pk=pk)
    if (subject.semester.course.college != request.user.college):
        raise PermissionDenied
    else:
        if(request.method == "POST"):
            subject.delete()
            messages.success(request, f"{subject.name} has been deleted!")
            return redirect('subjects-list' , subject.semester.course.id)
        context = {
            'obj':subject
        }
        return render(request,'college/delete_confirmation.html',context)

# @user_passes_test(is_college_admin, login_url='/')
# def delete_semester(request,pk):
#     semester = get_object_or_404(Semester, pk=pk)
#     if (semester.course.college != request.user.college):
#         raise PermissionDenied
#     else:
#         if(request.method == "POST"):
#             semester.delete()
#             messages.success(request, f"{semester.name} has been deleted!")
#             return redirect('college-course-list')
#         context = {
#             'obj':semester
#         }
#         return render(request,'college/delete_confirmation.html',context)
            
@user_passes_test(is_college_admin, login_url='/')
def delete_course(request,pk):
    course = get_object_or_404(Course, pk=pk)
    if (course.college != request.user.college):
        raise PermissionDenied
    else:
        if(request.method == "POST"):
            course.delete()
            messages.success(request, f"{course.name} has been deleted!")
            return redirect('college-course-list')
        context = {
            'obj':course
        }
        return render(request,'college/delete_confirmation.html',context)

@user_passes_test(is_college_admin, login_url='/')
def delete_faculty(request,pk):
    faculty = get_object_or_404(Faculty, pk=pk)
    if (faculty.user.college != request.user.college):
        raise PermissionDenied
    else:
        if(request.method == "POST"):
            faculty.user.delete()
            faculty.delete()
            messages.success(request, f"{faculty.user.first_name} has been deleted!")
            return redirect('college-faculties-list')
        context = {
            'obj':faculty
        }
        return render(request,'college/delete_confirmation.html',context)

@user_passes_test(is_college_admin, login_url='/')
def delete_student(request,pk):
    student = get_object_or_404(Student, pk=pk)
    if (student.user.college != request.user.college):
        raise PermissionDenied
    else:
        if(request.method == "POST"):
            student.user.delete()
            student.delete()
            messages.success(request, f"{student.user.first_name} has been deleted!")
            return redirect('college-students-list')
        context = {
            'obj':student
        }
        return render(request,'college/delete_confirmation.html',context)