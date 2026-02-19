# Generated manually - popula categoria, cidade, bairro nos leads existentes

from django.db import migrations


def populate_leads(apps, schema_editor):
    Lead = apps.get_model('crm', 'Lead')
    Lead.objects.filter(id__gte=1, id__lte=8).update(
        categoria='Clínica Médica',
        cidade='Florianópolis',
        bairro='Jurerê'
    )
    Lead.objects.filter(id__gte=9, id__lte=68).update(
        categoria='Imobiliária',
        cidade='Florianópolis',
        bairro='Jurerê'
    )


def reverse_populate(apps, schema_editor):
    Lead = apps.get_model('crm', 'Lead')
    Lead.objects.filter(id__gte=1, id__lte=68).update(
        categoria='',
        cidade='',
        bairro=''
    )


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0002_add_categoria_cidade_bairro_lead'),
    ]

    operations = [
        migrations.RunPython(populate_leads, reverse_populate),
    ]
