from django.db.models.query import QuerySet
from models import RboxFile, RboxFileConnector
from plug_manager_template import ExtendedGenericManager,create_plug
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
                                         rboxfileconnector__file_field_identifier=self.field_identifier)

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

        '''
        Filename's can be really long. Taking the last part of the filename to preserve extension.
        '''
        filename = kwargs['filename']
        if len(filename) > 100:
            kwargs['filename'] = filename[len(filename)-100:]

        if not 'filesize' in kwargs:
            kwargs['filesize'] = filepointer.size
        rbox_file = self.get_query_set().create(**kwargs)
        rboxfile_connector = RboxFileConnector(rbox_file=rbox_file, content_type=self.content_type,
                                               object_id=self.instance.id, file_field_identifier=self.field_identifier)
        rboxfile_connector.save()
        return rbox_file
        
    def add(self, rbox_file):
        if self.max_count and (self.all().count() >= self.max_count):
            raise FileManager.MaximumNumberofObjectsAlreadyCreated("Maximum number of objects already created")

        rboxfile_connector, created = RboxFileConnector.objects.get_or_create(rbox_file=rbox_file, content_type=self.content_type,
                                               object_id=self.instance.id, file_field_identifier=self.field_identifier)
        return rbox_file

    def remove(self, rbox_file):
        """ Remove doesnot deletes the file only deletes the connector model instance
            rather use delete method for deleting files
        """
        try:
            rboxfile_connector = RboxFileConnector.objects.get(rbox_file=rbox_file, content_type=self.content_type,
                                                           object_id=self.instance.id, file_field_identifier=self.field_identifier)
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
        raise AttributeError("'FileManager' object has no attribute 'delete'")




RboxFilePlug = create_plug(manager=FileManager, to=RboxFileConnector)
    
rboxfileplug_introspection_rules = [((RboxFilePlug,),[],{"field_identifier": ["field_identifier",{}],},)]
add_introspection_rules(rboxfileplug_introspection_rules, ["filemanager.models.RboxFilePlug"])
