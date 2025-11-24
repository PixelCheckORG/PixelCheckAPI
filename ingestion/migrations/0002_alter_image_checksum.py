from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ingestion", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="image",
            name="checksum",
            field=models.CharField(db_index=True, max_length=64),
        ),
    ]
