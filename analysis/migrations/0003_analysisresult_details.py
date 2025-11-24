from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("analysis", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="analysisresult",
            name="details",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
