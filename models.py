from django.db import models
from custom_filefield import RboxFileField
import uuid, datetime
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

def get_unique_key():
    return uuid.uuid4().hex
    
class RboxFile(models.Model):
    unique_key = models.CharField('Unique Key', max_length=100, default=get_unique_key, unique=True, db_index=True)
    filename = models.CharField('File Name', max_length=100)
    filelabel = models.CharField('File Type', max_length=50, blank=True, null=True)
    filesize = models.PositiveIntegerField('File Size')
    filepointer = RboxFileField('File Pointer', max_length=200, upload_to='filemanager.rboxfile')
    user = models.ForeignKey(User,null=True)
    date = models.DateTimeField(default=datetime.datetime.now)

class RboxFileConnector(models.Model):
    rbox_file = models.ForeignKey(RboxFile)
    content_type = models.ForeignKey(ContentType)
    file_field_identifier = models.CharField(max_length=100, default="attachments", db_index=True)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    

