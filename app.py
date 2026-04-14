import streamlit as st
import anthropic
import os

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

st.set_page_config(page_title="Payer Negotiation Tool", page_icon="🏥", layout="centered")

st.title("Free Payer Negotiation Tool")
st.subheader("Get a customized letter and action plan to negotiate better rates with your payers")
st.markdown("---")

with st.form("practice_form"):
    st.markdown("### Your contact information")

    contact_name = st.text_input("Your full name", placeholder="e.g. Dr. Sarah Johnson")
    contact_title = st.text_input("Your title", placeholder="e.g. Practice Owner, Managing Physician")
    contact_email = st.text_input("Email address", placeholder="e.g. sarah@riversidemed.com")
    contact_phone = st.text_input("Phone number", placeholder="e.g. (617) 555-1234")
    practice_address = st.text_input("Practice address", placeholder="e.g. 123 Main St, Boston, MA 02101")

    st.markdown("### Tell us about your practice")

    practice_name = st.text_input("Practice name", placeholder="e.g. Riverside Family Medicine")
    specialty = st.text_input("Specialty", placeholder="e.g. Family Medicine, Pediatrics, Cardiology")
    states = st.multiselect("State(s)", [
        "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
        "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
        "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
        "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
        "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
        "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
        "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
        "Wisconsin", "Wyoming"
    ], placeholder="Select one or more states")
    payers = st.multiselect("Which payers do you want to negotiate with?", [
        "Aetna", "Anthem / Blue Cross Blue Shield", "Cigna", "Humana",
        "UnitedHealthcare", "Medicare Advantage", "Medicaid", "Oscar Health",
        "Molina Healthcare", "Centene", "Other"
    ])
    practice_size = st.selectbox("Practice size", [
        "Solo provider (1 physician)",
        "Small group (2–5 providers)",
        "Mid-size group (6–10 providers)",
        "Large group (10+ providers)"
    ])
    years_in_network = st.number_input("How many years have you been in network with these payers?", min_value=0, max_value=50, value=3)
    patient_volume = st.selectbox("Annual patient volume", [
        "Under 500 patients", "500–1,000 patients", "1,000–3,000 patients",
        "3,000–5,000 patients", "5,000+ patients"
    ])
    current_concern = st.text_area(
        "What's your biggest frustration with your current rates? (optional)",
        placeholder="e.g. Our reimbursement for office visits hasn't changed in 5 years while our costs have increased significantly."
    )

    submitted = st.form_submit_button("Generate My Negotiation Package", type="primary")

if submitted:
    import re
    errors = []
    if not contact_name:
        errors.append("Full name is required")
    if not contact_title:
        errors.append("Title is required")
    if not contact_email or "@" not in contact_email:
        errors.append("A valid email address is required")
    if not contact_phone:
        errors.append("Phone number is required")
    else:
        digits = re.sub(r'\D', '', contact_phone)
        if len(digits) < 10:
            errors.append("Please enter a valid phone number (at least 10 digits)")
    if not practice_address:
        errors.append("Practice address is required")
    if not practice_name:
        errors.append("Practice name is required")
    if not specialty:
        errors.append("Specialty is required")
    if not states:
        errors.append("Please select at least one state")
    if not payers:
        errors.append("Please select at least one payer")

    if errors:
        for error in errors:
            st.error(f"• {error}")
    elif not errors:
        with st.spinner("Building your customized negotiation package..."):

            payers_list = ", ".join(payers)
            states_list = ", ".join(states)

            prompt = f"""You are an expert healthcare contract negotiation consultant helping an independent medical practice negotiate better reimbursement rates with insurance payers.

Practice details:
- Contact name: {contact_name}
- Contact title: {contact_title if contact_title else "Practice Owner"}
- Contact email: {contact_email}
- Contact phone: {contact_phone if contact_phone else "Not provided"}
- Practice address: {practice_address if practice_address else "Not provided"}
- Practice name: {practice_name}
- Specialty: {specialty}
- State(s): {states_list}
- Payers to negotiate with: {payers_list}
- Years in network: {years_in_network}
- Practice size: {practice_size}
- Annual patient volume: {patient_volume}
- Main frustration: {current_concern if current_concern else "Rates have not kept pace with rising costs"}

Please provide two things:

## PART 1: NEGOTIATION LETTER

Write a professional, compelling payer negotiation letter that {practice_name} can send to request a rate review. The letter should:
- Be addressed generically to "Provider Relations / Contract Management Team"
- Include a proper letterhead at the top with the practice name, address, contact name, title, phone, and email
- Open with a strong value statement about the practice's contribution to the payer's network
- Reference specific leverage points: years in network, patient volume, quality of care, cost-efficiency of independent practices vs. hospital systems
- Cite that independent practices are reimbursed significantly less than hospital systems for identical services — often 3-4x less — and frame this as unsustainable
- Make a clear, confident ask for a rate review meeting
- Be professional but assertive — not apologetic
- Be 3-4 paragraphs, ready to send

## PART 2: PAYER CONTACT & NEXT STEPS

For each payer listed ({payers_list}), provide:
1. The correct department/team to contact for rate negotiations (Provider Relations or Contract Management)
2. How to find the specific contact (e.g., look on the payer portal, call provider services line, check your current contract)
3. The best way to submit the letter (portal, email, certified mail)
**Key Negotiation Tip:** One sentence, direct and specific to this payer.

Be specific and actionable. Format Part 2 as a clear list by payer. Do not include any trailing text or section headers after the last payer."""

            response = client.messages.create(
                model="claude-opus-4-6",
                max_tokens=2500,
                messages=[{"role": "user", "content": prompt}]
            )

            result = response.content[0].text

        st.success("Your negotiation package is ready!")
        st.markdown("---")

        # Split and display the two parts
        # Try multiple possible split points
        split_markers = ["## PART 2", "PART 2:", "**PART 2"]
        parts = None
        for marker in split_markers:
            if marker in result:
                parts = result.split(marker, 1)
                break

        if parts and len(parts) == 2:
            letter_section = parts[0]
            # Remove any line containing PART 1 or NEGOTIATION LETTER header
            letter_lines = letter_section.split("\n")
            letter_lines = [
                line for line in letter_lines
                if not any(kw in line.upper() for kw in ["PART 1", "NEGOTIATION LETTER"])
            ]
            letter_section = "\n".join(letter_lines).strip()

            contacts_section = parts[1].strip()
            # Remove any line containing PART 2 or PAYER CONTACT & NEXT STEPS header
            contacts_lines = contacts_section.split("\n")
            contacts_lines = [
                line for line in contacts_lines
                if not any(kw in line.upper() for kw in ["PART 2", "PAYER CONTACT & NEXT STEPS", "PAYER CONTACT AND NEXT STEPS"])
            ]
            contacts_section = "\n".join(contacts_lines).strip()
            # Remove any trailing artifacts
            for trailer in ["GENERAL NEXT", "GENERAL TIPS", "NEXT STEPS:", "---"]:
                if contacts_section.endswith(trailer):
                    contacts_section = contacts_section[:-len(trailer)].strip()

            # CTA before the letter to catch attention
            st.markdown("""
<div style="background-color:#1B4F72;padding:20px 24px;border-radius:10px;margin-bottom:24px;">
    <h3 style="color:white;margin:0 0 8px 0;">Want to maximize your chances of a rate increase?</h3>
    <p style="color:#D6EAF8;margin:0 0 16px 0;">Our team has helped dozens of independent practices successfully negotiate higher reimbursement rates. Book a free 15-minute call and we'll walk through your specific situation before you send anything.</p>
    <a href="https://calendly.com/bracehealth" target="_blank" style="background-color:#F39C12;color:white;padding:10px 20px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:15px;">📅 Book Your Free 15-Min Call →</a>
</div>
""", unsafe_allow_html=True)

            st.markdown("---")

            st.markdown("## Your Negotiation Letter")
            st.markdown("""
<div style="background-color:#FDFEFE;border:1px solid #D5D8DC;border-left:4px solid #1B4F72;border-radius:6px;padding:32px 36px;font-family:Georgia,serif;font-size:15px;line-height:1.8;color:#1a1a1a;margin-bottom:24px;">
""" + letter_section + """
</div>
""", unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("## Your Payer Contacts & Next Steps")
            st.markdown(contacts_section)

        else:
            # Fallback: just show the full result
            st.markdown(result)

        st.markdown("---")
        st.caption("Generated by Brace Health · Questions? Reach us at hello@bracehealth.com")
