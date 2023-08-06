profile = {
    "sources": [
	    {
	        "nature": "db",
	        "name": "kyc_data",
	        "uri": "sqlite:///%(data_root)s/shared/aml/amldb.sqlite",
	        "query": "<query>",
	        "pipeline": [
		        "cleaner_query_result"
	        ]
	    },
        {
            "nature": "custom",
            "name": "peformance",
            "generate": "get_dataset_generic",
            "dataset": "perfdata",
            "filename": "data.csv",
            "params": {
                "low_memory": False,
                "usecols": [
                    "txn_date",
                    "status",
                    "gsv"
                ],
                "dtype": {
                    "status": "str",
                    "txn_date": "str",
                    "gsv": "float"
                }
            }
        }        
    ],
    "specs": [
	    {
            "name": "Engagement-Comparison",
	        "description": "Compare how lifetime/txn_velocity etc. compare across various dimensions",
            "sources": [
                "kyc_data",
                "perfdata",
            ],
		    "generate": "generate_result",
	        "pipeline": [
		        "store_result"
	        ]
	    }
    ]
}

def get_profile_spec():
    return profile 
