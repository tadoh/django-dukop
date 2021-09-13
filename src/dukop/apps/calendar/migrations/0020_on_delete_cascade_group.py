# Generated by Django 3.2 on 2021-09-13 18:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_group_deactivated'),
        ('calendar', '0019_rename_interval_recurrence'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='eventlink',
            options={'ordering': ('priority', 'link')},
        ),
        migrations.AlterField(
            model_name='event',
            name='host',
            field=models.ForeignKey(blank=True, help_text='A group may host an event and be displayed as the author of the event text.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='events', to='users.group'),
        ),
        migrations.AlterField(
            model_name='eventrecurrence',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recurrences', to='calendar.event'),
        ),
        migrations.AlterField(
            model_name='eventtime',
            name='recurrence',
            field=models.ForeignKey(blank=True, help_text='Belonging to a recurring recurrence', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='times', to='calendar.eventrecurrence', verbose_name='recurrence'),
        ),
        migrations.AlterField(
            model_name='eventtime',
            name='recurrence_auto',
            field=models.BooleanField(default=False, help_text='If true, this recurrence is currently maintained automatically and has not been rescheduled. If the recurrence is edited, it may be changed automatically', verbose_name='automatic recurrence'),
        ),
    ]