# Generated by Django 5.1.2 on 2024-11-07 06:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_drafttransaction_created_by_transaction_created_by'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='drafttransaction',
            name='due_amount',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='drafttransaction',
            name='payment_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('partial', 'Partial'), ('completed', 'Completed')], default='pending', max_length=10),
        ),
        migrations.AlterField(
            model_name='drafttransaction',
            name='type',
            field=models.CharField(choices=[('sale', 'Sale'), ('purchase', 'Purchase')], max_length=10),
        ),
        migrations.AlterField(
            model_name='drafttransaction',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_transactions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='due_amount',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='payment_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('partial', 'Partial'), ('completed', 'Completed')], default='pending', max_length=10),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='type',
            field=models.CharField(choices=[('sale', 'Sale'), ('purchase', 'Purchase')], max_length=10),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_transactions', to=settings.AUTH_USER_MODEL),
        ),
    ]
