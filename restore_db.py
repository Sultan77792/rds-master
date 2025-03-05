import os
import mysql.connector
from mysql.connector import Error

def restore_database():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="aigul",
            password="Qaz12345"
        )
        
        cursor = connection.cursor()
        
        # Create database if not exists
        cursor.execute("CREATE DATABASE IF NOT EXISTS fire_incidents")
        
        # Read and execute SQL dump
        with open('fire_incidents_dump.sql', 'r', encoding='utf-8') as file:
            sql_commands = file.read().split(';')
            
            for command in sql_commands:
                if command.strip():
                    cursor.execute(command)
                    
        connection.commit()
        print("Database restored successfully!")
        
    except Error as e:
        print(f"Error restoring database: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    restore_database()