from datetime import datetime

import pytz
from django.http import HttpResponse
from django.shortcuts import redirect, render

from Interview.models import Interview, Participant

from .utils import *

# create your views here.

utc = pytz.UTC


def index(request):
    return render(request, "Interview/home.html")


def create_interview(request):
    # create interview for participants and send mail to them
    # divided into 2 phases - phase1 (Selecting name, date and time) and phase2 (Selecting participants)

    if request.method == "POST":

        if request.POST.get("add_participant") == "submit":
            # adding participant to interview
            name = request.POST["name"]
            format = "%Y-%m-%dT%H:%M"  # The format for timestamp
            # formating start time and end time
            start_time = utc.localize(datetime.strptime(
                request.POST["start_time"], format))
            end_time = utc.localize(datetime.strptime(
                request.POST["end_time"], format))

            # validating if start_time is less than end_time
            error = validate_start_end_time(start_time, end_time)

            if error is not None:
                return render(
                    request,
                    "Interview/create_interview.html",
                    {
                        "name": name,
                        "start_time": start_time.strftime(format),
                        "end_time": end_time.strftime(format),
                        "error": error,
                        "phase": "phase1",
                    },
                )

            valid_participants = get_valid_participant(start_time, end_time)
            # sorting the valid participants on the basis of their name in ascending order
            valid_participants.sort(key=lambda participant: participant.name)

            return render(
                request,
                "Interview/create_interview.html",
                {
                    "name": name,
                    "start_time": start_time.strftime(format),
                    "end_time": end_time.strftime(format),
                    "valid_participants": valid_participants,
                    "valid_participants_size": len(valid_participants),
                    "phase": "phase2",
                },
            )
        elif request.POST.get("participant_submit") == "submit":
            # select Date and Time for the Interview
            name = request.POST["name"]
            print("after phase2 ", name)
            start_time = request.POST["start_time"]
            end_time = request.POST["end_time"]

            participants_list = request.POST.getlist("participants")

            interview = Interview(
                name=name, start_time=start_time, end_time=end_time)
            interview.save()
            participants_email_list = []
            for participant_id in participants_list:
                participant = Participant.objects.get(id=participant_id)
                participants_email_list.append(participant.email)
                interview.participants.add(participant)

            interview.save()
            send_mail_to_participants(participants_email_list, interview.id)
            return redirect("Interview:interview_details", interview_id=interview.id)

    else:
        return render(request, "Interview/create_interview.html", {"phase": "phase1"})


def interview_details(request, interview_id):
    # get the interview details for the given interview_id
    # check if id is valid interview_id or not
    print(interview_id, type(interview_id))
    if Interview.objects.filter(id=interview_id).exists() == False:
        return render(
            request, "404.html", {
                "error": "Interview of this id does not exists"}
        )
    else:
        interview = Interview.objects.get(id=interview_id)
        participant_list = interview.participants.all()
        return render(
            request,
            "Interview/detail_page.html",
            {
                "interview": interview,
                "participant_list": participant_list
            },
        )


def interview_list(request):
    # list of all interviews
    # today's date
    date_today = datetime.now(tz=utc).date()

    # get the list of all the interviews
    interview_list = Interview.objects.all()

    # filtering the interviews which are scheduled today and then upcomming ones
    todays_interview_list = []
    upcoming_interview_list = []

    for interview in interview_list:
        interview_start_date = interview.start_time.date()
        if interview_start_date == date_today:
            todays_interview_list.append(interview)
        elif interview_start_date > date_today:
            upcoming_interview_list.append(interview)

    # sorting the interviews on the basis of their start_time in ascending order
    todays_interview_list.sort(key=lambda interview: interview.start_time)
    upcoming_interview_list.sort(key=lambda interview: interview.start_time)

    return render(
        request,
        "Interview/interview_list.html",
        {
            "todays_interviews": todays_interview_list,
            "upcoming_interviews": upcoming_interview_list,
        },
    )


def edit_interview(request, interview_id):
    # edit interview for given interivew_id
    # divided into 2 phases - phase1 (for editing name, date and time) and phase2 (for editing participants)

    # check if id is valid interview_id or not
    if Interview.objects.filter(id=interview_id).exists() == False:
        return render(
            request, "404.html", {
                "error": "Interview of this id does not exists"}
        )

    if request.POST.get("add_participant") == "submit":
        # first part of interview edit for name, start_time and end_time

        name = request.POST["name"]
        interview = Interview.objects.get(id=interview_id)
        format = "%Y-%m-%dT%H:%M"
        start_time = utc.localize(datetime.strptime(
            request.POST["start_time"], format))
        end_time = utc.localize(datetime.strptime(
            request.POST["end_time"], format))

        error = validate_start_end_time(start_time, end_time)
        if error is not None:
            return render(
                request,
                "Interview/create_interview.html",
                {
                    "name": name,
                    "interview_id": interview_id,
                    "start_time": start_time.strftime(format),
                    "end_time": end_time.strftime(format),
                    "error": error,
                    "phase": "phase1",
                    "is_edit_page": True
                },
            )

        # interview_participants is the list of participants which are already added to the interview
        interview_participants = interview.participants.all()
        valid_participants = get_valid_participant(start_time, end_time)
        return render(
            request,
            "Interview/create_interview.html",
            {
                "name": name,
                "start_time": start_time.strftime(format),
                "interview_id": interview_id,
                "end_time": end_time.strftime(format),
                "checked_participants": interview_participants,
                "valid_participants": valid_participants,
                "phase": "phase2",
                "is_edit_page": True
            },
        )
    elif request.POST.get("participant_submit") == "submit":
        # final submit of the form

        # select Date and Time for the Interview
        name = request.POST["name"]
        start_time = request.POST["start_time"]
        end_time = request.POST["end_time"]

        participants_list = request.POST.getlist("participants")

        interview = Interview.objects.get(id=interview_id)
        interview.name = name
        interview.start_time = start_time
        interview.end_time = end_time
        participants_email_list = []
        interview.save()
        for participant_id in participants_list:
            participant = Participant.objects.get(id=participant_id)
            participants_email_list.append(participant.email)
            interview.participants.add(participant)
        interview.save()

        send_mail_to_participants(participants_email_list, interview_id)

        return redirect("Interview:interview_details", interview_id=interview.id)
    else:
        # when comes on the page for the first time

        interview = Interview.objects.get(id=interview_id)
        start_time = interview.start_time
        end_time = interview.end_time

        format = "%Y-%m-%dT%H:%M"
        return render(
            request,
            "Interview/create_interview.html",
            {
                "interview_id": interview.id,
                "name": interview.name,
                "start_time": start_time.strftime(format),
                "end_time": end_time.strftime(format),
                "phase": "phase1",
                "is_edit_page": True
            },
        )
