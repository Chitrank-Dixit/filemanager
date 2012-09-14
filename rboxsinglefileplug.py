from plug_manager_template import create_plug, ExtendedGenericManagerDescriptor
from rboxfileplug import FileManager
from models import RboxFileConnector, RboxFile
from south.modelsinspector import add_introspection_rules

class SingleFileManagerDescriptor(ExtendedGenericManagerDescriptor):
    """
    This class provides the functionality that makes the related-object
    managers available as attributes on a model class, for fields that have
    multiple "remote" values and have a GenericRelation defined in their model
    (rather than having another model pointed *at* them). In the example
    "article.publications", the publications attribute is a
    ReverseGenericRelatedObjectsDescriptor instance.
    """
    
    def __init__(self, field, field_identifier, max_count=1, manager_kwargs=None):
        if max_count > 1:
            raise TypeError("max_count in a singlefileplug should be always 1")
        self.field = field
        self.field_identifier = field_identifier
        self.max_count = max_count
        self.manager_kwargs = manager_kwargs
        

    def __get__(self, instance, instance_type=None, return_manager=False):
        manager = super(SingleFileManagerDescriptor, self).__get__(instance, instance_type=None)
        if return_manager:
            return manager
        try:
            return manager.all()[0]
        except IndexError:
            return None
        

    def __set__(self, instance, value):
        if instance is None:
            raise AttributeError("Manager must be accessed via instance")
            
        if not isinstance(value, RboxFile):
            raise TypeError("Only accepts a RboxFile object")
            
        manager = self.__get__(instance, return_manager=True)        
        manager.remove(manager.all()[0])
        manager.add(value)


RboxSingleFilePlug = create_plug(manager=FileManager, descriptor_cls=SingleFileManagerDescriptor, to=RboxFileConnector)

rboxsinglefileplug_introspection_rules = [((RboxSingleFilePlug,),[],{"field_identifier": ["field_identifier",{}],},)]
add_introspection_rules(rboxsinglefileplug_introspection_rules, ["filemanager.models.RboxSingleFilePlug"])
