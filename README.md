RboxFilePlug
============

A pluggable app that can be used to manage files across the entire application

Example
```python
from rboxfileplug import RboxFilePlug
from django.core.files import File

class Message(models.Model):
    text = models.TextField()
    files = RboxFilePlug()

>>> message.files.create(name='myfile.py', pointer = File(open('/path/to/myfile.py', 'r')))
>>>message.files.all()
```

