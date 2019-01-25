docker stop gateway_mod_evasive_node
docker rm gateway_mod_evasive_node
docker rmi gateway_mod_evasive --force
rem docker system prune --force

docker build -t gateway_mod_evasive -f dockerfile ..
docker run -dit --name gateway_mod_evasive_node -p 8080:80 -p 8443:443 gateway_mod_evasive
docker logs -f gateway_mod_evasive_node
