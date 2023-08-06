from datetime import date
from turtle import pos

# definition format variables
yes_no = {"validate": "list", "source": ["Yes", "No"]}
bcpnp_case_stream = {
    "validate": "list",
    "source": (
        [
            "EE-Skilled Worker",
            "EE-International Graduate",
            "EE-International Post-Graduate",
            "EE-Health Authority",
            "Skilled Worker",
            "International Graduate",
            "Entry-Level and Semi-Skilled Worker",
            "International Post-Graduate",
            "Health Authority",
        ]
    ),
}
corporate_structure = {
    "validate": "list",
    "source": [
        "Incorporated",
        "Limited Liability Partnership",
        "Extra-provincially-registered",
        "federally-incorporated",
        "Other",
    ],
}
canada_provinces = {
    "validate": "list",
    "source": [
        "AB",
        "BC",
        "MB",
        "NB",
        "NL",
        "NS",
        "NT",
        "NU",
        "ON",
        "PE",
        "QC",
        "SK",
        "YT",
    ],
}
english_french = {
    "validate": "list",
    "source": ["English", "French", "Both", "Neither"],
}
english_or_french = {"validate": "list", "source": ["English", "French"]}
english_french_chinese = {
    "validate": "list",
    "source": ["Chinese", "English", "French"],
}
imm_status = {
    "validate": "list",
    "source": [
        "Citizen",
        "Permanent Resident",
        "Worker",
        "Student",
        "Visitor",
        "Refugess",
        "Other",
    ],
}

salary_payment_way = {
    "validate": "list",
    "source": ["weekly", "bi-weekly", "semi-monthly", "monthly"],
}
wage_unit = {"validate": "list", "source": ["hourly", "weekly", "monthly", "annually"]}
lmia_duration_unit = {"validate": "list", "source": ["months", "years"]}
ot_after_hours_unit = {"validate": "list", "source": ["day", "week"]}
job_duration_unit = {"validate": "list", "source": ["day", "week", "month", "year"]}
purpose_of_lmia = {
    "validate": "list",
    "source": [
        "Supporting Permanent Resident only",
        "Supporting Work Permit only",
        "Supporting both Work Permit and Permanent Resident",
    ],
}
stream_of_lmia = {
    "validate": "list",
    "source": ["EE", "HWS", "LWS", "GTS", "AC", "AG", "CG"],
}
rent_unit = {"validate": "list", "source": ["week", "month"]}
accommodation_type = {
    "validate": "list",
    "source": ["house", "apartment", "dorm", "other"],
}
sex = {"validate": "list", "source": ["Male", "Female"]}
workpermit_type = {
    "validate": "list",
    "source": [
        "Co-op Work Permit",
        "Exemption from Labour Market Impact Assessment",
        "Labour Market Impact Assessment Stream",
        "Live-in Caregiver Program",
        "Open Work Permit",
        "Open work permit for vulnerable workers",
        "Other",
        "Post Graduation Work Permit",
        "Start-up Business Class",
        # "International Experience Canada (IEC)",
    ],
}
marital_status = {
    "validate": "list",
    "source": [
        "Annulled Marriage",
        "Common-Law",
        "Divorced",
        "Married",
        "Separated",
        "Single",
        "Unknown",
        "Widowed",
    ],
}
pre_relationship_type = {"validate": "list", "source": ["Common-Law", "Married"]}
language_test_type = {"validate": "list", "source": ["IELTS", "CELPIP", "TEF", "TCF"]}
education_level = {
    "validate": "list",
    "source": [
        "Doctor",
        "Master",
        "Post-graduate diploma",
        "Bachelor",
        "Associate",
        "Diploma/Certificate",
        "High school",
        "Less than high school",
    ],
}
trade_education_type = {
    "validate": "list",
    "source": [
        "Apprenticeship diploma/certificate",
        "Trade diploma/certificate",
        "Vocational school diploma/certificate",
    ],
}
relationship = {
    "validate": "list",
    "source": [
        "Grand Parent",
        "Parent",
        "Spouse",
        "Child",
        "Grand Child",
        "Sibling",
        "Aunt",
        "Uncle",
        "Niece",
        "Newphew",
        "Friend",
    ],
}
family_relationship = {
    "validate": "list",
    "source": ["Spouse", "Son", "Daughter", "Mother", "Father", "Brother", "Sister"],
}
pr_imm_program = {"validate": "list", "source": ["Economic", "Family"]}
pr_imm_category = {
    "validate": "list",
    "source": [
        "Provincial Nominee Program (PNP)",
        "Atlantic Immigration Program",
        "Spouse",
        "Common-law Partner",
        "Dependent Child",
        "Other Relative",
    ],
}
pr_imm_under = {
    "validate": "list",
    "source": [
        "Spouse or common-law partner in Canada class",
        "Family class (outside Canada)",
    ],
}
interview_canadian_status = {
    "validate": "list",
    "source": ["Citizen", "PR", "Foreigner", "Unknown"],
}
tr_application_purpose = {
    "validate": "list",
    "source": ["apply or extend", "restore status", "TRP"],
}
sp_paid_person = {"validate": "list", "source": ["Myself", "Parents", "Other"]}
vr_application_purpose = {
    "validate": "list",
    "source": ["apply or extend visitor record", "restore status as visotor", "TRP"],
}
sp_in_application_purpose = {
    "validate": "list",
    "source": ["apply or extend study permit", "restore status as student", "TRP"],
}
sp_apply_wp_type = {
    "validate": "list",
    "source": ["Co-op Work Permit", "Open Work Permit", "Post Graduation Work Permit"],
}
wp_in_application_purpose = {
    "validate": "list",
    "source": [
        "apply WP for same employer",
        "apply WP for new employer",
        "restore status as worker",
        "TRP with same employer",
        "TRP with new employer",
    ],
}
wp_apply_wp_type = {
    "validate": "list",
    "source": [
        "Co-op Work Permit",
        "Exemption from Labour Market Impact Assessment",
        "Labour Market Impact Assessment Stream",
        "Live-in Caregiver Program",
        "Open Work Permit",
        "Open Work Permit for Vulnerable Workers",
        "Other",
        "Post Graduation Work Permit",
        "Start-up Business Class",
    ],
}
visa_application_purpose = {"validate": "list", "source": ["Visitor Visa", "Transit"]}
tr_original_purpose = {
    "validate": "list",
    "source": ["Business", "Tourism", "Study", "Work", "Other", "Family Visit"],
}

visit_purpose_5257 = {
    "validate": "list",
    "source": [
        "Business",
        "Tourism",
        "Short-Term Studies",
        "Returning Student",
        "Returning Worker",
        "Super Visa: For Parents or Grandparents",
        "Other",
        "Family Visit",
    ],
}

date_format = {
    "validate": "date",
    "criteria": ">",
    "value": date(1800, 1, 1),
    "input_title": "请输入日期",
    "input_message": "格式:1999-06-30",
}
positive_int = {
    "validate": "integer",
    "criteria": ">",
    "value": 0,
    "input_title": "请输入整数:",
    "input_message": "必须是大于0",
}
positive_int_include_zero = {
    "validate": "integer",
    "criteria": ">=",
    "value": 0,
    "input_title": "请输入整数:",
    "input_message": "必须是大于等于0",
}
positive_int_decimal = {
    "validate": "decimal",
    "criteria": ">",
    "value": 0,
    "input_title": "请输入整数或小数:",
    "input_message": "必须是大于0",
}

int_decimal = {
    "validate": "decimal",
    "criteria": "between",
    "minimum": -100000000000,
    "maximum": 100000000000,
    "input_title": "请输入整数或小数:",
    "input_message": "无论正数负数",
}

eye_color = {
    "validate": "list",
    "source": ["Black", "Brown", "Blue", "Green"],
}

employment_type = {
    "validate": "list",
    "source": ["Employed", "Self-employed"],
}

relationship_to_pa = {
    "validate": "list",
    "source": [
        "Adopted Child",
        "Child",
        "Common-law partner",
        "Grandchild",
        # "Other": "5: 85",
        "Spouse",
        "Step-Child",
        "Step-Grandchild",
        "Parent",
        "Adoptive Parent",
    ],
}

dependant_type = {
    "validate": "list",
    "source": [
        "Type A Dependant",
        "Type B Dependant",
        "Type C Dependant",
    ],
}

eca_supplier = {
    "validate": "list",
    "source": [
        "Comparative Education Service - University of Toronto School of Continuing Studies",
        "International Credential Assessment Service of Canada",
        "World Education Services",
        "International Qualifications Assessment Service",
        "International Credential Evaluation Service",
        # "Medical Council of Canada (for Doctors)",
        # "Pharmacy Examining Board of Canada (for Pharmacists)",
    ],
}

language_remark = {
    "validate": "list",
    "source": ["Test Score", "Estimation"],
}

cap_exemption_type = {
    "validate": "list",
    "source": [
        "Caregiver positions in a health care facility (NOC 3012, 3233, and 3413)",
        "On-farm primary agricultural positions",
        "Position for the Global Talent Stream",
        "Position(s) is/are highly mobile",
        "Position(s) is/are truly temporary",
        "Seasonal 270-day exemption",
    ],
}


months = {
    "validate": "list",
    "source": [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ],
}

waive_creteria = {
    "validate": "list",
    "source": [
        "Caregiver positions in health care institutions",
        "Limited duration positions",
        "On-farm primary agricultural positions",
        "Positions within a specialized occupation",
        "Unique skills or traits",
    ],
}


# Validation data
validation = {
    # BCPNP
    "info-bcpnp": {
        "has_applied_before": yes_no,
        "case_stream": bcpnp_case_stream,
        "submission_date": date_format,
        "q1": yes_no,
        "q2": yes_no,
        "q3": yes_no,
        "q4": yes_no,
        "q5": yes_no,
        "q6": yes_no,
        "q7": yes_no,
    },
    # Employer
    "info-general": {
        "ft_employee_number": positive_int_include_zero,
        "pt_employee_number": positive_int_include_zero,
        "establish_date": date_format,
        "has_lmia_approved": yes_no,
        "corporate_structure": corporate_structure,
        "num_pnps": positive_int,
        "num_pnps_approved": positive_int,
        "num_pnps_in_process": positive_int_include_zero,
        "when_lmia_approved": date_format,
        "last_revenue": positive_int_decimal,
        "last_profit": int_decimal,
        "retained_earning": int_decimal,
        "before_last_revenue": int_decimal,
        "before_last_profit": int_decimal,
        "has_jobbank_account": yes_no,
        "has_bc_employer_certificate": yes_no,
    },
    "table-eraddress": {"province": canada_provinces},
    "table-contact": {
        "preferred_language": english_french,
        "province": canada_provinces,
    },
    "table-finance": {
        "year": positive_int,
    },
    "table-employee_list": {
        "wage": positive_int_decimal,
        "hours_per_week": positive_int_decimal,
        "employment_start_date": date_format,
        "immigration_status": imm_status,
    },
    "info-position": {
        "is_new": yes_no,
        "worked_working": yes_no,
        "under_cba": yes_no,
        "has_same": yes_no,
        "lowest": positive_int_decimal,
        "highest": positive_int_decimal,
        "lmia_refused": yes_no,
        "has_same_number": positive_int,
        "vacancies_number": positive_int_include_zero,
        "laidoff_with12": positive_int_include_zero,
        "laidoff_current": positive_int_include_zero,
    },
    "info-joboffer": {
        "license_request": yes_no,
        "license_met": yes_no,
        "union": yes_no,
        "atypical_schedule": yes_no,
        "days": positive_int_decimal,
        "hours": positive_int_decimal,
        "payment_way": salary_payment_way,
        "wage_unit": wage_unit,
        "wage_rate": positive_int_decimal,
        "ot_ratio": positive_int_decimal,
        "ot_after_hours": positive_int_decimal,
        "ot_after_hours_unit": ot_after_hours_unit,
        "is_working": yes_no,
        "work_start_date": date_format,
        "permanent": yes_no,
        "job_duration": positive_int_decimal,
        "job_duration_unit": job_duration_unit,
        "has_probation": yes_no,
        "probation_duration": positive_int_decimal,
        "disability_insurance": yes_no,
        "dental_insurance": yes_no,
        "empolyer_provided_persion": yes_no,
        "extended_medical_insurance": yes_no,
        "english_french": yes_no,
        "other_language_required": yes_no,
        "oral": english_or_french,
        "writing": english_or_french,
        "offer_date": date_format,
        "vacation_pay_weeks": positive_int_decimal,
        "vacation_pay_percentage": positive_int_decimal,
        "education_level": education_level,
        "is_trade": yes_no,
        "trade_type": trade_education_type,
    },
    # LMIA
    "info-lmiacase": {
        "area_index": positive_int,
        "province_index": positive_int,
        "unemploy_rate": positive_int_decimal,
        "area_median_wage": positive_int_decimal,
        "noc_outlook": positive_int,
        "provincial_median_wage": positive_int_decimal,
        "is_in_10_days_priority": yes_no,
        "top10_wages": positive_int_decimal,
        "is_waived_from_advertisement": yes_no,
        "purpose_of_lmia": purpose_of_lmia,
        "stream_of_lmia": stream_of_lmia,
        "has_another_employer": yes_no,
        "number_of_tfw": positive_int,
        "duration_number": positive_int,
        "duration_unit": lmia_duration_unit,
        "has_attestation": yes_no,
        "use_jobbank": yes_no,
    },
    "info-lmi": {
        "laid_off_in_12": yes_no,
        "is_work_sharing": yes_no,
        "labour_dispute": yes_no,
        "canadian_lost_job": yes_no,
        "laid_off_canadians": positive_int,
        "laid_off_tfw": positive_int,
    },
    "info-emp5624": {
        "hird_canadian": yes_no,
        "why_not": yes_no,
        "has_active_lmbp": yes_no,
    },
    "table-emp5624lmbp": {"start_date": date_format, "end_date": date_format},
    "info-emp5626": {
        "is_seasonal": yes_no,
        "start_month": months,
        "end_month": months,
        "last_canadian_number": positive_int,
        "last_tfw_number": positive_int,
        "current_canadian_number": positive_int,
        "current_tfw_number": positive_int,
        "tp_waivable": yes_no,
        "has_finished_tp": yes_no,
        "waive_creteria": waive_creteria,
    },
    "info-emp5627": {
        "named": yes_no,
        "is_in_seasonal_industry": yes_no,
        "provide_accommodation": yes_no,
        "rent_unit": rent_unit,
        "accommodation_type": accommodation_type,
        "rent_amount": positive_int_include_zero,
        "bedrooms": positive_int,
        "people": positive_int,
        "bathrooms": positive_int,
        "cap_exempted": yes_no,
        "which_exemption": cap_exemption_type,
    },
    # PA
    "info-personal": {
        "sex": sex,
        "height": positive_int,
        "eye_color": eye_color,
        "dob": date_format,
        "english_french": english_french,
        "which_one_better": english_or_french,
        "net_asset": positive_int,
        "liquid_asset": positive_int,
        "language_test": yes_no,
        "did_eca": yes_no,
        "intended_province": canada_provinces,
        "primary_school_years": positive_int,
        "secondary_school_years": positive_int,
        "post_secondary_school_years": positive_int,
        "other_school_years": positive_int,
        "relationship_to_pa": relationship_to_pa,
        "accompany_to_canada": yes_no,
        "dependant_type": dependant_type,
        "eca_supplier": eca_supplier,
        "ita_assessed": yes_no,
    },
    "table-personid": {"issue_date": date_format, "expiry_date": date_format},
    "info-status": {
        "current_country_status": imm_status,
        "current_workpermit_type": workpermit_type,
        "has_vr": yes_no,
        "current_status_start_date": date_format,
        "current_status_end_date": date_format,
        "last_entry_date": date_format,
    },
    "info-ee": {"ee_expiry_date": date_format, "ee_score": positive_int},
    "info-marriage": {
        "marital_status": marital_status,
        "married_date": date_format,
        "sp_in_canada": yes_no,
        "sp_language_type": language_test_type,
        "sp_language_r": positive_int_decimal,
        "sp_language_w": positive_int_decimal,
        "sp_language_l": positive_int_decimal,
        "sp_language_s": positive_int_decimal,
        "sp_canada_status": imm_status,
        "previous_married": yes_no,
        "pre_relationship_type": pre_relationship_type,
        "pre_sp_dob": date_format,
        "pre_start_date": date_format,
        "pre_end_date": date_format,
    },
    "table-assumption": {
        "hourly_rate": positive_int_decimal,
        "start_date": date_format,
        "end_date": date_format,
        "work_permit_type": workpermit_type,
        "province": canada_provinces,
    },
    "table-phone": {"number": positive_int},
    "table-history": {"start_date": date_format, "end_date": date_format},
    "table-addresshistory": {"start_date": date_format, "end_date": date_format},
    "table-language": {
        "test_date": date_format,
        "report_date": date_format,
        "reading": positive_int_decimal,
        "writting": positive_int_decimal,
        "listening": positive_int_decimal,
        "speaking": positive_int_decimal,
    },
    "table-education": {
        "start_date": date_format,
        "end_date": date_format,
        "education_level": education_level,
        "is_trade": yes_no,
        "academic_year": positive_int_decimal,
        "graduate_date": date_format,
    },
    "table-employment": {
        "start_date": date_format,
        "end_date": date_format,
        "weekly_hours": positive_int_decimal,
        "employment_type": employment_type,
        "share_percentage": positive_int_decimal,
        "bcpnp_qualified": yes_no,
        "ee_qualified": yes_no,
    },
    "table-canadarelative": {
        "province": canada_provinces,
        "status": imm_status,
        "relationship": relationship,
        "sex": sex,
        "age": positive_int,
        "years_in_canada": positive_int,
    },
    "table-family": {
        "marital_status": marital_status,
        "date_of_birth": date_format,
        "relationship": family_relationship,
        "date_of_death": date_format,
        "accompany_to_canada": yes_no,
    },
    "table-cor": {
        "start_date": date_format,
        "end_date": date_format,
        "status": imm_status,
    },
    "table-travel": {
        "start_date": date_format,
        "end_date": date_format,
        "length": positive_int,
    },
    "table-military": {"start_date": date_format, "end_date": date_format},
    "table-illtreatment": {"start_date": date_format, "end_date": date_format},
    "table-member": {"start_date": date_format, "end_date": date_format},
    "table-government": {"start_date": date_format, "end_date": date_format},
    # PR
    "info-prcase": {
        "submission_date": date_format,
        "last_entry_date": date_format,
        "imm_program": pr_imm_program,
        "imm_category": pr_imm_category,
        "imm_under": pr_imm_under,
        "communication_language": english_or_french,
        "interview_language": english_french_chinese,
        "need_translator": yes_no,
        "intended_province": canada_provinces,
        "has_csq": yes_no,
        "consent_of_info_release": yes_no,
        "number": positive_int,
    },
    "info-background": {
        "q1a": yes_no,
        "q1b": yes_no,
        "q1c": yes_no,
        "q2a": yes_no,
        "q2b": yes_no,
        "q2c": yes_no,
        "q3a": yes_no,
        "q4a": yes_no,
        "q5": yes_no,
        "q6": yes_no,
    },
    # Recruitment
    "table-advertisement": {"start_date": date_format, "end_date": date_format},
    "table-interviewrecord": {
        "canadian_status": interview_canadian_status,
        "interviewed": yes_no,
        "offered": yes_no,
        "accepted": yes_no,
    },
    "info-recruitmentsummary": {
        "reply2apply": yes_no,
        "emails_for_making_interview": yes_no,
        "interview_record": yes_no,
        "interview_process_evidence": yes_no,
        "emails_for_certificates": yes_no,
        "emais_for_references": yes_no,
        "reference_checked": yes_no,
        "reference_check_evidence": yes_no,
        "joboffer_email": yes_no,
        "joboffer_email_reply": yes_no,
        "after_offer_coomunication": yes_no,
        "interview_date": date_format,
    },
    # TR
    "info-trcasein": {
        "service_in": english_french,
        "original_entry_date": date_format,
        "most_recent_entry_date": date_format,
        "original_purpose": tr_original_purpose,
        "is_spouse_canadian": yes_no,
        "consent_of_info_release": yes_no,
        "submission_date": date_format,
    },
    "info-trcase": {
        "service_in": english_french,
        "same_as_cor": yes_no,
        "applying_status": imm_status,
        "applying_start_date": date_format,
        "applying_end_date": date_format,
        "submission_date": date_format,
    },
    "info-sp": {
        "study_level": education_level,
        "province": canada_provinces,
        "paid_person": sp_paid_person,
        "start_date": date_format,
        "end_date": date_format,
        "tuition_cost": positive_int_decimal,
        "room_cost": positive_int_decimal,
        "other_cost": positive_int_decimal,
        "fund_available": positive_int_decimal,
    },
    "info-vrincanada": {
        "application_purpose": vr_application_purpose,
        "visit_purpose": tr_original_purpose,
        "start_date": date_format,
        "end_date": date_format,
        "funds_available": positive_int_decimal,
        "paid_person": sp_paid_person,
    },
    "info-spincanada": {
        "application_purpose": sp_in_application_purpose,
        "study_level": education_level,
        "province": canada_provinces,
        "paid_person": sp_paid_person,
        "apply_work_permit": yes_no,
        "work_permit_type": sp_apply_wp_type,
        "start_date": date_format,
        "end_date": date_format,
        "tuition_cost": positive_int_decimal,
        "room_cost": positive_int_decimal,
        "other_cost": positive_int_decimal,
        "fund_available": positive_int_decimal,
        "expiry_date": date_format,
    },
    "info-wpincanada": {
        "application_purpose": wp_in_application_purpose,
        "work_province": canada_provinces,
        "work_permit_type": wp_apply_wp_type,
        "start_date": date_format,
        "end_date": date_format,
        "pnp_certificated": yes_no,
        "expiry_date": date_format,
    },
    "info-wp": {
        "work_province": canada_provinces,
        "work_permit_type": wp_apply_wp_type,
        "start_date": date_format,
        "end_date": date_format,
    },
    "info-visa": {
        "application_purpose": visa_application_purpose,
        "visit_purpose": visit_purpose_5257,
        "start_date": date_format,
        "end_date": date_format,
        "funds_available": positive_int_decimal,
    },
    "info-incanadacommon": {
        "original_purpose": tr_original_purpose,
        "original_entry_date": date_format,
        "most_recent_entry_date": date_format,
    },
    "info-trbackground": {
        "q1a": yes_no,
        "q1b": yes_no,
        "q2a": yes_no,
        "q2b": yes_no,
        "q2c": yes_no,
        "q3a": yes_no,
        "q4a": yes_no,
        "q5": yes_no,
        "q6": yes_no,
    },
    # PR
    "info-prbackground": {
        "q1": yes_no,
        "q2": yes_no,
        "q3": yes_no,
        "q4": yes_no,
        "q5": yes_no,
        "q6": yes_no,
        "q7": yes_no,
        "q8": yes_no,
        "q9": yes_no,
        "q10": yes_no,
        "q11": yes_no,
    },
}
