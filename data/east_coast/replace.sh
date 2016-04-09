while IFS=, read unit gps
do
    sed -i '' "s/${unit//[$'\t\r\n ']}/${gps//[$'\t\r\n ']}/g" allocations.csv
done < unit_to_gps.csv
