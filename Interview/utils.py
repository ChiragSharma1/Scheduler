from datetime import datetime

import pytz
from django.conf import settings
from django.core.mail import send_mail

from .models import Interview, Participant

utc = pytz.UTC

def validate_start_end_time(start_time,end_time):
    # function that checks and returns error if start time and end time are not valid
    error = None
    if start_time >= end_time:
        error = f"Start time should not be greater than or equal to End time"

    if start_time < datetime.now(tz=utc):
        error = f"Start time should not be less than current time"
    return error


def get_valid_participant(start_time,end_time):
    # function that checks and returns error if start time and end time are not valid
    participants_list = Participant.objects.all()
    valid_participants = []
    for participant in participants_list:
        flag = True
        interview_list = participant.interviews.all()
        for interview in interview_list:
            if interview.start_time <= start_time <= interview.end_time:
                flag = False
                break
            if interview.start_time <= end_time <= interview.end_time:
                flag = False
                break
            if (
                interview.start_time >= start_time
                and interview.end_time <= end_time
            ):
                flag = False
                break
        if flag:
            valid_participants.append(participant)
    return valid_participants




def send_mail_to_participants(participants_list, interview_id):
    # function that sends mail to participants
    interview = Interview.objects.get(id = interview_id)
    print(interview)
    start_time = interview.start_time
    end_time = interview.end_time
    interview_name = interview.name
    send_mail(
        f'Meet Scheduled',
        f'Your meeting - {interview_name} is begin scheduled during - {start_time} : {end_time}',
        settings.EMAIL_HOST_USER,
        participants_list
    )
    
