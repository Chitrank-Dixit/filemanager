from plug_manager_template import create_plug
from rboxfileplug import FileManager
from models import RboxFileConnector
from rboxsinglefileplug import SingleFileManagerDescriptor
from south.modelsinspector import add_introspection_rules

@property
def display_html(self):
    print "cool"

def process_rbox_file_to_resume_file(rboxfile_obj):
    setattr(rboxfile_obj.__class__, "display_html", display_html)
    return rboxfile_obj        

class ResumeFileManagerDescriptor(SingleFileManagerDescriptor):
    """
    A modified version of SingleFileManagerDescriptor for resumes
    """

    def __get__(self, instance, instance_type=None, return_manager=False):
        manager = super(ResumeFileManagerDescriptor, self).__get__(instance, instance_type=None, return_manager=True)
        if return_manager:
            return manager
        try:
            return process_rbox_file_to_resume_file(manager.all()[0])
        except IndexError:
            return None    


RboxResumeFilePlug = create_plug(manager=FileManager, descriptor_cls=ResumeFileManagerDescriptor, to=RboxFileConnector)
rboxresumefileplug_introspection_rules = [((RboxResumeFilePlug,),[],{"field_identifier": ["field_identifier",{}],},)]
add_introspection_rules(rboxresumefileplug_introspection_rules, ["filemanager.models.RboxSingleFilePlug"])
