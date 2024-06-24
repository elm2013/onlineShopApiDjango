# Generated by Django 5.0.6 on 2024-06-12 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_alter_otp_send_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='role',
            field=models.CharField(choices=[('admin', 'Admin'), ('operator', 'Operator'), ('customer', 'Customer')], default='customer', max_length=10),
        ),
        migrations.AlterField(
            model_name='account',
            name='status',
            field=models.CharField(choices=[('0', 'Pending'), ('1', 'Complete')], default='0', max_length=1),
        ),
    ]
