# Generated by Django 3.1.4 on 2020-12-29 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0011_merge_20201222_1644'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='kind',
            field=models.CharField(choices=[('Jewellery', 'Jewellery'), ('Cloth', 'Cloth')], max_length=50),
        ),
    ]
