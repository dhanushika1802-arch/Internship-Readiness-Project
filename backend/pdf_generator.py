import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf_report(dest_path, user_profile, skills, assessments, readiness, gaps, roadmap, suggested_projects):
    """
    Generates a structured PDF report summarizing student readiness.
    """
    try:
        doc = SimpleDocTemplate(dest_path, pagesize=letter,
                                rightMargin=40, leftMargin=40,
                                topMargin=40, bottomMargin=40)
        story = []
        styles = getSampleStyleSheet()

        # Custom Styles
        primary_color = colors.HexColor("#4f46e5")  # Indigo
        secondary_color = colors.HexColor("#0891b2") # Cyan
        dark_neutral = colors.HexColor("#1e293b")    # Dark Grey
        light_neutral = colors.HexColor("#f8fafc")   # Off White

        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            textColor=primary_color,
            spaceAfter=15
        )

        h1_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=primary_color,
            spaceBefore=15,
            spaceAfter=10,
            borderPadding=4
        )

        body_style = ParagraphStyle(
            'BodyTextCustom',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            textColor=dark_neutral,
            leading=14,
            spaceAfter=8
        )

        bold_style = ParagraphStyle(
            'BodyBold',
            parent=body_style,
            fontName='Helvetica-Bold'
        )

        # Header Title
        story.append(Paragraph("AI-Powered Internship Readiness Report", title_style))
        story.append(Paragraph("Personalized Skill Assessment, Gap Analysis & Career Roadmap", body_style))
        story.append(Spacer(1, 10))

        # Divider line
        divider = Table([[""]], colWidths=[530], rowHeights=[2])
        divider.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), primary_color),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
        ]))
        story.append(divider)
        story.append(Spacer(1, 15))

        # 1. Profile Block
        story.append(Paragraph("Student Profile", h1_style))
        profile_data = [
            [Paragraph("<b>Name:</b>", body_style), Paragraph(user_profile.get('name', 'N/A'), body_style),
             Paragraph("<b>Target Role:</b>", body_style), Paragraph(user_profile.get('target_role', 'N/A'), body_style)],
            [Paragraph("<b>Degree:</b>", body_style), Paragraph(user_profile.get('degree', 'N/A'), body_style),
             Paragraph("<b>Year of Study:</b>", body_style), Paragraph(f"Year {user_profile.get('year', 'N/A')}", body_style)],
            [Paragraph("<b>Email:</b>", body_style), Paragraph(user_profile.get('email', 'N/A'), body_style),
             Paragraph("<b>Date Generated:</b>", body_style), Paragraph("Current Session", body_style)]
        ]
        
        t_profile = Table(profile_data, colWidths=[80, 180, 90, 180])
        t_profile.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), light_neutral),
            ('BOX', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.lightgrey),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(t_profile)
        story.append(Spacer(1, 15))

        # 2. Readiness Score Block
        story.append(Paragraph("Internship Readiness Scoring", h1_style))
        score_val = readiness.get('overall_score', 0)
        level_val = readiness.get('readiness_level', 'Beginner')
        
        score_data = [
            [Paragraph(f"<font size=28 color='#4f46e5'><b>{score_val}/100</b></font><br/><b>Readiness Level: {level_val}</b>", body_style),
             Paragraph("<b>Scoring breakdown criteria:</b><br/>"
                       "• Assessment Tests (35%)<br/>"
                       "• Technical Skills Matrix (35%)<br/>"
                       "• Project Portfolio Check (15%)<br/>"
                       "• Resume Quality & Certifications (15%)", body_style)]
        ]
        t_score = Table(score_data, colWidths=[200, 330])
        t_score.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#eff6ff")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#bfdbfe")),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ]))
        story.append(t_score)
        story.append(Spacer(1, 15))

        # 3. Strengths and Weaknesses
        story.append(Paragraph("<b>Key Insights</b>", body_style))
        insights_data = []
        for strg in readiness.get('strengths', []):
            insights_data.append([Paragraph("<font color='green'><b>[Strength]</b></font>", body_style), Paragraph(strg, body_style)])
        for weak in readiness.get('weaknesses', []):
            insights_data.append([Paragraph("<font color='red'><b>[Skill Gap]</b></font>", body_style), Paragraph(weak, body_style)])
            
        if insights_data:
            t_insights = Table(insights_data, colWidths=[80, 450])
            t_insights.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ]))
            story.append(t_insights)
        story.append(Spacer(1, 15))

        # 4. Skills and Assessments
        story.append(Paragraph("Skill Matrix & Test Scores", h1_style))
        
        # Merge skills list and assessments list
        skills_summary = []
        skills_summary.append([Paragraph("<b>Technical Category</b>", bold_style), Paragraph("<b>Identified Score (0-100)</b>", bold_style), Paragraph("<b>Test Performance</b>", bold_style)])
        
        all_skills = set(list(skills.keys()) + list(assessments.keys()))
        for sk in sorted(all_skills):
            sk_score = skills.get(sk, 0)
            ast_score = assessments.get(sk, "Not Taken")
            ast_str = f"{ast_score}/100" if isinstance(ast_score, int) else ast_score
            skills_summary.append([Paragraph(sk, body_style), Paragraph(f"{sk_score}/100", body_style), Paragraph(ast_str, body_style)])
            
        t_skills = Table(skills_summary, colWidths=[200, 160, 170])
        t_skills.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e2e8f0")),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOX', (0,0), (-1,-1), 0.5, colors.grey),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.lightgrey),
        ]))
        story.append(t_skills)
        story.append(Spacer(1, 15))

        story.append(PageBreak()) # Move to next page for Roadmap

        # 5. Skill Gap Analysis
        story.append(Paragraph(f"Skill Gap Detector: Target Role - {user_profile.get('target_role', 'Software Developer')}", h1_style))
        story.append(Paragraph(f"<b>Match Rate:</b> {gaps.get('match_percentage', 0)}%", bold_style))
        story.append(Paragraph(f"<b>Skills Matched:</b> {', '.join(gaps.get('matched_skills', [])) if gaps.get('matched_skills') else 'None'}", body_style))
        story.append(Paragraph(f"<b>Skills Missing:</b> <font color='red'>{', '.join(gaps.get('missing_skills', [])) if gaps.get('missing_skills') else 'None (Fully Internship Ready!)'}</font>", body_style))
        story.append(Spacer(1, 10))

        # 6. Personalized Weekly Learning Roadmap
        story.append(Paragraph("Personalized 6-Week Learning Roadmap", h1_style))
        roadmap_data = []
        roadmap_data.append([Paragraph("<b>Week</b>", bold_style), Paragraph("<b>Target Milestone & Focus Tasks</b>", bold_style)])
        for item in roadmap:
            roadmap_data.append([
                Paragraph(f"Week {item.get('week', item.get('id', 'N/A'))}", bold_style),
                Paragraph(item.get('task', 'N/A'), body_style)
            ])
            
        t_roadmap = Table(roadmap_data, colWidths=[60, 470])
        t_roadmap.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
            ('BOX', (0,0), (-1,-1), 0.5, colors.grey),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.lightgrey),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t_roadmap)
        story.append(Spacer(1, 15))

        # 7. Recommended Projects
        story.append(Paragraph("Recommended Hands-on Projects", h1_style))
        for proj in suggested_projects[:3]:
            story.append(Paragraph(f"<b>• {proj.get('title', 'N/A')}</b> ({proj.get('difficulty', 'Beginner')})", bold_style))
            story.append(Paragraph(proj.get('description', 'N/A'), body_style))
            story.append(Spacer(1, 3))

        doc.build(story)
        return True
    except Exception as e:
        print(f"Error compiling ReportLab PDF: {e}")
        # Build raw text fallback
        try:
            with open(dest_path, "w", encoding='utf-8') as f:
                f.write("=== AI-POWERED INTERNSHIP READINESS SYSTEM REPORT ===\n\n")
                f.write(f"Student: {user_profile.get('name', 'N/A')}\n")
                f.write(f"Email: {user_profile.get('email', 'N/A')}\n")
                f.write(f"Target Role: {user_profile.get('target_role', 'N/A')}\n")
                f.write(f"Degree: {user_profile.get('degree', 'N/A')} (Year {user_profile.get('year', 'N/A')})\n\n")
                f.write(f"Overall Readiness Score: {readiness.get('overall_score', 0)}/100\n")
                f.write(f"Readiness Level: {readiness.get('readiness_level', 'N/A')}\n\n")
                f.write("=== SKILL GAPS ===\n")
                f.write(f"Match: {gaps.get('match_percentage', 0)}%\n")
                f.write(f"Missing: {', '.join(gaps.get('missing_skills', []))}\n\n")
                f.write("=== WEEKLY LEARNING ROADMAP ===\n")
                for item in roadmap:
                    f.write(f"Week {item.get('week')}: {item.get('task')}\n")
            return True
        except Exception as e2:
            print(f"Fallback generation failed: {e2}")
            return False
