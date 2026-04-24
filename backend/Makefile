SUPABASE_DEV_URI := $(shell grep SUPABASE_POSTGRES_URI .env.dev | cut -d '=' -f2-)
SUPABASE_PROD_URI := $(shell grep SUPABASE_POSTGRES_URI .env.prod | cut -d '=' -f2-)
MIGRATIONS_DIR := db/migrations

# Create a new timestamped migration file
new-migration:
ifndef name
	$(error Usage: make new-migration name=create_table_example)
endif
	dbmate --migrations-dir $(MIGRATIONS_DIR) new $(name)

# Apply all unapplied migrations
migrate-dev:
	DATABASE_URL=$(SUPABASE_DEV_URI) dbmate --migrations-dir $(MIGRATIONS_DIR) up && \
	$(MAKE) dump-schema-dev generate-schema-artifacts

migrate-prod:
	DATABASE_URL=$(SUPABASE_PROD_URI) dbmate --migrations-dir $(MIGRATIONS_DIR) up && \
	$(MAKE) dump-schema-prod generate-schema-artifacts

# Roll back the last migration
rollback-dev:
	DATABASE_URL=$(SUPABASE_DEV_URI) dbmate --migrations-dir $(MIGRATIONS_DIR) down && \
	$(MAKE) dump-schema-dev generate-schema-artifacts

rollback-prod:
	DATABASE_URL=$(SUPABASE_PROD_URI) dbmate --migrations-dir $(MIGRATIONS_DIR) down && \
	$(MAKE) dump-schema-prod generate-schema-artifacts

# Show migration status
status-dev:
	DATABASE_URL=$(SUPABASE_DEV_URI) dbmate --migrations-dir $(MIGRATIONS_DIR) status

status-prod:
	DATABASE_URL=$(SUPABASE_PROD_URI) dbmate --migrations-dir $(MIGRATIONS_DIR) status

dump-schema-dev:
	PGPASSWORD=$$(echo $(SUPABASE_DEV_URI) | sed -E 's/.*:([^@]+)@.*/\1/') \
	pg_dump --no-owner --no-privileges --schema=public \
	--username=$$(echo $(SUPABASE_DEV_URI) | sed -E 's/.*\/\/([^:]+):.*/\1/') \
	--host=$$(echo $(SUPABASE_DEV_URI) | sed -E 's/.*@([^:\/]+).*/\1/') \
	--port=5432 \
	--dbname=$$(echo $(SUPABASE_DEV_URI) | sed -E 's/.*\/([^?]+).*/\1/') \
	--file=db/schema.sql

dump-schema-prod:
	PGPASSWORD=$$(echo $(SUPABASE_PROD_URI) | sed -E 's/.*:([^@]+)@.*/\1/') \
	pg_dump --no-owner --no-privileges --schema=public \
	--username=$$(echo $(SUPABASE_PROD_URI) | sed -E 's/.*\/\/([^:]+):.*/\1/') \
	--host=$$(echo $(SUPABASE_PROD_URI) | sed -E 's/.*@([^:\/]+).*/\1/') \
	--port=5432 \
	--dbname=$$(echo $(SUPABASE_PROD_URI) | sed -E 's/.*\/([^?]+).*/\1/') \
	--file=db/schema.prod.sql

reset-dev:
	PGPASSWORD=$$(echo $(SUPABASE_DEV_URI) | sed -E 's/.*:([^@]+)@.*/\1/') \
	psql -U $$(echo $(SUPABASE_DEV_URI) | sed -E 's/.*\/\/([^:]+):.*/\1/') \
	-h $$(echo $(SUPABASE_DEV_URI) | sed -E 's/.*@([^:\/]+).*/\1/') \
	-d $$(echo $(SUPABASE_DEV_URI) | sed -E 's/.*\/([^?]+).*/\1/') \
	-c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

reset-prod:
	echo "[STOP] DO NOT RESET PROD. This will drop all production data."
	
generate-schema-artifacts:
	PYTHONPATH=.. python db/scripts/generate_sqlmodel_from_sql.py && \
	PYTHONPATH=.. python db/scripts/generate_crud_schemas.py