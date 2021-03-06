# Generated by Django 3.0.10 on 2020-10-07 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('private_ip', models.GenericIPAddressField(unique=True)),
                ('public_ip', models.GenericIPAddressField(unique=True)),
                ('status', models.CharField(choices=[('UP', 'Server is up'), ('DN', 'Server is down'), ('PD', 'Server is doing some task')], default='UP', max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_path', models.CharField(max_length=1000, unique=True)),
                ('hash', models.CharField(max_length=32)),
                ('size', models.CharField(max_length=32)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('storage', models.ManyToManyField(related_name='files', to='name_server.Storage')),
            ],
        ),
    ]
