from app.core.database import DATABASE_PATH, initialize_database


if __name__ == "__main__":
    initialize_database()
    print(f"Seeded GapScope demo database at {DATABASE_PATH}")
