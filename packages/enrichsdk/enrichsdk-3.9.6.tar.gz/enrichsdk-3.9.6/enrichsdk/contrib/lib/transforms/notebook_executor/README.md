 
{% extends 'README_DEFAULT.md' %} 

{% block specificdescription %}
Generalized notebook executor

* Support for custom args and environment
* Support for automatic capture and surfacing of output and err

{% endblock %}

{% block specificconfiguration %} 
Configuration looks like::

     from enrichsdk.contrib.lib.transforms import NotebookExecutorBase
     class MyTestNotebook(NotebookExecutorBase):
     
         def __init__(self, *args, **kwargs):
             super().__init__(*args, **kwargs)
             self.name = "TestNotebook"
             self.notebook = os.path.join(thisdir, "Test-Notebook.ipynb")
     
         @classmethod
         def instantiable(cls):
             return True
     
         def get_environment(self):
             return {
                 'SECRET': credentials
             }
     
{% endblock %} 

{% block specificoutputs %} 
{% endblock  %} 

{% block specificdependencies %} 
{% endblock  %} 
 
