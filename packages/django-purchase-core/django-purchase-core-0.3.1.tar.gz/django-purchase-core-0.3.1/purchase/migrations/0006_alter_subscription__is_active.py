# Generated by Django 3.2.7 on 2022-07-28 05:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0005_alter_subscription_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='_is_active',
            field=models.DateField(null=True),
        ),
    ]
