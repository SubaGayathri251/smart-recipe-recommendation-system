from recommendation_engine import connect_database


print("=" * 60)
print("TESTING MYSQL DATABASE CONNECTION")
print("=" * 60)

connection = connect_database()

if connection is not None:

    print("\nSUCCESS! MySQL connection is working.")

    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM recipes")

    total_recipes = cursor.fetchone()[0]

    print(f"Total recipes in database: {total_recipes}")

    cursor.close()
    connection.close()

    print("\nDatabase connection closed.")

else:

    print("\nFAILED! Could not connect to MySQL.")