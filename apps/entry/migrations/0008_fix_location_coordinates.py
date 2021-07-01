# Generated by Django 3.2.2 on 2021-07-01 20:35

from django.db import migrations


def fix_location_point(apps, schema_editor):
    TLocation = apps.get_model("entry", "TLocation")

    for t_location in TLocation.objects.all():
        t_location.point.x, t_location.point.y = t_location.point.y, t_location.point.x
        t_location.save()


class Migration(migrations.Migration):

    dependencies = [
        ('entry', '0007_update_verbose_names'),
    ]

    operations = [
        migrations.RunPython(fix_location_point, reverse_code=fix_location_point)
    ]
