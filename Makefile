default: help

# Default
MAIN_APP=odoo
DB_APP=db
DC_FILE=docker-compose.yml
# -p 9999 - for tests, to avoid the error "port is in use".
# Needs to be defined in the include
include odoo-dev.env

.PHONY: help
help: # Show help for each of the Makefile recipes.
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

.PHONY: build
build: # Build main Odoo image.
	docker compose -f $(DC_FILE) build $(MAIN_APP)

.PHONY: up
up: # Service up.
	rm -f ./helpers/localdev/local_flags/odoo_debug_flag.tmp
	docker compose -f $(DC_FILE) up -d
	@echo "---------------------------------------"
	@echo "> Connect at: http://localhost:38069/web"
	@echo "---------------------------------------"

.PHONY: down
down: # Downs the application.
	rm -f ./helpers/localdev/local_flags/odoo_debug_flag.tmp
	docker compose -f $(DC_FILE) down

.PHONY: down-cleanup
down-cleanup: # Downs the application and remove volumes.
	rm -f ./helpers/localdev/local_flags/odoo_debug_flag.tmp
	docker compose -f $(DC_FILE) down -v

.PHONY: h
h: # Show help about the app.
	@echo "---------------------------------------"
	@echo "> Connect at: http://localhost:38069/web"
	@echo "> Databases:  http://localhost:38069/web/database/manager"
	@echo "---------------------------------------"

.PHONY: up-db
up-db: # PostgreSQL Database up.
	docker compose -f $(DC_FILE) up -d $(DB_APP)
	@echo "> Connect via port 9015"

.PHONY: restart-web
restart-web: # Restart main Odoo app.
	docker compose -f $(DC_FILE) restart $(MAIN_APP)

.PHONY: shell
shell: # Log into app shell if container is up.
	docker compose -f $(DC_FILE) exec $(MAIN_APP) /bin/bash

.PHONY: shell-new
shell-new: # Log into app shell. Starts new terminal session.
	docker compose -f $(DC_FILE) run $(MAIN_APP) /bin/bash

.PHONY: logs
logs: # Show logs of Odoo container.
	docker compose -f $(DC_FILE) logs -f $(MAIN_APP)

.PHONY: logs-db
logs-db: # Show logs of DB container.
	docker compose -f $(DC_FILE) logs -f $(DB_APP)

.PHONY: stop
stop: # Downs the application.
	rm -f ./helpers/localdev/local_flags/odoo_debug_flag.tmp
	docker compose -f $(DC_FILE) stop

.PHONY: start
start: # Starts the application.
	rm -f ./helpers/localdev/local_flags/odoo_debug_flag.tmp
	docker compose -f $(DC_FILE) start

.PHONY: start-debug
start-debug: # Start the application with the debug module enabled.
	touch ./helpers/localdev/local_flags/odoo_debug_flag.tmp
	docker compose -f $(DC_FILE) start

.PHONY: ps
ps: # Running containers of the App.
	docker compose -f $(DC_FILE) ps

.PHONY: install-custom
install-custom: # Installs predefined custom module.
	docker compose -f $(DC_FILE) exec $(MAIN_APP) /entrypoint.sh odoo -p 9999 -d $(DEV_DB) -i $(MOD) --stop-after-init

.PHONY: uninstall-custom
uninstall-custom: # Installs predefined custom module.
	docker compose -f $(DC_FILE) exec $(MAIN_APP) /entrypoint.sh odoo -p 9999 -d $(DEV_DB) -u $(MOD) --stop-after-init

.PHONY: update-custom
update-custom: # Updates predefined custom module.
	docker compose -f $(DC_FILE) exec $(MAIN_APP) /entrypoint.sh odoo -p 9999 -d $(DEV_DB) -u $(MOD) --stop-after-init

.PHONY: update-all
update-all: # Updates predefined custom module.
	docker compose -f $(DC_FILE) exec $(MAIN_APP) /entrypoint.sh odoo -p 9999 -d $(DEV_DB) -u all --stop-after-init

.PHONY: scaffold
scaffold: # Updates predefined custom module.
	docker compose -f $(DC_FILE) exec $(MAIN_APP) /entrypoint.sh odoo  scaffold $(MOD)  $(MOD_PATH)

.PHONY: test-custom
test-custom: # Testing custom module with its tests.
	docker compose -f $(DC_FILE) exec $(MAIN_APP) /entrypoint.sh odoo -p 9999 -d $(DEV_DB) -u $(MOD) --test-tags $(MOD_TEST_TAGS) --stop-after-init

.PHONY: install-new
install-new: # Install new BLANK Odoo database from scratch.
	docker compose -f $(DC_FILE) exec $(MAIN_APP) /entrypoint.sh odoo -d $(DEV_DB) -i base --stop-after-init

.PHONY: test-custom-short
test-custom-short: # Testing custom module with its tests. Without module -u.
	docker compose -f $(DC_FILE) exec $(MAIN_APP) /entrypoint.sh odoo -p 9999 --test-tags $(MOD_TEST_TAGS) -d $(DEV_DB) --stop-after-init

.PHONY: copy-odoo-addons
copy-odoo-addons: # Copies Odoo addons to a mounted dedicated folder (preparation)
	docker compose -f $(DC_FILE) exec $(MAIN_APP) cp -R /usr/lib/python3/dist-packages/odoo /usr/lib/python3/dist-packages/odoo-src-extract

.PHONY: env
env: # Shows ENV for main app.
	docker compose -f $(DC_FILE) exec $(MAIN_APP) printenv

.PHONY: fix-permissions
fix-permissions: # Fix permissions for the image
	docker compose -f $(DC_FILE) exec -u root $(MAIN_APP) chown odoo:odoo /mnt/custom_addons /mnt/enterprise
	@echo "---------------------------------------"
	@echo "> /mnt/custom_addons /mnt/enterprise"
	@echo "---------------------------------------"
	docker compose -f $(DC_FILE) exec -u root $(MAIN_APP) chown -R odoo:odoo /var/lib/odoo

.PHONY: fix-local-permissions
fix-local-permissions: # Fix local permissions for the project
	# Fix helpers dir
	chmod a+x helpers/docker/entrypoint.sh helpers/docker/install_manifest.sh helpers/testing/test_modules.sh
	# Fix pginit dir
	chmod a+x postgres-init/dev/init-odoo-db.sh postgres-init/prod/init-odoo-db.sh



# master-ps = mk8d-j7t9-2u4c, admin

