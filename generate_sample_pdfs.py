"""
generate_sample_pdfs.py
Generates realistic sample sales call transcript PDFs for testing.
Run this once to populate data/pdfs/ with demo data.

Usage:
    python generate_sample_pdfs.py
"""

import os
from pathlib import Path

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


TRANSCRIPTS = [
    {
        "filename": "sarah_johnson_call.pdf",
        "lead_name": "Sarah Johnson",
        "content": """SALES CALL TRANSCRIPT
Date: November 15, 2024
Sales Rep: Mike Chen
Lead: Sarah Johnson, VP of Operations, TechFlow Inc.

Mike: Hi Sarah, thanks for jumping on a call today. How are things going at TechFlow?

Sarah: Pretty hectic honestly. We've been dealing with a lot of manual processes that are really slowing us down. That's actually why I wanted to connect.

Mike: Tell me more about that. What's causing the biggest headaches?

Sarah: We're onboarding about 200 new employees per quarter and our current HR software can't handle the volume. We're spending 40 hours a week on manual data entry alone. Our CFO actually approved a budget for a new solution last week — we have $80,000 allocated for this fiscal year.

Mike: Wow, that's a significant pain point. When are you hoping to have something in place?

Sarah: We need it running by January. We have a massive hiring push in Q1 and if we don't have automation by then, we're going to be in serious trouble. I've already got board approval to move fast on this.

Mike: That's great. Our platform handles exactly that. Did you get a chance to look at the demo I sent?

Sarah: Yes! I showed it to our IT Director and she loved the API integration options. Can we schedule a technical deep-dive next week? I want to get procurement involved too because we'd like to move to contract by December 15th.

Mike: Absolutely. What about the other solutions you're evaluating?

Sarah: We looked at two others but honestly yours has the best workflow automation. The price point fits our budget and the implementation timeline works. I just need to make sure our data migration will be smooth.

Mike: Our team handles full migration support. We've done it for 50+ companies your size.

Sarah: That's exactly what I needed to hear. Let's move forward with the technical review. I'll loop in procurement this week.
""",
    },
    {
        "filename": "david_park_call.pdf",
        "lead_name": "David Park",
        "content": """SALES CALL TRANSCRIPT
Date: November 18, 2024
Sales Rep: Lisa Torres
Lead: David Park, IT Manager, MidWest Logistics

Lisa: David, great to connect. You filled out a form about our cloud storage solution?

David: Yeah, I was just doing some research. We're not really in a position to buy anything right now to be honest.

Lisa: That's completely fine. What are you researching for?

David: Our contract with our current vendor is up in 8 months. I'm just starting to understand options. Nothing is urgent.

Lisa: What's working and not working with your current setup?

David: Storage costs are kind of high. But my director hasn't really committed to changing anything. I'd have to convince him first and he's pretty skeptical about cloud.

Lisa: What would it take to get him on board?

David: Honestly I'm not sure. He's old school. Might need a full ROI analysis, but even then — our budgets are frozen until next fiscal year which starts in July. I really can't move on anything before then.

Lisa: Understood. Would it be worth staying in touch for a potential evaluation later in the year?

David: Sure, you can follow up in like March or April. That would be more appropriate timing. Right now I'm literally just window shopping.

Lisa: Makes sense. I'll send some materials and check in then.

David: Yeah that works. No rush on our end at all.
""",
    },
    {
        "filename": "emma_wilson_call.pdf",
        "lead_name": "Emma Wilson",
        "content": """SALES CALL TRANSCRIPT
Date: November 20, 2024
Sales Rep: Ryan O'Brien  
Lead: Emma Wilson, Chief Revenue Officer, ScaleUp SaaS

Ryan: Emma, thanks for the time. I know you mentioned being in the middle of a growth push.

Emma: Yes, we just closed a Series B — $25 million — and we're scaling the sales team from 10 to 40 reps in the next 60 days. We desperately need better sales tooling yesterday.

Ryan: Congratulations on the raise. What's breaking right now?

Emma: Everything related to pipeline management and forecasting. My reps are using spreadsheets. I have zero visibility into deal health. I told the board we'd have this fixed before the new reps start ramping in January.

Ryan: What's your evaluation process like?

Emma: I have full authority to sign contracts up to $200,000 without board approval. I've already shortlisted two vendors including you. I want to make a decision by November 30th. I have a board meeting December 5th and I want to show them the new system.

Ryan: That's a tight timeline. Are you comfortable with that?

Emma: I've done this before. If your demo on Thursday goes well, I'm ready to sign a one-year contract. My team loved the features from the video you sent. The $45,000 price point is well within budget.

Ryan: What are the remaining concerns?

Emma: Just the onboarding timeline and whether your API plays nicely with Salesforce. My Head of Sales is joining the Thursday call. If he gives a thumbs up, we're good to go.

Ryan: We have a Salesforce-certified integration and can have you live in 2 weeks.

Emma: That seals it. See you Thursday. Have the contract ready.
""",
    },
    {
        "filename": "carlos_mendez_call.pdf",
        "lead_name": "Carlos Mendez",
        "content": """SALES CALL TRANSCRIPT
Date: November 22, 2024
Sales Rep: Jennifer Walsh
Lead: Carlos Mendez, Senior Buyer, Global Manufacturing Co.

Jennifer: Carlos, thanks for meeting. You attended our webinar last month?

Carlos: Yes, it was interesting. We're always evaluating vendors but I should be upfront — our procurement process is very formal. Any new vendor has to go through an RFP process that takes about 9 to 12 months.

Jennifer: I appreciate the transparency. What's driving the interest right now?

Carlos: Our current software contract expires in 18 months. I'm starting early research per our policy. There's no burning need right now.

Jennifer: Is there any pain with the current solution?

Carlos: Some complaints from users about the UI but it's not critical. Look, I'd recommend you submit an RFP response when we issue it in Q3 next year. That's the earliest we'd seriously evaluate anyone.

Jennifer: Is there anyone else involved in this decision?

Carlos: Yeah, a committee of 7 people. I'm just one vote. The CIO has final say and he tends to stick with established vendors unless there's a compelling reason to switch.

Jennifer: What would compelling look like?

Carlos: Significant cost savings — like 40% — or features our current vendor simply can't do. We're not there yet based on what I've seen. Your product looks solid but so does the competition.

Jennifer: Understood. I'll make sure we're ready for your RFP process.

Carlos: That's the right approach. No point rushing anything on our end.
""",
    },
    {
        "filename": "nina_patel_call.pdf",
        "lead_name": "Nina Patel",
        "content": """SALES CALL TRANSCRIPT
Date: November 25, 2024
Sales Rep: Tom Bradley
Lead: Nina Patel, CEO, Patel Consulting Group

Tom: Nina, I saw you commented on our LinkedIn post about AI automation. Thanks for reaching out.

Nina: Yes! We've been looking for exactly what you described. We have a very specific problem — our consultants waste about 15 hours a week on report generation. At our billing rate, that's costing us roughly $30,000 a month in lost billable hours.

Tom: That's a clear ROI case. How many consultants do you have?

Nina: 22 right now, growing to 30 by February. I'm the decision-maker here — it's my company. I don't need committee approval.

Tom: What does your timeline look like?

Nina: I'd ideally want this running before the holidays so we can start fresh in January fully optimized. If the pilot goes well this week — I signed up for your trial yesterday — I'd be ready to discuss a company-wide license.

Tom: What's your budget range?

Nina: I've set aside $50,000 for tooling this year and I have room in next year's budget too. Your pricing looked reasonable. I did a quick ROI calc and it pays for itself in month 2.

Tom: How was the trial so far?

Nina: Genuinely impressive. My best consultant said it cut her report time by 70%. I'm going to have everyone try it by Friday and if I get positive feedback, I'll call you Monday to discuss contract terms. I want to move fast — this is a no-brainer for us.

Tom: That's great to hear. I'll have pricing options ready for Monday.

Nina: Perfect. Expect my call.
""",
    },
]


def generate_pdfs(output_dir: str = "./data/pdfs") -> None:
    """Generate sample PDF transcripts into the specified directory."""
    if not REPORTLAB_AVAILABLE:
        print("reportlab not installed. Installing...")
        os.system("pip install reportlab --break-system-packages -q")
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    styles = getSampleStyleSheet()
    body_style = ParagraphStyle(
        "body",
        parent=styles["Normal"],
        fontSize=11,
        leading=16,
        spaceAfter=6,
    )

    for transcript in TRANSCRIPTS:
        filepath = os.path.join(output_dir, transcript["filename"])
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=inch,
        )

        story = []
        for line in transcript["content"].strip().split("\n"):
            if line.strip():
                story.append(Paragraph(line, body_style))
            else:
                story.append(Spacer(1, 8))

        doc.build(story)
        print(f"  ✓ Generated: {filepath}")

    print(f"\n✅ {len(TRANSCRIPTS)} sample PDFs created in {output_dir}/")
    print("\nLeads generated:")
    for t in TRANSCRIPTS:
        print(f"  - {t['lead_name']}")


if __name__ == "__main__":
    generate_pdfs()
