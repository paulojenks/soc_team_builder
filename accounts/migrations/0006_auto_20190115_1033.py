# Generated by Django 2.0.6 on 2019-01-15 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20181230_1714'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(default='avatars/avatar-159236_1280.png', upload_to='soc_team_builder/media/avatars'),
        ),
    ]