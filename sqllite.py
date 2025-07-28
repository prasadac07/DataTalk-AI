import sqlite3

# Connect to your SQLite database
conn = sqlite3.connect('./sqllite_1.db')

# Create a cursor object
cur = conn.cursor()

# ===========================
# Existing STUDENTS Table
# ===========================

# Drop the existing STUDENTS table if it exists
cur.execute("DROP TABLE IF EXISTS STUDENTS;")

# SQL command to create the STUDENTS table with an additional MARKS column
create_table_STUDENTS = """
CREATE TABLE STUDENTS (
    NAME TEXT,
    CLASS TEXT,
    SECTION TEXT,
    MARKS INTEGER
);
"""

# Execute the query to create the STUDENTS table
cur.execute(create_table_STUDENTS)

# Insert some example data into the STUDENTS table
STUDENTS_data = [
    ('Alice', 'Data Science', 'A', 85),
    ('Bob', 'AI', 'B', 90),
    ('Charlie', 'Cyber Security', 'C', 78),
    ('David', 'Data Science', 'A', 88),
    ('Eva', 'AI', 'B', 92),
    ('Frank', 'Cyber Security', 'C', 80),
    ('Grace', 'Data Science', 'A', 87),
    ('Helen', 'AI', 'B', 95),
    ('Ian', 'Cyber Security', 'C', 82),
    ('Jack', 'Data Science', 'A', 91),
    ('Karen', 'AI', 'B', 89),
    ('Liam', 'Cyber Security', 'C', 77),
    ('Mia', 'Data Science', 'A', 93)
]

# Insert the new data into the STUDENTS table
cur.executemany("INSERT INTO STUDENTS (NAME, CLASS, SECTION, MARKS) VALUES (?, ?, ?, ?)", STUDENTS_data)

# ===========================
# Existing WORKERS Table
# ===========================

# Drop the existing WORKERS table if it exists
cur.execute("DROP TABLE IF EXISTS WORKERS;")

# SQL command to create the WORKERS table with additional columns for job role and salary
create_table_WORKERS = """
CREATE TABLE WORKERS (
    NAME TEXT,
    DEPARTMENT TEXT,
    ROLE TEXT,
    SALARY INTEGER
);
"""

# Execute the query to create the WORKERS table
cur.execute(create_table_WORKERS)

# Insert some example data into the WORKERS table
WORKERS_data = [
    ('John', 'HR', 'Manager', 75000),
    ('Sarah', 'Finance', 'Analyst', 68000),
    ('Tom', 'IT', 'Developer', 82000),
    ('Emma', 'Operations', 'Supervisor', 70000),
    ('Chris', 'Marketing', 'Coordinator', 65000),
    ('Olivia', 'Finance', 'Accountant', 72000),
    ('Liam', 'IT', 'System Admin', 78000),
    ('Sophia', 'HR', 'Recruiter', 64000),
    ('Noah', 'Operations', 'Logistics Manager', 73000),
    ('Ava', 'Marketing', 'Content Specialist', 69000)
]

# Insert the new data into the WORKERS table
cur.executemany("INSERT INTO WORKERS (NAME, DEPARTMENT, ROLE, SALARY) VALUES (?, ?, ?, ?)", WORKERS_data)

# ===========================
# New COURSES Table
# ===========================

# Drop the existing COURSES table if it exists
cur.execute("DROP TABLE IF EXISTS COURSES;")

# SQL command to create the COURSES table
create_table_COURSES = """
CREATE TABLE COURSES (
    COURSE_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    COURSE_NAME TEXT,
    DESCRIPTION TEXT,
    CREDITS INTEGER
);
"""

# Execute the query to create the COURSES table
cur.execute(create_table_COURSES)

# Insert some example data into the COURSES table
COURSES_data = [
    ('Machine Learning', 'An introduction to machine learning algorithms and applications.', 4),
    ('Data Structures', 'Study of data organization and manipulation.', 3),
    ('Network Security', 'Fundamentals of securing computer networks.', 4),
    ('Database Systems', 'Comprehensive overview of database design and management.', 3),
    ('Web Development', 'Building and maintaining websites and web applications.', 3)
]

# Insert the new data into the COURSES table
cur.executemany("INSERT INTO COURSES (COURSE_NAME, DESCRIPTION, CREDITS) VALUES (?, ?, ?)", COURSES_data)

# ===========================
# New ENROLLMENTS Table
# ===========================

# Drop the existing ENROLLMENTS table if it exists
cur.execute("DROP TABLE IF EXISTS ENROLLMENTS;")

# SQL command to create the ENROLLMENTS table
create_table_ENROLLMENTS = """
CREATE TABLE ENROLLMENTS (
    ENROLLMENT_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    STUDENT_NAME TEXT,
    COURSE_ID INTEGER,
    ENROLL_DATE TEXT,
    FOREIGN KEY (STUDENT_NAME) REFERENCES STUDENTS(NAME),
    FOREIGN KEY (COURSE_ID) REFERENCES COURSES(COURSE_ID)
);
"""

# Execute the query to create the ENROLLMENTS table
cur.execute(create_table_ENROLLMENTS)

# Insert some example data into the ENROLLMENTS table
ENROLLMENTS_data = [
    ('Alice', 1, '2024-01-15'),
    ('Bob', 2, '2024-02-20'),
    ('Charlie', 3, '2024-03-10'),
    ('David', 1, '2024-01-17'),
    ('Eva', 2, '2024-02-25'),
    ('Frank', 3, '2024-03-15'),
    ('Grace', 1, '2024-01-20'),
    ('Helen', 4, '2024-04-05'),
    ('Ian', 3, '2024-03-20'),
    ('Jack', 5, '2024-05-01'),
    ('Karen', 2, '2024-02-28'),
    ('Liam', 3, '2024-03-22'),
    ('Mia', 1, '2024-01-25')
]

# Insert the new data into the ENROLLMENTS table
cur.executemany("INSERT INTO ENROLLMENTS (STUDENT_NAME, COURSE_ID, ENROLL_DATE) VALUES (?, ?, ?)", ENROLLMENTS_data)

# ===========================
# New PROJECTS Table
# ===========================

# Drop the existing PROJECTS table if it exists
cur.execute("DROP TABLE IF EXISTS PROJECTS;")

# SQL command to create the PROJECTS table
create_table_PROJECTS = """
CREATE TABLE PROJECTS (
    PROJECT_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    PROJECT_NAME TEXT,
    DEPARTMENT TEXT,
    BUDGET INTEGER,
    START_DATE TEXT,
    END_DATE TEXT
);
"""

# Execute the query to create the PROJECTS table
cur.execute(create_table_PROJECTS)

# Insert some example data into the PROJECTS table
PROJECTS_data = [
    ('Website Redesign', 'Marketing', 15000, '2024-06-01', '2024-09-30'),
    ('Cloud Migration', 'IT', 50000, '2024-07-15', '2024-12-31'),
    ('Employee Training', 'HR', 10000, '2024-08-01', '2024-10-31'),
    ('Financial Audit', 'Finance', 20000, '2024-09-01', '2024-11-30'),
    ('Cybersecurity Upgrade', 'IT', 30000, '2024-10-01', '2025-01-31')
]

# Insert the new data into the PROJECTS table
cur.executemany("INSERT INTO PROJECTS (PROJECT_NAME, DEPARTMENT, BUDGET, START_DATE, END_DATE) VALUES (?, ?, ?, ?, ?)", PROJECTS_data)

# ===========================
# Commit Changes and Close Connection
# ===========================

# Commit changes and close the connection
conn.commit()
conn.close()

print("STUDENTS, WORKERS, COURSES, ENROLLMENTS, and PROJECTS tables created and sample data inserted successfully.")
