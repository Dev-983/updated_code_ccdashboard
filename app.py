from flask import Flask, render_template,request,jsonify
import pandas as pd
# import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import time
from flask_cors import CORS
from collections import Counter
import os
import json


file_path = 'https://bpxai-my.sharepoint.com/personal/manas_shalgar_bpx_ai/_layouts/15/download.aspx?share=EW7IZR3VH_ZDp_rhgbv9GlQBowPIosXVpfUCXsAUTYNJ8Q'
#file_path="Mockup_Dashboard_cleandatav2.xlsx"
app = Flask(__name__, static_folder='static')
CORS(app)

DATA_FILE = 'boxes_data.json'
##################################################################
#################################################################

@app.route('/save_data2', methods=['POST'])
def save_data2_study():
    data = request.json
    with open('data.txt', 'w') as f:
        json.dump(data, f)
    return jsonify({'status': 'success'})

@app.route('/load_data2', methods=['GET'])
def load_data2_study():
    try:
        with open('data.txt', 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify([]) 



###########################################################
######################################################
def main_all_data():
    #file_path = 'Mockup_Dashboard_cleandatav2.xlsx'

# Read the data from each sheet
    df_sheet_name4 = pd.read_excel(file_path, sheet_name='Total Risk')
    df_sheet_name = pd.read_excel(file_path, sheet_name='Financials Data')
    df_sheet_name3 = pd.read_excel(file_path, sheet_name='PM Defined Status')
    df_sheet_name2 = pd.read_excel(file_path, sheet_name='Project Status')
    df_sheet_name5 = pd.read_excel(file_path, sheet_name='Issues')
    df_sheet_name6 = pd.read_excel(file_path, sheet_name='Project Data')

    project_dict = {}
# Process data from 'Total Risk' sheet
    for index, row in df_sheet_name4.iterrows():
        project_id = row['Project ID']
        project_dict[project_id] = {
            'Pace': row['Pace'],
            'Execution': row['Execution'],
            'Resources': row['Resources']
        }
    # Process data from 'Financials Data' sheet
    for index, row in df_sheet_name.iterrows():
        project_id = row['Project ID']
        if project_id not in project_dict:
            project_dict[project_id] = {}
        project_dict[project_id].update({
            'LT_Budget': row['LT_Budget'],
            'LT_Budget_Cashout': row['Cash Out'],
            'LT_Budget_Accrual': row['Accrual Unit'] * row['Accrual #'],
            'DateDiff': row['Accrual #'],
            'milestonecompletion_per':row['% Completed'],
            'actualprogess':row['Total Completed'],
            'Totalmilestone':row['Total Possible'],
            'Q1':row['Q1'],'Q2':(row['Q2']-row['Q1']),
            'Q3':(row['Q3']-row['Q2']),'Q4':(row['Q4']-row['Q3'])
        })

# Process data from 'PM Defined Status' sheet
    for index, row in df_sheet_name3.iterrows():
        project_id = row['Project ID']
        if project_id not in project_dict:
            project_dict[project_id] = {}
        project_dict[project_id].update({
            'Overall': row['OVERALL'],
            'Scope': row['Scope'],
            'Schedule': row['Schedule'],
            'Budget': row['Budget']
        })
    #print(f"After PM Defined Status: {project_id} -> {project_dict[project_id]}")

# Process final status data
    for index, row in df_sheet_name2.iterrows():
        project_id = row['Project ID']
        if project_id not in project_dict:
            project_dict[project_id] = {}
        project_dict[project_id].update({
        'Status': row['Project Status']
    })
    
#Process Issues Data
    for index, row in df_sheet_name5.iterrows():
        project_id=row['Project ID']
        if project_id not in project_dict:
            project_dict[project_id] = {}
        project_dict[project_id].update({
            'IssuesCount': row['Count'],
            'Issues': row['Lookup']
        })

#Project Data
    for index, row in df_sheet_name6.iterrows():
        project_id=row['Project ID']
        if project_id not in project_dict:
            project_dict[project_id] = {}
        project_dict[project_id].update({
            'startdate': row['Start Date'],
            'enddate': row['Due Date'],
            'type': row['Type']
        })

    def is_nan(value):
        return value != value
# Remove entries with nan keys
    cleaned_data = {k: v for k, v in project_dict.items() if not (is_nan(k) or any(is_nan(vv) for vv in v.values()))}

    return cleaned_data

################################ PAGE 2 ############################  
@app.route('/testtable')
def testtable():
    project_dict = main_all_data()
    return jsonify({'result': project_dict})

#################################################################
def page2_table2():
    df_sheet_name = pd.read_excel(file_path, sheet_name='Financials Data')
    tab2 = {}
    for index, row in df_sheet_name.iterrows():
        project_id = row['Project ID']
        if project_id not in tab2:
            tab2[project_id] = {}
        tab2[project_id].update({
            'Q1':row['Q1'],'Q2':(row['Q2']-row['Q1']),
            'Q3':(row['Q3']-row['Q2']),'Q4':(row['Q4']-row['Q3'])
        })
    return tab2
def page2_table1():
    df_sheet_name = pd.read_excel(file_path, sheet_name='Project Data')
    df_sheet_name3 = pd.read_excel(file_path, sheet_name='PM Defined Status')

    projectdata={}
    for index, row in df_sheet_name3.iterrows():
        project_id = row['Project ID']
        if project_id not in projectdata:
            projectdata[project_id] = {}
        projectdata[project_id].update({
            'Overall': row['OVERALL'],
            'Scope': row['Scope'],
            'Schedule': row['Schedule'],
            'Budget': row['Budget']
        })

    
    for index, row in df_sheet_name.iterrows():
        project_id=row['Project ID']
        if project_id not in projectdata:
            projectdata[project_id] = {}
        projectdata[project_id].update({
            'projectid':row['Project ID'],
            'status':row['Status'],
            'startdate':row['Start Date'],
            'duedate':row['Due Date'],
            'type':row['Type']
            })

    return projectdata
###################################################################
####################################################################
def indexpage_top():
	df_budget_sheet = pd.read_excel(file_path, sheet_name='Gauges')
	budget_total_value = round(df_budget_sheet['Total Budget'].sum(), 2)
	budget_current_value = round(df_budget_sheet['Current Spend'].sum(), 2)
	status_current = round(df_budget_sheet['Current Status'].sum(),2)
	status_total = 100
	return budget_total_value,budget_current_value,status_current
####################################################################
##################### TABLE 2 DATA IN INDEX MAIN PAGE #######################
def financedata_indexpage():
    df_sheet_name = pd.read_excel(file_path, sheet_name='Financials Data')
    financedata={}
    for index, row in df_sheet_name.iterrows():
        project_id=row['Project ID']
        if project_id not in financedata:
            financedata[project_id] = {}
        financedata[project_id].update({
            'projectid':row['Project ID'],
            'milestone':round((row['% Completed']*100),2),
            'recentdate':row['MostRecentDate'],

            })
    return financedata

############################### END   #################
#############################  TABLE 1 DATA IN INDEX MAIN PAGE #############################
#@app.route('/projectdata')
def indexpage_projectdata():
    df_sheet_name = pd.read_excel(file_path, sheet_name='Project Data')
    projectdata={}
    for index, row in df_sheet_name.iterrows():
        project_id=row['Project ID']
        if project_id not in projectdata:
            projectdata[project_id] = {}

        projectdata[project_id].update({
            'projectid':row['Project ID'],
            'status':row['Status'],
            'startdate':row['Start Date'],
            'duedate':row['Due Date'],
            'type':row['Type']
            })
    return projectdata

#################################### END ##########################################
######################## FUNNEL CHART #########################################
@app.route('/funnel')
def funnel():
    df_sheet_name = pd.read_excel(file_path, sheet_name='Funnel')
    funnelchart={}
    for index, row in df_sheet_name.iterrows():
        project_id=row['Project Status']
        if project_id not in funnelchart:
            funnelchart[project_id] = {}
        funnelchart[project_id].update({
                'projectstatus':row['Project Status'],
                'conversion':row['Conversions']
            })
    return jsonify(funnelchart)
################## END ######################################
######################### TOP 5 AND BOTTOM 5 CASOUT V/S ACCRUAL ###################
def data_1():
    df_sheet_name2 = pd.read_excel(file_path, sheet_name='Financials Data')
    project_dict1={}
    for index, row in df_sheet_name2.iterrows():
        project_id=row['Project ID']
        if project_id not in project_dict1:
            project_dict1[project_id] = {}
        project_dict1[project_id].update({
            'projectid':row['Project ID'],
            'ltbudget': row['LT_Budget'],
            'accrual': row['Accrual Unit'] * row['Accrual #'],
            'cashout': row['Cash Out']
        })
    return project_dict1

@app.route('/top5')
def get_data1():
    project_dict1 = data_1()
    sorted_accruals = sorted(project_dict1.items(), key=lambda x: x[1]['accrual'])
    top_5_accruals = sorted_accruals[-5:]
    top_5_output = [(proj_id,details['ltbudget'] ,details['accrual'], details['cashout']) for proj_id, details in top_5_accruals]
    return jsonify(top_5_output)

@app.route('/bottom5')
def get_data2():

    project_dict1 = data_1()
    sorted_accruals = sorted(project_dict1.items(), key=lambda x: x[1]['accrual'])
    bottom_5_accruals = sorted_accruals[:5]
    bottom_5_output = [(proj_id, details['ltbudget'] , details['accrual'], details['cashout']) for proj_id, details in bottom_5_accruals]

    return jsonify(bottom_5_output)
############################### END ###########################
def milstone_gauntchart():
    
    # Read the data from the 'Financials Data' sheet
    df_sheet_name = pd.read_excel(file_path, sheet_name='Financials Data')   
    # Initialize an empty dictionary to store milestones
    milestones = {}   
    # Iterate over each row in the dataframe
    for index, row in df_sheet_name.iterrows():
        project_id = row['Project ID']       
        # Ensure the project_id exists in the dictionary
        if project_id not in milestones:
            milestones[project_id] = {}        
        # Update the dictionary with milestone data, excluding NaN and NaT values
        milestones[project_id].update({
            'm1': row['Milestone1'] if pd.notna(row['Milestone1']) else None,
            'm2': row['Milestone2'] if pd.notna(row['Milestone2']) else None,
            'm3': row['Milestone3'] if pd.notna(row['Milestone3']) else None,
            'm4': row['Milestone4'] if pd.notna(row['Milestone4']) else None,
            'm5': row['Milestone5'] if pd.notna(row['Milestone5']) else None,
            'm6': row['Milestone6'] if pd.notna(row['Milestone6']) else None,
            'm7': row['Milestone7'] if pd.notna(row['Milestone7']) else None,
            'm8': row['Milestone8'] if pd.notna(row['Milestone8']) else None,
            'm9': row['Milestone9'] if pd.notna(row['Milestone9']) else None,
            'm10': row['Milestone10'] if pd.notna(row['Milestone10']) else None
        })        
        # Remove keys with None values
        milestones[project_id] = {k: v for k, v in milestones[project_id].items() if v is not None}
    
    return milestones

########### PROJECT ACTIVITY TAB ##################
#priject activity page
@app.route('/process',methods=['GET'])
def process():
    mdata = request.args.get('data')

    project_dict = main_all_data()
    milestonedata = milstone_gauntchart()
    if mdata in project_dict:
        value = project_dict[mdata]
        value2 = milestonedata[mdata]
    else:
        print("Key not found")

    #return jsonify({'result': value})
    return jsonify({'result': value,'result2':value2})
#############################################################
@app.route('/projectactivity')
def projectActivity():
    df_sheet_name2 = pd.read_excel(file_path, sheet_name='Financials Data')
    projectid=df_sheet_name2['Project ID'].unique()
    unique_list = []
    for x in projectid:
        if x not in unique_list:
            unique_list.append(x)

    return render_template('project_activity.html',ids=unique_list)

############### END #########################################
@app.route('/project_overallscope')
def project_overallscope():
    df_sheet_name3 = pd.read_excel(file_path, sheet_name='PM Defined Status')
    project_dict = {}
# Process data from 'Total Risk' sheet
    for index, row in df_sheet_name3.iterrows():
        project_id = row['Project ID']
        project_dict[project_id] = {
        'overall': row['OVERALL'],
        'scope': row['Scope'],
        'schedule': row['Schedule'],'budget': row['Budget']
    }
    return jsonify(project_dict)

@app.route('/finance_projecttype')
def projecttype():
    df_sheet_name2 = pd.read_excel(file_path, sheet_name='Project Data')
    column_data = df_sheet_name2['Type'].tolist()
    counter = Counter(column_data)
    return jsonify(counter)
############################ FINANCEIAL TAB ROUTE #################
@app.route('/finance')
def finance():
    return render_template('financial.html')

################################# END ##########
################################ PROJECT OVERVIEW  ROUTE ###################
def risk_data():
    df_issues = pd.read_excel(file_path, sheet_name='Issues')
    issues_dict = {}
    for _, row in df_issues.iterrows():
        project_id = row['Project ID']
        issues_dict[project_id] = {
            'IssuesCount': row['Count'],
            'Issues': row['Lookup']
        }

    # Load the data from the 'Total Risk' sheet
    df_total_risk = pd.read_excel(file_path, sheet_name='Total Risk')
    project_dict = {}
    for _, row in df_total_risk.iterrows():
        project_id = row['Project ID']
        project_dict[project_id] = {
            'Pace': row['Pace'],
            'Execution': row['Execution'],
            'Resources': row['Resources']
        }

        # Update project_dict with issue data if available
        if project_id in issues_dict:
            project_dict[project_id].update(issues_dict[project_id])
        else:
            # Ensure that projects without issues have default values
            project_dict[project_id].update({
                'IssuesCount': 0,
                'Issues': 0
            })

    return project_dict
#############################################################################################
#############################################################################################
def get_project_data():

    df = pd.read_excel(file_path, sheet_name='Financials Data')
    df.fillna(0, inplace=True)

    project_dict = {}
    for _, row in df.iterrows():
        project_id = row['Project ID']
        milestones = [
            row.get('Milestone1', 0), row.get('Milestone2', 0), row.get('Milestone3', 0), row.get('Milestone4', 0),
            row.get('Milestone5', 0), row.get('Milestone6', 0), row.get('Milestone7', 0), row.get('Milestone8', 0),
            row.get('Milestone9', 0), row.get('Milestone10', 0)
        ]
        
        formatted_milestones = [
            milestone.strftime('%Y-%m-%d') if isinstance(milestone, pd.Timestamp) else milestone
            for milestone in milestones
        ]
        
        project_dict[project_id] = formatted_milestones

    temp={}
    for i , row in df.iterrows():
        ids=row['Project ID']
        temp[ids]=row['Total Possible']

    return project_dict,temp

@app.route('/project_milestone')
def projectmilestone():
    data1,data2 = get_project_data()
    return render_template('project_milestones.html',project_data=data1,totalmilestone=data2)

################################ END #################################################
############################ NOTES AND ISSUE PAGE ###################################
@app.route('/loadData', methods=['GET'])
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            data = json.load(file)
    else:
        data = []
    return jsonify(data)

@app.route('/saveData', methods=['POST'])
def save_data():
    data = request.get_json()  # Get the JSON data from the request
    try:
        # Save the data to a JSON file
        with open(DATA_FILE, 'w') as json_file:
            json.dump(data, json_file, indent=4)
        
        return jsonify({'message': 'Data saved successfully'}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@app.route('/notes_issues')
def notesissues():
    with open(DATA_FILE) as f:
        data = json.load(f)
    return render_template('notes_issues.html',data=data)



##############################################################################################
############################## PROJECT OVERVIEW PAGE##########################################
@app.route('/projectoverview')
def projectOverview():

    data = main_all_data()
    return render_template('project_overview.html',data1 =data)

############################ END ############################
@app.route('/studytimeline')
def studytimeline():
    return render_template('project_studytimeline.html')
################################## INDEX PAGE MAIN ROUTE #######################
@app.route('/')
def index():
	#data=main_all_data()
    totalbudge,currentspend,currentstatus = indexpage_top()
    data1={'a':totalbudge,'b':currentspend,'c':currentstatus}
    projectdata=indexpage_projectdata()
    financedate = financedata_indexpage()
   
    return render_template('index.html',data1=data1,data2=projectdata,data3=financedate)

if __name__ == '__main__':

    app.run(debug=True)