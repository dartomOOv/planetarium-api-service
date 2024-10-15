# Generated by Django 5.1.2 on 2024-10-14 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "planetarium",
            "0002_alter_astronomyshow_title_alter_planetariumdome_rows_and_more",
        ),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="ticket",
            constraint=models.UniqueConstraint(
                fields=("row", "seat", "show_session"), name="unique_row_seat_show"
            ),
        ),
    ]