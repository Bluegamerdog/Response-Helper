import sqlite3

# Connect to the source database
source_conn = sqlite3.connect('main_database.db')
source_cur = source_conn.cursor()

# Export the table as a SQL script
table_name = 'devaccess'
with open('main_database.sql', 'w') as f:
    for line in source_conn.iterdump():
        if f'CREATE TABLE {table_name}' in line:
            f.write(f'{line}\n')
            for l in source_cur.execute(f'SELECT * FROM {table_name}'):
                f.write(f'INSERT INTO {table_name} VALUES {l};\n')
            f.write('\n')
source_conn.close()

# Connect to the destination database
dest_conn = sqlite3.connect('user_database.db')
dest_cur = dest_conn.cursor()

# Execute the SQL script to create the table in the destination database
with open('devaccess.sql', 'r') as f:
    sql_script = f.read()
    dest_cur.executescript(sql_script)

dest_conn.commit()
dest_conn.close()