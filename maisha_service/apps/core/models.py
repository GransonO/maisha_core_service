from django.db import models


# Create your models here.
class MaishaCore(models.Model):
    session_id = models.CharField(unique=True, max_length=350, default='')
    doctor_id = models.CharField(max_length=350, default='')  # Accepting doctor
    patient_id = models.CharField(max_length=350, default='')
    description = models.TextField(default='')
    speciality = models.TextField(default='GENERAL')
    proximity = models.IntegerField(default=0)  # 0=AUTO, 1=CLOSE COORDINATES
    remarks = models.TextField(default='')
    type = models.CharField(max_length=50, default='')  # VIDEO CHAT
    # REQUESTED, ACCEPTED, STARTED, COMPLETED, CANCELLED, IGNORED
    status = models.CharField(max_length=350, default='REQUESTED')

    # Patient stuff
    patient_rating = models.FloatField(default=0.0)
    is_completed = models.BooleanField(default=False)

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
