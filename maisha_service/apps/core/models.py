from datetime import datetime
import uuid

from django.db import models


# Create your models here.
class MaishaCore(models.Model):
    session_id = models.CharField(
        unique=True,
        max_length=350,
        default=uuid.uuid4,
        null=False,
        editable=False
    )
    doctor_id = models.CharField(max_length=350, default='')  # Accepting doctor
    patient_id = models.CharField(max_length=350, default='')
    description = models.TextField(default='')
    speciality = models.TextField(default='GENERAL')
    proximity = models.IntegerField(default=0)  # 0=AUTO, 1=CLOSE COORDINATES
    remarks = models.TextField(default='')
    type = models.CharField(max_length=50, default='')  # VIDEO CHAT
    # REQUESTED, ACCEPTED, STARTED, COMPLETED, CANCELLED, IGNORED
    status = models.CharField(max_length=350, default='REQUESTED')
    # PENDING, ONGOING, COMPLETED
    patient_session_status = models.CharField(max_length=350, default='PENDING')
    doctor_session_status = models.CharField(max_length=350, default='PENDING')

    # Patient stuff
    patient_rating = models.FloatField(default=0.0)
    is_completed = models.BooleanField(default=False)
    is_scheduled = models.IntegerField(default=0)

    # Doctor stuff
    doctor_rating = models.FloatField(default=0.0)
    doctor_completed = models.BooleanField(default=False)
    doctor_remarks = models.TextField(default='')

    session_patient_rating = models.FloatField(default=0.0)
    session_doctor_rating = models.FloatField(default=0.0)

    # Accounting
    session_value = models.FloatField(default=0.0) # Amount to be paid
    session_settled = models.BooleanField(default=False)

    createdAt = models.DateTimeField(auto_now_add=True, null=True)
    updatedAt = models.DateTimeField(auto_now=True, null=True)  # will show completed date

    def __str__(self):
        """ String representation of db object """
        return 'session_id : {} ,description: {}, doctor_id: {}'.format(
            self.session_id, self.description, self.doctor_id)


class SessionBounce(models.Model):
    session_id = models.CharField(max_length=350, default='')
    doctor_id = models.CharField(max_length=350, default='')  # Accepting doctor
    patient_id = models.CharField(max_length=350, default='')
    doc_response = models.CharField(max_length=350, default='')  # ACCEPTED, IGNORED
    request_count = models.IntegerField(default=0)

    createdAt = models.DateTimeField(auto_now_add=True, null=True)
    updatedAt = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        """ String representation of db object """
        return 'session_id : {} ,request_count: {}'.format(
            self.session_id, self.request_count)


class MaishaChats(models.Model):
    session_id = models.CharField(max_length=350, default='')
    image = models.TextField(default='')
    message = models.TextField(default='')
    message_id = models.CharField(unique=True, max_length=350, default='')
    reply_body = models.TextField(default='')
    user_id = models.CharField(max_length=550, default='')
    username = models.CharField(max_length=550, default='')
    created_at = models.CharField(max_length=100, default='')

    createdAt = models.DateTimeField(auto_now_add=True, null=True)
    updatedAt = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        """ String representation of db object """
        return 'session_id : {} ,message: {}'.format(
            self.session_id, self.message)


class CoreComplaints(models.Model):
    complaint_id = models.CharField(unique=True, max_length=350, default='')
    session_id = models.CharField(max_length=350, default='')
    complaint = models.TextField(default='')
    complaint_response = models.TextField(default='')
    category = models.TextField(default='')
    user_id = models.CharField(max_length=550, default='')

    createdAt = models.DateTimeField(auto_now_add=True, null=True)
    updatedAt = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        """ String representation of db object """
        return 'complaint_id : {} ,complaint: {}'.format(
            self.complaint_id, self.complaint)


class DoctorPatientCreditTransfer(models.Model):
    doctor_id = models.CharField(max_length=350, default='non', unique=False)
    patient_id = models.CharField(max_length=350, default='non', unique=False)
    session_id = models.CharField(max_length=350, default='non', unique=False)
    amount_transferred = models.FloatField(default=0.0)
    transaction_status = models.CharField(max_length=350, default='non')
    """ COMPLETE, INCOMPLETE"""

    createdAt = models.DateTimeField(auto_now_add=True, null=True)
    updatedAt = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        """ String representation of db object """
        return 'session_id : {} ,amount_transferred: {}'.format(
            self.session_id, self.amount_transferred)


class ScheduledSessionsModel(models.Model):
    session_id = models.CharField(max_length=350, default='non', unique=True)
    session_date_time = models.DateTimeField(default=datetime.now)
    doctor_accepted_rejected = models.CharField(max_length=350, default='non')

    createdAt = models.DateTimeField(auto_now_add=True, null=True)
    updatedAt = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        """ String representation of db object """
        return 'session_id : {} ,doctor_accepted_rejected: {}'.format(
            self.session_id, self.doctor_accepted_rejected)
