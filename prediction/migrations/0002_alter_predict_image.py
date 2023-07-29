# Generated by Django 4.2.2 on 2023-07-27 07:19

from django.db import migrations, models
import prediction.models


class Migration(migrations.Migration):

    dependencies = [
        ('prediction', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='predict',
            name='image',
            field=models.ImageField(upload_to='images/', validators=[prediction.models.validate_image_size]),
        ),
    ]
