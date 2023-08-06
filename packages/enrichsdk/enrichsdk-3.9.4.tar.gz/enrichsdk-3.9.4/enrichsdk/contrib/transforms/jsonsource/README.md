
{% extends 'README_DEFAULT.md' %}

{% block specificconfiguration %}
Params are meant to be passed as parameter to update_frame.

Example configuration::

     "args": {
         test': {
             'frametype': 'dict',
             'filename': '%(data_root)s/shared/hello.json',
             'params': {}
         }
{% endblock %}

{% block specificoutputs %}
Any extra information about outputs of this module
{% endblock  %}

{% block specificdependencies %}
Any information on dependencies
{% endblock  %}

