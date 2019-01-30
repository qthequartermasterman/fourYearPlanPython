import unittest
from main import *
import StringIO
import sys
import string

converted_test_audit = {
    14.5: Semester({Course(catoid=u'17', compound="PSCI2G05")}, 14, 5),
    15.8: Semester({Course(catoid=u'17', compound="ENGL2210"),
                    Course(catoid=u'17', compound="ENGL2220"),
                    Course(catoid=u'17', compound="HIST1050"),
                    Course(catoid=u'17', compound="HIST1060"),
                    Course(catoid=u'17', compound="HIST1N01"),
                    Course(catoid=u'17', compound="HNRS1500"),
                    Course(catoid=u'17', compound="MATH1710"),
                    Course(catoid=u'17', compound="MATH1710"),
                    Course(catoid=u'17', compound="MATH1720"),
                    Course(catoid=u'17', compound="MATH2700"),
                    Course(catoid=u'17', compound="MATH2730"),
                    Course(catoid=u'17', compound="MUAS1506"),
                    Course(catoid=u'17', compound="MUTH1400"),
                    Course(catoid=u'17', compound="MUTH1500"),
                    Course(catoid=u'17', compound="PHYS1270"),
                    Course(catoid=u'17', compound="PHYS1410"),
                    Course(catoid=u'17', compound="PHYS1420"),
                    Course(catoid=u'17', compound="PHYS1430"),
                    Course(catoid=u'17', compound="PHYS1440"),
                    Course(catoid=u'17', compound="SPAN1010"),
                    Course(catoid=u'17', compound="SPAN1020"),
                    Course(catoid=u'17', compound="SPAN2040"),
                    Course(catoid=u'17', compound="SPAN2050"),
                    Course(catoid=u'17', compound="TNTX1100")
                    }, 15, 8),
    16.1: Semester({Course(catoid=u'17', compound="MATH2100"),
                    Course(catoid=u'17', compound="MATH3000"),
                    Course(catoid=u'17', compound="MUTH2400"),
                    Course(catoid=u'17', compound="PHYS2220"),
                    Course(catoid=u'17', compound="PHYS2240"),
                    Course(catoid=u'17', compound="PSCI1041"),
                    Course(catoid=u'17', compound="TNTX1200")
                    }, 16, 1),
    16.8: Semester({Course(catoid=u'17', compound="CSCE1030"),
                    Course(catoid=u'17', compound="ECON1110"),
                    Course(catoid=u'17', compound="MATH3610"),
                    Course(catoid=u'17', compound="MATH3680"),
                    Course(catoid=u'17', compound="PHYS3010"),
                    Course(catoid=u'17', compound="PHYS3030")
                    }, 16, 8),
    19.1: Semester({Course(catoid=u'17', compound="CSCE1040"),
                    Course(catoid=u'17', compound="EDCI3500"),
                    Course(catoid=u'17', compound="ENGL1310"),
                    Course(catoid=u'17', compound="MATH2000"),
                    Course(catoid=u'17', compound="MATH3510")
                    }, 19, 1)
}  # type: dict[Semester]

converted_test_audit_unmet_requirements = {
    RequiredCourse({Course(u'17', compound="ENGL1320"),
                    Course(u'17', compound="ENGL1321"),
                    Course(u'17', compound="ENGL1325"),
                    Course(u'17', compound="LING1322"),
                    Course(u'17', compound="TECM1322"),
                    Course(u'17', compound="TECM2700")
                    },
                   None,
                   'e885538a-ab0a-420b-8ebb-bc9ba8fcf246'
                   ),
    RequiredCourse({Course(u'17', compound="ART 1300"),
                    Course(u'17', compound="ART 1301"),
                    Course(u'17', compound="ART 2360"),
                    Course(u'17', compound="COMM2060"),
                    Course(u'17', compound="DANC1200"),
                    Course(u'17', compound="DANC2800"),
                    Course(u'17', compound="MUJS3400"),
                    Course(u'17', compound="MUMH2040"),
                    Course(u'17', compound="MUMH3000"),
                    Course(u'17', compound="MUMH3010"),
                    Course(u'17', compound="MUMH3500"),
                    Course(u'17', compound="MUMH3510"),
                    Course(u'17', compound="THEA1340"),
                    Course(u'17', compound="THEA2340"),
                    Course(u'17', compound="THEA3030"),
                    Course(u'17', compound="THEA3040")
                    },
                   None,
                   'bc0bb004-3a0f-4169-b599-53d3364cab17'),
    RequiredCourse({Course(u'17', compound="HIST2600"),
                    Course(u'17', compound="HIST2675"),
                    Course(u'17', compound="TECM2700"),
                    Course(u'17', compound="TECM2700"),
                    Course(u'17', compound="TECM2700"),
                    Course(u'17', compound="TECM2700"),
                    },
                   None,
                   '665e41a7-ad67-483a-95b0-32f097fa8ab8')
} # type: Set[RequiredCourse]

class TestCourseMethods(unittest.TestCase):
    def setUp(self):
        self.testCourse = Course(u'17', u'63011')
        self.page_data = self.testCourse._get_dom_from_webpage()

    def test_get_dom_from_webpage(self):
        # self.testCourse._get_dom_from_webpage()
        pass

    def test_determine_title(self):
        self.assertEquals(self.testCourse._determine_title(self.page_data),
                          "CSCE 4240 - Introduction to Digital Image Processing")

    def test_compound_init(self):
        self.testCourse = Course(u'13', compound="PSCI1041")
        self.assertEquals(self.testCourse.coid, u'43946')
        self.assertEquals(self.testCourse.prefix, u'PSCI')
        self.assertEquals(self.testCourse.number, u'1041')

    def test_is_identical_to_another_course(self):
        self.assertTrue(self.testCourse.is_identical_to_another_course(compound="CSCE4240"))

    def test_nonexistant_class(self):
        self.testCourse = Course(u'17', compound="PSCI2G05")


class TestSemesterMethods(unittest.TestCase):
    def setUp(self):
        self.testSemester = Semester({Course(catoid=u'17', compound="CSCE1040"),
                                      Course(catoid=u'17', compound="EDCI3500")
                                      }, 19, 1)

    def test_print_semester(self):
        # We have to do some tricky manipulation to test a print. We have to hijack the print function.
        captured_output = StringIO.StringIO()
        sys.stdout = captured_output
        self.testSemester.print_semester()
        sys.stdout = sys.__stdout__
        # self.assertEquals(captured_output.getvalue().encode('utf-8').translate(None,string.whitespace),
        #                   test_output.translate(None,string.whitespace))
        # This old test is bad, because sometimes the order can change. Instead we'll just look for certain keywords.
        self.assertIn('CSCE 1040 - Computer Science II', captured_output.getvalue())
        self.assertIn('EDCI 3500 - Knowing and Learning in Mathematics, Science and Computer Science',
                      captured_output.getvalue())


class TestFourYearPlanMethods(unittest.TestCase):
    def setUp(self):
        self.testFourYearPlan = FourYearPlan()

    def test_import_audit(self):
        audit_uri = "testAudit.html"

        self.testFourYearPlan.import_audit(audit_uri)
        print self.testFourYearPlan.semesters, converted_test_audit
        # self.assertEqual(self.testFourYearPlan.semesters, converted_test_audit)

        # Test if we got all the previously completed coursework
        for semester in converted_test_audit:
            if semester in self.testFourYearPlan.semesters:
                check_semester = converted_test_audit[semester]
                test_semester = self.testFourYearPlan.semesters[semester]
                # check_semester.print_semester()
                for course in check_semester.classes:
                    # see if course (or an identical one) is in test_semester.classes
                    # check over each course in test_semester.classes. if they have the same id then there is a match.
                    # if there is no match, then throw a failure
                    self.assertTrue(any(
                        (test_class.is_identical_to_another_course(prefix=course.prefix, number=course.number)) for
                        test_class in test_semester.classes))
            else:
                fail("Missing semester")

        # Test if we imported all of the degree plan requirements.
        self.assertTrue(len(self.testFourYearPlan.unmet_requirements) > 0) # check if we got any requirements.
        for subrequirement in converted_test_audit_unmet_requirements:
            assertTrue(any(subrequirement.equals_other_requirement(test_req) for test_req in self.testFourYearPlan.unmet_requirements))

        self.testFourYearPlan.print_plan()


if __name__ == '__main__':
    unittest.main()
