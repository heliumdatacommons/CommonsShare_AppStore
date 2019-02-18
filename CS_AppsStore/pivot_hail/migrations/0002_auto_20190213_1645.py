from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pivot_hail', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HailStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appliance_id', models.CharField(max_length=160)),
                ('status', models.CharField(choices=[('R', 'running'), ('D', 'deleted')], default='R', max_length=2)),
                ('insts', models.PositiveIntegerField()),
                ('memory', models.PositiveIntegerField()),
                ('cpus', models.PositiveIntegerField()),
                ('start_timestamp', models.DateTimeField(blank=True, null=True)),
                ('end_timestamp', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='hail_status', related_query_name='hail_status', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='hailstatus',
            unique_together=set([('user', 'appliance_id', 'status', 'start_timestamp', 'end_timestamp')]),
        ),
    ]
