from plug_manager_template import create_plug
from rboxfileplug import FileManager
from models import RboxFileConnector
from rboxsinglefileplug import SingleFileManagerDescriptor
from south.modelsinspector import add_introspection_rules


class ResumeFileManagerDescriptor(SingleFileManagerDescriptor):
    """
    A modified version of SingleFileManagerDescriptor for resumes
    """
    pass
    
RboxResumeFilePlug = create_plug(manager=FileManager, descriptor_cls=ResumeFileManagerDescriptor, to=RboxFileConnector)
rboxresumefileplug_introspection_rules = [((RboxResumeFilePlug,),[],{"field_identifier": ["field_identifier",{}],},)]
add_introspection_rules(rboxresumefileplug_introspection_rules, ["filemanager.models.RboxSingleFilePlug"])
