#!/usr/bin/env python3
# <!--- Imports --->
from data.workflow import extract_data, print_table
from log import info

# <!--- Main Application Workflow --->
if __name__ == "__main__":
    info("Starting...")
    # Parse arguments
    # Make sure the data is reachable
    table_header, table_body = extract_data()
    print_table(table_header, table_body)
    # Execute interface
