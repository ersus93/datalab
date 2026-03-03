#!/usr/bin/env python3
"""
Access Database Analyzer for DataLab Migration
Analyzes RM2026.accdb (frontend) and RM2026_be.accdb (backend)
"""

import pyodbc
import pandas as pd
import json
from datetime import datetime

def get_connection_string(db_path):
    """Create connection string for Access database."""
    return (
        r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
        f'DBQ={db_path};'
    )

def connect_to_access(db_path):
    """Connect to Access database and return connection."""
    conn_str = get_connection_string(db_path)
    try:
        conn = pyodbc.connect(conn_str, timeout=10)
        return conn
    except pyodbc.Error as e:
        print(f"Error connecting to {db_path}: {e}")
        return None

def get_tables(conn):
    """Get list of all tables in the database."""
    cursor = conn.cursor()
    tables = []
    for row in cursor.tables(tableType='TABLE'):
        table_name = row.table_name
        # Skip system tables
        if not table_name.startswith('MSys') and not table_name.startswith('~'):
            tables.append(table_name)
    return sorted(tables)

def get_table_schema(conn, table_name):
    """Get schema information for a table."""
    cursor = conn.cursor()
    columns = []
    
    # Get column information
    for row in cursor.columns(table=table_name):
        columns.append({
            'name': row.column_name,
            'data_type': row.type_name,
            'nullable': row.is_nullable == 'YES',
            'default': row.column_def,
            'ordinal': row.ordinal_position
        })
    
    # Get primary key
    pk_columns = []
    try:
        for row in cursor.primaryKeys(table=table_name):
            pk_columns.append(row.column_name)
    except:
        pass
    
    # Get indexes
    indexes = []
    try:
        for row in cursor.statistics(table=table_name):
            if row.index_name:
                indexes.append({
                    'name': row.index_name,
                    'column': row.column_name,
                    'unique': not row.non_unique
                })
    except:
        pass
    
    return {
        'columns': columns,
        'primary_key': pk_columns,
        'indexes': indexes
    }

def get_row_count(conn, table_name):
    """Get row count for a table."""
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT COUNT(*) FROM [{table_name}]")
        return cursor.fetchone()[0]
    except:
        return -1

def get_sample_data(conn, table_name, limit=5):
    """Get sample data from a table."""
    try:
        query = f"SELECT TOP {limit} * FROM [{table_name}]"
        df = pd.read_sql(query, conn)
        return df.to_dict('records')
    except Exception as e:
        return {'error': str(e)}

def get_relationships(conn):
    """Get foreign key relationships."""
    cursor = conn.cursor()
    relationships = []
    try:
        for row in cursor.foreignKeys():
            relationships.append({
                'fk_table': row.fk_table_name,
                'fk_column': row.fk_column_name,
                'pk_table': row.pk_table_name,
                'pk_column': row.pk_column_name,
                'constraint': row.fk_name
            })
    except:
        pass
    return relationships

def get_queries(conn):
    """Get list of queries (views) in the database."""
    cursor = conn.cursor()
    queries = []
    try:
        for row in cursor.tables(tableType='VIEW'):
            query_name = row.table_name
            if not query_name.startswith('MSys'):
                queries.append(query_name)
    except:
        pass
    return queries

def analyze_database(db_path, db_name):
    """Complete analysis of an Access database."""
    print(f"\n{'='*80}")
    print(f"ANALYZING: {db_name}")
    print(f"PATH: {db_path}")
    print(f"{'='*80}\n")
    
    conn = connect_to_access(db_path)
    if not conn:
        print(f"Failed to connect to {db_name}")
        return None
    
    analysis = {
        'database_name': db_name,
        'path': db_path,
        'analysis_date': datetime.now().isoformat(),
        'tables': {},
        'relationships': [],
        'queries': []
    }
    
    # Get all tables
    print("Discovering tables...")
    tables = get_tables(conn)
    print(f"Found {len(tables)} tables\n")
    
    # Analyze each table
    for table_name in tables:
        print(f"Analyzing table: {table_name}")
        
        schema = get_table_schema(conn, table_name)
        row_count = get_row_count(conn, table_name)
        sample_data = get_sample_data(conn, table_name)
        
        analysis['tables'][table_name] = {
            'schema': schema,
            'row_count': row_count,
            'sample_data': sample_data
        }
        
        print(f"  - Columns: {len(schema['columns'])}")
        print(f"  - Rows: {row_count}")
        print(f"  - Primary Key: {schema['primary_key']}")
    
    # Get relationships
    print("\nDiscovering relationships...")
    relationships = get_relationships(conn)
    analysis['relationships'] = relationships
    print(f"Found {len(relationships)} relationships")
    for rel in relationships:
        print(f"  - {rel['fk_table']}.{rel['fk_column']} -> {rel['pk_table']}.{rel['pk_column']}")
    
    # Get queries
    print("\nDiscovering queries...")
    queries = get_queries(conn)
    analysis['queries'] = queries
    print(f"Found {len(queries)} queries/views")
    for query in queries:
        print(f"  - {query}")
    
    conn.close()
    return analysis

def generate_summary_report(analysis_fe, analysis_be):
    """Generate a comprehensive summary report."""
    print("\n" + "="*80)
    print("MIGRATION ANALYSIS SUMMARY")
    print("="*80)
    
    # Frontend analysis
    if analysis_fe:
        print("\n## FRONTEND DATABASE (RM2026.accdb)")
        print(f"Tables: {len(analysis_fe['tables'])}")
        print(f"Queries/Views: {len(analysis_fe['queries'])}")
        print(f"Relationships: {len(analysis_fe['relationships'])}")
        
        print("\nTables in Frontend:")
        for table_name, table_info in sorted(analysis_fe['tables'].items()):
            cols = len(table_info['schema']['columns'])
            rows = table_info['row_count']
            print(f"  - {table_name}: {cols} columns, {rows} rows")
    
    # Backend analysis
    if analysis_be:
        print("\n## BACKEND DATABASE (RM2026_be.accdb)")
        print(f"Tables: {len(analysis_be['tables'])}")
        print(f"Queries/Views: {len(analysis_be['queries'])}")
        print(f"Relationships: {len(analysis_be['relationships'])}")
        
        print("\nTables in Backend:")
        for table_name, table_info in sorted(analysis_be['tables'].items()):
            cols = len(table_info['schema']['columns'])
            rows = table_info['row_count']
            pk = table_info['schema']['primary_key']
            print(f"  - {table_name}: {cols} columns, {rows} rows, PK: {pk}")
    
    # Migration recommendations
    print("\n## MIGRATION RECOMMENDATIONS")
    print("1. Data Migration Priority:")
    
    if analysis_be:
        high_priority = []
        medium_priority = []
        low_priority = []
        
        for table_name, table_info in analysis_be['tables'].items():
            rows = table_info['row_count']
            if rows > 1000:
                high_priority.append((table_name, rows))
            elif rows > 100:
                medium_priority.append((table_name, rows))
            else:
                low_priority.append((table_name, rows))
        
        print("\n   HIGH PRIORITY (Large tables):")
        for name, rows in sorted(high_priority, key=lambda x: -x[1]):
            print(f"     - {name}: {rows} rows")
        
        print("\n   MEDIUM PRIORITY (Medium tables):")
        for name, rows in sorted(medium_priority, key=lambda x: -x[1]):
            print(f"     - {name}: {rows} rows")
        
        print("\n   LOW PRIORITY (Small tables):")
        for name, rows in sorted(low_priority, key=lambda x: -x[1]):
            print(f"     - {name}: {rows} rows")

def save_detailed_report(analysis_fe, analysis_be, filename='access_analysis_report.json'):
    """Save detailed analysis to JSON file."""
    report = {
        'analysis_date': datetime.now().isoformat(),
        'frontend': analysis_fe,
        'backend': analysis_be
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\nDetailed report saved to: {filename}")

def main():
    # Database paths
    fe_path = r'C:\Users\ernes\datalab\utiles\RM2026.accdb'
    be_path = r'C:\Users\ernes\datalab\utiles\RM2026_be.accdb'
    
    print("="*80)
    print("DATALAB ACCESS DATABASE ANALYZER")
    print("="*80)
    
    # Analyze frontend
    analysis_fe = analyze_database(fe_path, "Frontend (RM2026.accdb)")
    
    # Analyze backend
    analysis_be = analyze_database(be_path, "Backend (RM2026_be.accdb)")
    
    # Generate summary
    generate_summary_report(analysis_fe, analysis_be)
    
    # Save detailed report
    if analysis_fe or analysis_be:
        save_detailed_report(analysis_fe, analysis_be)
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)

if __name__ == '__main__':
    main()
