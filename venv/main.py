# import libraries
import urllib2
from bs4 import BeautifulSoup
import urlparse
import re
import time

alreadyGeneratedCourses = {}


class Course:
    prereqs = []
    coreqs = []

    def get_coid(self):
        if self.coid is not None:
            return self.coid
        else:
            return None
            # TODO: Implement this.

    def _get_dom_from_webpage(self):
        # type: () -> BeautifulSoup
        # We will scape the data from the webpage, so as to make it accesible from the catalog.
        course_url = "http://unt.catalog.acalog.com/preview_course.php?catoid=" + str(self.catoid) \
                     + "&coid=" + str(self.coid)
        page = urllib2.urlopen(course_url)
        return BeautifulSoup(page, 'html.parser')  # This will allow us to use the web page as an object

    def _determine_title(self, page_data):
        # type: (BeautifulSoup) -> str
        # The title is in an <h1> tag with id #course_preview_title
        return page_data.find('h1', attrs={'id': 'course_preview_title'}).string

    def _determine_prefix(self, title):
        # type: (string) -> str
        splitstring = title.split(" ")
        if len(splitstring) > 1:
            return splitstring[0]
        else:
            return str(title)[:4]

    def _determine_number(self, title):
        # type: (string) -> str
        splitstring = title.split(" ")
        if len(splitstring) > 1:
            return splitstring[1]
        else:
            return str(title)[4:]

    def is_identical_to_another_course(self, compound=None, prefix=None, number=None):
        if compound is not None:
            are_prefixes_identical = (self._determine_prefix(compound) == self.prefix)
            are_numbers_identical = (self._determine_number(compound) == self.number)
        else:
            are_prefixes_identical = (prefix == self.prefix)
            are_numbers_identical = (number == self.number)
        return are_numbers_identical and are_prefixes_identical

    def add_course_to_list(self, prereqcatoid, prereqcoid, list):
        if prereqcoid in alreadyGeneratedCourses:
            list.append(alreadyGeneratedCourses[prereqcoid])
        else:
            list.append(Course(prereqcatoid, prereqcoid))

    def find_catoid_from_href(self, href):
        parsed_url = urlparse.urlparse(href)
        return urlparse.parse_qs(parsed_url.query)['catoid'][0]

    def find_coid_from_href(self, href):
        parsed_url = urlparse.urlparse(href)
        return urlparse.parse_qs(parsed_url.query)['coid'][0]

    def _determine_prereqs(self, page_data):
        # the links to the prereqs are <a> elements that are children of .block_content_popup class elements that are
        # after the text "Prerequisite(s):"
        links = page_data.find('td', attrs={'class': 'block_content_popup'}).findChildren('a', recursive=False)
        courses_that_are_pre_reqs = []
        for link in links:
            if "Prerequisite(s):" in link.previous_sibling:
                if link.previous_sibling == "Prerequisite(s): ":
                    # only add this to the prereqs list if it really is a prereq
                    # parsedUrlToPreReq = urlparse.urlparse(link['href'])
                    # preReqCatoid = urlparse.parse_qs(parsedUrlToPreReq.query)['catoid'][0]
                    # preReqCoid = urlparse.parse_qs(parsedUrlToPreReq.query)['coid'][0]

                    self.add_course_to_list(self.find_catoid_from_href(link['href']),
                                            self.find_coid_from_href(link['href']), courses_that_are_pre_reqs)
                    # This next part is really hacked together. We'll iterate over the next sibling elements until we
                    # hit a <br>. If it is a link, then we'll add it to the prereq list.
                    nextelementtocheck = link.find_next_sibling(['br', 'a'])
                    while True:
                        if nextelementtocheck.name == u'br':
                            break
                        else:
                            self.add_course_to_list(self.find_catoid_from_href(nextelementtocheck['href']),
                                                    self.find_coid_from_href(nextelementtocheck['href']),
                                                    courses_that_are_pre_reqs)
                            nextelementtocheck = nextelementtocheck.find_next_sibling(['br', 'a'])

                else:
                    print "ODD PREREQ DETECTED WITH CATOID: " + self.catoid + " COID: " + self.coid
        return courses_that_are_pre_reqs

    def _determine_coreqs(self, page_data):
        links = page_data.find('td', attrs={'class': 'block_content_popup'}).findChildren('a', recursive=False)
        courses_that_are_co_reqs = []
        for link in links:
            if "Corequisite(s):" in link.previous_sibling:
                if link.previous_sibling == "Corequisite(s): ":
                    # only add this to the prereqs list if it really is a prereq
                    parsed_url_to_co_req = urlparse.urlparse(link['href'])
                    co_req_catoid = urlparse.parse_qs(parsed_url_to_co_req.query)['catoid'][0]
                    co_req_coid = urlparse.parse_qs(parsed_url_to_co_req.query)['coid'][0]
                    if co_req_coid in alreadyGeneratedCourses:
                        courses_that_are_co_reqs.append(alreadyGeneratedCourses[co_req_coid])
                    else:
                        courses_that_are_co_reqs.append(Course(co_req_catoid, co_req_coid))
                else:
                    print "ODD PREREQ DETECTED WITH CATOID: " + self.catoid + " COID: " + self.coid
        return courses_that_are_co_reqs

    def _determine_hours(self, page_data):
        credit_hour_text = page_data.find('hr').previous_sibling
        try:
            return int(credit_hour_text.split(" hours")[0])
        except ValueError:
            return [float(s) for s in re.findall(r'-?\d+\.?\d*', credit_hour_text.split(" hours")[0])][0]

    def printinfo(self, tabs=0, show_prereqs=False, recursive_show_prereqs=False):
        print '\t' * tabs + self.title
        print "\t" * tabs + "catoid: " + str(self.catoid)
        print "\t" * tabs + "coid: " + str(self.coid)
        print "\t" * tabs + "prefix: " + str(self.prefix)
        print "\t" * tabs + "number: " + str(self.number)
        print "\t" * tabs + "hours: " + str(self.hours)
        print "\t" * tabs + "prereqs: " + ''.join(str(x.coid) for x in self.prereqs)
        print "\t" * tabs + "coreqs: " + ''.join(str(x.coid) for x in self.coreqs)
        if len(self.prereqs) > 0 and show_prereqs:
            print '\t' * tabs + "Prerequisite(s):"
            for course in self.prereqs:
                # print course
                course.printinfo(tabs + 1, show_prereqs=recursive_show_prereqs,
                                 recursive_show_prereqs=recursive_show_prereqs)
        # print "\n"

    def find_coid_from_prefix_and_number(self, catoid, prefix, number):
        '''search_url = "http://catalog.unt.edu/content.php?filter[27]=" + str(prefix) + "&filter[29]=" + str(
            number) + "&cur_cat_oid=" + str(catoid) + "&navoid=1723"
            '''
        search_url = "http://catalog.unt.edu/search_advanced.php?cur_cat_oid=" + str(
            catoid) + "&filter[keyword]=" + str(prefix) + str("+") + str(number) + "&filter[exact_match]=1&filter[3]=1"
        # print search_url
        page = urllib2.urlopen(search_url)
        soup = BeautifulSoup(page, 'html.parser')
        links_to_courses = soup.select('a[href^="preview_course_nopop.php"]')
        # print links_to_courses
        href_to_class = None
        if len(links_to_courses):  # check if it exists, so that we don't throw an error
            href_to_class = links_to_courses[0]['href']
            parsed_url = urlparse.urlparse(href_to_class)
            parsed_queries = urlparse.parse_qs(parsed_url.query)
            found_coid = None
            # print parsed_queries
            if u'coid' in parsed_queries:
                found_coid = parsed_queries['coid'][0]  # This checks the url for whatever is in the coid spot.
            else:
                # For some forsaken reason, there is an extra, blank link on some pages. I can't find a pattern to it
                # right now.
                if len(links_to_courses) > 1:
                    href_to_class = links_to_courses[1]['href']
                    parsed_url = urlparse.urlparse(href_to_class)
                    parsed_queries = urlparse.parse_qs(parsed_url.query)
                    # print "New parsed queries: " + str(parsed_queries)
                    found_coid = parsed_queries['coid'][0]
                else:
                    found_coid = None
                    # raise Exception("We couldn't find a coid?")
            return found_coid
        else:
            print('Course does not seem to exist in that search')
            return None

    def __init__(self, catoid, coid=None, prefix=None, number=None, compound=None):
        print "generating Course: ", time.time()
        self.coid = None

        if coid is None and compound is None:
            self.coid = self.find_coid_from_prefix_and_number(catoid, prefix, number)
        elif coid is None and compound is not None:
            self.coid = self.find_coid_from_prefix_and_number(catoid, str(compound)[:4].replace(" ","+"), str(compound)[4:])
        else:
            self.coid = coid

        self.catoid = catoid


        # Add this instance to the alreadyGeneratedCourses List at spot [coid]
        alreadyGeneratedCourses[coid] = self
        if self.coid is not None:
            pageData = self._get_dom_from_webpage()  # Scrape the page data from the webpage
            self.title = self._determine_title(pageData)
            self.prefix = self._determine_prefix(self.title)
            self.number = self._determine_number(self.title)
            # self.prereqs = self._determine_prereqs(pageData)
            # self.coreqs = self._determine_coreqs(pageData)
            self.hours = self._determine_hours(pageData)
        else:
            if compound is not None:
                self.prefix = self._determine_prefix(compound)
                self.number = self._determine_number(compound)
            if compound is None:
                if prefix is not None:
                    self.prefix = prefix
                if number is not None:
                    self.number = number
            self.title = "Unknown Title"
            self.hours = "?"


class RequiredCourse:
    select_courses = ""
    not_courses = ""
    id = ""
    catoid = None

    def __init__(self, select_courses, not_courses, id, catoid = None):
        self.select_courses = select_courses
        self.not_courses = not_courses
        self.id = id
        self.catoid = catoid

    def print_requiredcourse(self):
        print id, self.select_courses, " NOT: ", self.not_courses, "\n"

    def equals_other_requirement(self, other_requirement):
        # Check if the select courses are the same
        for course in other_requirement.select_courses: # type: Course
            if not (any((test_class.is_identical_to_another_course(prefix=course.prefix,number=course.number)) for test_class in self.select_courses)):
                return false;
        # Check if the not courses are the same
        for course in other_requirement.not_courses: # type: Course
            if not (any((test_class.is_identical_to_another_course(prefix=course.prefix,number=course.number)) for test_class in self.not_courses)):
                return false;
        # check if the ID is the same
        if other_requirement.id != self.id:
            return false
        return true

    @staticmethod
    def extract_courses(subrequirement,catoid):
        # subrequirement should be a BeautifulSoup object
        courses_objects = {}  # type: Set(Courses)
        coursesSoups = subrequirement.select("span.course.draggable span.number")
        for course in coursesSoups:
            courses_objects.add(Course(catoid, compound=course.string))
        return courses_objects


# Class Semester
# The Semester class has properties including year and term
# method "get_hours" which calculates and returns how many hours of classes are taken that semester
# method "get_classes" returns the set of classes
class Semester:
    classes = {}  # type: Course

    def __init__(self, classes=None, year=None, term=None, compound_semester_id=None):
        if classes is not None:
            self.classes = classes

        if year is not None and term is not None:
            self.year = year
            self.term = term
        elif compound_semester_id and year is None and term is None:
            split_str = str(compound_semester_id).split(".")
            self.year = split_str[0]
            self.term = split_str[1]
        else:
            raise Exception('Invalid semester initialization.')

    def get_classes(self):
        return self.classes

    def add_class(self, course):
        self.classes.add(course)

    def get_hours(self):
        running_total_of_hours = 0
        for course in self.classes:
            running_total_of_hours += course.hours
        return running_total_of_hours

    def print_semester(self):
        print "Semester: " + str(self.year) + "." + str(self.term)
        for course in self.classes:
            course.printinfo(tabs=1)
            print "\n"


class FourYearPlan:
    semesters = {}  # type: Semester
    unmet_requirements = {}  # type: RequiredCourse

    def __init__(self, semesters={}):
        self.semesters = semesters

    def print_plan(self):
        for semester in self.semesters:
            self.semesters[semester].print_semester()
        print "Currently unmatched requirements: \n"
        for req in self.unmet_requirements:
            req.print_requiredcourse()

    def add_semester(self, semester):
        self.semesters[float(str(semester.year) + "." + str(semester.term))] = semester

    def check_semester_for_prereqs(self, semesterIndex):
        # loop over each course in semester with index semesterIndex
        # record the pre req courses into a dictionary with value False, meaning that it has not yet been marked
        # as taken check each semester, if it's earlier, then check each class.
        # If said class matches on in the above dictionary, change value to True
        # If there is a class that is still False at the end, return an error message saying that the class is
        # missing a pre req

        # make a composite list of all previous classes
        all_previous_classes = {}
        for individualIndex in self.semesters:
            if individualIndex < semesterIndex:
                for previous_course in self.semesters[individualIndex].classes:
                    all_previous_classes.append(previous_course)

        for course in self.semesters[semesterIndex].classes:
            required_prereqs = {}
            for prereq in course.prereqs:
                required_prereqs[prereq.coid] = False
            for previous_course in all_previous_classes:
                if previous_course == course:
                    required_prereqs[course.coid] = True
            print required_prereqs
            # if False in required_prereqs.values():
            #    raise Exception('spam', 'egg')
            # TODO: Implement some way of notifying the program if prereqs aren't satisfied.

        '''
        for course in self.semesters[semesterIndex].classes:
            required_prereqs = {}
            for prereq in course.prereqs:
                required_prereqs[prereq.coid] = False
            for individualIndex in self.semesters:
                if individualIndex < semesterIndex:
                    for previous_course in self.semesters[individualIndex].classes:
                        if previous_course == course:
                            required_prereqs[course.coid] = True
        '''

    # function import_audit
    # inputs: str audit_uri
    # outputs: void
    # import_audit takes a URI to an audit html file, then turns all the already completed and in progress classes into
    # Course objects in the parent FourYearPlan object.
    def import_audit(self, audit_uri):
        soup = BeautifulSoup(open(audit_uri), 'html.parser')
        audit_catoid = None
        for td in soup.find(attrs={"class": "auditHeaderTable"}).findAll("td"):
            if td.previous_sibling.string == "Catalog Year":
                catalog_string = td.string
                catalog_year = int(catalog_string.split(" ")[1])
                audit_catoid = 2 * catalog_year - 4017  # This formula converts the catalog year into the catoid. It's
                # funky because the catoids started in 2009. Graduate catalogs are even numbers (staritng with 0) and
                # undergrads are odd numbers (starting with 1)
        # We import all of the previously taken courses and currently in progress course.
        for blarg in soup.findAll("tr", attrs={"class", "takenCourse"}):
            semester_id = blarg.find(attrs={"class": "term"}).string
            course_compound_id = blarg.find(attrs={"class": "course"}).string
            if float(semester_id) in self.semesters:
                # add course to semester
                self.semesters[float(semester_id)].add_class(Course(catoid=audit_catoid, compound=course_compound_id))
            else:
                # add semester then add course
                temp_semester_variable = Semester(classes={Course(catoid=audit_catoid, compound=course_compound_id)},
                                                  compound_semester_id=semester_id)
                self.add_semester(temp_semester_variable)

        # We now import all of the courses that need to be taken as an array that has class RequiredCourse
        # instead of Course.

        for subreq in soup.find_all(attrs={"class": "subreqNeeds"}):
            print "found subreq", subreq
            subreq_id = subreq.find_parent(attrs={"class": "subrequirement"})['id']
            select_courses = subreq.find(attrs={"class": "selectcourses"})
            not_courses = subreq.find(attrs={"class": "notcourses"})
            number_of_courses = 0
            if select_courses is not None:
                number_node = select_courses.select('.count.number')
                if number_node is not None:
                    number_of_courses = int(number_node.string)
                else:
                    number_node = select_courses.selct('.hours.number')
                    if number_node is not None:
                        number_of_courses = int(float(number_node.string) / 3)
            print "we will add ", number_of_courses, " classes to unmet."
            for x in xrange(number_of_courses):
                select_courses_objects = RequiredCourse.extract_courses(select_courses, audit_catoid)
                not_courses_objects = RequiredCourse.extract_courses(not_courses,audit_catoid)
                self.unmet_requirements.append(RequiredCourse(select_courses_objects, not_courses_objects, subreq_id))


# testSemester = Semester({Course(u'17', u'63011'), Course(u'17', u'63942'), Course(u'17', u'63929')}, 17, 0)
# testPlan = FourYearPlan()


# #####
# Importer notes
# Test document: testAudit.html
# All courses that could be taken to fulfill something in the audit has the css selector span.course
# All courses that have been taken are "tr.takenCourse:not(.ip)"
# All courses that are in progress are "tr.takenCourse.ip"
# #####


'''
def main():
    # print "started"
    #testCourse = Course(u'17', u'63011')
    #testCourse.printinfo(show_prereqs=True)

    # print alreadyGeneratedCourses
    # for course in alreadyGeneratedCourses:
    #    alreadyGeneratedCourses[course].printinfo()

    # testPlan.add_semester(testSemester)
    # print testSemester.get_classes()
    # print testSemester.get_hours()

    # testPlan.check_semester_for_prereqs(17.0)
    # print testPlan.semesters[17.0]

if __name__ == "__main__":
    main()

'''
