# Generated by Django 4.1.7 on 2023-03-27 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("backend_order", "0002_alter_category_options_alter_order_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="type",
            field=models.CharField(
                choices=[
                    ("shop", "Магазин"),
                    ("customer", "Покупатель"),
                    ("admin", "Админ"),
                ],
                default="customer",
                max_length=20,
                verbose_name="Тип пользователя",
            ),
        ),
    ]
