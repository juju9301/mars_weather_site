from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("weather", "0006_remove_post_author_delete_comment_delete_post"),
    ]

    operations = [
        migrations.AlterField(
            model_name="weather",
            name="orig_id",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
