from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("libraries", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="library",
            name="description",
            field=models.TextField(blank=True),
        ),
    ]
