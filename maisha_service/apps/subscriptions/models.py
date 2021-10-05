from django.db import models


# Create your models here.
class Subscription(models.Model):
    doctor_id = models.CharField(max_length=350, default='non')
    patient_id = models.CharField(max_length=350, default='non')
    subscribed_blogs = models.BooleanField(default=False)
    subscribed_pods = models.BooleanField(default=False)

    createdAt = models.DateTimeField(auto_now_add=True, null=True)
    updatedAt = models.DateTimeField(auto_now=True, null=True)  # will show completed date

    def __str__(self):
        """ String representation of db object """
        return 'doctor_id : {} ,patient_id: {}'.format(
            self.doctor_id, self.patient_id)
