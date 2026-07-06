import os
import base64
import logging
from django.template.loader import render_to_string
from django.conf import settings
from main.models import SecurityAssessmentResult

logger = logging.getLogger(__name__)

def generate_pdf(result, history_attempts, response_buffer):
    """
    Renders the scorecard HTML template and compiles it into a PDF.
    Uses WeasyPrint as the primary engine, falling back to Playwright if
    WeasyPrint library dependencies are missing on the runtime environment (Azure/Windows).
    """
    # ----------------------------------------------------
    # 1. Gather Data and Context Variables
    # ----------------------------------------------------
    score_pct = round((result.score / result.total) * 100) if result.total > 0 else 0
    
    # Rating levels
    if score_pct >= 90:
        rating_class = "excellent"
        rating_label = "Excellent"
        rating_desc = "You are taking outstanding steps to maintain your personal safety online."
    elif score_pct >= 75:
        rating_class = "good"
        rating_label = "Good"
        rating_desc = "You are taking strong steps to stay secure."
    elif score_pct >= 60:
        rating_class = "moderate"
        rating_label = "Moderate"
        rating_desc = "Your security posture shows potential vulnerabilities that require attention."
    else:
        rating_class = "at-risk"
        rating_label = "At Risk"
        rating_desc = "Critical security deficiencies detected. Action must be taken immediately."

    # Risk scale position
    risk_level = "Low"
    risk_scale_percentage = 12.5
    if score_pct >= 90:
        risk_level = "Low"
        risk_scale_percentage = 12.5
    elif score_pct >= 75:
        risk_level = "Moderate"
        risk_scale_percentage = 37.5
    elif score_pct >= 60:
        risk_level = "High"
        risk_scale_percentage = 62.5
    else:
        risk_level = "Critical"
        risk_scale_percentage = 87.5

    # Categories breakdown mapping
    domains_data = []
    mapped_categories = result.category_scores if result.category_scores else {}
    for cat_key, stat in mapped_categories.items():
        pct = stat.get('percentage', 0)
        if pct >= 80:
            status_class = "pass"
        elif pct >= 60:
            status_class = "warning"
        else:
            status_class = "fail"
            
        domains_data.append({
            'name': stat.get('name', cat_key.replace('_', ' ').title()),
            'percentage': pct,
            'status_class': status_class
        })

    # Badge achievements mapping
    badge_definitions = [
        {"name": "Cyber Champion", "earned": score_pct >= 90, "rarity_class": "champion", "icon_char": "🏆"},
        {"name": "Password Guardian", "earned": mapped_categories.get("password_security", {}).get("percentage", 0) >= 80, "rarity_class": "silver", "icon_char": "🔑"},
        {"name": "Phishing Defender", "earned": mapped_categories.get("phishing", {}).get("percentage", 0) >= 80, "rarity_class": "silver", "icon_char": "🐟"},
        {"name": "Banking Protector", "earned": mapped_categories.get("banking_fraud", {}).get("percentage", 0) >= 80, "rarity_class": "bronze", "icon_char": "🏦"},
        {"name": "Mobile Defender", "earned": mapped_categories.get("mobile_security", {}).get("percentage", 0) >= 80, "rarity_class": "bronze", "icon_char": "📱"},
        {"name": "Safe Browser", "earned": mapped_categories.get("safe_browsing", {}).get("percentage", 0) >= 80, "rarity_class": "bronze", "icon_char": "🌐"}
    ]

    # Historical Attempts Score Trend
    hist_scores = []
    hist_dates = []
    for attempt_id in history_attempts:
        try:
            prev = SecurityAssessmentResult.objects.get(id=attempt_id)
            prev_score = round((prev.score / prev.total) * 100) if prev.total > 0 else 0
            hist_scores.append(prev_score)
            hist_dates.append(prev.created_at.strftime('%b %d'))
        except SecurityAssessmentResult.DoesNotExist:
            continue
            
    if not hist_scores or hist_scores[-1] != score_pct:
        hist_scores.append(score_pct)
        hist_dates.append(result.created_at.strftime('%b %d'))
        
    hist_scores = hist_scores[-5:]
    hist_dates = hist_dates[-5:]

    # Calculate SVG path coordinates for line chart (width 320, height 120, plot padding y:[20, 110], x:[30, 300])
    chart_points = []
    num_points = len(hist_scores)
    for i in range(num_points):
        if num_points > 1:
            x = 30 + i * 270 / (num_points - 1)
        else:
            x = 30 + 135
        # Y maps: 0% -> 110px, 100% -> 20px
        y = 110 - (hist_scores[i] / 100.0) * 90
        chart_points.append({
            'x': x,
            'y': y,
            'label_y': y - 7,
            'score': hist_scores[i],
            'date': hist_dates[i]
        })
        
    chart_line_path = ""
    if chart_points:
        chart_line_path = " ".join([f"{'M' if idx == 0 else 'L'} {p['x']} {p['y']}" for idx, p in enumerate(chart_points)])

    # Score Delta calculation
    score_delta_text = ""
    if len(hist_scores) > 1:
        diff = hist_scores[-1] - hist_scores[0]
        if diff > 0:
            score_delta_text = f"{diff} point improvement since {hist_dates[0]}"
        elif diff < 0:
            score_delta_text = f"{abs(diff)} point decline since {hist_dates[0]}"

    # Recommendations Mapping
    weak_categories = [cat_key for cat_key, stat in mapped_categories.items() if stat.get('percentage', 0) < 60]
    category_recs_map = {
        'password_security': {
            'title': 'Improve Password Hygiene',
            'body': 'Avoid recycling passwords. Migrate existing credentials to a secure password manager.',
            'status_class': 'fail'
        },
        'phishing': {
            'title': 'Inspect Link Domain Headers',
            'body': 'Be suspicious of urgent alerts and verify secure URLs and sender addresses before clicking.',
            'status_class': 'fail'
        },
        'mobile_security': {
            'title': 'Restrict Mobile App Permissions',
            'body': 'Only download verified applications and audit background file/location permissions.',
            'status_class': 'fail'
        },
        'banking_fraud': {
            'title': 'Avoid UPI Fraud Scams',
            'body': 'Never enter your secret UPI PIN to receive money or scan unknown code plates.',
            'status_class': 'fail'
        },
        'privacy_protection': {
            'title': 'Lock Aadhaar Biometrics',
            'body': 'Configure biometric locking on the official mAadhaar application to prevent identity theft.',
            'status_class': 'fail'
        }
    }
    
    default_recs = [
        {
            'title': 'Enable Multi-Factor Authentication',
            'body': 'Configure authenticator apps across all primary email and financial accounts.',
            'status_class': 'pass'
        },
        {
            'title': 'Maintain Strong Security Hygiene',
            'body': 'Keep up the great work! Continue monitoring and updating your security controls regularly.',
            'status_class': 'pass'
        }
    ]
    
    recommendations = []
    for cat in weak_categories:
        if cat in category_recs_map:
            recommendations.append(category_recs_map[cat])
            
    for rec in default_recs:
        if len(recommendations) >= 4:
            break
        if rec not in recommendations:
            recommendations.append(rec)

    # ----------------------------------------------------
    # 2. Base64 Assets and CSS Inlining (For Sandbox Safety)
    # ----------------------------------------------------
    css_path = os.path.join(settings.BASE_DIR, 'static', 'pdf', 'scorecard.css')
    css_content = ""
    if os.path.exists(css_path):
        try:
            with open(css_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
        except Exception as e:
            logger.error(f"Error reading scorecard CSS: {e}")

    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'CyberSafe_icon.png')
    logo_base64 = ""
    if os.path.exists(logo_path):
        try:
            with open(logo_path, 'rb') as image_file:
                logo_base64 = f"data:image/png;base64,{base64.b64encode(image_file.read()).decode('utf-8')}"
        except Exception as e:
            logger.error(f"Error loading logo image: {e}")

    # Render HTML to string
    html_context = {
        'logo_url': logo_base64,
        'percentage': score_pct,
        'dash_offset': 283 - (283 * score_pct) / 100,
        'rating_class': rating_class,
        'rating_label': rating_label,
        'rating_desc': rating_desc,
        'risk_level': risk_level,
        'risk_scale_percentage': risk_scale_percentage,
        'date': result.created_at.strftime('%B %d, %Y'),
        'assessment_id': f"CS-{result.created_at.strftime('%m%d')}-{str(result.id)[:4].upper()}",
        'domains': domains_data,
        'badges': badge_definitions,
        'chart_points': chart_points,
        'chart_line_path': chart_line_path,
        'score_delta_text': score_delta_text,
        'recommendations': recommendations,
    }
    
    html_string = render_to_string('pdf/scorecard.html', html_context)
    
    # Inject CSS internally into template string to guarantee rendering compatibility
    html_string = html_string.replace('</head>', f'<style>{css_content}</style></head>')

    # ----------------------------------------------------
    # 3. PDF Compile (WeasyPrint primary -> ReportLab fallback)
    # ----------------------------------------------------
    try:
        logger.info("Attempting PDF rendering via WeasyPrint...")
        from weasyprint import HTML
        HTML(string=html_string).write_pdf(response_buffer)
        logger.info("PDF scorecard rendered successfully via WeasyPrint.")
        return
    except Exception as weasy_err:
        logger.warning(f"WeasyPrint failed or dependencies missing: {weasy_err}. Falling back to ReportLab...")
        
    try:
        _compile_pdf_with_reportlab(result, history_attempts, response_buffer)
        logger.info("PDF scorecard rendered successfully via ReportLab fallback.")
        return
    except Exception as reportlab_err:
        logger.error(f"ReportLab PDF rendering fallback failed: {reportlab_err}", exc_info=True)
        raise RuntimeError(f"All PDF engines failed: {reportlab_err}")


def _compile_pdf_with_reportlab(result, history_attempts, response_buffer):
    import os
    from django.conf import settings
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.graphics.shapes import Drawing, Circle, Rect, Line, String as DString

    # Page settings: A4 is 595.27 x 841.89 points
    # Printable width: 539.27 points (with 28pt margins on left/right)
    doc = SimpleDocTemplate(
        response_buffer,
        pagesize=A4,
        leftMargin=28,
        rightMargin=28,
        topMargin=28,
        bottomMargin=28
    )

    story = []
    styles = getSampleStyleSheet()

    # Colors
    c_primary = colors.HexColor('#2563eb')
    c_secondary = colors.HexColor('#1e293b')
    c_text_muted = colors.HexColor('#64748b')
    c_border = colors.HexColor('#e2e8f0')
    c_bg_light = colors.HexColor('#f8fafc')

    # Text Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=c_secondary,
        spaceAfter=2
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=c_text_muted
    )

    tagline_style = ParagraphStyle(
        'Tagline',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=c_primary,
        alignment=2
    )

    section_title_style = ParagraphStyle(
        'SecTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=c_secondary,
        spaceAfter=8,
        keepWithNext=True
    )

    card_title_style = ParagraphStyle(
        'CardTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#475569')
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155')
    )

    body_bold_style = ParagraphStyle(
        'BodyBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    scale_label_style = ParagraphStyle(
        'ScaleLabel',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=9,
        textColor=c_text_muted,
        alignment=1
    )
    scale_label_left = ParagraphStyle(
        'ScaleLabelLeft',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=9,
        textColor=c_text_muted,
        alignment=0
    )
    scale_label_right = ParagraphStyle(
        'ScaleLabelRight',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=9,
        textColor=c_text_muted,
        alignment=2
    )


    # Data Processing
    score_pct = round((result.score / result.total) * 100) if result.total > 0 else 0

    if score_pct >= 90:
        rating_label = "Excellent"
        rating_color = colors.HexColor('#10b981')
        rating_desc = "You are taking outstanding steps to maintain your personal safety online."
        risk_level = "Low"
        risk_scale_pct = 12.5
    elif score_pct >= 75:
        rating_label = "Good"
        rating_color = colors.HexColor('#3b82f6')
        rating_desc = "You are taking strong steps to stay secure."
        risk_level = "Moderate"
        risk_scale_pct = 37.5
    elif score_pct >= 60:
        rating_label = "Moderate"
        rating_color = colors.HexColor('#f59e0b')
        rating_desc = "Your security posture shows potential vulnerabilities that require attention."
        risk_level = "High"
        risk_scale_pct = 62.5
    else:
        rating_label = "At Risk"
        rating_color = colors.HexColor('#ef4444')
        rating_desc = "Critical security deficiencies detected. Action must be taken immediately."
        risk_level = "Critical"
        risk_scale_pct = 87.5

    # 1. Header Row
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'CyberSafe_icon.png')
    logo_flowable = None
    if os.path.exists(logo_path):
        try:
            logo_flowable = Image(logo_path, width=32, height=32)
        except Exception:
            pass
    if not logo_flowable:
        d_shield = Drawing(32, 32)
        d_shield.add(Circle(16, 16, 15, fillColor=c_primary, strokeColor=None))
        d_shield.add(DString(16, 11, "CS", textAnchor='middle', fontName='Helvetica-Bold', fontSize=14, fillColor=colors.white))
        logo_flowable = d_shield

    header_left_data = [
        [logo_flowable, Paragraph("CyberSafe Scorecard", title_style)],
        ['', Paragraph("Your Cybersecurity Assessment Summary", subtitle_style)]
    ]
    header_left_table = Table(header_left_data, colWidths=[40, 240])
    header_left_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('SPAN', (0,0), (0,1)),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))

    header_right_p = Paragraph("SECURE TODAY. SAFER TOMORROW.", tagline_style)

    header_table = Table([[header_left_table, header_right_p]], colWidths=[320, 219])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('LINEBELOW', (0,0), (-1,-1), 1, c_border),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 15))

    # 2. Section 1: Overview Cards
    d_score = Drawing(120, 100)
    d_score.add(Circle(60, 50, 42, fillColor=None, strokeColor=colors.HexColor('#f1f5f9'), strokeWidth=6))
    d_score.add(Circle(60, 50, 42, fillColor=None, strokeColor=rating_color, strokeWidth=6))
    d_score.add(DString(60, 44, f"{score_pct}", textAnchor='middle', fontName='Helvetica-Bold', fontSize=26, fillColor=c_secondary))
    d_score.add(DString(60, 28, "/100", textAnchor='middle', fontName='Helvetica', fontSize=10, fillColor=c_text_muted))

    rating_lbl_style = ParagraphStyle(
        'RatingLbl',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=rating_color,
        alignment=1
    )
    rating_desc_style = ParagraphStyle(
        'RatingDesc',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=c_text_muted,
        alignment=1
    )

    score_card_content = [
        Paragraph("OVERALL SCORE", card_title_style),
        Spacer(1, 4),
        d_score,
        Spacer(1, 4),
        Paragraph(rating_label.upper(), rating_lbl_style),
        Spacer(1, 2),
        Paragraph(rating_desc, rating_desc_style)
    ]

    d_risk = Drawing(140, 25)
    d_risk.add(Rect(0, 4, 32, 6, fillColor=colors.HexColor('#10b981'), strokeColor=None))
    d_risk.add(Rect(34, 4, 32, 6, fillColor=colors.HexColor('#3b82f6'), strokeColor=None))
    d_risk.add(Rect(68, 4, 32, 6, fillColor=colors.HexColor('#f59e0b'), strokeColor=None))
    d_risk.add(Rect(102, 4, 32, 6, fillColor=colors.HexColor('#ef4444'), strokeColor=None))
    x_indicator = (risk_scale_pct / 100.0) * 134
    d_risk.add(Circle(x_indicator, 7, 4, fillColor=c_secondary, strokeColor=None))

    risk_lbl_style = ParagraphStyle(
        'RiskLbl',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=rating_color
    )
    risk_desc_style = ParagraphStyle(
        'RiskDesc',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=c_text_muted
    )

    risk_card_content = [
        Paragraph("RISK LEVEL", card_title_style),
        Spacer(1, 10),
        Paragraph(risk_level.upper(), risk_lbl_style),
        Spacer(1, 4),
        Paragraph(f"Your system has a {risk_level.lower()} level of security risk.", risk_desc_style),
        Spacer(1, 10),
        d_risk,
        Spacer(1, 4),
        Table([
            [Paragraph("LOW", scale_label_left),
             Paragraph("MODERATE", scale_label_style),
             Paragraph("HIGH", scale_label_style),
             Paragraph("CRITICAL", scale_label_right)]
        ], colWidths=[32, 34, 34, 34], style=[
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ])
    ]

    date_str = result.created_at.strftime('%B %d, %Y')
    assessment_id_str = f"CS-{result.created_at.strftime('%m%d')}-{str(result.id)[:4].upper()}"

    details_lbl_style = ParagraphStyle(
        'DetailsLbl',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=9,
        textColor=c_text_muted
    )
    details_val_style = ParagraphStyle(
        'DetailsVal',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=c_secondary
    )

    details_table_data = [
        [Paragraph("📅 ASSESSMENT DATE", details_lbl_style)],
        [Paragraph(date_str, details_val_style)],
        [Spacer(1, 4)],
        [Paragraph("👤 ASSESSMENT TYPE", details_lbl_style)],
        [Paragraph("CyberSafe Standard Assessment", details_val_style)],
        [Spacer(1, 4)],
        [Paragraph("📋 ASSESSMENT ID", details_lbl_style)],
        [Paragraph(assessment_id_str, details_val_style)],
    ]
    details_table = Table(details_table_data, colWidths=[160])
    details_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))

    details_card_content = [
        Paragraph("DETAILS", card_title_style),
        Spacer(1, 10),
        details_table
    ]

    overview_table = Table([[score_card_content, risk_card_content, details_card_content]], colWidths=[175, 175, 189])
    overview_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (-1,-1), c_bg_light),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 1, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(overview_table)
    story.append(Spacer(1, 15))

    # 3. Section 2: Domain Score Breakdown & Badge Achievements
    domains_data = []
    mapped_categories = result.category_scores if result.category_scores else {}
    for cat_key, stat in mapped_categories.items():
        pct = stat.get('percentage', 0)
        if pct >= 80:
            bar_color = colors.HexColor('#10b981')
        elif pct >= 60:
            bar_color = colors.HexColor('#f59e0b')
        else:
            bar_color = colors.HexColor('#ef4444')

        d_bar = Drawing(120, 10)
        d_bar.add(Rect(0, 2, 90, 6, fillColor=colors.HexColor('#e2e8f0'), strokeColor=None))
        d_bar.add(Rect(0, 2, 90 * (pct / 100.0), 6, fillColor=bar_color, strokeColor=None))
        d_bar.add(DString(95, 1, f"{pct}%", fontName='Helvetica-Bold', fontSize=8, fillColor=c_secondary))

        name = stat.get('name', cat_key.replace('_', ' ').title())
        domains_data.append([
            Paragraph(name, body_style),
            d_bar
        ])

    domains_table = Table(domains_data, colWidths=[130, 120])
    domains_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.HexColor('#f1f5f9')),
    ]))

    col_a_content = [
        Paragraph("DOMAIN SCORE BREAKDOWN", section_title_style),
        Spacer(1, 6),
        domains_table
    ]

    badge_definitions = [
        {"name": "Cyber Champion", "earned": score_pct >= 90, "icon": "🏆"},
        {"name": "Password Guardian", "earned": mapped_categories.get("password_security", {}).get("percentage", 0) >= 80, "icon": "🔑"},
        {"name": "Phishing Defender", "earned": mapped_categories.get("phishing", {}).get("percentage", 0) >= 80, "icon": "🐟"},
        {"name": "Banking Protector", "earned": mapped_categories.get("banking_fraud", {}).get("percentage", 0) >= 80, "icon": "🏦"},
        {"name": "Mobile Defender", "earned": mapped_categories.get("mobile_security", {}).get("percentage", 0) >= 80, "icon": "📱"},
        {"name": "Safe Browser", "earned": mapped_categories.get("safe_browsing", {}).get("percentage", 0) >= 80, "icon": "🌐"}
    ]

    badges_table_data = []
    row = []
    for idx, badge in enumerate(badge_definitions):
        earned_text = "Earned" if badge["earned"] else "Locked"
        status_color = "#10b981" if badge["earned"] else "#94a3b8"
        icon_box = badge["icon"]

        badge_p = Paragraph(
            f"<b>{icon_box} {badge['name']}</b><br/>"
            f"<font size=7 color='{status_color}'>{earned_text}</font>",
            body_style
        )
        row.append(badge_p)
        if len(row) == 2:
            badges_table_data.append(row)
            row = []
    if row:
        row.append('')
        badges_table_data.append(row)

    badges_table = Table(badges_table_data, colWidths=[125, 125])
    badges_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ffffff')),
        ('BOX', (0,0), (-1,-1), 0.5, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))

    col_b_content = [
        Paragraph("BADGE ACHIEVEMENTS", section_title_style),
        Spacer(1, 6),
        badges_table
    ]

    split_table_1 = Table([[col_a_content, col_b_content]], colWidths=[260, 260])
    split_table_1.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(split_table_1)
    story.append(Spacer(1, 15))

    # 4. Section 3: Trend & Recommendations
    hist_scores = []
    hist_dates = []
    for attempt_id in history_attempts:
        try:
            from main.models import SecurityAssessmentResult as SAR
            prev = SAR.objects.get(id=attempt_id)
            prev_score = round((prev.score / prev.total) * 100) if prev.total > 0 else 0
            hist_scores.append(prev_score)
            hist_dates.append(prev.created_at.strftime('%b %d'))
        except Exception:
            continue

    if not hist_scores or hist_scores[-1] != score_pct:
        hist_scores.append(score_pct)
        hist_dates.append(result.created_at.strftime('%b %d'))

    hist_scores = hist_scores[-5:]
    hist_dates = hist_dates[-5:]

    d_chart = Drawing(240, 110)
    y_vals = [20, 42.5, 65, 87.5, 110]
    labels_y = ["100", "75", "50", "25", "0"]
    for i, y_val in enumerate(y_vals):
        rl_y = 120 - y_val
        d_chart.add(Line(25, rl_y, 230, rl_y, strokeColor=colors.HexColor('#f1f5f9'), strokeWidth=0.8))
        d_chart.add(DString(5, rl_y - 3, labels_y[i], fontName='Helvetica', fontSize=7, fillColor=c_text_muted))

    num_points = len(hist_scores)
    points_list = []
    for i in range(num_points):
        if num_points > 1:
            x = 35 + i * 185 / (num_points - 1)
        else:
            x = 35 + 92
        y = 10 + (hist_scores[i] / 100.0) * 90
        points_list.append({'x': x, 'y': y, 'score': hist_scores[i], 'date': hist_dates[i]})

    if len(points_list) > 1:
        for idx in range(len(points_list) - 1):
            p1 = points_list[idx]
            p2 = points_list[idx + 1]
            d_chart.add(Line(p1['x'], p1['y'], p2['x'], p2['y'], strokeColor=c_primary, strokeWidth=2))

    for p in points_list:
        d_chart.add(Circle(p['x'], p['y'], 3, fillColor=colors.HexColor('#10b981'), strokeColor=c_primary, strokeWidth=1))
        d_chart.add(DString(p['x'], p['y'] + 6, f"{p['score']}", textAnchor='middle', fontName='Helvetica-Bold', fontSize=8, fillColor=c_secondary))
        d_chart.add(DString(p['x'], 0, p['date'], textAnchor='middle', fontName='Helvetica', fontSize=7.5, fillColor=c_text_muted))

    delta_text = ""
    if len(hist_scores) > 1:
        diff = hist_scores[-1] - hist_scores[0]
        if diff > 0:
            delta_text = f"↑ {diff} pt improvement since {hist_dates[0]}"
        elif diff < 0:
            delta_text = f"↓ {abs(diff)} pt decline since {hist_dates[0]}"

    col_chart_content = [
        Paragraph("SCORE HISTORY", section_title_style),
        Spacer(1, 4),
        d_chart,
        Spacer(1, 4),
        Paragraph(f"<font size=8 color='#10b981'><b>{delta_text}</b></font>" if delta_text else "", body_style)
    ]

    weak_categories = [cat_key for cat_key, stat in mapped_categories.items() if stat.get('percentage', 0) < 60]
    category_recs_map = {
        'password_security': {
            'title': 'Improve Password Hygiene',
            'body': 'Avoid recycling passwords. Migrate credentials to a secure manager.',
            'color': '#ef4444'
        },
        'phishing': {
            'title': 'Inspect Link Domains',
            'body': 'Be suspicious of urgent alerts; check secure URLs before clicking.',
            'color': '#ef4444'
        },
        'mobile_security': {
            'title': 'Audit App Permissions',
            'body': 'Download verified apps only; restrict background location access.',
            'color': '#ef4444'
        },
        'banking_fraud': {
            'title': 'Avoid UPI Fraud Scams',
            'body': 'Never enter your UPI PIN to receive funds or scan unknown QR plates.',
            'color': '#ef4444'
        },
        'privacy_protection': {
            'title': 'Lock Aadhaar Biometrics',
            'body': 'Configure biometric locking on the mAadhaar app to secure your ID.',
            'color': '#ef4444'
        }
    }

    default_recs = [
        {
            'title': 'Enable Multi-Factor Authentication',
            'body': 'Configure authenticator apps across all primary email and financial accounts.',
            'color': '#10b981'
        },
        {
            'title': 'Maintain Strong Security Hygiene',
            'body': 'Keep up the great work! Continue monitoring and updating your security controls.',
            'color': '#10b981'
        }
    ]

    recommendations = []
    for cat in weak_categories:
        if cat in category_recs_map:
            recommendations.append(category_recs_map[cat])

    for rec in default_recs:
        if len(recommendations) >= 4:
            break
        if rec not in recommendations:
            recommendations.append(rec)

    recs_table_data = []
    for rec in recommendations:
        bullet_p = Paragraph(f"<font color='{rec['color']}'><b>●</b></font>", body_bold_style)
        content_p = Paragraph(f"<b>{rec['title']}</b>: {rec['body']}", body_style)
        recs_table_data.append([bullet_p, content_p])

    recs_table = Table(recs_table_data, colWidths=[15, 245])
    recs_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))

    col_recs_content = [
        Paragraph("RECOMMENDATIONS", section_title_style),
        Spacer(1, 6),
        recs_table
    ]

    split_table_2 = Table([[col_chart_content, col_recs_content]], colWidths=[260, 260])
    split_table_2.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(split_table_2)
    story.append(Spacer(1, 15))

    # 5. Section 4: Callout Section
    callout_1 = [
        Paragraph("🛡️ <b>Continuous Journey</b>", body_bold_style),
        Spacer(1, 2),
        Paragraph("Cybersecurity is a continuous journey. Keep improving, keep evolving, and stay CyberSafe.", body_style)
    ]
    callout_2 = [
        Paragraph("🔑 <b>LOCALIZED THREAT INSIGHT</b>", body_bold_style),
        Spacer(1, 2),
        Paragraph("WhatsApp Financial Scam (UPI Fraud) remains one of the most common threats affecting users in India.", body_style)
    ]

    callout_table = Table([[callout_1, callout_2]], colWidths=[260, 260])
    callout_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (-1,-1), c_bg_light),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 1, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(callout_table)
    story.append(Spacer(1, 20))

    # 6. Footer
    footer_p1 = Paragraph("🌐 www.cybersafe.com", body_style)
    footer_p2 = Paragraph("✉ info@cybersafe.com", body_style)
    footer_p3 = Paragraph("🛡️ Secure Today. Safer Tomorrow.", tagline_style)

    footer_table = Table([[footer_p1, footer_p2, footer_p3]], colWidths=[160, 160, 200])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEABOVE', (0,0), (-1,-1), 1, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(footer_table)

    doc.build(story)

