import os
import shutil
import copy
import xml.etree.cElementTree as ET
import lxml.etree as etree
import yaml
import cyrtranslit
import random
import string
import re
from datetime import datetime
from .util import copy_dir, filter_name

_BUILD_PATH = "_build"
_EXPORT_PATH = "export"
_BUILD_YAML_PATH = "_build/index.yaml"
_BUILD_STATIC_PATH = "_build/_static"
_BUILD_IMAGE_PATH = "_build/_image"

class ScormPackager:

    _LOCALAZIE_STRIGNS = {
        'en': {"About": "About the course"},
        'sr': {"About": "O kursu"},
        'sr-Latn': {"About": "O kursu"},
        'sr-Cyrl': {"About": "О курсу"},
    }

    def __init__(self):
        manifest = ET.Element("manifest",
                              identifier="manifest_" + datetime.now().strftime("%d-%b-%Y-%H-%M-"),
                              version="1.0",
                              xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2")

        manifest.set("xmlns:adlcp", "http://www.adlnet.org/xsd/adlcp_rootv1p2")
        manifest.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        manifest.set("xsi:schemaLocation", "http://www.imsproject.org/xsd/imscp_rootv1p1p2 imscp_rootv1p1p2.xsd http://www.imsglobal.org/xsd/imsmd_rootv1p2p1 imsmd_rootv1p2p1.xsd http://www.adlnet.org/xsd/adlcp_rootv1p2 adlcp_rootv1p2.xsd")

        metadata = ET.SubElement(manifest, "metadata")

        ET.SubElement(metadata, "schema").text = "ADL SCORM"
        ET.SubElement(metadata, "schemaversion").text = "1.2"

        organizations = ET.SubElement(
            manifest, "organizations", default="petlja_org")
        resources = ET.SubElement(manifest, "resources")

        common_resource = ET.SubElement(
            resources, "resource", identifier="common_files", type="webcontent")
        common_resource.set("adlcp:scormtype", "asset")

        for root, _, files in os.walk(_BUILD_STATIC_PATH):
            for file in files:
                relative_path = os.path.join(root, file).replace(
                    "_build", ".").replace("\\", "/")
                file = ET.SubElement(
                    common_resource, "file", href=relative_path)

        for root, _, files in os.walk(_BUILD_IMAGE_PATH):
            for file in files:
                relative_path = os.path.join(root, file).replace(
                    "_build", ".").replace("\\", "/")
                file = ET.SubElement(
                    common_resource, "file", href=relative_path)

        self.manifest_template = [manifest, organizations, resources]
        self._skip_files = ["doctrees", "_sources", ".buildinfo", "search.html",
                            "searchindex.js", "objects.inv", "pavement.py", "course-errors.js", "genindex.html", "index.yaml"]

        self._load_data_from_yaml()
        if self.course_data:
            for lesson in self.course_data["lessons"]:
                self._skip_files.append(lesson["folder"])

            self.course_lang = self.course_data['lang'] if self.course_data[
                'lang'] in ScormPackager._LOCALAZIE_STRIGNS else 'en'

    def _load_data_from_yaml(self):
        try:
            with open(_BUILD_YAML_PATH, encoding="utf8") as f:
                self.course_data = yaml.load(f, Loader=yaml.FullLoader)
        except IOError:
            self.course_data = None

    def create_package_for_course(self):
        self._create_imsmanifest_for_course()
        self._create_archive_for_course()

    def create_package_for_single_sco_course(self):
        self._create_imsmanifest_for_single_sco_course()
        self._create_archive_for_course()

    def create_packages_for_lectures(self):
        if not self.course_data:
            return None
        if not os.path.exists(_EXPORT_PATH):
            os.mkdir(_EXPORT_PATH)
        for lesson in self.course_data["lessons"]:
            if not os.path.exists(os.path.join(_EXPORT_PATH, cyrtranslit.to_latin(lesson["normalized_title"]))):
                os.mkdir(os.path.join(_EXPORT_PATH,
                                      cyrtranslit.to_latin(lesson["normalized_title"])))
            self._skip_files.remove(lesson["folder"])
            copy_dir(_BUILD_PATH, os.path.join(
                _EXPORT_PATH, cyrtranslit.to_latin(lesson["normalized_title"])), self._filter_by_name)
            self._skip_files.append(lesson["folder"])

            manifest, organizations, resources = copy.deepcopy(
                self.manifest_template)
            organization = ET.SubElement(
                organizations, "organization", identifier="petlja_org")
            ET.SubElement(organization, "title").text = lesson["title"]
            lecture_item = ET.SubElement(
                organization, "item", identifier=self._get_random_string_for_id())
            ET.SubElement(lecture_item, "title").text = lesson["title"]
            for activity in lesson["activities"]:
                resource_id = self._create_id(
                    lesson["title"], activity["title"])
                activity_item = ET.SubElement(
                    lecture_item, "item", identifier=self._get_random_string_for_id(), identifierref=resource_id)
                ET.SubElement(activity_item, "title").text = activity["title"]
                resource = ET.SubElement(resources, "resource", identifier=resource_id, type="webcontent", href=os.path.join(
                    lesson["folder"], activity["file"]).replace("\\", "/"))
                resource.set("adlcp:scormtype", "sco")
                ET.SubElement(resource, "file", href=os.path.join(
                    lesson["folder"], activity["file"]).replace("\\", "/"))
                ET.SubElement(resource, "dependency",
                              identifierref="common_files")

            tree = ET.ElementTree(manifest)

            manifest_path = os.path.join(os.path.join(
                _EXPORT_PATH, cyrtranslit.to_latin(lesson["normalized_title"])), "imsmanifest.xml")
            tree.write(manifest_path)

            x = etree.parse(manifest_path)
            with open(manifest_path, mode="w+", encoding="utf-8") as file:
                file.write(etree.tostring(x, pretty_print=True, encoding=str))

            self._create_archive_for_lecutres(
                cyrtranslit.to_latin(lesson["normalized_title"]))

    def create_single_sco_packages_for_lectures(self):
        if not self.course_data:
            return None
        if not os.path.exists(_EXPORT_PATH):
            os.mkdir(_EXPORT_PATH)
        for lesson in self.course_data["lessons"]:
            if not os.path.exists(os.path.join(_EXPORT_PATH, cyrtranslit.to_latin(lesson["normalized_title"]))):
                os.mkdir(os.path.join(_EXPORT_PATH,
                                      cyrtranslit.to_latin(lesson["normalized_title"])))
            self._skip_files.remove(lesson["folder"])
            copy_dir(_BUILD_PATH, os.path.join(
                _EXPORT_PATH, cyrtranslit.to_latin(lesson["normalized_title"])), self._filter_by_name)
            self._skip_files.append(lesson["folder"])

            manifest, organizations, resources = copy.deepcopy(
                self.manifest_template)
            organization = ET.SubElement(
                organizations, "organization", identifier="petlja_org")
            ET.SubElement(organization, "title").text = lesson["title"]
            lecture_item = ET.SubElement(
                organization, "item", identifier=self._get_random_string_for_id())
            ET.SubElement(lecture_item, "title").text = lesson["title"]

            activity = lesson["activities"][0]
            resource_id = self._create_id(lesson["title"], activity["title"])
            activity_item = ET.SubElement(
                lecture_item, "item", identifier=self._get_random_string_for_id(), identifierref=resource_id)
            ET.SubElement(activity_item, "title").text = activity["title"]
            resource = ET.SubElement(resources, "resource", identifier=resource_id, type="webcontent", href=os.path.join(
                lesson["folder"], activity["file"]).replace("\\", "/"))
            resource.set("adlcp:scormtype", "sco")
            ET.SubElement(resource, "file", href=os.path.join(
                lesson["folder"], activity["file"]).replace("\\", "/"))
            for activity in lesson["activities"][1:]:
                ET.SubElement(resource, "file", href=os.path.join(
                    lesson["folder"], activity["file"]).replace("\\", "/"))

            ET.SubElement(resource, "dependency", identifierref="common_files")
            tree = ET.ElementTree(manifest)
            manifest_path = os.path.join(os.path.join(
                _EXPORT_PATH, cyrtranslit.to_latin(lesson["normalized_title"])), "imsmanifest.xml")
            tree.write(manifest_path)

            x = etree.parse(manifest_path)
            with open(manifest_path, mode="w+", encoding="utf-8") as file:
                file.write(etree.tostring(x, pretty_print=True, encoding=str))

            self._create_archive_for_lecutres(
                cyrtranslit.to_latin(lesson["normalized_title"]))

    def _create_imsmanifest_for_course(self):
        if not self.course_data:
            return None
        manifest, organizations, resources = copy.deepcopy(
            self.manifest_template)
        organization = ET.SubElement(
            organizations, "organization", identifier="petlja_org")
        ET.SubElement(organization, "title").text = self.course_data["title"]
        # Setup a homepage as index.html
        lecture_item = ET.SubElement(
            organization, "item", identifier="home_page")
        ET.SubElement(lecture_item, "title").text = self.course_data["title"]
        activity_item = ET.SubElement(
            lecture_item, "item", identifier="indexid", identifierref="index")
        ET.SubElement(
            activity_item, "title").text = ScormPackager._LOCALAZIE_STRIGNS[self.course_lang]['About']
        resource = ET.SubElement(
            resources, "resource", identifier="index", type="webcontent", href="index.html")
        resource.set("adlcp:scormtype", "sco")
        ET.SubElement(resource, "file", href="index.html")

        for lesson in self.course_data["lessons"]:
            lecture_item = ET.SubElement(
                organization, "item", identifier=self._get_random_string_for_id())
            ET.SubElement(lecture_item, "title").text = lesson["title"]
            for activity in lesson["activities"]:
                resource_id = self._create_id(
                    lesson["title"], activity["title"])
                activity_item = ET.SubElement(
                    lecture_item, "item", identifier=self._get_random_string_for_id(), identifierref=resource_id)
                ET.SubElement(activity_item, "title").text = activity["title"]
                resource = ET.SubElement(resources, "resource", identifier=resource_id, type="webcontent", href=os.path.join(
                    lesson["folder"], activity["file"]).replace("\\", "/"))
                resource.set("adlcp:scormtype", "sco")
                ET.SubElement(resource, "file", href=os.path.join(
                    lesson["folder"], activity["file"]).replace("\\", "/"))
                ET.SubElement(resource, "dependency",
                              identifierref="common_files")

        manifest_path = os.path.join(_BUILD_PATH, "imsmanifest.xml")
        tree = ET.ElementTree(manifest)
        tree.write(manifest_path)

        x = etree.parse(manifest_path)
        with open(manifest_path, mode="w+", encoding="utf-8") as file:
            file.write(etree.tostring(x, pretty_print=True, encoding=str))

    def _create_imsmanifest_for_single_sco_course(self):
        if not self.course_data:
            return None
        manifest, organizations, resources = copy.deepcopy(
            self.manifest_template)
        organization = ET.SubElement(
            organizations, "organization", identifier="petlja_org")
        ET.SubElement(organization, "title").text = self.course_data["title"]
        # Setup a homepage as index.html
        lecture_item = ET.SubElement(
            organization, "item", identifier="home_page")
        ET.SubElement(lecture_item, "title").text = self.course_data["title"]
        activity_item = ET.SubElement(
            lecture_item, "item", identifier="indexid", identifierref="index")
        ET.SubElement(
            activity_item, "title").text = ScormPackager._LOCALAZIE_STRIGNS[self.course_lang]['About']
        resource = ET.SubElement(
            resources, "resource", identifier="index", type="webcontent", href="index.html")
        resource.set("adlcp:scormtype", "sco")
        ET.SubElement(resource, "file", href="index.html")

        for lesson in self.course_data["lessons"]:
            for activity in lesson["activities"]:
                ET.SubElement(resource, "file", href=os.path.join(
                    lesson["folder"], activity["file"]).replace("\\", "/"))

        ET.SubElement(resource, "dependency", identifierref="common_files")

        manifest_path = os.path.join(_BUILD_PATH, "imsmanifest.xml")
        tree = ET.ElementTree(manifest)
        tree.write(manifest_path)

        x = etree.parse(manifest_path)
        with open(manifest_path, mode="w+", encoding="utf-8") as file:
            file.write(etree.tostring(x, pretty_print=True, encoding=str))

    def _create_archive_for_course(self):
        if not self.course_data:
            return None
        _path = os.path.join(
            _EXPORT_PATH, cyrtranslit.to_latin(self.course_data["title"]))
        copy_dir(_BUILD_PATH, _path, filter_name)
        shutil.make_archive(_path, "zip", _path)
        shutil.rmtree(_path)

    def _create_archive_for_lecutres(self, title):
        if not self.course_data:
            return None
        shutil.make_archive(os.path.join(_EXPORT_PATH, title),
                            "zip", os.path.join(_EXPORT_PATH, title))
        shutil.rmtree(os.path.join(_EXPORT_PATH, title))

    def _filter_by_name(self, item):
        if item not in self._skip_files:
            return True
        else:
            return False

    def _get_random_string_for_id(self):
        return ''.join((random.choice(string.ascii_lowercase) for x in range(10)))

    def _create_id(self, lesson_title, activity_title):
        return re.sub(r'\W+', '', 'r_' + cyrtranslit.to_latin(lesson_title + "_" + activity_title).replace(" ", "_"))
