# FALCO
docker run -d --name falco \
  --privileged \
  -v /var/run/docker.sock:/host/var/run/docker.sock \
  -v /proc:/host/proc:ro \
  -v /boot:/host/boot:ro \
  -v /lib/modules:/host/lib/modules:ro \
  falcosecurity/falco:latest

# CIBLE
docker run -d --name webapp nginx

# EVENT SUSPECT
docker exec -it webapp bash