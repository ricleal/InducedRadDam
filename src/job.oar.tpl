# OAR job/script file

# This will launch XDS followed by best 

echo "OAR file created on the `date +%F` at `date +%T`"
echo "OAR_NODEFILE: $$OAR_NODEFILE"
echo "OAR_JOB_ID: $$OAR_JOB_ID"
echo "OAR_RESOURCE_PROPERTIES_FILE: $$OAR_RESOURCE_PROPERTIES_FILE"
echo "OAR_JOB_NAME: $$OAR_JOB_NAME"
echo "OAR_PROJECT_NAME: $$OAR_PROJECT_NAME"

echo "Executing $firstExecutable"

$firstExecutable

echo "Done: $firstExecutable"

echo "Executing $secondExecutable"

$secondExecutable

echo "Done: $secondExecutable"

echo "Done all"


