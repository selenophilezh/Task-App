import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime

# Database setup
conn = sqlite3.connect("task_tracker_dummy_v2.db")
cursor = conn.cursor()

# Tabs for app functionality
tab1, tab2, tab3 = st.tabs(["Add Task", "View Tasks", "Edit Task"])

# 1. Add Task
with tab1:
    st.header("Add New Task")
    task_name = st.text_input("Task Name")
    task_date = st.date_input("Date", value=datetime.now())
    analyst = st.text_input("Analyst")
    supervisor = st.selectbox("Supervisor", ["LHH", "MHS", "MSS", "LWL", "ALAK"])
    status = st.selectbox("Status", ["Pending Analyst", "Pending Supervisor", "Pending DD", "Completed"])
    workfile = st.text_input("Workfile")
    path = st.text_input("Path")
    remark = st.text_area("Remark")

    if st.button("Add Task"):
        cursor.execute('''
            INSERT INTO tasks (task_name, task_date, analyst, supervisor, status, workfile, path, remark)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (task_name, task_date, analyst, supervisor, status, workfile, path, remark))
        conn.commit()
        st.success("Task added successfully!")

# 2. View Tasks
with tab2:
    st.header("View Tasks")

    # Load data into pandas DataFrame
    df = pd.read_sql_query("SELECT * FROM tasks", conn)

    # Filters
    filter_analyst = st.text_input("Filter by Analyst")
    filter_supervisor = st.selectbox("Filter by Supervisor", ["All"] + ["LHH", "MHS", "MSS", "LWL", "ALAK"])
    filter_status = st.selectbox("Filter by Status", ["All", "Pending Analyst", "Pending Supervisor", "Pending DD", "Completed"])

    # Apply filters
    if filter_analyst:
        df = df[df["analyst"].str.contains(filter_analyst, case=False, na=False)]
    if filter_supervisor != "All":
        df = df[df["supervisor"] == filter_supervisor]
    if filter_status != "All":
        df = df[df["status"] == filter_status]

    st.write("Filtered Results:")
    st.dataframe(df)

# 3. Edit Task
with tab3:
    st.header("Edit Task")

    # Input Task ID for search
    task_id_to_edit = st.text_input("Enter Task ID to Search")

    # Check if the Task ID is provided
    if task_id_to_edit:
        try:
            # Convert input to integer and fetch the task details
            selected_id = int(task_id_to_edit)
            task_to_edit = pd.read_sql_query(f"SELECT * FROM tasks WHERE id = {selected_id}", conn)

            if not task_to_edit.empty:
                # Pre-fill fields with current data
                task_row = task_to_edit.iloc[0]  # Get the first (and only) row
                edit_task_name = st.text_input("Task Name", value=task_row["task_name"], key="edit_task_name")
                edit_task_date = st.date_input("Date", value=datetime.strptime(task_row["task_date"], '%Y-%m-%d').date(), key="edit_task_date")
                edit_analyst = st.text_input("Analyst", value=task_row["analyst"], key="edit_analyst")
                edit_supervisor = st.selectbox("Supervisor", ["LHH", "MHS", "MSS", "LWL", "ALAK"], 
                                               index=["LHH", "MHS", "MSS", "LWL", "ALAK"].index(task_row["supervisor"]), key="edit_supervisor")
                edit_status = st.selectbox("Status", ["Pending Analyst", "Pending Supervisor", "Pending DD", "Completed"], 
                                           index=["Pending Analyst", "Pending Supervisor", "Pending DD", "Completed"].index(task_row["status"]), key="edit_status")
                edit_workfile = st.text_input("Workfile", value=task_row["workfile"], key="edit_workfile")
                edit_path = st.text_input("Path", value=task_row["path"], key="edit_path")
                edit_remark = st.text_area("Remark", value=task_row["remark"], key="edit_remark")

                # Update Task
                if st.button("Update Task"):
                    cursor.execute('''
                        UPDATE tasks
                        SET task_name = ?, task_date = ?, analyst = ?, supervisor = ?, status = ?, workfile = ?, path = ?, remark = ?
                        WHERE id = ?
                    ''', (edit_task_name, edit_task_date, edit_analyst, edit_supervisor, edit_status, edit_workfile, edit_path, edit_remark, selected_id))
                    conn.commit()
                    st.success("Task updated successfully!")
            else:
                st.warning(f"No task found with ID {selected_id}!")

        except ValueError:
            st.error("Please enter a valid numeric Task ID!")



# Close the database connection
conn.close()
