# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from sqlalchemy.orm.exc import NoResultFound
from uw_person_client.clients import AbstractUWPersonClient
from uw_person_client.databases.uwpds import UWPDS
from uw_person_client.exceptions import PersonNotFoundException
from uw_person_client.components import Person, Student, Employee, \
    Transcript, Major, Sport, Adviser, Term, Transfer, Ethnicity


class UWPersonClient(AbstractUWPersonClient):

    """
    Public methods
    """

    def __init__(self):
        self.DB = UWPDS()

    def get_person_by_uwnetid(self, uwnetid, **kwargs):
        sqla_person = self.DB.session.query(self.DB.HistoricalPerson).filter(
            self.DB.HistoricalPerson.prior_uwnetid == uwnetid).first()
        if not sqla_person:
            raise PersonNotFoundException()
        return self._map_person(sqla_person, **kwargs)

    def get_person_by_uwregid(self, uwregid, **kwargs):
        sqla_person = self.DB.session.query(self.DB.HistoricalPerson).filter(
            self.DB.HistoricalPerson.prior_uwregid == uwregid).first()
        if not sqla_person:
            raise PersonNotFoundException()
        return self._map_person(sqla_person, **kwargs)

    def get_person_by_student_number(self, student_number, **kwargs):
        sqla_person = self.DB.session.query(self.DB.Person).join(
            self.DB.Student).filter(
            self.DB.Student.student_number == student_number).one_or_none()
        if not sqla_person:
            raise PersonNotFoundException()
        return self._map_person(sqla_person, **kwargs)

    def get_person_by_system_key(self, system_key, **kwargs):
        sqla_person = self.DB.session.query(self.DB.Person).join(
            self.DB.Student).filter(
            self.DB.Student.system_key == system_key).one_or_none()
        if not sqla_person:
            raise PersonNotFoundException()
        return self._map_person(sqla_person, **kwargs)

    def get_persons(self, page=None, page_size=None, **kwargs):
        sqla_persons = self.DB.session.query(self.DB.Person)
        return self._get_page(sqla_persons,
                              self._map_person,
                              page=page,
                              page_size=page_size,
                              **kwargs)

    def get_registered_students(self, page=None, page_size=None, **kwargs):
        sqla_persons = self.DB.session.query(self.DB.Person).join(
            self.DB.Student).filter(
                self.DB.Student.enroll_status_code == '12'  # registered
        )
        return self._get_page(sqla_persons,
                              self._map_person,
                              page=page,
                              page_size=page_size,
                              **kwargs)

    def get_active_students(self, page=None, page_size=None, **kwargs):
        sqla_persons = self.DB.session.query(self.DB.Person).filter(
            self.DB.Person._is_active_student == True)  # noqa
        return self._get_page(sqla_persons,
                              self._map_person,
                              page=page,
                              page_size=page_size,
                              **kwargs)

    def get_active_employees(self, page=None, page_size=None, **kwargs):
        sqla_persons = self.DB.session.query(self.DB.Person).filter(
            self.DB.Person._is_active_employee == True)  # noqa
        return self._get_page(sqla_persons,
                              self._map_person,
                              page=page,
                              page_size=page_size,
                              **kwargs)

    def get_advisers(self, advising_program=None, **kwargs):
        sqla_persons = self.DB.session.query(self.DB.Person).join(
            self.DB.Employee).join(self.DB.Adviser)
        if advising_program:
            sqla_persons = sqla_persons.filter(
                self.DB.Adviser.advising_program == advising_program)
        return [self._map_person(item, **kwargs)for item in sqla_persons.all()]

    def get_persons_by_adviser_netid(self, uwnetid, **kwargs):
        sqla_adviser = self.DB.session.query(self.DB.Adviser).join(
            self.DB.Employee).join(self.DB.Person).filter(
            self.DB.Person.uwnetid == uwnetid).one()
        sqla_persons = self.DB.session.query(self.DB.Person).join(
            self.DB.Student).join(self.DB.StudentToAdviser).join(
            self.DB.Adviser).filter(self.DB.Adviser.id == sqla_adviser.id)
        return [self._map_person(item, **kwargs)for item in sqla_persons.all()]

    def get_persons_by_adviser_regid(self, uwregid, **kwargs):
        sqla_adviser = self.DB.session.query(self.DB.Adviser).join(
            self.DB.Employee).join(self.DB.Person).filter(
            self.DB.Person.uwregid == uwregid).one()
        sqla_persons = self.DB.session.query(self.DB.Person).join(
            self.DB.Student).join(self.DB.StudentToAdviser).join(
            self.DB.Adviser).filter(self.DB.Adviser.id == sqla_adviser.id)
        return [self._map_person(item, **kwargs)for item in sqla_persons.all()]

    """
    Private Methods
    """

    def _get_page(self, query, mapper, page=None, page_size=None, **kwargs):
        """
        Returns results for a single page of data. If page and page_size are
        not specified, all results are returned
        """
        if page is not None and page_size is not None:
            # limit results to page
            query = query.limit(page_size).offset(
                (page - 1) * page_size)
        return [mapper(item, **kwargs)for item in query.all()]

    def _map_person(self, sqla_person,
                    include_employee=True,
                    include_student=True,
                    include_student_transcripts=True,
                    include_student_transfers=True,
                    include_student_sports=True,
                    include_student_advisers=True,
                    include_student_majors=True,
                    include_student_intended_majors=True,
                    include_student_pending_majors=True,
                    include_student_requested_majors=True):
        person = Person()
        person.uwnetid = sqla_person.uwnetid
        person.uwregid = sqla_person.uwregid
        prior_uwnetids = self.DB.session.query(self.DB.PriorUWNetID).filter(
            self.DB.PriorUWNetID.person_id == sqla_person.id).all()
        person.prior_uwnetids = [pni.uwnetid for pni in prior_uwnetids]
        prior_uwregids = self.DB.session.query(self.DB.PriorUWRegID).filter(
            self.DB.PriorUWRegID.person_id == sqla_person.id).all()
        person.prior_uwregids = [pri.uwregid for pri in prior_uwregids]
        person.pronouns = sqla_person.pronouns
        person.full_name = sqla_person.full_name
        person.display_name = sqla_person.display_name
        person.first_name = sqla_person.first_name
        person.surname = sqla_person.surname
        person.preferred_first_name = sqla_person.preferred_first_name
        person.preferred_middle_name = \
            sqla_person.preferred_middle_name
        person.preferred_surname = sqla_person.preferred_surname
        person.whitepages_publish = sqla_person.whitepages_publish
        person.active_student = sqla_person._is_active_student
        person.active_employee = sqla_person._is_active_employee

        if include_student:
            try:
                sqla_student = self.DB.session.query(self.DB.Student).filter(
                    self.DB.Student.person_id == sqla_person.id).one()
                person.student = self._map_student(
                    sqla_student,
                    include_student_transcripts=include_student_transcripts,
                    include_student_transfers=include_student_transfers,
                    include_student_sports=include_student_sports,
                    include_student_advisers=include_student_advisers,
                    include_student_majors=include_student_majors,
                    include_student_intended_majors=include_student_intended_majors,  # noqa
                    include_student_pending_majors=include_student_pending_majors,  # noqa
                    include_student_requested_majors=include_student_requested_majors)  # noqa
            except NoResultFound:
                pass

        if include_employee:
            try:
                sqla_employee = self.DB.session.query(self.DB.Employee).filter(
                    self.DB.Employee.person_id == sqla_person.id).one()
                person.employee = self._map_employee(sqla_employee)
            except NoResultFound:
                pass

        return person

    def _map_student(self, sqla_student,
                     include_student_transcripts=True,
                     include_student_transfers=True,
                     include_student_sports=True,
                     include_student_advisers=True,
                     include_student_majors=True,
                     include_student_intended_majors=True,
                     include_student_pending_majors=True,
                     include_student_requested_majors=True):
        student = Student()

        student.system_key = sqla_student.system_key
        student.student_number = sqla_student.student_number
        student.application_status_code = sqla_student.application_status_code
        student.application_status_desc = sqla_student.application_status_desc
        student.application_type_code = sqla_student.application_type_code
        student.application_type_desc = sqla_student.application_type_desc
        student.applied_to_graduate_yr_qtr_desc = \
            sqla_student.applied_to_graduate_yr_qtr_desc
        student.applied_to_graduate_yr_qtr_id = \
            sqla_student.applied_to_graduate_yr_qtr_id
        student.asuwind = sqla_student.asuwind
        student.birth_city = sqla_student.birth_city
        student.birth_country = sqla_student.birth_country
        student.birth_state = sqla_student.birth_state
        student.birthdate = sqla_student.birthdate
        student.campus_code = sqla_student.campus_code
        student.campus_desc = sqla_student.campus_desc
        student.child_of_alumni = sqla_student.child_of_alumni
        student.citizen_country = sqla_student.citizen_country
        student.class_code = sqla_student.class_code
        student.class_desc = sqla_student.class_desc
        student.cumulative_gpa = sqla_student.cumulative_gpa
        student.directory_release_ind = sqla_student.directory_release_ind
        student.disability_ind = sqla_student.disability_ind
        student.emergency_email = sqla_student.emergency_email
        student.emergency_name = sqla_student.emergency_name
        student.emergency_phone = sqla_student.emergency_phone
        student.enroll_status_code = sqla_student.enroll_status_code
        student.exemption_code = sqla_student.exemption_code
        student.exemption_desc = sqla_student.exemption_desc
        student.external_email = sqla_student.external_email
        student.first_generation_4yr_ind = \
            sqla_student.first_generation_4yr_ind
        student.first_generation_ind = sqla_student.first_generation_ind
        student.gender = sqla_student.gender
        student.high_school_gpa = sqla_student.high_school_gpa
        student.high_school_graduation_date = \
            sqla_student.high_school_graduation_date
        student.hold_office_name_combined = \
            sqla_student.hold_office_name_combined
        student.hold_reason_desc_combined = \
            sqla_student.hold_reason_desc_combined
        student.honors_program_code = sqla_student.honors_program_code
        student.honors_program_ind = sqla_student.honors_program_ind
        student.iss_perm_resident_country = \
            sqla_student.iss_perm_resident_country
        student.jr_col_gpa = sqla_student.jr_col_gpa
        student.last_enrolled_yr_qtr_desc = \
            sqla_student.last_enrolled_yr_qtr_desc
        student.last_enrolled_yr_qtr_id = sqla_student.last_enrolled_yr_qtr_id
        student.local_addr_4digit_zip = sqla_student.local_addr_4digit_zip
        student.local_addr_5digit_zip = sqla_student.local_addr_5digit_zip
        student.local_addr_city = sqla_student.local_addr_city
        student.local_addr_country = sqla_student.local_addr_country
        student.local_addr_line1 = sqla_student.local_addr_line1
        student.local_addr_line2 = sqla_student.local_addr_line2
        student.local_addr_postal_code = sqla_student.local_addr_postal_code
        student.local_addr_state = sqla_student.local_addr_state
        student.local_phone_number = sqla_student.local_phone_number
        student.new_continuing_returning_code = \
            sqla_student.new_continuing_returning_code
        student.new_continuing_returning_desc = \
            sqla_student.new_continuing_returning_desc
        student.parent_name = sqla_student.parent_name
        student.perm_addr_4digit_zip = sqla_student.perm_addr_4digit_zip
        student.perm_addr_5digit_zip = sqla_student.perm_addr_5digit_zip
        student.perm_addr_city = sqla_student.perm_addr_city
        student.perm_addr_country = sqla_student.perm_addr_country
        student.perm_addr_line1 = sqla_student.perm_addr_line1
        student.perm_addr_line2 = sqla_student.perm_addr_line2
        student.perm_addr_postal_code = sqla_student.perm_addr_postal_code
        student.perm_addr_state = sqla_student.perm_addr_state
        student.previous_institution_name = \
            sqla_student.previous_institution_name
        student.previous_institution_type = \
            sqla_student.previous_institution_type
        student.previous_institution_type_desc = \
            sqla_student.previous_institution_type_desc
        student.record_load_dttm = sqla_student.record_load_dttm
        student.record_update_dttm = sqla_student.record_update_dttm
        student.reg_first_yr_qtr_desc = sqla_student.reg_first_yr_qtr_desc
        student.reg_first_yr_qtr_id = sqla_student.reg_first_yr_qtr_id
        student.registered_in_quarter = sqla_student.registered_in_quarter
        student.registration_hold_ind = sqla_student.registration_hold_ind
        student.resident_code = sqla_student.resident_code
        student.resident_desc = sqla_student.resident_desc
        student.special_program_code = sqla_student.special_program_code
        student.special_program_desc = sqla_student.special_program_desc
        student.sr_col_gpa = sqla_student.sr_col_gpa
        student.student_email = sqla_student.student_email
        student.total_credits = sqla_student.total_credits
        student.total_deductible_credits = \
            sqla_student.total_deductible_credits
        student.total_extension_credits = sqla_student.total_extension_credits
        student.total_grade_attempted = sqla_student.total_grade_attempted
        student.total_grade_points = sqla_student.total_grade_points
        student.total_lower_div_transfer_credits = \
            sqla_student.total_lower_div_transfer_credits
        student.total_non_graded_credits = \
            sqla_student.total_non_graded_credits
        student.total_registered_credits = \
            sqla_student.total_registered_credits
        student.total_transfer_credits = \
            sqla_student.total_transfer_credits
        student.total_uw_credits = sqla_student.total_uw_credits
        student.total_upper_div_transfer_credits = \
            sqla_student.total_upper_div_transfer_credits
        student.veteran_benefit_code = sqla_student.veteran_benefit_code
        student.veteran_benefit_desc = sqla_student.veteran_benefit_desc
        student.veteran_desc = sqla_student.veteran_desc
        student.visa_type = sqla_student.visa_type

        # map academic term
        student.academic_term = self._map_term(sqla_student.academic_term)

        student.admitted_for_yr_qtr_desc = \
            sqla_student.admitted_for_yr_qtr_desc
        student.admitted_for_yr_qtr_id = sqla_student.admitted_for_yr_qtr_id

        # map ethnicity
        student.ethnicities = []
        for ethnicity in sqla_student.ethnicities:
            ethnicity = self._map_ethnicity(ethnicity)
            student.ethnicities.append(ethnicity)

        if include_student_majors:
            # map majors
            student.majors = []
            for major in sqla_student.major:
                major = self._map_major(major)
                student.majors.append(major)

        if include_student_pending_majors:
            # map pending majors
            student.pending_majors = []
            for major in sqla_student.pending_major:
                major = self._map_major(major)
                student.pending_majors.append(major)

        if include_student_requested_majors:
            # map requested majors
            student.requested_majors = []
            for major in sqla_student.requested_major:
                major = self._map_major(major)
                student.requested_majors.append(major)

        if include_student_intended_majors:
            # map intended majors
            student.intended_majors = []
            for major in sqla_student.intended_major:
                major = self._map_major(major)
                student.intended_majors.append(major)

        if include_student_sports:
            # map sports
            student.sports = []
            for sport in sqla_student.sport:
                sport = self._map_sport(sport)
                student.sports.append(sport)

        if include_student_advisers:
            # map advisers
            student.advisers = []
            for adviser in sqla_student.adviser:
                adviser_person = self._map_person(adviser.employee.person,
                                                  include_student=False)
                student.advisers.append(adviser_person)

        if include_student_transcripts:
            # map transcripts
            student.transcripts = []
            for transcript in sqla_student.transcript:
                transcript = self._map_transcript(transcript)
                student.transcripts.append(transcript)

        if include_student_transfers:
            # map transfers
            student.transfers = []
            for transfer in sqla_student.transfer:
                transfer = self._map_transfer(transfer)
                student.transfers.append(transfer)

        return student

    def _map_employee(self, sqla_employee):
        employee = Employee()
        employee.employee_number = sqla_employee.employee_number
        employee.employee_affiliation_state = \
            sqla_employee.employee_affiliation_state
        employee.email_addresses = sqla_employee.email_addresses
        employee.home_department = sqla_employee.home_department
        employee.primary_title = sqla_employee.title
        employee.primary_department = sqla_employee.department

        if sqla_employee.adviser:
            employee.adviser = self._map_adviser(sqla_employee.adviser)

        return employee

    def _map_adviser(self, sqla_adviser):
        adviser = Adviser()
        adviser.is_dept_adviser = sqla_adviser.is_dept_adviser
        adviser.advising_email = sqla_adviser.advising_email
        adviser.advising_phone_number = \
            sqla_adviser.advising_phone_number
        adviser.advising_program = sqla_adviser.advising_program
        adviser.advising_pronouns = sqla_adviser.advising_pronouns
        adviser.booking_url = sqla_adviser.booking_url
        return adviser

    def _map_sport(self, sqla_sport):
        sport = Sport()
        sport.sport_code = sqla_sport.sport_code
        return sport

    def _map_ethnicity(self, sqla_ethnicity):
        ethnicity = Ethnicity()
        ethnicity.assigned_ethnic_code = sqla_ethnicity.assigned_ethnic_code
        ethnicity.assigned_ethnic_desc = sqla_ethnicity.assigned_ethnic_desc
        ethnicity.assigned_ethnic_group_desc = \
            sqla_ethnicity.assigned_ethnic_group_desc
        return ethnicity

    def _map_major(self, sqla_major):
        major = Major()
        major.major_abbr_code = sqla_major.major_abbr_code
        major.major_pathway = sqla_major.major_pathway
        major.major_branch = sqla_major.major_branch
        major.major_name = sqla_major.major_name
        major.major_full_name = sqla_major.major_full_name
        major.major_short_name = sqla_major.major_short_name
        major.major_desc = sqla_major.major_desc
        major.major_home_url = sqla_major.major_home_url
        major.major_dept = sqla_major.major_dept
        major.major_last_yr = sqla_major.major_last_yr
        major.major_last_qtr = sqla_major.major_last_qtr
        major.major_first_yr = sqla_major.major_first_yr
        major.major_first_qtr = sqla_major.major_first_qtr
        major.major_cip_code = sqla_major.major_cip_code
        major.major_undergrad = sqla_major.major_undergrad
        major.major_graduate = sqla_major.major_graduate
        major.major_professional = sqla_major.major_professional
        major.major_non_degree = sqla_major.major_non_degree
        major.major_minor = sqla_major.major_minor
        major.major_not_termin = sqla_major.major_not_termin
        major.major_ug_certif = sqla_major.major_ug_certif
        major.major_grad_certif = sqla_major.major_grad_certif
        major.major_evening = sqla_major.major_evening
        major.major_ss_std_act = sqla_major.major_ss_std_act
        major.major_ss_inelig = sqla_major.major_ss_inelig
        major.major_osfa_inelig = sqla_major.major_osfa_inelig
        major.major_dist_learn = sqla_major.major_dist_learn
        major.major_concur_cc = sqla_major.major_concur_cc
        major.major_measles_ex = sqla_major.major_measles_ex
        major.major_premaj = sqla_major.major_premaj
        major.major_premaj_ext = sqla_major.major_premaj_ext
        major.major_nonmatric = sqla_major.major_nonmatric
        major.major_gnm = sqla_major.major_gnm
        major.college = sqla_major.college
        return major

    def _map_transcript(self, sqla_transcript):
        transcript = Transcript()
        transcript.tran_term = self._map_term(
            sqla_transcript.tran_term)
        transcript.leave_ends_term = self._map_term(
            sqla_transcript.leave_ends_term)
        transcript.resident = sqla_transcript.resident
        transcript.resident_cat = sqla_transcript.resident_cat
        transcript.veteran = sqla_transcript.veteran
        transcript.veteran_benefit = sqla_transcript.veteran_benefit
        transcript.class_code = sqla_transcript.class_code
        transcript.qtr_grade_points = \
            float(sqla_transcript.qtr_grade_points)
        transcript.qtr_graded_attmp = \
            float(sqla_transcript.qtr_graded_attmp)
        transcript.qtr_nongrd_earned = sqla_transcript.qtr_nongrd_earned
        transcript.qtr_deductible = sqla_transcript.qtr_deductible
        transcript.over_qtr_grade_pt = sqla_transcript.over_qtr_grade_pt
        transcript.over_qtr_grade_at = sqla_transcript.over_qtr_grade_at
        transcript.over_qtr_nongrd = sqla_transcript.over_qtr_nongrd
        transcript.over_qtr_deduct = sqla_transcript.over_qtr_deduct
        transcript.qtr_comment = sqla_transcript.qtr_comment
        transcript.honors_program = sqla_transcript.honors_program
        transcript.special_program = sqla_transcript.special_program
        transcript.scholarship_type = sqla_transcript.scholarship_type
        transcript.yearly_honor_type = sqla_transcript.yearly_honor_type
        transcript.exemption_code = sqla_transcript.exemption_code
        transcript.grad_status = sqla_transcript.grad_status
        transcript.num_ind_study = sqla_transcript.num_ind_study
        transcript.num_courses = sqla_transcript.num_courses
        transcript.enroll_status = sqla_transcript.enroll_status
        transcript.tenth_day_credits = float(sqla_transcript.tenth_day_credits)
        transcript.tr_en_stat_dt = sqla_transcript.tr_en_stat_dt
        return transcript

    def _map_transfer(self, sqla_transfer):
        transfer = Transfer()
        transfer.institution_code = sqla_transfer.institution_code
        transfer.year_ending = sqla_transfer.year_ending
        transfer.year_beginning = sqla_transfer.year_beginning
        transfer.transfer_gpa = sqla_transfer.transfer_gpa
        transfer.trans_updt_dt = sqla_transfer.trans_updt_dt
        transfer.trans_updt_id = sqla_transfer.trans_updt_id
        transfer.degree_earned = sqla_transfer.degree_earned
        transfer.degree_earned_yr = sqla_transfer.degree_earned_yr
        transfer.degree_earned_mo = sqla_transfer.degree_earned_mo
        transfer.credential_lvl = sqla_transfer.credential_lvl
        transfer.credential_yr = sqla_transfer.credential_yr
        transfer.transfer_comment = sqla_transfer.transfer_comment
        transfer.institution_name = sqla_transfer.institution_name
        transfer.inst_addr_line_1 = sqla_transfer.inst_addr_line_1
        transfer.inst_addr_line_2 = sqla_transfer.inst_addr_line_2
        transfer.inst_city = sqla_transfer.inst_city
        transfer.inst_state = sqla_transfer.inst_state
        transfer.inst_zip_5 = sqla_transfer.inst_zip_5
        transfer.inst_zip_filler = sqla_transfer.inst_zip_filler
        transfer.inst_country = sqla_transfer.inst_country
        transfer.inst_postal_cd = sqla_transfer.inst_postal_cd
        transfer.inst_record_stat = sqla_transfer.inst_record_stat
        transfer.two_year = sqla_transfer.two_year
        transfer.wa_cc = sqla_transfer.wa_cc
        return transfer

    def _map_term(self, sqla_term):
        term = Term()
        term.year = sqla_term.year
        term.quarter = sqla_term.quarter
        return term
