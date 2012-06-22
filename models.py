from django.db import models
from django.db.models.query import QuerySet
from custom_filefield import RboxFileField
from custom_filefield import S3BotoStorage
from django.contrib.auth.models import User
import uuid
import datetime
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from extendedgenericrelation import ExtendedGenericPlug, ExtendedGenericManager,\
                                    ExtendedGenericManagerDescriptor, ExtendedGenericRelation

from south.modelsinspector import add_introspection_rules


class FileManager(ExtendedGenericManager):
    
    class FileDoesNotExist(Exception):
        pass

    class FileNameDidNoTMatch(Exception):
        pass

    class MaximumNumberofObjectsAlreadyCreated(Exception):
        pass        


    def get_query_set(self):
        """Returns a new QuerySet object.  Subclasses can override this method
        to easily customize the behavior of the Manager.
        """
        return QuerySet(RboxFile).filter(rboxfileconnector__content_type=self.content_type,
                                         rboxfileconnector__object_id=self.instance.id,
                                         rboxfileconnector__file_field_identifier=self.file_field_identifier)

    def all(self):                
        if hasattr(self, 'ondelete'):            
            if self.ondelete:
                return self.none()
        return self.get_query_set()

    def create(self, **kwargs):
        if self.max_count and (self.all().count() >= self.max_count):
            raise FileManager.MaximumNumberofObjectsAlreadyCreated("Maximum number of objects already created")
        filepointer = kwargs['filepointer']
        if kwargs.get('filename', None):
            if kwargs['filename'] != filepointer.name:
                raise FileManager.FileNameDidNoTMatch("the keyword argument filename didnot match with filepointer.name")            
        if not 'filename' in kwargs:
            kwargs['filename'] = filepointer.name
        if not 'filesize' in kwargs:
            kwargs['filesize'] = filepointer.size
        rbox_file = self.get_query_set().create(**kwargs)
        rboxfile_connector = RboxFileConnector(rbox_file=rbox_file, content_type=self.content_type,
                                               object_id=self.instance.id, file_field_identifier=self.file_field_identifier)
        rboxfile_connector.save()
        return rbox_file
        
    def add(self, rbox_file):
        if self.max_count and (self.all().count() >= self.max_count):
            raise FileManager.MaximumNumberofObjectsAlreadyCreated("Maximum number of objects already created")

        rboxfile_connector, created = RboxFileConnector.objects.get_or_create(rbox_file=rbox_file, content_type=self.content_type,
                                               object_id=self.instance.id, file_field_identifier=self.file_field_identifier)
        return rbox_file

    def remove(self, rbox_file):
        """ Remove doesnot deletes the file only deletes the connector model instance
            rather use delete method for deleting files
        """
        try:
            rboxfile_connector = RboxFileConnector.objects.get(rbox_file=rbox_file, content_type=self.content_type,
                                                           object_id=self.instance.id, file_field_identifier=self.file_field_identifier)
            rboxfile_connector.delete()
        except RboxFileConnector.DoesNotExist:
            pass
        return

    def get(self, **kwargs):
        if self.max_count == 1:
            try:
                return self.all()[0]
            except IndexError:
                return None
        else:
            try:
                return super(FileManager,self).get(**kwargs)
            except RboxFile.DoesNotExist:
                raise FileManager.FileDoesNotExist

    def delete(self, **kwargs):
        if self.max_count == 1:
            return self.all().delete()
        else:
            raise AttributeError("'FileManager' object has no attribute 'delete'")


class FileManagerDescriptor(ExtendedGenericManagerDescriptor):
    """
    This class provides the functionality that makes the related-object
    managers available as attributes on a model class, for fields that have
    multiple "remote" values and have a GenericRelation defined in their model
    (rather than having another model pointed *at* them). In the example
    "article.publications", the publications attribute is a
    ReverseGenericRelatedObjectsDescriptor instance.
    """

    def get_filemanager(self):
        return FileManager


class CustomFileRelation(ExtendedGenericRelation):    
    def get_filemanager_descriptor(self):
        return FileManagerDescriptor


def get_unique_key():
    return uuid.uuid4().hex
    
class RboxFile(models.Model):
    unique_key = models.CharField('Unique Key', max_length=100, default=get_unique_key, unique=True, db_index=True)
    filename = models.CharField('File Name', max_length=100)
    filelabel = models.CharField('File Type', max_length=50, blank=True, null=True)
    filesize = models.PositiveIntegerField('File Size')
    filepointer = RboxFileField('File Pointer', max_length=200, upload_to='filemanager.rboxfile', backup_storage=S3BotoStorage(zip_n_save=True))
    user = models.ForeignKey(User,null=True)
    date = models.DateTimeField(default=datetime.datetime.now)

class RboxFileConnector(models.Model):
    rbox_file = models.ForeignKey(RboxFile)
    content_type = models.ForeignKey(ContentType)
    file_field_identifier = models.CharField(max_length=100, default="attachments", db_index=True)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
   

class GenericFilePlug(ExtendedGenericPlug):
    def __init__(self,related_name=None, file_field_identifier=None, max_count=None, *args, **kwargs):
        if not related_name:
            related_name = uuid.uuid4().hex
        kwargs['related_name'] = related_name
        kwargs['to'] = RboxFileConnector
        super(GenericFilePlug,self).__init__(**kwargs)
        self.file_field_identifier = file_field_identifier
        self.max_count = max_count

    def value_from_object(self, obj):
        import django
        if django.__dict__['VERSION'] == (1, 2, 3, 'final', 0):
            manager_obj = getattr(obj, self.attname)
            manager_obj.ondelete = True
            return manager_obj
        else:
            return super(GenericFilePlug,self).value_from_object(obj)

class GenericSingleFilePlug(object):
    def __init__(self, *args, **kwargs):
        kwargs['max_count'] = 1
        super(GenericSingleFilePlug,self).__init__(*args, **kwargs)


class RboxFilePlug(GenericFilePlug, CustomFileRelation):
    pass

class RboxSingleFilePlug(GenericSingleFilePlug, RboxFilePlug):
    pass
    
class Message(models.Model):
    docs = RboxFilePlug()

rboxfileplug_introspection_rules = [((RboxFilePlug,),[],{"file_field_identifier": ["file_field_identifier",{}],},)]
add_introspection_rules(rboxfileplug_introspection_rules, ["filemanager.models.RboxFilePlug"])

rboxsinglfileplug_introspection_rules = [((RboxSingleFilePlug,),[],{"file_field_identifier": ["file_field_identifier",{}],},)]
add_introspection_rules(rboxsinglfileplug_introspection_rules, ["filemanager.models.RboxSingleFilePlug"])