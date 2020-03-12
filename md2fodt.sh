#!/bin/bash
#
# Author: Alexandre Bartel

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

INPUT_FILE=$1
OUTPUT_FILE="${INPUT_FILE}.fodt"
cat "${DIR}/header.html" > ${OUTPUT_FILE}
pandoc -f markdown -t html "${INPUT_FILE}" --filter "${DIR}/filter.py" >> ${OUTPUT_FILE}
cat "${DIR}/footer.html" >> ${OUTPUT_FILE}

