=====================
This Is A New Project
=====================

.. Here is were you specify the content and order of your new book.

.. Each section heading (e.g. "SECTION 1: A Random Section") will be
   a heading in the table of contents. Source files that should be
   generated and included in that section should be placed on individual
   lines, with one line separating the first source filename and the
   :maxdepth: line.

.. Sources can also be included from subfolders of this directory.
   (e.g. "DataStructures/queues.rst").

SECTION 1: Introduction
:::::::::::::::::::::::

Congratulations!   If you can see this file you have probably successfully run the ``petljadoc init-runestone`` command.  

If you are looking at this as a source file you should now run ``petljadoc preview``  to generate html files and preview 
them in your browser.

This is just a sample of what you can do.  The index.rst file is the table of contents for your entire project.
 You can put all of your writing in the index, or  you can include additional rst files. 
 Those files may even be in subdirectories that you can reference using a relative path.


::


   .. toctree::
      :maxdepth: 2

      some/path/myfile.rst


Section 2: Links
::::::::::::::::

Runestone uses the ``restructuredText`` (rst) markup language.  We chose this over markdown largely because rst is extensible.  Nearly all of the basic markup tasks are already handled by restructuredText.  You should check out the docs for the basics of restructuredText (link below). Our extensions are all for the interactive elements.  One key hint about restructuredText:  Its like **Python** -- *indentation matters!*

* Section `restructuredText <https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html>`_ from Sphinx Docs 
* `Runestone Author’s Guide <https://runestone.academy/runestone/static/authorguide/index.html>`_
* `PetljaDoc README <https://github.com/Petlja/PetljaDoc/blob/master/README.md>`_ 
* An Overview of Runestone Interactive `source <https://github.com/RunestoneInteractive/overview>`_ and 
  `published book <https://runestone.academy/runestone/static/overview/overview.html>`_
* A PetljaDoc project Textual Programming in Python `source code <https://github.com/Petlja/TxtProgInPythonEng/>`_ and 
  `public preview <https://petlja.github.io/TxtProgInPythonEng/>`_


SECTION 3: Sample Directives
::::::::::::::::::::::::::::::::::::::

ActiveCode
----------

.. activecode:: codeexample1
   :coach:
   :caption: This is a caption

   print("My first program adds a list of numbers")
   myList = [2, 4, 6, 8, 10]
   total = 0
   for num in myList:
       total = total + num
   print(total)

Multiple Choice
---------------

.. mchoice:: question1_2
    :multiple_answers:
    :correct: a,b,d
    :answer_a: red
    :answer_b: yellow
    :answer_c: black
    :answer_d: green
    :feedback_a: Red is a definitely on of the colors.
    :feedback_b: Yes, yellow is correct.
    :feedback_c: Remember the acronym...ROY G BIV.  B stands for blue.
    :feedback_d: Yes, green is one of the colors.

    Which colors might be found in a rainbow? (choose all that are correct)

Now feel free to modify this file to start creating your own interactive page.
