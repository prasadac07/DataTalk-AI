import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
import json

# Google Gemini AI
import google.generativeai as genai

# Database connectors
import sqlite3
import mysql.connector
import psycopg2
from pymongo import MongoClient

# Load environment vars
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

# Initialize Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

app = Flask(__name__)
CORS(app)

# --------------------
# Gemini SQL Generator with Auto-correction
# --------------------
def generate_sql_with_gemini(prompt: str, max_retries: int = 3) -> str:
    """
    Send prompt to Gemini and return the SQL query string.
    Uses the correct Gemini API format.
    """
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        sql = response.text.strip()
        
        # Clean the SQL (remove markdown formatting if present)
        if sql.startswith('```sql'):
            sql = sql.replace('```sql', '').replace('```', '').strip()
        elif sql.startswith('```'):
            sql = sql.replace('```', '').strip()
            
        return sql
    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")

def auto_correct_and_execute(db_type: str, db_params: dict, sql: str, schema_info: str, original_question: str, max_retries: int = 3):
    """
    Execute SQL with auto-correction capability.
    If the query fails, it will attempt to fix it using Gemini.
    """
    for attempt in range(max_retries):
        try:
            # Execute the SQL query
            if db_type == 'sqlite':
                results = execute_sql_sqlite(db_params['path'], sql)
            elif db_type == 'mysql':
                results = execute_sql_mysql(db_params, sql)
            elif db_type == 'postgres':
                results = execute_sql_postgres(db_params, sql)
            elif db_type == 'mongo':
                # For MongoDB, we need to convert SQL-like query to MongoDB query
                results = execute_sql_mongo(db_params, sql, db_params.get('collection'))
            else:
                raise Exception('Unsupported database type')
            
            return {
                'success': True,
                'results': results,
                'final_sql': sql,
                'attempts': attempt + 1
            }
            
        except Exception as e:
            error_msg = str(e)
            
            if attempt < max_retries - 1:  # Not the last attempt
                # Generate correction prompt
                correction_prompt = f"""
The following SQL query failed with error: {error_msg}

Original question: {original_question}
Schema: {schema_info}
Failed SQL: {sql}

Please provide a corrected SQL query that fixes this error. 
Return only the SQL query without any explanation or formatting.
"""
                try:
                    corrected_sql = generate_sql_with_gemini(correction_prompt)
                    sql = corrected_sql  # Use corrected SQL for next attempt
                except Exception as correction_error:
                    return {
                        'success': False,
                        'error': f"Auto-correction failed: {str(correction_error)}",
                        'original_error': error_msg,
                        'attempts': attempt + 1
                    }
            else:
                # Last attempt failed
                return {
                    'success': False,
                    'error': error_msg,
                    'final_sql': sql,
                    'attempts': attempt + 1
                }

# --------------------
# Database Connection Functions
# --------------------
def execute_sql_sqlite(db_path: str, sql: str):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # This allows column names in results
    cur = conn.cursor()
    cur.execute(sql)
    
    if sql.strip().upper().startswith('SELECT'):
        results = [dict(row) for row in cur.fetchall()]
    else:
        conn.commit()
        results = {"affected_rows": cur.rowcount}
    
    conn.close()
    return results

def execute_sql_mysql(params: dict, sql: str):
    conn = mysql.connector.connect(**params)
    cur = conn.cursor(dictionary=True)  # Return results as dictionaries
    cur.execute(sql)
    
    if sql.strip().upper().startswith('SELECT'):
        results = cur.fetchall()
    else:
        conn.commit()
        results = {"affected_rows": cur.rowcount}
    
    conn.close()
    return results

def execute_sql_postgres(params: dict, sql: str):
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    cur.execute(sql)
    
    if sql.strip().upper().startswith('SELECT'):
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        results = [dict(zip(columns, row)) for row in rows]
    else:
        conn.commit()
        results = {"affected_rows": cur.rowcount}
    
    conn.close()
    return results

def execute_sql_mongo(params: dict, query_text: str, collection: str):
    """
    For MongoDB, we need to convert natural language to MongoDB query syntax
    """
    # This is a simplified approach - in practice, you'd want more sophisticated parsing
    client = MongoClient(host=params.get('host', 'localhost'), 
                        port=params.get('port', 27017),
                        username=params.get('username'),
                        password=params.get('password'))
    
    db = client[params.get('database')]
    coll = db[collection]
    
    # Try to parse the query_text as a MongoDB query
    try:
        if query_text.strip().startswith('{'):
            # Assume it's already a MongoDB query
            mongo_query = json.loads(query_text)
        else:
            # Convert SQL-like syntax to basic MongoDB query
            # This is very basic - you might want to enhance this
            mongo_query = {}
        
        results = list(coll.find(mongo_query))
        # Convert ObjectId to string for JSON serialization
        for result in results:
            if '_id' in result:
                result['_id'] = str(result['_id'])
    except Exception as e:
        raise Exception(f"MongoDB query error: {str(e)}")
    finally:
        client.close()
    
    return results

# --------------------
# Helper Functions
# --------------------
def build_prompt(question: str, schema_info: str, db_type: str) -> str:
    prompt = f"""
You are an expert SQL assistant. Convert the following natural language request into a {db_type.upper()} query.

Database Schema:
{schema_info}

Natural Language Request: {question}

Important guidelines:
- Return only the SQL query, no explanations or formatting
- Use proper {db_type.upper()} syntax
- Make sure column names and table names match the schema exactly
- For aggregations, use appropriate GROUP BY clauses
- Handle NULL values appropriately

SQL Query:
"""
    return prompt

def get_schema_info(db_type: str, db_params: dict) -> str:
    """
    Automatically extract schema information from the database
    """
    try:
        if db_type == 'sqlite':
            conn = sqlite3.connect(db_params['path'])
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cur.fetchall()
            
            schema_info = "Tables:\n"
            for table in tables:
                table_name = table[0]
                cur.execute(f"PRAGMA table_info({table_name});")
                columns = cur.fetchall()
                schema_info += f"\n{table_name}:\n"
                for col in columns:
                    schema_info += f"  - {col[1]} ({col[2]})\n"
            
            conn.close()
            return schema_info
            
        elif db_type == 'mysql':
            conn = mysql.connector.connect(**db_params)
            cur = conn.cursor()
            cur.execute("SHOW TABLES;")
            tables = cur.fetchall()
            
            schema_info = "Tables:\n"
            for table in tables:
                table_name = table[0]
                cur.execute(f"DESCRIBE {table_name};")
                columns = cur.fetchall()
                schema_info += f"\n{table_name}:\n"
                for col in columns:
                    schema_info += f"  - {col[0]} ({col[1]})\n"
            
            conn.close()
            return schema_info
            
        # Add similar logic for PostgreSQL and MongoDB
        else:
            return "Schema auto-detection not implemented for this database type yet."
            
    except Exception as e:
        return f"Could not retrieve schema: {str(e)}"

# --------------------
# API Endpoints
# --------------------
@app.route('/generate_query', methods=['POST'])
def generate_query():
    data = request.get_json() or {}
    question = data.get('question')
    schema = data.get('schema')
    db_type = data.get('db_type', 'sqlite')

    if not question or not schema:
        return jsonify({'error': 'Provide question and schema'}), 400

    prompt = build_prompt(question, schema, db_type)
    try:
        sql = generate_sql_with_gemini(prompt)
        return jsonify({'sql': sql})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/execute_query', methods=['POST'])
def execute_query():
    data = request.get_json() or {}
    db_type = data.get('dbType')
    db_params = data.get('dbParams')
    sql = data.get('sql')
    schema = data.get('schema', '')
    question = data.get('question', '')

    if not all([db_type, db_params, sql]):
        return jsonify({'error': 'dbType, dbParams, and sql required'}), 400

    # Execute with auto-correction
    result = auto_correct_and_execute(db_type, db_params, sql, schema, question)
    
    if result['success']:
        return jsonify({
            'success': True,
            'results': result['results'],
            'final_sql': result['final_sql'],
            'attempts': result['attempts']
        })
    else:
        return jsonify({
            'success': False,
            'error': result['error'],
            'attempts': result.get('attempts', 1)
        }), 500

@app.route('/get_schema', methods=['POST'])
def get_schema():
    """
    New endpoint to automatically extract schema from database
    """
    data = request.get_json() or {}
    db_type = data.get('dbType')
    db_params = data.get('dbParams')

    if not all([db_type, db_params]):
        return jsonify({'error': 'dbType and dbParams required'}), 400

    try:
        schema_info = get_schema_info(db_type, db_params)
        return jsonify({'schema': schema_info})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)