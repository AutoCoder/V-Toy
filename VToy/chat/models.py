from django.db import models

MessageType = (
 (0, 'Voice'),
 (1, 'Text'),
 (2, 'Image'),
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
    user = models.ForeignKey(VToyUser)
    receive_time = models.DateTimeField(auto_now_add=True)
    message_type = models.CharField(max_length=1, choices=MessageType)
    mac = models.CharField(max_length=20)
    voice_id = models.IntegerField()
    text_id = models.IntegerField()
    image_id = models.IntegerField()
    class Meta:
        db_table = 'chat_wx2device'

class ChatDeviceToWx(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(VToyUser)
    receive_time = models.DateTimeField(auto_now_add=True)
    message_type = models.CharField(max_length=1, choices=MessageType)
    mac = models.CharField(max_length=20)
    issend2all = models.BooleanField(False)
    voice_id = models.IntegerField()
    text_id = models.IntegerField()
    image_id = models.IntegerField()    
    class Meta:
        db_table = 'chat_device2wx'

class ChatVoices(models.Model):
    id = models.AutoField(primary_key=True, db_column='Id') # Field name made lowercase.
    voice_data = models.BinaryField()
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

class ChatGroups(models.Model):
    id = models.AutoField(primary_key=True, db_column='Id') # Field name made lowercase.
    hardware_mac = models.CharField(max_length=30)
    clients = models.TextField() #json
    sync_mark_of_device = models.DateTimeField()
    class Meta:
        db_table = 'chat_group'
