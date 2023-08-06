{% extends 'README_DEFAULT.md' %} 

{% block specificoutputs %} 
Loaded dataframes 
{% endblock %} 

{% block specificdependencies %} 
Dependencies specified in the configuration as shown in the example below. 
{% endblock %} 

{% block specificconfiguration %} 

Parameters specific to this module include: 

* args: A dictionary of dataframe names and how to load them. It has
  a number of attributes:

    * type: Output type. Only 'table' value is supported for this
      option. 
    * filename: Output filename. You can use default parameters such
      runid 
    * params: Params are arguments to [pandas read_csv](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_csv.html) 

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
                     "type": "file", 
                     "filename": "%(data)s/ArticleData.csv", 
                     "params": {
                         "delimiter": "|",
                         "dtype": { 
                             "sku": "category", 
                             "mc_code": "int64", 
                             "sub_class": "category",
                             "priority": "float64"
                             ...
                         }
                     }
                  }
                  ...
              }
           }
        ...
       }
     }

{% endblock %} 
