# pylint: disable=line-too-long
from pathlib import Path
from docutils.core import publish_parts
import yaml
import os


class Course:
    def __init__(self, courseId, lang, title, longDesc, shortDesc, willlearn, requirements, toc, extranalLinks,
                 archived_lessons, active_lessons):
        self.courseId = courseId
        self.lang = lang
        self.title = title
        self.willlearn = willlearn
        self.requirements = requirements
        self.toc = toc
        self.externalLinks = extranalLinks
        self.archived_lessons = archived_lessons
        self.active_lessons = active_lessons
        self.longDesc = longDesc
        self.shortDesc = shortDesc
        self.dict = {}

    def guid_check(self):
        guid_list = self.archived_lessons
        for lesson in self.active_lessons:
            guid_list = guid_list + lesson.archived_activities
            guid_list.append(lesson.guid)
            for activity in lesson.active_activies:
                guid_list.append(activity.guid)
        guid_list = duplicates(guid_list)
        return {'status': len(guid_list) == 0, 'guid_duplicate_list': guid_list}

    def source_check(self):
        missing_activities_src = []
        missing_activities = []
        missing_status = True
        for lesson in self.active_lessons:
            for activity in lesson.active_activies:
                if activity.type in ['reading', 'quiz']:
                    if activity.get_src_type() == 'rst':
                        if not Path('_sources/'+lesson.folder+'/'+activity.src).is_file():
                            missing_activities_src.append(
                                '_sources/'+lesson.folder+'/'+activity.src)
                            missing_activities.append(activity.title)
                            missing_status = False
                    if activity.get_src_type() == 'ipynb':
                        if activity.nbsrc:
                            if not Path(activity.nbsrc).is_file():
                                missing_activities_src.append(
                                    activity.nbsrc)
                                missing_activities.append(activity.title)
                                missing_status = False
                        else:
                            if not Path('_sources/'+lesson.folder+'/'+activity.src).is_file():
                                missing_activities_src.append(
                                    '_sources/'+lesson.folder+'/'+activity.src)
                                missing_activities.append(activity.title)
                                missing_status = False
                    if activity.get_src_type() == 'pdf':
                        if not Path('_static/'+activity.src).is_file():
                            missing_activities_src.append(
                                '_static/'+activity.src)
                            missing_activities.append(activity.title)
                            missing_status = False
        return {'status': missing_status, 'missing_activitie_titles': missing_activities, 'missing_activitie_src': missing_activities_src}

    def create_YAML(self, desc):
        self.dict['courseId'] = self.courseId
        self.dict['title'] = self.title
        self.dict['lang'] = self.lang
        self.dict['description'] = {}
        self.dict['description']['willLearn'] = self.willlearn
        self.dict['description']['shortDescription'] = self.shortDesc
        self.dict['description']['longDescription'] = publish_parts(self.longDesc, writer_name='html')[
            'html_body'] if self.longDesc.find('\n') != -1 else self.longDesc
        self.dict['description']['requirements'] = self.requirements
        self.dict['description']['toc'] = self.toc
        self.dict['description']['externalLinks'] = []
        for el in self.externalLinks:
            self.dict['description']['externalLinks'].append(
                {'text': el.text, 'href': el.link})
        self.dict['lessons'] = []
        for lesson in self.active_lessons:
            tmp_activities = []
            for activity in lesson.active_activies:
                tmp_activities.append({'type': activity.type,
                                       'title': activity.title,
                                       'src': activity.src,
                                       'file': activity.html_file_src,
                                       'description': activity.description,
                                       'guid': activity.guid}
                                      )
            tmp_archived = []
            for activity in lesson.archived_activities:
                tmp_archived.append({'guid': activity}
                                    )
            self.dict['lessons'].append({'title': lesson.title,
                                         'normalized_title': lesson.normalized_title,
                                         'guid': lesson.guid,
                                         'description':  lesson.description,
                                         'folder': lesson.folder,
                                         'activities': tmp_activities,
                                         'archived-activities': tmp_archived, }
                                        )
            if len(self.archived_lessons):
                self.dict['archived-lessons'] = []
                for al in self.archived_lessons:
                    self.dict['archived-lessons'].append({'guid': al})

        with open(desc, 'w', encoding='utf-8') as outfile:
            yaml.dump(self.dict, outfile, default_flow_style=False,
                      encoding='utf-8', allow_unicode=True)

    def to_dict(self):
        course_dict = dict()
        course_dict['active_lessons'] = []
        course_dict['longDesc'] = self.longDesc
        course_dict['shortDesc'] = self.shortDesc
        course_dict['willLearn'] = self.willlearn
        course_dict['requirements'] = self.requirements
        course_dict['toc'] = self.toc
        course_dict['title'] = self.title
        course_dict['lang'] = self.lang
        course_dict['externalLinkTexts'] = [
            el.text for el in self.externalLinks]
        course_dict['externalLinkLinks'] = [
            el.link for el in self.externalLinks]
        for lesson in self.active_lessons:
            lesson_dict = dict()
            lesson_dict['title'] = lesson.title
            lesson_dict['folder_url'] = lesson.folder_url
            lesson_dict['active_activies'] = []
            for activity in lesson.active_activies:
                activity_dict = dict()
                activity_dict['toc_url'] = activity.toc_url
                activity_dict['type'] = activity.type
                activity_dict['title'] = activity.title
                lesson_dict['active_activies'].append(activity_dict)
            course_dict['active_lessons'].append(lesson_dict)
        return course_dict


class Lesson:
    def __init__(self, title, folder, guid, description, archived_activities, active_activities):
        self.title = title
        self.normalized_title = normalize(title)
        self.guid = guid
        self.description = description if description else ''
        self.archived_activities = archived_activities
        self.active_activies = active_activities
        self.folder = folder if folder else '_missing_folder_name'
        self.folder_url = self.folder.replace(" ", "%20")


class Activity:
    def __init__(self, type, title, src, guid, description, nbsrc):
        self.type = type
        self.title = title
        self.guid = guid
        self.description = description if description else ''
        self.nbsrc = nbsrc
        if self.type in ["reading", "quiz", 'coding-quiz']:
            self.src = src
        elif self.type == 'video':
            self.src = yt_id(src)
        if self.type in ['reading', 'quiz'] and self.get_src_type() == 'rst':
            self.toc_url = self.src.replace('.rst', '').replace(' ', '%20')
            self.html_file_src = self.src.replace('.rst', '.html')
        else:
            self.html_file_src = normalize(self.title) + '.html'
            self.rst_file_src = normalize(self.title) + '.rst'
            self.toc_url = normalize(self.title).replace(" ", "%20")
        if self.nbsrc and self.get_src_type() == 'ipynb':
            # root of the nbsrc path is _sources folder, script executes from project root folder
            # so we need to adjust the path and then add the notebook file
            self.nbsrc = os.path.join(self.nbsrc[3:], src)

    def get_src_type(self):
        if self.type in ['reading', 'quiz']:
            if len(self.src.rsplit('.')) > 1:
                return self.src.rsplit('.')[1]
        if self.type == 'vide':
            return 'video_url'
        if self.type == 'coding-quiz':
            return 'coding_quiz_list'
        return ''


class ExternalLink:
    def __init__(self, text, link):
        self.text = text
        self.link = link

    def __str__(self):
        return self.text + "<" + self.link + ">"


class YamlLoger:

    ATR_COURSE_ID = 'courseId'
    ATR_LANG = 'lang'
    ATR_TITLE = 'title'
    ATR_DESC = 'description'
    ATR_DESC_LINE = 'description_line'
    ATR_WILL_LEARN = 'willLearn'
    ATR_REQUIREMENTS = 'requirements'
    ATR_TOC = 'toc'
    ATR_GUID = 'guid'
    ATR_FILE = 'file'
    ATR_URL = 'url'
    ATR_FOLDER = 'folder'
    ATR_TYPE = 'type'
    ATR_ACTIVITY = 'activities'
    ATR_ARCHIVED_ACTIVITY = 'archived-activities'
    ATR_SHORT_DESC = 'shortDescription'
    ATR_LONG_DESC = 'longDescription'
    ATR_EXTERNAL_LINK = 'externalLinks'
    ATR_EXTRENAL_LINK_LINE = 'link_line'
    ATR_EXTERNAL_LINKS_TEXT = 'text'
    ATR_EXTERNAL_LINKS_LINK = 'href'
    ATR_LESSONS = 'lessons'
    ATR_ARCHIVED_LESSON = 'archived-lessons'
    ATR_ARCHIVED_LESSON_LINE = 'archived-lessons_line'
    ATR_ARCHIVED_LESSON_GUID = 'guid'
    ATR_LESSON_LINE = '_line'
    ATR_LESSON_TITLE = 'title'
    ATR_LESSON_FOLDER = 'folder'
    ATR_LESSON_GUID = 'guid'
    ATR_LESSON_DESC = 'description'
    ATR_LESSON_NBSRC = 'nbsrc-folder'
    ATR_LESSON_ACTIVITIES = 'lesson_activities'
    ATR_LESSON_ARCHIVED_ACTIVITIES = 'lesson_archived_activities'
    ATR_LESSON_ARCHIVED_ACTIVITIE_LINE = 'lesson_archived_activities_line'
    ATR_LESSON_ARCHIVED_ACTIVITIE_GUID = 'lesson_archived_activities_guid'
    ATR_ACTIVITY_LINE = 'activity_line'
    ATR_ACTIVITY_TYPE = 'type'
    ATR_ACTIVITY_TITLE = 'title'
    ATR_ACTIVITY_GUID = 'guid'
    ATR_ACTIVITY_DESC = 'descripiton'
    ATR_ACTIVITY_SRC = 'src'
    ATR_ACTIVITY_TYPE_VALUE = 'activity_type_value'
    ATR_ACTIVITY_PROBLEMS = 'problems'
    DUPLICATE_GUID = 'guid_integrity'
    SOURCE_MISSING = 'source_integrity'
    YAML_PARSER_ERROR = 'yaml_parser_error'
    YAML_PARSER_ERROR_MSG = 'yaml_parser_error_msg'
    YAML_TYPE_ERROR = 'yaml_type_error'
    ERROR_YAML_LOAD = 'yaml_load_error'
    ERROR_MSGS = {
        't': {
            ATR_COURSE_ID: 'Missing required attribute "courseId" (Top level).',
            ATR_LANG: 'Missing required attribute "lang" (Top level).',
            ATR_TITLE: 'Missing required attribute "title" (Top level).',
            ATR_DESC: 'Missing required attribute "description" (Top level).',
            ATR_WILL_LEARN: 'In "description" (line: {}). Missing required attribute "willLearn".',
            ATR_REQUIREMENTS: 'In "description" (line: {}). Missing required attribute "requirements".',
            ATR_TOC: 'In "description" (line: {}). Missing required attribute "toc" (Table of content).',
            ATR_SHORT_DESC: 'In "description" (line: {}). Missing required attribute "shortDescription".',
            ATR_LONG_DESC: 'In "description" (line: {}). Missing required attribute "longDescription".',
            ATR_EXTERNAL_LINKS_TEXT: 'In "externalLinks" (line: {}). External link {} is missing required attribute "text".',
            ATR_EXTERNAL_LINKS_LINK: 'In "externalLinks" (line: {}). External link {} is missing required attribute "href".',
            ATR_LESSONS: 'Missing required attribute "lessons" (Top level).',
            ATR_ARCHIVED_LESSON_GUID: 'In "archived-lessons" (line: {}). Lesson {} is missing required attribute "guid".',
            DUPLICATE_GUID: 'Duplicated GUID found: {}.',
            SOURCE_MISSING: 'Activity "{}" source missing. File should be here:\n>> {}',
            YAML_TYPE_ERROR: 'Yaml stucture error.',
            ERROR_YAML_LOAD: 'Yaml could not be loaded.'
        },
        'l': {
            ATR_LESSON_TITLE: 'In "lessons" (line: {}). Lesson {} is missing the required attribute "title".',
            ATR_LESSON_FOLDER: 'In "lessons" (line: {}). Lesson {} is missing the required attribute "folder".',
            ATR_LESSON_GUID: 'In "lessons" (line: {}). Lesson {} is missing the required attribute "guid".',
            ATR_LESSON_ACTIVITIES: 'In "lessons" (line: {}). Lesson {} is missing the required attribute "activities".',
        },
        'a': {
            ATR_ACTIVITY_TYPE: 'In "lesson" {}. Activity {} (line: {}) is missing the required attribute "type".',
            ATR_ACTIVITY_TITLE: 'In "lesson" {}. Activity {} (line: {}) is missing the required attribute "title".',
            ATR_ACTIVITY_GUID: 'In "lesson" {}. Activity {} (line: {}) is missing the required attribute "guid".',
            ATR_ACTIVITY_SRC: 'In "lesson" {}. Activity {} (line: {}) is missing the source("file" or "url").',
            ATR_LESSON_ARCHIVED_ACTIVITIE_GUID: 'In Lesson {} "archived-activities" {} (line: {}) missing required attribute "guid".',
            ATR_ACTIVITY_TYPE_VALUE: 'Unsupported activity type {}.',
            ATR_ACTIVITY_PROBLEMS: 'In "lesson" {}. Activity {} (line: {}) is missing "problems"',
            ATR_FILE: 'In "lesson" {}. Activity {} (line: {}) is missing the source("file" or "url").',
            ATR_URL: 'In "lesson" {}. Activity {} (line: {}) is missing the source("file" or "url").',
        }
    }


def duplicates(guid_list):
    seen = {}
    dupes = []

    for el in guid_list:
        if el not in seen:
            seen[el] = 1
        else:
            if seen[el] == 1:
                dupes.append(el)
            seen[el] += 1
    return dupes


def yt_id(src):
    if len(src) > 11:
        pos = src.find('v=')
        if pos == -1:
            src = ''
        else:
            pos = pos + 2
            src = src[pos:pos+11]

    return src


class ActivityTypeValueError(Exception):
    def __init__(self, *args):
        super(ActivityTypeValueError, self).__init__(args[0])
        if args:
            self.message = args[0]
        else:
            self.message = None


def normalize(string: str):
    reserved_chars = ['?', '>', ':', '"', '/', '\\', '|', '*']
    return ''.join(char for char in string if char not in reserved_chars)
