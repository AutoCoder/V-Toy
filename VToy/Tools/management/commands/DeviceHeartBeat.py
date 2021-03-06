from django.core.management.base import BaseCommand, CommandError
from chat.serializer import DBWrapper
from VToy.WeiXinUtils import WeiXinUtils

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        #parser.add_argument('poll_id', nargs='+', type=int)
        pass

    def handle(self, *args, **options):
        # for poll_id in options['poll_id']:
        #     try:
        #         poll = Poll.objects.get(pk=poll_id)
        #     except Poll.DoesNotExist:
        #         raise CommandError('Poll "%s" does not exist' % poll_id)

        #     poll.opened = False
        #     poll.save()

        #     self.stdout.write('Successfully closed poll "%s"' % poll_id)
        print "Start update HeartBeat from device to wx side ...."
        i=0
        for item in DBWrapper.heartbeatFactroy():
            print 'idx %d' % i
            i+=1
            print WeiXinUtils.updateDeviceStatus(openId=item[0], deviceId=item[1], wxMpId=item[2], deviceStatus=item[3])
        print "Finished"