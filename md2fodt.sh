#!/bin/bash
#
# Author: Alexandre Bartel

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
  case $1 in
    -i|--include-images)
      SHOW_IMG_FODT="true"
      export SHOW_IMG_FODT
      shift # past argument
      ;;
    -*|--*)
      echo "Unknown option $1"
      exit 1
      ;;
    *)
      POSITIONAL_ARGS+=("$1") # save positional arg
      shift # past argument
      ;;
  esac
done

set -- "${POSITIONAL_ARGS[@]}" # restore positional parameters

INPUT_FILE=${POSITIONAL_ARGS[0]}
OUTPUT_FILE="${INPUT_FILE}.fodt"
cat "${DIR}/header.html" > ${OUTPUT_FILE}
pandoc -f markdown -t html "${INPUT_FILE}" --filter "${DIR}/filter.py" >> ${OUTPUT_FILE}
cat "${DIR}/footer.html" >> ${OUTPUT_FILE}

