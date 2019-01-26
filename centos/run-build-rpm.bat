call run-cleanup.bat

docker build -t gateway_mod_evasive -f dockerfile ..
docker run -dit --name gateway_mod_evasive_node gateway_mod_evasive bash

mkdir RPMS

docker cp gateway_mod_evasive_node:/tmp/mod_evasive-rpm/RPMS/x86_64/. ./RPMS

rem call run-cleanup.bat

