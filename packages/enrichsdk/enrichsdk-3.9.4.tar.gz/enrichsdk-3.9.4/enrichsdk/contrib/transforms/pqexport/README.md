
{% extends 'README_DEFAULT.md' %}

{% block specificdescription %}
{% endblock %}

{% block specificconfiguration %}

The configuration requires a list of exports, each of which specifies a pattern for the frame name,

     'conf': {
        'args': {
            "exports": [
              {
    	        "name": "%(frame)s_pq",
    	        "type": "pq", # optional. Default is pq
    	        "frames": ["cars"],
    	        "filename": "%(output)s/%(runid)s/%(frame)s.pq",
                "params": {
                        # parquet parameters.
                        # "compression": 'gzip'
                        # "engine": 'auto'
                        # "index" :None,
                        # "partition_cols": None
                 }
    	      }
            ]
        }
    }


{% endblock %}

{% block specificoutputs %}
{% endblock  %}

{% block specificdependencies %}
{% endblock  %}

