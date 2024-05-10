import os
import re
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

""" Function to parse deployment logs and return a DataFrame""" 
def parse_deployment_logs(log_dir):
    data = []
    for log_file in os.listdir(log_dir):
        with open(os.path.join(log_dir, log_file), 'r') as file:
            content = file.read()
            operator_info = re.search(r'Operator: (.+) from IP (.+)', content)
            if not operator_info:
                print(f"Missing operator information in file {log_file}")
                continue
            
            operator = operator_info.group(1)
            operator_ip = operator_info.group(2)
            
            deployment_blocks = content.split('--------------------------------------------------')
            
            for block in deployment_blocks:
                if not block.strip():
                    continue

                deployment_start = re.search(r'Deployment start: (.+)', block)
                deployment_end = re.search(r'Deployment end: (.+)', block)
                device = re.search(r'Device: (.+) \((.+)\)', block)
                result = re.search(r'Deployment result: (.+)', block)
                activation_status = re.search(r'Activation status: (.+)', block)
                generated_config = re.search(r'Generated config file: (.+)', block)
                
                missing_fields = []
                if not deployment_start:
                    missing_fields.append('deployment_start')
                if not deployment_end:
                    missing_fields.append('deployment_end')
                if not device:
                    missing_fields.append('device')
                if not result:
                    missing_fields.append('result')
                if not activation_status:
                    missing_fields.append('activation_status')
                if not generated_config:
                    missing_fields.append('generated_config')
                
                if missing_fields:
                    print(f"Missing fields {missing_fields} in block: {block.strip()[:100]}...")
                    continue
                
                try:
                    start_time = datetime.datetime.strptime(deployment_start.group(1), '%Y-%m-%d %H:%M:%S')
                    end_time = datetime.datetime.strptime(deployment_end.group(1), '%Y-%m-%d %H:%M:%S')
                    duration = (end_time - start_time).total_seconds()
                    
                    data.append({
                        'operator': operator,
                        'operator_ip': operator_ip,
                        'device': device.group(1),
                        'device_type': device.group(2),
                        'result': result.group(1),
                        'start_time': start_time,
                        'end_time': end_time,
                        'activation_status': activation_status.group(1),
                        'template': generated_config.group(1),
                        'duration': duration
                    })
                except ValueError as e:
                    print(f"Error parsing dates in block: {block.strip()[:100]}: {e}")
    
    return pd.DataFrame(data)

""" Function to generate PDF report """
def generate_pdf_report(data, timeframe, output_file):
    if data.empty:
        print("No data to generate report.")
        return

    doc = SimpleDocTemplate(output_file, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    story.append(Paragraph('Deployment Report', styles['Title']))
    story.append(Spacer(1, 12))
    
    # Timeframe
    story.append(Paragraph(f'Timeframe: {timeframe}', styles['Heading2']))
    story.append(Spacer(1, 12))
    
    # Weekly activations
    this_week = data[data['start_time'] >= (datetime.datetime.now() - datetime.timedelta(days=7))]
    weekly_activations = len(this_week)
    story.append(Paragraph(f'Weekly Activations: {weekly_activations}', styles['Heading2']))
    story.append(Spacer(1, 12))
    
    # Monthly activations
    this_month = data[data['start_time'] >= (datetime.datetime.now() - datetime.timedelta(days=30))]
    monthly_activations = len(this_month)
    story.append(Paragraph(f'Monthly Activations: {monthly_activations}', styles['Heading2']))
    story.append(Spacer(1, 12))

    # Add charts
    add_charts(data, story)

    # Deployment counts by device
    device_counts = data['device'].value_counts().reset_index()
    device_counts.columns = ['Device', 'Count']
    story.append(Paragraph('Deployments by Device', styles['Heading2']))
    device_table = Table([device_counts.columns.tolist()] + device_counts.values.tolist())
    story.append(device_table)
    story.append(Spacer(1, 12))
    
    # Deployment outcomes
    outcome_counts = data['result'].value_counts().reset_index()
    outcome_counts.columns = ['Result', 'Count']
    story.append(Paragraph('Deployment Outcomes', styles['Heading2']))
    outcome_table = Table([outcome_counts.columns.tolist()] + outcome_counts.values.tolist())
    story.append(outcome_table)
    story.append(Spacer(1, 12))
    
    # Deployment scenarios
    scenario_counts = data['activation_status'].value_counts().reset_index()
    scenario_counts.columns = ['Scenario', 'Count']
    story.append(Paragraph('Deployment Scenarios', styles['Heading2']))
    scenario_table = Table([scenario_counts.columns.tolist()] + scenario_counts.values.tolist())
    story.append(scenario_table)
    story.append(Spacer(1, 12))
    
    # Average deployment times
    avg_times = data.groupby('activation_status')['duration'].mean().reset_index()
    avg_times.columns = ['Scenario', 'Average Time (s)']
    story.append(Paragraph('Average Deployment Times', styles['Heading2']))
    avg_time_table = Table([avg_times.columns.tolist()] + avg_times.values.tolist())
    story.append(avg_time_table)
    story.append(Spacer(1, 12))
    
    # Jinja2 template usage
    template_counts = data['template'].value_counts().reset_index()
    template_counts.columns = ['Template', 'Count']
    story.append(Paragraph('Jinja2 Template Usage', styles['Heading2']))
    template_table = Table([template_counts.columns.tolist()] + template_counts.values.tolist())
    story.append(template_table)
    story.append(Spacer(1, 12))
    
    # Build PDF
    doc.build(story)

""" Function to add charts to the PDF report """
def add_charts(data, story):
    if data.empty:
        print("No data available to plot charts.")
        return

    # Weekly activations chart
    weekly_data = data[data['start_time'] >= (datetime.datetime.now() - datetime.timedelta(days=7))]
    weekly_counts = weekly_data['start_time'].dt.date.value_counts().sort_index()
    if not weekly_counts.empty:
        plt.figure(figsize=(10, 6))
        weekly_counts.plot(kind='bar', color='skyblue')
        plt.title('Weekly Activations')
        plt.xlabel('Date')
        plt.ylabel('Count')
        plt.tight_layout()
        weekly_chart = 'weekly_activations.png'
        plt.savefig(weekly_chart)
        plt.close()
        story.append(Image(weekly_chart, 6 * inch, 4 * inch))
        story.append(Spacer(1, 12))

    # Monthly activations chart
    monthly_data = data[data['start_time'] >= (datetime.datetime.now() - datetime.timedelta(days=30))]
    monthly_counts = monthly_data['start_time'].dt.date.value_counts().sort_index()
    if not monthly_counts.empty:
        plt.figure(figsize=(10, 6))
        monthly_counts.plot(kind='bar', color='skyblue')
        plt.title('Monthly Activations')
        plt.xlabel('Date')
        plt.ylabel('Count')
        plt.tight_layout()
        monthly_chart = 'monthly_activations.png'
        plt.savefig(monthly_chart)
        plt.close()
        story.append(Image(monthly_chart, 6 * inch, 4 * inch))
        story.append(Spacer(1, 12))

    # Deployment outcomes chart
    outcome_counts = data['result'].value_counts()
    if not outcome_counts.empty:
        plt.figure(figsize=(10, 6))
        outcome_counts.plot(kind='pie', autopct='%1.1f%%', colors=['green', 'red'], labels=outcome_counts.index)
        plt.title('Deployment Outcomes')
        plt.tight_layout()
        outcomes_chart = 'deployment_outcomes.png'
        plt.savefig(outcomes_chart)
        plt.close()
        story.append(Image(outcomes_chart, 6 * inch, 4 * inch))
        story.append(Spacer(1, 12))

if __name__ == "__main__":
    log_dir = 'audit_logs'
    report_dir = 'reports'
    
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    
    timeframe = datetime.datetime.now().strftime('%d-%m-%Y')
    output_file = os.path.join(report_dir, f'customer_deployment_report_{timeframe}.pdf')
    
    data = parse_deployment_logs(log_dir)
    
    print(data.head())
    
    generate_pdf_report(data, timeframe, output_file)
    
    print(f'PDF report generated: {output_file}')
