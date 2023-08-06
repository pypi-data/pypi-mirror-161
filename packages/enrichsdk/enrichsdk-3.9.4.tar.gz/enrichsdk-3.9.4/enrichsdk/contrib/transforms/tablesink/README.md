{% extends 'README_DEFAULT.md' %} 

{% block specificoutputs %} 
Files dumped on the filesystem 
{% endblock %} 

{% block specificdependencies %} 
Dependencies specified in the configuration as shown in the example below. 
{% endblock %} 

{% block specificconfiguration %} 

Parameters specific to this module include: 

* args: A dictionary of dataframe names and how to output them. It has a number of attributes:
    * type: Output type. Only 'table' value is supported for this
      option right now. 
    * filename: Output filename. You can use default parameters such
      runid 

Example: 

    ....
    "transforms": {
        "enabled": {
           ...
           "TableSink": {
             {% for p, v in example.items() -%} 
             "{{p}}": {{v}},
             {% endfor -%} 
              "args": {
                  "article": {
                     "frametype": "pandas",
                     "filename": "%(output)s/%(runid)s/inputs/article.csv", 
                     "params": {
                         "sep": "|"
                     } 
                  },
                   ...
              }
           }
        ...
       }
     }

{% endblock %} 
