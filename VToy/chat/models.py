from django.db import models

MessageType = (
 (0, 'Voice'),
 (1, 'Text'),
 (2, 'Image'),
)

DeviceStatus = (
    (0, 'Not alive'),
    (1, 'alive'),
)

CloseStrategy = (
    (1, 'disconnect when quit from vtoy'),
    (2, 'still connect after quit from vtoy'),
    (3, 'always attempt to connect'),
)

# Create your models here.
class VToyUser(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=30, unique=True)
    weixin_id = models.CharField(max_length=30, unique=True)
    class Meta:
        db_table = 'v_toy_user'

class ChatWxToDevice(models.Model):
    id = models.AutoField(primary_key=True)
    from_user = models.ForeignKey(VToyUser)#open_id
    receive_time = models.DateTimeField(auto_now_add=True)
    create_time = models.DateTimeField()
    session_id = models.CharField(max_length=64, default='')
    message_type = models.CharField(max_length=1, choices=MessageType)
    device_id = models.CharField(max_length=64)
    device_type = models.CharField(max_length=32)
    msg_id = models.CharField(max_length=64)
    voice_id = models.IntegerField(null=True)
    text_id = models.IntegerField(null=True)
    image_id = models.IntegerField(null=True)
    class Meta:
        db_table = 'chat_wx2device'

class ChatDeviceToWx(models.Model):
    id = models.AutoField(primary_key=True)
    to_user = models.ForeignKey(VToyUser)
    receive_time = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=64)
    message_type = models.CharField(max_length=1, choices=MessageType)
    device_id = models.CharField(max_length=64)
    device_type = models.CharField(max_length=32)
    voice_id = models.IntegerField(null=True)
    text_id = models.IntegerField(null=True)
    image_id = models.IntegerField(null=True)
    is_posted = models.BooleanField(default=False)
    class Meta:
        db_table = 'chat_device2wx'

class ChatVoices(models.Model):
    id = models.AutoField(primary_key=True, db_column='Id') # Field name made lowercase.
    voice_data = models.BinaryField()
    voice_format = models.CharField(max_length=8) #amr wav
    class Meta:
        db_table = 'chat_voice'

class ChatTexts(models.Model):
    id = models.AutoField(primary_key=True, db_column='Id') # Field name made lowercase.
    content = models.TextField()
    class Meta:
        db_table = 'chat_text'

class ChatImages(models.Model):
    id = models.AutoField(primary_key=True, db_column='Id') # Field name made lowercase.
    image_date = models.BinaryField()
    class Meta:
        db_table = 'chat_image'

class DeviceStatus(models.Model):
    id = models.AutoField(primary_key=True, db_column='Id') # Field name made lowercase.
    device_id = models.CharField(max_length=64, unique=True)
    mac = models.CharField(max_length=64, unique=True)
    lastest_syncfromdevice_time = models.DateTimeField()
    latest_msg_receive_time = models.DateTimeField()
    class Meta:
        db_table = 'device_status'

class DeviceInfo(models.Model):
    id = models.AutoField(primary_key=True, db_column='Id') # Field name made lowercase.
    device_id = models.CharField(max_length=64, unique=True)
    mac = models.CharField(max_length=64, unique=True)
    qr_ticket = models.CharField(max_length=128, unique=True)
    connect_protocol = models.CharField(max_length=8, default='4')
    auth_key = models.CharField(max_length=64)
    conn_strategy = models.CharField(max_length=1, default='1')
    close_strategy = models.CharField(max_length=1, choices=CloseStrategy, default='1')
    crypt_method = models.CharField(max_length=1, default='1')
    auth_ver = models.CharField(max_length=1, default='1')
    manu_mac_pos = models.CharField(max_length=8,default='-1')
    ser_mac_pos = models.CharField(max_length=8,default='-2')
    obsolete = models.BooleanField(default=False)
    class Meta:
        db_table = 'device_info'