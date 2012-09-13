from plug_manager_template import create_plug, ExtendedGenericManagerDescriptor
from rboxfileplug import FileManager
from models import RboxFileConnector
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
    __relatedmanager__ = None
    
    def __init__(self, field, field_identifier, max_count=None, manager_kwargs=None):
        self.field = field
        self.field_identifier = field_identifier
        self.max_count = 1
        self.manager_kwargs = manager_kwargs

    def __get__(self, instance, instance_type=None):
        manager = super(SingleFileManagerDescriptor,self).__get__(instance, instance_type=None)
        try:
            return manager.all()[0]
        except IndexError:
            return None
        

    def __set__(self, instance, value):
        if instance is None:
            raise AttributeError("Manager must be accessed via instance")
        manager = self.__get__(instance)
        manager.clear()
        for obj in value:
            manager.add(obj)


RboxSingleFilePlug = create_plug(manager=FileManager, descriptor_cls=SingleFileManagerDescriptor, to=RboxFileConnector)

rboxsinglfileplug_introspection_rules = [((RboxSingleFilePlug,),[],{"field_identifier": ["field_identifier",{}],},)]
add_introspection_rules(rboxsinglfileplug_introspection_rules, ["filemanager.models.RboxSingleFilePlug"])
