# Generated by Django 3.2 on 2021-07-31 22:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20210424_1531'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='token_expiry',
            field=models.DateTimeField(editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='token_passphrase',
            field=models.CharField(blank=True, help_text='One time passphrase', max_length=128, null=True),
        ),
    ]
