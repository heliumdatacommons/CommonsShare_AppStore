from json import load

from django.core.management.base import BaseCommand

from pivot_i2b2_transmart_copdgene.models import TransmartCOPDGeneConfig


class Command(BaseCommand):
    """
    This script synchronize PIVOT i2b2 Transmart COPDGene JSON configuration file under
    pivot_i2b2_transmart_copdgene/data/pivot_copdgene.json
    to database TransmartCOPDGeneConfig table on an as-needed basis, e.g., when JSON file is
    manually updated.
    To run this command, do:
    python manage.py sync_i2b2_transmart_copdgene_config_to_db pivot_i2b2_transmart_copdgene/data/pivot_copdgene.json
    """
    help = "synchronize PIVOT i2b2 Transmart COPDGene JSON configuration file to database"

    def add_arguments(self, parser):
        # pivot configuration file with full relative path
        parser.add_argument('config_file', help='PIVOT i2b2 Transmart COPDGene JSON configuration '
                                                'file with full relative path')


    def handle(self, *args, **options):
        if options['config_file'].endswith('.json'):
            config_file = options['config_file']
            with open(config_file, 'r') as fp:
                p_data = load(fp)
                if not 'id' in p_data or not 'containers' in p_data:
                    print("PIVOT JSON Configuration file is not valid")
                else:
                    conf_qs = TransmartCOPDGeneConfig.objects.all()
                    if not conf_qs:
                        TransmartCOPDGeneConfig.objects.create(data=p_data)
                    else:
                        obj = conf_qs.first()
                        obj.data = p_data
                        obj.save()
