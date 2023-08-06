{% extends 'README_DEFAULT.md' %} 

{% block specificconfiguration %} 

Params are meant to be passed as parameter to update_frame.

Example configuration:: 

     "args": {
         test': {
             'frametype': 'dict', 
             'filename': '%(data_root)s/JSONSink/mytestoutput.json',
             'params': {} 
         }

{% endblock %} 

{% block specificoutputs %} 
{% endblock  %} 

{% block specificdependencies %} 
{% endblock  %} 
 
