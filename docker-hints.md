# LDAP service in docker

Following [advice](https://computingforgeeks.com/run-openldap-server-in-docker-containers/)...

CONTENTS

- [LDAP service in docker](#ldap-service-in-docker)
  - [command-line test](#command-line-test)
  - [server](#server)
    - [directories](#directories)
    - [docker-compose](#docker-compose)
    - [LDIF file](#ldif-file)
  - [admininstrative interface](#admininstrative-interface)

## command-line test

```bash
docker exec \
    openldap ldapsearch -x \
    -H ldap://localhost \
    -b dc=example,dc=org \
    -D "cn=admin,dc=example,dc=org" \
    -w admin
```

## server

Start an LDAP server: [directories](#directories), 
[docker-compose](#docker-compose), or [LDIF](#ldif-file).

### directories

This is a good way to start a local server.  Needs to have information added
(directly or by import).

```bash
PROJECT_DIR="$(realpath -e $(pwd))"
LDAP_IMAGE=osixia/openldap:latest
# LDAP_IMAGE=bitnami/openldap:latest  # FIXME: cannot authenticate with this
LDAP_SERVER_NAME=openldap
LDAP_DOMAIN=example.org
LDAP_SERVICE_HOSTNAME="ldap.${example}"
SLAPD_DIR="${PROJECT_DIR}/slapd"  # created if not existing

docker run \
  --name "${LDAP_SERVER_NAME}" \
  --rm \
  -p 1389:389 \
  -p 1636:636 \
  --hostname "${LDAP_SERVICE_HOSTNAME}" \
  --env LDAP_ORGANISATION="Organization Without Doors" \
  --env LDAP_DOMAIN="${LDAP_DOMAIN}" \
  --env LDAP_ADMIN_USERNAME="admin" \
  --env LDAP_ADMIN_PASSWORD="admin" \
  --env LDAP_BASE_DN="dc=example,dc=org" \
  --volume "${SLAPD_DIR}/database:/var/lib/ldap" \
  --volume "${SLAPD_DIR}/config:/etc/ldap/slapd.d" \
  --detach "${LDAP_IMAGE}"

  # --volume /data/slapd/database:/var/lib/ldap \
  # --volume /data/slapd/config:/etc/ldap/slapd.d \
```

### docker-compose

Useful for running in CI process:

```bash
docker-compose -p tiled-demo -f ./ldap-docker-compose.yml up -d
```

### LDIF file

This should start a server with information from an LDIF file.

<details>
<summary>Server fails to start with error 68.</summary>

```
6320b282 conn=1014 op=1 ADD dn="dc=example,dc=org"
6320b282 conn=1014 op=1 RESULT tag=105 err=68 text=
6320b282 conn=1014 op=2 UNBIND
6320b282 conn=1014 fd=12 closed
6320b282 conn=1015 fd=12 ACCEPT from IP=127.0.0.1:44720 (IP=0.0.0.0:389)
6320b282 conn=1015 op=0 BIND dn="cn=admin,dc=example,dc=org" method=128
6320b282 conn=1015 op=0 BIND dn="cn=admin,dc=example,dc=org" mech=SIMPLE ssf=0
6320b282 conn=1015 op=0 RESULT tag=97 err=0 text=
6320b282 conn=1015 op=1 ADD dn="dc=example,dc=org"
6320b282 conn=1015 op=1 RESULT tag=105 err=68 text=
6320b282 conn=1015 op=2 UNBIND
6320b282 conn=1015 fd=12 closed
***  DEBUG  | 2022-09-13 16:40:34 | ldap_add: Already exists (68)
adding new entry "dc=example,dc=org"

ldap_add: Already exists (68)
adding new entry "dc=example,dc=org"
***  ERROR  | 2022-09-13 16:40:34 | /container/run/startup/slapd failed with status 68

***  DEBUG  | 2022-09-13 16:40:34 | Run commands before finish...
***  INFO   | 2022-09-13 16:40:34 | Killing all processes...
6320b282 daemon: shutdown requested and initiated.
6320b282 slapd shutdown: waiting for 0 operations/tasks to finish
6320b282 slapd stopped.
```

</details>

```bash
PROJECT_DIR="$(realpath -e $(pwd))"
LDAP_IMAGE=osixia/openldap:latest
# LDAP_IMAGE=bitnami/openldap:latest  # FIXME: cannot authenticate with this
LDAP_SERVER_NAME=openldap
LDAP_DOMAIN=example.org
LDAP_SERVICE_HOSTNAME="ldap.${example}"
LDIF_FILE="${PROJECT_DIR}/LDAP_LDIF_credentials.txt"

# FIXME: does not start

docker run \
  --volume "${LDIF_FILE}:/container/service/slapd/assets/config/bootstrap/ldif/50-bootstrap.ldif" \
  "${LDAP_IMAGE}" --copy-service --loglevel debug

  # --volume /data/slapd/database:/var/lib/ldap \
  # --volume /data/slapd/config:/etc/ldap/slapd.d \
```

## admininstrative interface

```bash
ADMIN_IMAGE=osixia/phpldapadmin:latest
ADMIN_HOSTNAME=phpldapadmin-service
LDAP_SERVER_NAME=openldap
LDAP_SERVER_HOST=192.168.144.97
LDAP_DOMAIN=example.org
LDAP_SERVICE_HOSTNAME="ldap.${example}"

docker run \
  --name php_ldap_admin \
  --rm \
  -p 10080:80 \
  -p 10443:443 \
  --hostname "${ADMIN_HOSTNAME}" \
  --link "${LDAP_SERVER_NAME}:${LDAP_SERVER_HOST}" \
  --env PHPLDAPADMIN_LDAP_HOSTS="${LDAP_SERVICE_HOSTNAME}" \
  --detach "${ADMIN_IMAGE}"

# https://192.168.144.97:10443
# u: `cn=admin,dc=example,dc=org`
# p: `admin`
```
