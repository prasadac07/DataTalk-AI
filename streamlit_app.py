import streamlit as st
import requests
import json
import pandas as pd

st.set_page_config(
    page_title="🧠 Gemini SQL Assistant", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🧠 Gemini SQL Assistant")
st.write("Generate and execute SQL queries from natural language using Gemini AI with auto-correction capabilities.")

# Initialize session state
if 'generated_sql' not in st.session_state:
    st.session_state.generated_sql = ""
if 'db_connected' not in st.session_state:
    st.session_state.db_connected = False
if 'schema_info' not in st.session_state:
    st.session_state.schema_info = ""

# Backend URL
BACKEND_URL = "http://localhost:5000"

# Sidebar for database configuration
st.sidebar.header("🔧 Database Configuration")

db_type = st.sidebar.selectbox(
    "Choose your database type:", 
    ["sqlite", "mysql", "postgres", "mongo"]
)

db_params = {}

if db_type == "sqlite":
    db_params["path"] = st.sidebar.text_input(
        "SQLite DB Path", 
        value="./test.db",
        help="Path to your SQLite database file"
    )
    
elif db_type in ["mysql", "postgres"]:
    db_params["host"] = st.sidebar.text_input("Host", value="localhost")
    default_port = "3306" if db_type == "mysql" else "5432"
    db_params["port"] = st.sidebar.text_input("Port", value=default_port)
    db_params["user"] = st.sidebar.text_input("Username", value="root" if db_type == "mysql" else "postgres")
    db_params["password"] = st.sidebar.text_input("Password", type="password")
    db_params["database"] = st.sidebar.text_input("Database name")
    
elif db_type == "mongo":
    db_params["host"] = st.sidebar.text_input("MongoDB Host", value="localhost")
    db_params["port"] = st.sidebar.number_input("Port", value=27017, min_value=1, max_value=65535)
    db_params["username"] = st.sidebar.text_input("Username (optional)")
    db_params["password"] = st.sidebar.text_input("Password (optional)", type="password")
    db_params["database"] = st.sidebar.text_input("Database name")
    db_params["collection"] = st.sidebar.text_input("Collection name")

# Auto-extract schema button
if st.sidebar.button("🔍 Auto-Extract Schema"):
    if all(db_params.values()) or (db_type == "sqlite" and db_params.get("path")):
        with st.spinner("Extracting database schema..."):
            try:
                response = requests.post(f"{BACKEND_URL}/get_schema", json={
                    "dbType": db_type,
                    "dbParams": db_params
                })
                
                if response.status_code == 200:
                    schema_data = response.json()
                    st.session_state.schema_info = schema_data.get("schema", "")
                    st.session_state.db_connected = True
                    st.sidebar.success("Schema extracted successfully!")
                else:
                    st.sidebar.error(f"Failed to extract schema: {response.json().get('error', 'Unknown error')}")
            except Exception as e:
                st.sidebar.error(f"Connection error: {str(e)}")
    else:
        st.sidebar.warning("Please fill in all required database parameters.")

# Manual schema input
manual_schema = st.sidebar.text_area(
    "Or enter schema manually:",
    value=st.session_state.schema_info,
    height=200,
    help="Describe your database schema, tables, and columns"
)

if manual_schema:
    st.session_state.schema_info = manual_schema

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 Natural Language Query")
    
    # Example queries
    with st.expander("💡 Example Queries"):
        st.write("""
        - "Show me all customers who made purchases last month"
        - "What's the total revenue by product category?"
        - "Find the top 10 most popular products"
        - "List employees with salary greater than 50000"
        - "Count orders by status for this year"
        """)
    
    # Query input
    question = st.text_area(
        "Enter your natural language query:",
        height=100,
        placeholder="e.g., Show me all users who registered in the last 30 days"
    )
    
    # Generate SQL button
    if st.button("🚀 Generate SQL", type="primary"):
        if not question:
            st.warning("Please enter a question.")
        elif not st.session_state.schema_info:
            st.warning("Please provide database schema information.")
        else:
            with st.spinner("Generating SQL using Gemini..."):
                try:
                    response = requests.post(f"{BACKEND_URL}/generate_query", json={
                        "question": question,
                        "schema": st.session_state.schema_info,
                        "db_type": db_type
                    })
                    
                    if response.status_code == 200:
                        result = response.json()
                        sql = result.get("sql", "")
                        if sql:
                            st.session_state.generated_sql = sql
                            st.success("SQL generated successfully!")
                        else:
                            st.error("Failed to generate SQL.")
                    else:
                        st.error(f"Error: {response.json().get('error', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Connection error: {str(e)}")

with col2:
    st.header("💻 Generated SQL")
    
    if st.session_state.generated_sql:
        st.code(st.session_state.generated_sql, language="sql")
        
        # Execute button
        if st.button("⚡ Execute Query with Auto-Correction", type="secondary"):
            # Validate database parameters
            required_filled = False
            if db_type == "sqlite":
                required_filled = bool(db_params.get("path"))
            elif db_type in ["mysql", "postgres"]:
                required_filled = all([
                    db_params.get("host"),
                    db_params.get("user"),
                    db_params.get("database")
                ])
            elif db_type == "mongo":
                required_filled = all([
                    db_params.get("host"),
                    db_params.get("database"),
                    db_params.get("collection")
                ])
            
            if not required_filled:
                st.error("Please fill in all required database connection parameters.")
            else:
                payload = {
                    "dbType": db_type,
                    "dbParams": db_params,
                    "sql": st.session_state.generated_sql,
                    "schema": st.session_state.schema_info,
                    "question": question
                }
                
                with st.spinner("Executing SQL with auto-correction..."):
                    try:
                        response = requests.post(f"{BACKEND_URL}/execute_query", json=payload)
                        result = response.json()
                        
                        if result.get("success"):
                            st.success(f"✅ Query executed successfully! (Attempts: {result.get('attempts', 1)})")
                            
                            # Show final SQL if it was corrected
                            final_sql = result.get("final_sql")
                            if final_sql != st.session_state.generated_sql:
                                st.info("🔧 Query was auto-corrected:")
                                st.code(final_sql, language="sql")
                            
                            # Display results
                            results = result.get("results", [])
                            if results:
                                if isinstance(results, list) and len(results) > 0:
                                    if isinstance(results[0], dict):
                                        # Convert to DataFrame for better display
                                        df = pd.DataFrame(results)
                                        st.dataframe(df, use_container_width=True)
                                        
                                        # Download button
                                        csv = df.to_csv(index=False)
                                        st.download_button(
                                            label="📥 Download as CSV",
                                            data=csv,
                                            file_name="query_results.csv",
                                            mime="text/csv"
                                        )
                                    else:
                                        st.write("Results:")
                                        st.json(results)
                                elif isinstance(results, dict):
                                    st.write("Query Result:")
                                    st.json(results)
                                else:
                                    st.write("No results returned.")
                            else:
                                st.info("Query executed successfully but returned no results.")
                                
                        else:
                            st.error(f"❌ Query execution failed after {result.get('attempts', 1)} attempts")
                            st.error(f"Error: {result.get('error', 'Unknown error')}")
                            
                    except Exception as e:
                        st.error(f"Connection error: {str(e)}")
    else:
        st.info("Generate a SQL query first to see it here.")

# Footer with connection status
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.session_state.db_connected:
        st.success("🟢 Database Connected")
    else:
        st.warning("🟡 Database Not Connected")

with col2:
    if st.session_state.schema_info:
        st.success("🟢 Schema Loaded")
    else:
        st.warning("🟡 No Schema Information")

with col3:
    if st.session_state.generated_sql:
        st.success("🟢 SQL Ready")
    else:
        st.info("🔵 Waiting for Query")

# Schema preview
if st.session_state.schema_info:
    with st.expander("📋 View Current Schema"):
        st.text(st.session_state.schema_info)

# Help section
with st.expander("❓ Help & Tips"):
    st.markdown("""
    ### How to use:
    1. **Configure Database**: Fill in your database connection details in the sidebar
    2. **Extract Schema**: Click "Auto-Extract Schema" or manually enter your schema
    3. **Ask Question**: Enter your query in natural language
    4. **Generate SQL**: Click "Generate SQL" to create the query
    5. **Execute**: Run the query with auto-correction enabled
    
    ### Features:
    - **Auto-correction**: If a query fails, the system will automatically try to fix it
    - **Multiple attempts**: Up to 3 correction attempts for each query
    - **Schema detection**: Automatically extract schema from your database
    - **Export results**: Download query results as CSV
    
    ### Supported Databases:
    - SQLite
    - MySQL
    - PostgreSQL  
    - MongoDB (basic support)
    
    ### Tips for better results:
    - Be specific in your natural language queries
    - Mention exact column names when known
    - Use clear time references (e.g., "last 30 days", "this year")
    - Provide complete schema information for best results
    """)