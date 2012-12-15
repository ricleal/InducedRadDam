# Condor submission file

# the job description
universe= vanilla
notification = never

executable = $executable

output 	=  $executable_name.$$(Cluster).$$(Process).out
error 	=  $executable_name.$$(Cluster).$$(Process).err

# log can't be in NFS system, nor it is possible to pass $$(Cluster) over
log 	= /tmp/autoInduceRadDam.condor.$wedge_number.log

# absoluted needed in 32-bit/64-bit mixed environment
requirements = ((Arch == "INTEL") || (Arch == "x86_64"))

# current working directory on the machine where the job is executed
initialdir = $folder

queue
