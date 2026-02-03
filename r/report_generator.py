from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from django.conf import settings
import os
import json
import csv
from datetime import datetime

class ReportGenerator:
    
    def generate_report(self, comparison, result, format_type, include_viz, include_code, include_metrics):
        """Generate report in specified format"""
        
        if format_type == 'pdf':
            return self._generate_pdf(comparison, result, include_viz, include_code, include_metrics)
        elif format_type == 'csv':
            return self._generate_csv(comparison, result)
        elif format_type == 'json':
            return self._generate_json(comparison, result)
        elif format_type == 'html':
            return self._generate_html(comparison, result, include_viz, include_code, include_metrics)
        
        return None
    
    def _generate_pdf(self, comparison, result, include_viz, include_code, include_metrics):
        """Generate PDF report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'similarity_report_{comparison.request_id}_{timestamp}.pdf'
        filepath = os.path.join(settings.MEDIA_ROOT, 'reports', filename)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=1
        )
        story.append(Paragraph('Code Similarity Analysis Report', title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Comparison Information
        story.append(Paragraph('Comparison Details', styles['Heading2']))
        comparison_data = [
            ['Request ID:', str(comparison.request_id)],
            ['User:', comparison.user.username],
            ['Date:', comparison.created_at.strftime('%Y-%m-%d %H:%M:%S')],
            ['Type:', comparison.get_comparison_type_display()],
            ['Source File:', comparison.source_submission.title],
            ['Target File:', comparison.target_submission.title if comparison.target_submission else 'N/A'],
        ]
        
        comparison_table = Table(comparison_data, colWidths=[2*inch, 4*inch])
        comparison_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        story.append(comparison_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Similarity Scores
        story.append(Paragraph('Similarity Scores', styles['Heading2']))
        score_data = [
            ['Metric', 'Score', 'Percentage'],
            ['Overall Similarity', f'{result.overall_similarity_score:.4f}', f'{result.overall_similarity_score*100:.2f}%'],
            ['Token Similarity', f'{result.token_similarity:.4f}', f'{result.token_similarity*100:.2f}%'],
            ['Structural Similarity', f'{result.structural_similarity:.4f}', f'{result.structural_similarity*100:.2f}%'],
            ['AST Similarity', f'{result.ast_similarity:.4f}', f'{result.ast_similarity*100:.2f}%'],
        ]
        
        if result.ml_similarity:
            score_data.append(['ML Prediction', f'{result.ml_similarity:.4f}', f'{result.ml_similarity*100:.2f}%'])
        
        score_table = Table(score_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')]),
        ]))
        story.append(score_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Identical Segments
        if include_code and result.identical_segments:
            story.append(Paragraph(f'Identical Code Segments ({len(result.identical_segments)} found)', styles['Heading2']))
            
            for idx, segment in enumerate(result.identical_segments[:5], 1):
                segment_info = f"Segment {idx}: Lines {segment['source_start']}-{segment['source_end']} (Source) matches Lines {segment['target_start']}-{segment['target_end']} (Target)"
                story.append(Paragraph(segment_info, styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
        
        # Code Metrics
        if include_metrics and result.code_metrics:
            story.append(PageBreak())
            story.append(Paragraph('Code Metrics Comparison', styles['Heading2']))
            
            metrics = result.code_metrics
            if 'source_metrics' in metrics and 'target_metrics' in metrics:
                metrics_data = [
                    ['Metric', 'Source Code', 'Target Code', 'Difference'],
                    ['Lines of Code', 
                     str(metrics['source_metrics'].get('loc', 'N/A')),
                     str(metrics['target_metrics'].get('loc', 'N/A')),
                     str(metrics.get('loc_diff', 'N/A'))],
                    ['Complexity',
                     f"{metrics['source_metrics'].get('complexity', 0):.2f}",
                     f"{metrics['target_metrics'].get('complexity', 0):.2f}",
                     f"{metrics.get('complexity_diff', 0):.2f}"],
                ]
                
                metrics_table = Table(metrics_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
                metrics_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                story.append(metrics_table)
        
        # Build PDF
        doc.build(story)
        return filepath
    
    def _generate_csv(self, comparison, result):
        """Generate CSV report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'similarity_report_{comparison.request_id}_{timestamp}.csv'
        filepath = os.path.join(settings.MEDIA_ROOT, 'reports', filename)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow(['Code Similarity Analysis Report'])
            writer.writerow([])
            
            # Comparison Info
            writer.writerow(['Comparison Information'])
            writer.writerow(['Request ID', str(comparison.request_id)])
            writer.writerow(['User', comparison.user.username])
            writer.writerow(['Date', comparison.created_at.strftime('%Y-%m-%d %H:%M:%S')])
            writer.writerow(['Type', comparison.get_comparison_type_display()])
            writer.writerow([])
            
            # Similarity Scores
            writer.writerow(['Similarity Scores'])
            writer.writerow(['Metric', 'Score', 'Percentage'])
            writer.writerow(['Overall Similarity', f'{result.overall_similarity_score:.4f}', f'{result.overall_similarity_score*100:.2f}%'])
            writer.writerow(['Token Similarity', f'{result.token_similarity:.4f}', f'{result.token_similarity*100:.2f}%'])
            writer.writerow(['Structural Similarity', f'{result.structural_similarity:.4f}', f'{result.structural_similarity*100:.2f}%'])
            writer.writerow(['AST Similarity', f'{result.ast_similarity:.4f}', f'{result.ast_similarity*100:.2f}%'])
            
            if result.ml_similarity:
                writer.writerow(['ML Prediction', f'{result.ml_similarity:.4f}', f'{result.ml_similarity*100:.2f}%'])
            
            writer.writerow([])
            
            # Identical Segments
            writer.writerow(['Identical Segments', len(result.identical_segments)])
            writer.writerow(['Near-Identical Segments', len(result.near_identical_segments)])
        
        return filepath
    
    def _generate_json(self, comparison, result):
        """Generate JSON report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'similarity_report_{comparison.request_id}_{timestamp}.json'
        filepath = os.path.join(settings.MEDIA_ROOT, 'reports', filename)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        report_data = {
            'comparison_info': {
                'request_id': str(comparison.request_id),
                'user': comparison.user.username,
                'date': comparison.created_at.isoformat(),
                'type': comparison.get_comparison_type_display(),
                'source_file': comparison.source_submission.title,
                'target_file': comparison.target_submission.title if comparison.target_submission else None,
            },
            'similarity_scores': {
                'overall': result.overall_similarity_score,
                'token': result.token_similarity,
                'structural': result.structural_similarity,
                'ast': result.ast_similarity,
                'ml_prediction': result.ml_similarity,
            },
            'segments': {
                'identical': result.identical_segments,
                'near_identical': result.near_identical_segments,
            },
            'code_metrics': result.code_metrics,
        }
        
        with open(filepath, 'w', encoding='utf-8') as jsonfile:
            json.dump(report_data, jsonfile, indent=2, default=str)
        
        return filepath
    
    def _generate_html(self, comparison, result, include_viz, include_code, include_metrics):
        """Generate HTML report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'similarity_report_{comparison.request_id}_{timestamp}.html'
        filepath = os.path.join(settings.MEDIA_ROOT, 'reports', filename)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Similarity Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
                .container {{ background: white; padding: 30px; border-radius: 10px; }}
                h1 {{ color: #2c3e50; text-align: center; }}
                h2 {{ color: #3498db; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 12px; text-align: left; border: 1px solid #ddd; }}
                th {{ background-color: #3498db; color: white; }}
                .score-high {{ color: #e74c3c; font-weight: bold; }}
                .score-medium {{ color: #f39c12; font-weight: bold; }}
                .score-low {{ color: #2ecc71; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Code Similarity Analysis Report</h1>
                
                <h2>Comparison Information</h2>
                <table>
                    <tr><th>Request ID</th><td>{comparison.request_id}</td></tr>
                    <tr><th>User</th><td>{comparison.user.username}</td></tr>
                    <tr><th>Date</th><td>{comparison.created_at.strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
                    <tr><th>Type</th><td>{comparison.get_comparison_type_display()}</td></tr>
                </table>
                
                <h2>Similarity Scores</h2>
                <table>
                    <tr><th>Metric</th><th>Score</th><th>Percentage</th></tr>
                    <tr>
                        <td>Overall Similarity</td>
                        <td class="{'score-high' if result.overall_similarity_score >= 0.8 else 'score-medium' if result.overall_similarity_score >= 0.5 else 'score-low'}">{result.overall_similarity_score:.4f}</td>
                        <td>{result.overall_similarity_score*100:.2f}%</td>
                    </tr>
                    <tr><td>Token Similarity</td><td>{result.token_similarity:.4f}</td><td>{result.token_similarity*100:.2f}%</td></tr>
                    <tr><td>Structural Similarity</td><td>{result.structural_similarity:.4f}</td><td>{result.structural_similarity*100:.2f}%</td></tr>
                    <tr><td>AST Similarity</td><td>{result.ast_similarity:.4f}</td><td>{result.ast_similarity*100:.2f}%</td></tr>
                </table>
                
                <h2>Analysis Summary</h2>
                <p><strong>Identical Segments Found:</strong> {len(result.identical_segments)}</p>
                <p><strong>Near-Identical Segments Found:</strong> {len(result.near_identical_segments)}</p>
            </div>
        </body>
        </html>
        """
        
        with open(filepath, 'w', encoding='utf-8') as htmlfile:
            htmlfile.write(html_content)
        
        return filepath
