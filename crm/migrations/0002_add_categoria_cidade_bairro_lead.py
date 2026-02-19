# Generated manually - novos campos Lead (categoria, cidade, bairro)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0001_add_coleta_lead'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='categoria',
            field=models.CharField(blank=True, max_length=200, verbose_name='Categoria'),
        ),
        migrations.AddField(
            model_name='lead',
            name='cidade',
            field=models.CharField(blank=True, max_length=150, verbose_name='Cidade'),
        ),
        migrations.AddField(
            model_name='lead',
            name='bairro',
            field=models.CharField(blank=True, max_length=150, verbose_name='Bairro'),
        ),
    ]
