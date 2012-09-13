from rboxfileplug import RboxFilePlug
from rboxsinglefileplug import RboxSingleFilePlug
from rboxresumefileplug import RboxResumeFilePlug
from models import RboxFile

def create_file(**kwargs):
    filepointer = kwargs['filepointer']
    if not 'filename' in kwargs:
        kwargs['filename'] = filepointer.name
    if not 'filesize' in kwargs:
        kwargs['filesize'] = filepointer.size
    rbox_file = RboxFile.objects.create(**kwargs)
    return rbox_file

def objects_manager():
    return RboxFile.objects
