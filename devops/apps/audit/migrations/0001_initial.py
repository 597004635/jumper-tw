# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-12-11 14:39
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('command', models.TextField()),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Host',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hostname', models.CharField(max_length=64, unique=True)),
                ('ip_addr', models.GenericIPAddressField(unique=True)),
                ('port', models.IntegerField(default=22)),
                ('enabled', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='HostGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='HostUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auth_type', models.SmallIntegerField(choices=[(0, 'ssh-password'), (1, 'ssh-key')])),
                ('username', models.CharField(max_length=32)),
                ('password', models.CharField(blank=True, default='', max_length=128, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='HostUserBind',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('host', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='audit.Host')),
                ('host_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='audit.HostUser')),
            ],
        ),
        migrations.CreateModel(
            name='SessionLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField(auto_now_add=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='audit.Account')),
                ('host_user_bind', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='audit.HostUserBind')),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_type', models.SmallIntegerField(choices=[(0, 'command'), (1, 'file_transfer')])),
                ('content', models.TextField(verbose_name='任务内容')),
                ('timeout', models.IntegerField(default=30, verbose_name='任务超时')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='audit.Account')),
            ],
        ),
        migrations.CreateModel(
            name='TaskLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result', models.TextField(default='Initialization ...')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('status', models.SmallIntegerField(choices=[(0, '成功'), (1, '失败'), (2, '超时'), (3, '初始化')])),
                ('host_user_bind', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='audit.HostUserBind')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='audit.Task')),
            ],
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('val', models.CharField(max_length=128, unique=True)),
                ('expire', models.IntegerField(default=10800, verbose_name='超时时间(s)')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='audit.Account')),
                ('host_user_bind', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='audit.HostUserBind')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='hostuser',
            unique_together=set([('username', 'password')]),
        ),
        migrations.AddField(
            model_name='hostgroup',
            name='host_user_binds',
            field=models.ManyToManyField(to='audit.HostUserBind'),
        ),
        migrations.AddField(
            model_name='auditlog',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='audit.SessionLog'),
        ),
        migrations.AddField(
            model_name='account',
            name='host_groups',
            field=models.ManyToManyField(blank=True, to='audit.HostGroup'),
        ),
        migrations.AddField(
            model_name='account',
            name='host_user_binds',
            field=models.ManyToManyField(blank=True, to='audit.HostUserBind'),
        ),
        migrations.AddField(
            model_name='account',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='tasklog',
            unique_together=set([('task', 'host_user_bind')]),
        ),
        migrations.AlterUniqueTogether(
            name='hostuserbind',
            unique_together=set([('host', 'host_user')]),
        ),
    ]