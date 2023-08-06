# New Spark project 

This repository is roughly based on `pyspark-template-project`. They
have embedded in the code, some best practices. We have extended them
to handle the specifics of the project.

## Project Structure

The basic project structure is as follows:

```bash
root/
 |   run.sh 
 |   requirements.txt 
 |-- dependencies/
 |   |-- logging.py
 |   |-- spark.py
 |   |-- enrich.py 
 |   |-- supernova.py 
 |-- jobs/
 |   |-- run_spark.py
 |-- configs/
 |   |-- etl_config.json
```

The main Python module containing the ETL job (which will be sent to
the Spark cluster), is `jobs/run_spark.py`. 

Any external addition configuration parameters required by
`run_spark.py` are stored in JSON format in 
`configs/etl_config.json`.

Additional modules that support this job are kept in the
`dependencies` folder. This includes generic spark configuration,
logging, and enrich-specific configuration scripts. In addition, the
application can store application-specific code. 

`run.sh` is bash script for building these dependencies into a
jar-file to be sent to the cluster (`lib.jar`). 

## Dynamic Input 

`run_spark.py` requires a pointer to the root directory where the
script can find additional configuration, datasets, and where the logs
are stored.
```bash
root/
 |-- config.py
 |-- data/
 |   |-- members.csv
 |-- log/
     |-- log.txt 
```

`config.py` specifies parameters that the `run_spark.py` understands
such as path to the data, and tagger configuration.

```javascript
{
    "name": "member_perday",
    "data": {
        "members": "data/members.csv"
    },
    "params": {
    	"taggers": [
	       {
	     	"name": "persona2",
     		"owner": "Dilloy",
     		"filepath": "..."
    	    }
	     ]
    }
}
```


## Running the ETL job

`run.sh` does the following:

1. Builds a jar file from the `requirements.txt` and dependencies
   directories.

2. Starts `spark-submit` with the `run_spark.py` 

The run.sh should be run with a directory containing the dynamic input
to the script.

```
$ run.sh 
########################
Enrich Spark Job Runner
########################

Usage: run.sh --root=... [--recompile]
```

```bash
spark-submit \
    --py-files=$ROOT/lib.jar \
    $THISDIR/jobs/run_spark.py \
    --config $ROOT/config.json 

```
