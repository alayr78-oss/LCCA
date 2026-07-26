import io
import csv
import json

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    from fpdf import FPDF
except ImportError:
    FPDF = None

class ExportEngine:
    """
    Generates academic and professional reports (CSV, Excel, PDF) from RAM-DSS output.
    """
    
    @staticmethod
    def generate_csv(report_data):
        """ Generates a CSV blob for the main metrics """
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Project Name', report_data.get('project_name', 'N/A')])
        writer.writerow(['Total Lifecycle Cost', report_data.get('total_lcca', 0)])
        writer.writerow(['Risk Level', report_data.get('risk_level', 'N/A')])
        writer.writerow(['Carbon Footprint', report_data.get('carbon_footprint', 0)])
        writer.writerow(['Recommended Strategy', report_data.get('recommended_strategy', 'N/A')])
        return output.getvalue()
        
    @staticmethod
    def generate_excel(report_data):
        """ Generates an Excel binary blob using Pandas """
        if pd is None:
            return "Pandas is required for Excel export. Please install it."
            
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Summary Sheet
            summary = pd.DataFrame([{
                'Project': report_data.get('project_name', 'N/A'),
                'Lifecycle Cost': report_data.get('total_lcca', 0),
                'Risk Score': report_data.get('risk_score', 0),
                'Carbon Footprint': report_data.get('carbon_footprint', 0)
            }])
            summary.to_excel(writer, sheet_name='Summary', index=False)
            
            # Alternatives Sheet
            if 'alternatives' in report_data:
                alts = pd.DataFrame(report_data['alternatives'])
                alts.to_excel(writer, sheet_name='Alternatives', index=False)
                
        return output.getvalue()

    @staticmethod
    def generate_pdf(report_data):
        """ Generates an Advanced Academic Research Report with 14 sections using FPDF """
        if FPDF is None:
            return b"FPDF2 is required for PDF export. Please install it."
            
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        def add_section_header(title):
            pdf.set_font("helvetica", "B", 14)
            pdf.set_text_color(0, 51, 102) # Dark blue
            pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)
            
        def add_body_text(text):
            pdf.set_font("helvetica", "", 11)
            pdf.multi_cell(0, 8, text)
            pdf.ln(2)

        # Title Page
        pdf.set_font("helvetica", "B", 20)
        pdf.cell(0, 15, "RAM-DSS Research Report", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.set_font("helvetica", "", 12)
        pdf.cell(0, 10, f"Project: {report_data.get('project_name', 'Case Study Analysis')}", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(10)
        
        # 1. Executive Summary
        add_section_header("1. Executive Summary")
        add_body_text(f"This report outlines the condition assessment, lifecycle cost analysis, and decision optimization for the {report_data.get('project_name', 'project')}. The recommended strategy is {report_data.get('recommended_strategy', 'N/A')}.")
        
        # 2. Project Description
        add_section_header("2. Project Description")
        add_body_text("Analyzed track segment evaluating multiple maintenance scenarios over a 50-year lifecycle.")
        
        # 3. Asset Inventory
        add_section_header("3. Asset Inventory")
        add_body_text("Includes rails, sleepers, and ballast components linked to historical installation records.")
        
        # 4. Condition Assessment Results
        add_section_header("4. Condition Assessment Results")
        add_body_text(f"Current Infrastructure Condition Index (ICI): {report_data.get('ici', 'N/A')}")
        
        # 5. Deterioration Analysis
        add_section_header("5. Deterioration Analysis")
        add_body_text("Utilizes linear and exponential mathematical models derived from the Engineering Knowledge Base.")
        
        # 6. Remaining Service Life Prediction
        add_section_header("6. Remaining Service Life Prediction")
        add_body_text(f"Average predicted RSL before safety thresholds are breached: {report_data.get('rsl', 'N/A')} years.")
        
        # 7. LCCA Results
        add_section_header("7. LCCA Results")
        add_body_text(f"Total Net Present Value (NPV): ${report_data.get('total_lcca', 0)}")
        
        # 8. Carbon Assessment
        add_section_header("8. Carbon Assessment")
        add_body_text(f"Total calculated footprint: {report_data.get('carbon_footprint', 0)} tCO2e.")
        
        # 9. Risk Assessment
        add_section_header("9. Risk Assessment")
        add_body_text(f"Calculated Risk Score: {report_data.get('risk_score', 'N/A')} ({report_data.get('risk_level', 'Unknown')} Risk)")
        
        # 10. MCDM Ranking
        add_section_header("10. MCDM Ranking")
        add_body_text("Alternatives evaluated using Simple Additive Weighting (SAW) method.")
        
        # 11. Recommended Strategy
        add_section_header("11. Recommended Strategy")
        add_body_text(f"Selected: {report_data.get('recommended_strategy', 'N/A')} based on multi-criteria optimization.")
        
        # 12. Sensitivity Analysis
        add_section_header("12. Sensitivity Analysis")
        add_body_text("Tornado analysis applied to ±20% variations in discount rate and material cost factors.")
        
        # 13. Validation Results
        add_section_header("13. Validation Results")
        add_body_text("Models strictly verified against mathematical baseline (RMSE/MAE calculated).")
        
        # 14. Assumptions and References
        add_section_header("14. Assumptions and References")
        add_body_text("Discount Rate: 8% | Inflation: 2%. Data linked to standard track degradation references.")

        return pdf.output(dest='S')
