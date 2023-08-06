 
{% extends 'README_DEFAULT.md' %} 

{% block specificdescription %}
Generalized query execution transform. It should

* Support query engines (MySQL, Hive, Presto) 
* Support templatized execution 
* Support arbitrary number of queries 

{% endblock %}

{% block specificconfiguration %} 
Configuration looks like::
  
    "args": {
	
	   "executors": {
	        "hive": {
			    "handler": "call_hive",
                "params": {
				     "cred": "hivecred",
				}
			}
	   },
	   'specs': [
               {
                   "name": "roomdb",
                   "cred": "roomdb",
                   "queries": [ 
                       {
                           "name": "select_star",
                           "output": "%(data_root)s/shared/db/select_star/%(dt)s.tsv",
                           "sql": "%(transform_root)s/SQL/select_star.sql",
                           "params": {
                            "alpha": 22
                           }
                       }
                   ]
               },
               {
                   "enable": False,
                   "name": "hive",
                   "cred": "hiveserver",
                   "queries": [ 
                       {
                           "name": "employees",
                           "output": "%(data_root)s/shared/db/employee/%(dt)s.tsv",
                           "sql": "%(transform_root)s/SQL/employees.hql",
                       }
                   ]
               }
	   ]
    }
{% endblock %} 

{% block specificoutputs %} 
{% endblock  %} 

{% block specificdependencies %} 
{% endblock  %} 
 
