# Generated by Django 2.1.4 on 2018-12-31 00:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20181229_1615'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='application',
            unique_together={('user', 'position')},
        ),
    ]
