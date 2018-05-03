# Generated by Django 2.0.1 on 2018-01-23 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('author', models.TextField(default='', max_length=20)),
                ('tag', models.TextField(default='', max_length=10)),
                ('likes', models.DecimalField(decimal_places=10, default=0, max_digits=10)),
                ('image_url', models.TextField(default='', max_length=100)),
            ],
        ),
    ]
