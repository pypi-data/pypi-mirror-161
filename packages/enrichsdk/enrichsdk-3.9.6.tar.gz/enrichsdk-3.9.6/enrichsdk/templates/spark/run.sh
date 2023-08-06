#!/bin/bash 

echo "########################"
echo "Enrich Spark Job Runner"
echo "########################"
echo ""

if [ $# -eq 0 ];
then
    echo "Usage: run.sh --root=... [--recompile]"
    exit 
fi

while [ $# -gt 0 ]; do
  case "$1" in
    --root=*)
      ROOT="${1#*=}"
      ;;
    --recompile)
      RECOMPILE=1 
      ;;
    *)
      printf "***************************\n"
      printf "* Error: Invalid argument ${1}*\n"
      printf "***************************\n"
      exit 1
  esac
  shift
done

THISDIR=$(dirname $0)
THISDIR=$(realpath "$THISDIR")

CONFIG="$ROOT/config.json"
DEPENDENCIES="$ROOT/dependencies"
LIB="$ROOT/lib"
LOGS="$ROOT/logs"

cd $THISDIR

if [ "$RECOMPILE" = "1" ]; then 
    mkdir -p $LIB

    # Install requirements 
    REQUIREMENTS="$THISDIR/requirements.txt"
    if [ -e "$REQUIREMENTS" ]; then 
	pip3 install -U -t $LIB -r $REQUIREMENTS 
    fi

    # Add any additional requirements 
    
    # Now create the jar file...
    jar uf $ROOT/lib.jar -C $LIB . 

    # Now add dependencies...
    jar uvf $ROOT/lib.jar -C $THISDIR dependencies
    
fi

cd $THISDIR

mkdir -p $LOGS

# => Now run the spark submit script...
spark-submit \
    --py-files=$ROOT/lib.jar \
    $THISDIR/jobs/run_spark.py \
    --config $ROOT/config.json > $LOGS/log.txt 
