#!/bin/bash
# jupyter nbconvert ./ia/reports/notebooks/Deps_by_resolution_date.ipynb --TagRemovePreprocessor.remove_input_tags='{"remove_input"}' --to html
# jupyter nbconvert ./ia/reports/notebooks/External_dependency_for_DANCOE.ipynb --TagRemovePreprocessor.remove_input_tags='{"remove_input"}' --to html

FILES=./notebooks/*.ipynb
shopt -s nullglob
for f in $FILES; do 
    echo "Processing $f file..."
    jupyter nbconvert --execute "$f" --ExecutePreprocessor.timeout=1200; 
done

