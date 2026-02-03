from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, HttpResponse
from django.contrib import messages
from users.models import ComparisonRequest, SimilarityResult
from .models import SimilarityReport
from .report_generator import ReportGenerator
import os

@login_required
def generate_report_view(request, request_id):
    """Generate similarity report"""
    comparison = get_object_or_404(ComparisonRequest, request_id=request_id, user=request.user)
    
    if comparison.status != 'completed':
        messages.error(request, 'Cannot generate report for incomplete comparison.')
        return redirect('users:comparison_detail', request_id=request_id)
    
    if request.method == 'POST':
        report_format = request.POST.get('format', 'pdf')
        include_visualizations = request.POST.get('include_visualizations') == 'on'
        include_code_segments = request.POST.get('include_code_segments') == 'on'
        include_metrics = request.POST.get('include_metrics') == 'on'
        
        # Generate report
        generator = ReportGenerator()
        report_path = generator.generate_report(
            comparison,
            comparison.result,
            report_format,
            include_visualizations,
            include_code_segments,
            include_metrics
        )
        
        # Save report record
        report = SimilarityReport.objects.create(
            user=request.user,
            comparison=comparison,
            result=comparison.result,
            report_format=report_format,
            file_path=report_path,
            file_size=os.path.getsize(report_path),
            include_visualizations=include_visualizations,
            include_code_segments=include_code_segments,
            include_metrics=include_metrics
        )
        
        messages.success(request, 'Report generated successfully!')
        return redirect('reports:download_report', report_id=report.report_id)
    
    return render(request, 'reports/generate_report.html', {'comparison': comparison})


@login_required
def download_report_view(request, report_id):
    """Download report"""
    report = get_object_or_404(SimilarityReport, report_id=report_id, user=request.user)
    
    report.download_count += 1
    report.last_downloaded = timezone.now()
    report.save()
    
    file_path = report.file_path.path
    
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Type'] = f'application/{report.report_format}'
        response['Content-Disposition'] = f'attachment; filename="similarity_report_{report.report_id}.{report.report_format}"'
        return response
    else:
        messages.error(request, 'Report file not found.')
        return redirect('reports:my_reports')


@login_required
def my_reports_view(request):
    """View all user reports"""
    reports = SimilarityReport.objects.filter(user=request.user).select_related(
        'comparison', 'result'
    ).order_by('-generated_at')
    
    context = {'reports': reports}
    return render(request, 'reports/my_reports.html', context)
