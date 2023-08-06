"""
This migrations moves the reduction script contents from ReductionRun.script into
`ReductionScript.text`. This is done to allow the script to be re-used across runs
if it is not changed.
"""

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


def move_script_into_reduction_script(apps, _):
    ReductionRun = apps.get_model("reduction_viewer", "ReductionRun")
    ReductionScript = apps.get_model("reduction_viewer", "ReductionScript")

    for run in ReductionRun.objects.all():
        try:
            rscript = ReductionScript.objects.get(text=run.tmp_script)
        except:  # pylint:disable=bare-except
            rscript = ReductionScript.objects.create(text=run.tmp_script)
        rscript.save()
        run.script_id = rscript.pk
        run.save()


class Migration(migrations.Migration):

    dependencies = [
        ('reduction_viewer', '0009_reductionrun_run_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReductionScript',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(blank=True, validators=[django.core.validators.MaxLengthValidator(100000)])),
            ],
        ),
        migrations.RenameField(model_name='reductionrun', old_name='script', new_name='tmp_script'),
        migrations.AddField(
            model_name='reductionrun',
            name='script',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='reduction_runs',
                to='reduction_viewer.reductionscript',
                # make it null=True first, otherwise there is an IntegrityError,
                # the field will be altered to null=False after the scripts are migrated
                null=True),
        ),
        migrations.RunPython(move_script_into_reduction_script),
        migrations.AlterField(model_name='reductionrun',
                              name='script',
                              field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                                      related_name='reduction_runs',
                                                      to='reduction_viewer.reductionscript',
                                                      null=False)),
        migrations.RemoveField(model_name='reductionrun', name='tmp_script'),
    ]
