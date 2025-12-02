DVWA
docker run --rm -it -p 80:80 vulnerables/web-dvwa
changer le niveau de difficulté à “low”

Juice Shop
docker run --rm -p 127.0.0.1:3000:3000 bkimminich/juice-shop

Log4Shell
docker run --name vulnerable-app --rm -p 8080:8080 ghcr.io/christophetd/log4shell-vulnerable-app
https://github.com/kozmer/log4j-shell-poc

SSRF_Vulnerable_Lab
git clone https://github.com/incredibleindishell/SSRF_Vulnerable_Lab
docker build –t ssrf .
docker run –p 9000:9000 ssrf
