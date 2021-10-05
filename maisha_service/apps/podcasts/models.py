from django.db import models


class Podcasts(models.Model):
    """ Run Challenge """
    podcast_id = models.CharField(max_length=250, default='non')
    user_id = models.CharField(max_length=250, default='non')
    uploaded_by = models.CharField(max_length=250, default='non')
    details = models.CharField(max_length=2050, default='non')
    title = models.CharField(max_length=1050, default='non')
    interest = models.CharField(max_length=250, default='non')
    audio_image = models.CharField(max_length=1050, default='non')
    audio_file = models.CharField(max_length=1050, default='non')
    tags = models.CharField(max_length=250, default='non')

    createdAt = models.DateTimeField(auto_now_add=True, null=True)
    updatedAt = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        """ String representation of db object """
        return 'podcast_id : {} ,user_id: {}'.format(
            self.podcast_id, self.user_id)
