# Skin Disease Detection

## Import dependencies
   ```bash
   pip install -r requirements.txt
   ```

## Setup PostgreSQL Database

1. Connect to default database:
   ```sql
   psql postgres
   ```

2. Create database:
   ```sql
   CREATE DATABASE skin_disease_detection;
   ```

3. Create user with password (same as in config):
   ```sql
   CREATE USER admin_user WITH PASSWORD 'admnin123user';
   ```

4. Grant privileges:
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE skin_disease_detection TO admin_user;
   ```
   
5. Grant schema usage and create permissions:
   ```sql
   GRANT USAGE ON SCHEMA public TO admin_user;
   GRANT CREATE ON SCHEMA public TO admin_user;
   ```
   
6. Alter the default privileges:
   ```sql
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO admin_user;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO admin_user;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO admin_user;
   ```

7. Alter the default privileges:
   ```sql
   GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin_user;
   GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin_user;
   ```

8. Exit psql:
   ```sql
   \q
   ```

9. Create tables by predefined schema:
   ```bash
   psql -U admin_user -d skin_disease_detection -f schema.sql
   ```

10. Insert dummy data for initial version
   ```bash
   python insert_dummy_data.py
   ```

## Start the Streamlit App
1. Start Streamlit App
   ```bash
   streamlit run main.py
   ```

2. Login in with prefixed account:
   - Account: **admin-user**
   - Password: **admin123user**
