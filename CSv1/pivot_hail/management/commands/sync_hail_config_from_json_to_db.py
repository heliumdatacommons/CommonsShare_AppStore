from json import load

from django.core.management.base import BaseCommand

from pivot_hail.models import HailConfig


class Command(BaseCommand):
    """
    This script synchronize PIVOT HAIL JSON configuration file under pivot_hail/data/pivot_hail.json
    to database HailConfig table on an as-needed basis, e.g., when JSON file is manually updated.
    To run this command, do:
    python manage.py sync_hail_config_from_json_to_db pivot_hail/data/pivot_hail.json
    """
    help = "synchronize PIVOT HAIL JSON configuration file to database"

    def add_arguments(self, parser):
        # pivot hail configuration file with full relative path
        parser.add_argument('config_file', help='PIVOT HAIL JSON configuration file with full '
                                                'relative path')


    def handle(self, *args, **options):
        if options['config_file'].endswith('.json'):
            config_file = options['config_file']
            with open(config_file, 'r') as fp:
                p_data = load(fp)
                if not 'id' in p_data or not 'containers' in p_data:
                    print "PIVOT JSON Configuration file is not valid"
                else:
                    conf_qs = HailConfig.objects.all()
                    if not conf_qs:
                        HailConfig.objects.create(data=p_data)
                    else:
                        obj = conf_qs.first()
                        obj.data = p_data
                        obj.save()
