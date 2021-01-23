# Generated by Django 3.1.4 on 2021-01-06 21:55

import django.contrib.gis.db.models.fields
import django.db.models.deletion
import files.upload
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("post", "0002_register_status_kinds"),
    ]

    operations = [
        migrations.CreateModel(
            name="TFile",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("file", models.FileField(upload_to=files.upload.upload_to)),
                ("uuid", models.UUIDField()),
                ("filename", models.CharField(max_length=128)),
                (
                    "point",
                    django.contrib.gis.db.models.fields.PointField(
                        blank=True, null=True, srid=4326
                    ),
                ),
            ],
            options={
                "verbose_name": "File",
                "db_table": "t_file",
            },
        ),
        migrations.CreateModel(
            name="TFilePost",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "t_file",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="files.tfile"
                    ),
                ),
                (
                    "t_post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="post.tpost"
                    ),
                ),
            ],
            options={
                "verbose_name": "File-Post",
                "db_table": "t_file_post",
            },
        ),
        migrations.AddField(
            model_name="tfile",
            name="posts",
            field=models.ManyToManyField(through="files.TFilePost", to="post.TPost"),
        ),
    ]