from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('piling', '0001_initial'),
    ]

    operations = [
        # PilingProject — new defaults
        migrations.AddField(
            model_name='pilingproject',
            name='default_lap_length_m',
            field=models.FloatField(default=1.6, help_text='Lap length above cutoff level (m). Default 1.6m.'),
        ),
        migrations.AddField(
            model_name='pilingproject',
            name='default_concrete_cover_mm',
            field=models.FloatField(default=75.0, help_text='Concrete cover to reinforcement (mm). Typical 75mm for piles.'),
        ),

        # Pile — main bars
        migrations.AddField(
            model_name='pile',
            name='main_bar_count',
            field=models.PositiveSmallIntegerField(blank=True, null=True, help_text='Number of main longitudinal bars (e.g. 12)'),
        ),
        migrations.AddField(
            model_name='pile',
            name='main_bar_dia_mm',
            field=models.FloatField(blank=True, null=True, help_text='Main bar diameter in mm (e.g. 32)'),
        ),

        # Pile — stiffener rings
        migrations.AddField(
            model_name='pile',
            name='stiffener_dia_mm',
            field=models.FloatField(blank=True, null=True, help_text='Stiffener ring bar diameter in mm (e.g. 16)'),
        ),
        migrations.AddField(
            model_name='pile',
            name='stiffener_spacing_m',
            field=models.FloatField(blank=True, null=True, help_text='Stiffener ring centre-to-centre spacing (m)'),
        ),

        # Pile — spiral
        migrations.AddField(
            model_name='pile',
            name='spiral_dia_mm',
            field=models.FloatField(blank=True, null=True, help_text='Spiral bar diameter in mm (e.g. 10)'),
        ),
        migrations.AddField(
            model_name='pile',
            name='spiral_pitch_m',
            field=models.FloatField(blank=True, null=True, help_text='Spiral ring centre-to-centre pitch (m)'),
        ),

        # Pile — overrides
        migrations.AddField(
            model_name='pile',
            name='lap_length_m',
            field=models.FloatField(blank=True, null=True, help_text='Lap length above cutoff level (m). Leave blank to use project default (1.6m).'),
        ),
        migrations.AddField(
            model_name='pile',
            name='concrete_cover_mm',
            field=models.FloatField(blank=True, null=True, help_text='Concrete cover to reinforcement (mm). Leave blank for project default.'),
        ),

        # Pile — projection above ground
        migrations.AddField(
            model_name='pile',
            name='projection_above_ground_m',
            field=models.FloatField(blank=True, null=True, default=0.0, help_text='Length cast above ground / cutoff level (m). Default 0.'),
        ),

        # Pile — remove old free-text rebar fields (replaced by structured fields)
        migrations.RemoveField(
            model_name='pile',
            name='main_bars_spec',
        ),
        migrations.RemoveField(
            model_name='pile',
            name='stiffener_spec',
        ),
        migrations.RemoveField(
            model_name='pile',
            name='spiral_bars_spec',
        ),
    ]
