from core.models import TimestampModel
from django.contrib.gis.db import models as geo_models
from django.db import models
from django.urls import reverse

from .upload import format_upload_to, upload_to


class TFile(TimestampModel):
    file = models.FileField(upload_to=upload_to)
    uuid = models.UUIDField()
    filename = models.CharField(max_length=128)
    mime_type = models.CharField(max_length=32)
    exif = models.JSONField(default=dict)
    point = geo_models.PointField(blank=True, null=True)

    posts = models.ManyToManyField(
        "post.TPost", through="TFilePost", through_fields=("t_file", "t_post")
    )

    class Meta:
        db_table = "t_file"
        verbose_name = "File"

    def get_absolute_url(self):
        return reverse("get_media", args=[self.uuid])

    def __str__(self):
        return self.filename


class TFilePost(TimestampModel):

    t_file = models.ForeignKey(TFile, on_delete=models.CASCADE)
    t_post = models.ForeignKey("post.TPost", on_delete=models.CASCADE)

    class Meta:
        db_table = "t_file_post"
        verbose_name = "File-Post"


class TFormattedImage(TimestampModel):
    file = models.FileField(upload_to=format_upload_to)
    t_file = models.ForeignKey(
        TFile, on_delete=models.CASCADE, related_name="ref_t_formatted_image"
    )
    filename = models.CharField(max_length=128)
    mime_type = models.CharField(max_length=32)

    width = models.IntegerField()
    height = models.IntegerField()

    class Meta:
        db_table = "t_formatted_image"
        verbose_name = "Formatted Image"
        unique_together = ("t_file", "mime_type")

    def __str__(self):
        return self.filename
