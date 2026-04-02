# backup of the db
docker exec -t pgsql pg_dump -U gusmmm unidade > private/backup_$(date +%Y%m%d_%H%M%S).sql
