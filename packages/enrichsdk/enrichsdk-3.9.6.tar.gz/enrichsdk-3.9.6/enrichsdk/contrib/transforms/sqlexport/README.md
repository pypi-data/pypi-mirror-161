{% extends 'README_DEFAULT.md' %} 

{% block specificoutputs %} 
The output depends on the role. Currently supported role:

* Export: Dump the output of the SQL query into a table. 

{% endblock %} 

{% block specificconfiguration %} 

Parameters specific to this module include: 

* args: A specification of the export 
  * exports: A list of files that must be exported. Each is a 
    dictionary with the following elements: 
      * name: Name of this export. Used for internal tracking and notifications. 
      * filename: Output filename. Can refer to other global attributes such as `data_root`, `enrich_root_dir` etc
      * type: Type of the export. Only `sqlite` supported for now 
      * frames: List of frames of the type `pandas` that should 
        exported as part of this file 

Example: 

    ....
    "transforms": {
        "enabled": [
           ...
           { 
             "transform": "SQLExport", 
             {% for p, v in example.items() -%} 
             "{{p}}": {{v}},
             {% endfor -%} 
              "args": {
                  "exports": [
                    { 
                       "type": "sqlite", 
                       "filename": "%(output)s/cars.sqlite",
                       "frames": ["cars", "alpha"]
                    },
                   ...
                  ]
                },
               ...
           }
        ...
       }
     }

{% endblock specificconfiguration %} 
