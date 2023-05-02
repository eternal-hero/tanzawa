# Generated by Django 3.1.4 on 2021-02-07 21:48

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("indieweb", "0002_twebmentionsend"),
    ]

    operations = [
        migrations.CreateModel(
            name="MMicropubScope",
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
                ("key", models.CharField(max_length=12, unique=True)),
                ("name", models.CharField(max_length=16)),
            ],
            options={
                "db_table": "m_micropub_scope",
            },
        ),
        migrations.CreateModel(
            name="TToken",
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
                ("auth_token", models.CharField(blank=True, max_length=40)),
                ("key", models.CharField(blank=True, max_length=40)),
                ("client_id", models.URLField()),
            ],
            options={
                "db_table": "t_token",
            },
        ),
        migrations.CreateModel(
            name="TTokenMicropubScope",
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
                    "m_micropub_scope",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="indieweb.mmicropubscope",
                    ),
                ),
                (
                    "t_token",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="indieweb.ttoken",
                    ),
                ),
            ],
            options={
                "db_table": "t_token_micropub_scope",
                "unique_together": {("t_token", "m_micropub_scope")},
            },
        ),
        migrations.AddField(
            model_name="ttoken",
            name="micropub_scope",
            field=models.ManyToManyField(through="indieweb.TTokenMicropubScope", to="indieweb.MMicropubScope"),
        ),
        migrations.AddField(
            model_name="ttoken",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ref_t_token",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
