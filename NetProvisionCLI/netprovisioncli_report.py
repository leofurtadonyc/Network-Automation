import os
import re
import datetime
from datetime import timedelta
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors

""" Function to parse deployment logs and generate a PDF report """
def parse_deployment_logs(log_dir, verbose=False):
    data = []
    for log_file in os.listdir(log_dir):
        with open(os.path.join(log_dir, log_file), 'r') as file:
            content = file.read()
            operator_info = re.search(r'Operator: (.+) from IP (.+)', content)
            if not operator_info:
                if verbose:
                    print(f"Missing operator information in file {log_file}")
                continue

            operator = operator_info.group(1)
            operator_ip = operator_info.group(2)

            # Extract end time once for the entire log file
            end_time_match = re.search(r'Completed at: (.+)', content)
            if end_time_match:
                end_time = datetime.datetime.strptime(end_time_match.group(1), '%Y-%m-%d %H:%M:%S')
            else:
                if verbose:
                    print(f"Missing end time in file {log_file}")
                continue

            deployment_blocks = content.split('--------------------------------------------------')

            for block in deployment_blocks:
                if not block.strip():
                    continue

                duration_match = re.search(r'Duration of execution: Deployment completed in ([\d.]+) seconds', block)
                device = re.search(r'Device: (.+) \((.+)\)', block)
                result = re.search(r'Deployment result: (.+)', block)
                activation_status = re.search(r'Activation status: (.+)', block)
                generated_config = re.search(r'Generated config file: (.+)', block)

                missing_fields = []
                if not duration_match:
                    missing_fields.append('duration')
                if not device:
                    missing_fields.append('device')
                if not result:
                    missing_fields.append('result')
                if not activation_status:
                    missing_fields.append('activation_status')
                if not generated_config:
                    missing_fields.append('generated_config')

                if missing_fields:
                    if verbose:
                        print(f"Missing fields {missing_fields} in block: {block.strip()[:100]}...")
                    continue

                try:
                    duration = float(duration_match.group(1))
                    start_time = end_time - timedelta(seconds=duration)

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
                    if verbose:
                        print(f"Error parsing dates in block: {block.strip()[:100]}: {e}")

    return pd.DataFrame(data)

""" Function to generate a PDF report with deployment statistics"""
def generate_pdf_report(data, timeframe, output_file, report_dir):
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
    weekly_activations = len(this_week.drop_duplicates(subset=['end_time']))
    story.append(Paragraph(f'Weekly Activations: {weekly_activations}', styles['Heading2']))
    story.append(Spacer(1, 12))

    # Monthly activations
    this_month = data[data['start_time'] >= (datetime.datetime.now() - datetime.timedelta(days=30))]
    monthly_activations = len(this_month.drop_duplicates(subset=['end_time']))
    story.append(Paragraph(f'Monthly Activations: {monthly_activations}', styles['Heading2']))
    story.append(Spacer(1, 12))

    # Add charts
    chart_files = add_charts(data, story, report_dir)

    # Deployment counts by device
    device_counts = data['device'].value_counts().reset_index()
    device_counts.columns = ['Device', 'Count']
    story.append(Paragraph('Deployments by Device', styles['Heading2']))
    device_table = Table([device_counts.columns.tolist()] + device_counts.values.tolist(), hAlign='LEFT')
    device_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(device_table)
    story.append(Spacer(1, 12))

    # Deployment outcomes
    unique_deployments = data.drop_duplicates(subset=['end_time'])
    outcome_counts = unique_deployments['result'].value_counts().reset_index()
    outcome_counts.columns = ['Result', 'Count']
    story.append(Paragraph('Deployment Outcomes', styles['Heading2']))
    outcome_table = Table([outcome_counts.columns.tolist()] + outcome_counts.values.tolist(), hAlign='LEFT')
    outcome_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(outcome_table)
    story.append(Spacer(1, 12))

    # Deployment scenarios
    scenario_counts = unique_deployments['activation_status'].value_counts().reset_index()
    scenario_counts.columns = ['Scenario', 'Count']
    story.append(Paragraph('Deployment Scenarios', styles['Heading2']))
    scenario_table = Table([scenario_counts.columns.tolist()] + scenario_counts.values.tolist(), hAlign='LEFT')
    scenario_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(scenario_table)
    story.append(Spacer(1, 12))

    # Average deployment times
    avg_times = data.groupby('activation_status')['duration'].mean().reset_index()
    avg_times.columns = ['Scenario', 'Average Time (s)']
    story.append(Paragraph('Average Deployment Times', styles['Heading2']))
    avg_time_table = Table([avg_times.columns.tolist()] + avg_times.values.tolist(), hAlign='LEFT')
    avg_time_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(avg_time_table)
    story.append(Spacer(1, 12))

    # Jinja2 template usage
    template_counts = data['template'].value_counts().reset_index()
    template_counts.columns = ['Template', 'Count']
    story.append(Paragraph('Jinja2 Template Usage', styles['Heading2']))
    template_table = Table([template_counts.columns.tolist()] + template_counts.values.tolist(), hAlign='LEFT')
    template_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(template_table)
    story.append(Spacer(1, 12))

    # Build PDF
    doc.build(story)

    for chart_file in chart_files:
        if os.path.exists(chart_file):
            os.remove(chart_file)

""" Function to add charts to the PDF report """
def add_charts(data, story, report_dir):
    chart_files = []

    if data.empty:
        print("No data available to plot charts.")
        return chart_files

    # Weekly activations chart
    weekly_data = data[data['start_time'] >= (datetime.datetime.now() - datetime.timedelta(days=7))]
    weekly_counts = weekly_data.drop_duplicates(subset=['end_time'])['start_time'].dt.date.value_counts().sort_index()
    if not weekly_counts.empty:
        plt.figure(figsize=(10, 6))
        weekly_counts.plot(kind='bar', color='skyblue')
        plt.title('Weekly Activations')
        plt.xlabel('Date')
        plt.ylabel('Count')
        plt.tight_layout()
        weekly_chart = os.path.join(report_dir, 'weekly_activations.png')
        plt.savefig(weekly_chart)
        plt.close()
        story.append(Image(weekly_chart, 6 * inch, 4 * inch))
        story.append(Spacer(1, 12))
        chart_files.append(weekly_chart)

    # Monthly activations chart
    monthly_data = data[data['start_time'] >= (datetime.datetime.now() - datetime.timedelta(days=30))]
    monthly_counts = monthly_data.drop_duplicates(subset=['end_time'])['start_time'].dt.date.value_counts().sort_index()
    if not monthly_counts.empty:
        plt.figure(figsize=(10, 6))
        monthly_counts.plot(kind='bar', color='skyblue')
        plt.title('Monthly Activations')
        plt.xlabel('Date')
        plt.ylabel('Count')
        plt.tight_layout()
        monthly_chart = os.path.join(report_dir, 'monthly_activations.png')
        plt.savefig(monthly_chart)
        plt.close()
        story.append(Image(monthly_chart, 6 * inch, 4 * inch))
        story.append(Spacer(1, 12))
        chart_files.append(monthly_chart)

    # Deployment outcomes chart
    unique_deployments = data.drop_duplicates(subset=['end_time'])
    outcome_counts = unique_deployments['result'].value_counts()
    if not outcome_counts.empty:
        plt.figure(figsize=(10, 6))
        outcome_counts.plot(kind='pie', autopct='%1.1f%%', colors=['green', 'red'], labels=outcome_counts.index)
        plt.title('Deployment Outcomes')
        plt.tight_layout()
        outcomes_chart = os.path.join(report_dir, 'deployment_outcomes.png')
        plt.savefig(outcomes_chart)
        plt.close()
        story.append(Image(outcomes_chart, 6 * inch, 4 * inch))
        story.append(Spacer(1, 12))
        chart_files.append(outcomes_chart)

    return chart_files

if __name__ == "__main__":
    log_dir = 'audit_logs'
    report_dir = 'reports'
    
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    
    timeframe = datetime.datetime.now().strftime('%d-%m-%Y')
    output_file = os.path.join(report_dir, f'customer_deployment_report_{timeframe}.pdf')
    
    data = parse_deployment_logs(log_dir, verbose=False)
    
    print(data.head())
    
    generate_pdf_report(data, timeframe, output_file, report_dir)
    
    print(f'PDF report generated: {output_file}')
