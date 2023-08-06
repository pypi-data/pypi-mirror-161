 
{% extends 'README_DEFAULT.md' %} 

{% block specificconfiguration %} 

The transform takes a list of actions. The only action type supported
for now is `copy`. Each copy task requires source, destination, and
instruction on what to do with existing file.

Example::
 
    {
		"transform": "FileOperations",
		"enable": true,
		"dependencies": {
                   ....
		},
		"args": {
		    "actions": [
     			{
			    "action": "copy",
			    "src": "%(output)s/%(runid)s/profile.sqlite",
			    "dst": "%(data_root)s/shared/campaigns/profile_daily/profile.sqlite",
			    "backupsuffix": ".backup"	
	     		},
             ]
         }
    }


{% endblock %} 

{% block specificoutputs %} 
{% endblock  %} 

{% block specificdependencies %} 
{% endblock  %} 
 
