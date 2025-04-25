import psycopg2

connection = None
cur = None
conn = None # Initialize conn here as well, potentially used in finally

def search_table(table_name, cur):
    """Fetch and display all rows from the given table."""
    # It's generally safer to use parameter substitution for table names too,
    # but psycopg2 doesn't support it directly. Be *very* careful if
    # `table_name` comes from user input without strict validation.
    # Here, it's derived from a limited set of choices, which is safer.
    cur.execute(f"SELECT * FROM {table_name};")
    rows = cur.fetchall()
    if not rows:
        print(f"No records found in {table_name}.")
        return []
    print(f"\nAll records in {table_name}:")
    for row in rows:
        print(row)
    return rows

def get_record_by_id(table_name, record_id, cur):
    """Fetch a single row by id (returns a tuple or None)."""
    # Ensure table_name is safe
    if table_name not in ('companies', 'employees'):
        print("Error: Invalid table name.")
        return None
    cur.execute(
        f"SELECT * FROM {table_name} WHERE id = %s;",
        (record_id,)
    )
    return cur.fetchone()

# --- Corrected Function Definitions ---
def createNewEntry(table_name, cur, conn): # Added 'conn'
# first it should ask if this is a new entry for employees or companies
# from choice then we can present insert for employees or companies
# Commit changes at the end
    if table_name not in ('companies', 'employees'):
        print("Error: Invalid table name for creation.")
        return

    if table_name == 'companies':
        print("\nEnter details for the new Company:")
        name       = input("  Company name: ").strip()
        industry   = input("  Industry: ").strip()
        hq         = input("  Headquarters: ").strip()
        founded    = input("  Founded date (YYYY-MM-DD): ").strip()
        website    = input("  Website URL: ").strip()
        cur.execute(
            """
            INSERT INTO companies
              (name, industry, headquarters, founded_date, website)
            VALUES (%s,%s,%s,%s,%s);
            """,
            (name, industry, hq, founded, website)
        )
    else:  # employees
        print("\nEnter details for the new Employee:")
        company_id = input("  Company ID: ").strip()
        first      = input("  First name: ").strip()
        last       = input("  Last name: ").strip()
        email      = input("  Email: ").strip()
        title      = input("  Job title: ").strip()
        hire_date  = input("  Hire date (YYYY-MM-DD): ").strip()
        salary     = input("  Salary (e.g. 55000.00): ").strip()
        cur.execute(
            """
            INSERT INTO employees
              (company_id, first_name, last_name, email, job_title, hire_date, salary)
            VALUES (%s,%s,%s,%s,%s,%s,%s);
            """,
            (company_id, first, last, email, title, hire_date, salary)
        )
    conn.commit()
    print("✅ Insert successful.")


def updateTables(table_name, cur, conn): # Added 'conn'
# should ask what does the user want to update
# based on that it should do a search on the table selected
# and then asked what item it wants to update
# Commit changes at the end
    if table_name not in ('companies', 'employees'):
        print("Error: Invalid table name for update.")
        return

    rows = search_table(table_name, cur)
    if not rows:
        return

    # 2) Choose record
    record_id = input(f"\nEnter the ID of the {table_name[:-1]} to update: ").strip()
    # Basic check if record_id is a digit
    if not record_id.isdigit():
         print("Invalid ID. Please enter a number.")
         return

    # Check if the record exists before attempting update
    record = get_record_by_id(table_name, record_id, cur)
    if not record:
        print(f"No {table_name[:-1]} found with ID {record_id}.")
        return


    # 3) Choose column
    #   (In a real app you might load columns dynamically; here we hardcode a few)
    if table_name == 'companies':
        cols = ['name','industry','headquarters','founded_date','website']
    else: # employees
        cols = ['company_id','first_name','last_name','email','job_title','hire_date','salary','is_active'] # added is_active based on likely employee table

    print("\nWhich field to update?")
    for i,col in enumerate(cols, start=1):
        print(f"  {i}) {col}")
    col_choice_str = input("Enter number: ").strip()
    if not col_choice_str.isdigit() or not (1 <= int(col_choice_str) <= len(cols)):
        print("Invalid column choice.")
        return

    col_choice = int(col_choice_str) - 1
    col_name   = cols[col_choice]

    # 4) New value
    new_val = input(f"New value for {col_name}: ").strip()

    # 5) Execute UPDATE
    # Be careful with column names coming from user input, ensure they are valid table columns
    # A safer approach would involve checking col_name against a hardcoded list of valid columns
    try:
        cur.execute(
            f"UPDATE {table_name} SET {col_name} = %s, updated_at = now() WHERE id = %s;",
            (new_val, record_id)
        )
        conn.commit()
        print("✅ Update successful.")
    except Exception as e:
        conn.rollback() # Rollback on error
        print(f"Error updating record: {e}")


def deleteEntry(table_name, cur, conn): # Added 'conn'
# it should ask what does the user want to delete from
# then display the table and ask what entry to delete
# Commit changes at the end
    if table_name not in ('companies', 'employees'):
        print("Error: Invalid table name for deletion.")
        return

    # 1) Show existing
    rows = search_table(table_name, cur)
    if not rows:
        return

    # 2) Choose record
    record_id = input(f"\nEnter the ID of the {table_name[:-1]} to delete: ").strip()
    # Basic check if record_id is a digit
    if not record_id.isdigit():
         print("Invalid ID. Please enter a number.")
         return

    # Check if the record exists before attempting deletion
    record = get_record_by_id(table_name, record_id, cur)
    if not record:
        print(f"No {table_name[:-1]} found with ID {record_id}.")
        return


    # 3) Confirm
    print(f"Are you sure you want to delete the following record?")
    print(record)
    confirm = input(f"Type 'yes' to confirm deletion of id={record_id}: ").strip().lower()
    if confirm != 'yes':
        print("❌ Deletion cancelled.")
        return

    # 4) Execute DELETE
    try:
        cur.execute(
            f"DELETE FROM {table_name} WHERE id = %s;",
            (record_id,)
        )
        conn.commit()
        print("✅ Deletion successful.")
    except Exception as e:
        conn.rollback() # Rollback on error
        print(f"Error deleting record: {e}")


def main():
     # ask user what will he like to do: create a new company or employee,
    # update an existing company or employee,
    # delete a current employee or company,
    # or just search an existing company or employee

    global conn, cur # Declare global to use the connection/cursor in finally block outside try

    try:
            conn = psycopg2.connect(database="management")
            cur  = conn.cursor()

            action_prompt = """
What would you like to do?
  1) Create a new record
  2) Update an existing record
  3) Delete a record
  4) Search for a record

Enter the number of your choice: """
            table_prompt = """
Which table?
  1) Company
  2) Employee

Enter the number of your choice: """

            choice = input(action_prompt).strip()
            if choice not in ('1','2','3','4'):
                 print("Invalid action choice.")
                 return # Exit main if action is invalid

            tbl_choice = input(table_prompt).strip()
            if tbl_choice == '1':
                table_name = 'companies'
            elif tbl_choice == '2':
                table_name = 'employees'
            else:
                 print("Invalid table choice.")
                 return # Exit main if table is invalid


            # --- Pass 'conn' to the functions ---
            if choice == '1':
                createNewEntry(table_name, cur, conn)
            elif choice == '2':
                updateTables(table_name, cur, conn)
            elif choice == '3':
                deleteEntry(table_name, cur, conn)
            elif choice == '4':
                # reuse your existing search flow
                all_rows = search_table(table_name, cur)
                if all_rows:
                    selected_id = input(f"\nEnter the ID of the {table_name[:-1]} to view: ").strip()
                    # Basic check if selected_id is a digit
                    if not selected_id.isdigit():
                         print("Invalid ID. Please enter a number.")
                    else:
                        record = get_record_by_id(table_name, selected_id, cur)
                        print("\nYou selected:\n", record if record else "Not found.")

    except Exception as error:
            # Rollback any pending transaction if an error occurs
            if conn:
                conn.rollback()
            print("Error:", error)
    finally:
        # Ensure cursor and connection are closed even if errors occur
        if cur is not None:
            cur.close()
        if conn is not None: # Use conn here, not connection
            conn.close()


if __name__ == "__main__": # Standard practice to call main
    main()