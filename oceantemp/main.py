#!/usr/bin/env python3
# <!--- Imports --->
from data.workflow import extract_data, print_table
from log import info

# <!--- Main Application Workflow --->
if __name__ == "__main__":
    info("Starting...")
    # Parse arguments
    # Make sure the data is reachable
    table = extract_data()
    print_table(table[0], table[1])
    # Execute interface
