# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['manim_automata',
 'manim_automata.mobjects',
 'manim_automata.mobjects.automata_dependencies']

package_data = \
{'': ['*']}

install_requires = \
['xmltodict>=0.13.0,<0.14.0']

entry_points = \
{'manim.plugins': ['manim_automata = manim_automata']}

setup_kwargs = {
    'name': 'manim-automata',
    'version': '0.2.4',
    'description': 'A Manim implementation of automata',
    'long_description': 'MANIM AUTOMATA\n==============\nA Manim plugin that allows you to generate scenes with Finite State Machines and their inputs. The plugin will automatically generate these animations with minimal setup from the user.\n\nThis plugin has been funded by the University of Leeds.\n\nYOUTUBE VIDEO EXAMPLE\n=====================\n[![Finite State Machine in Manim](https://img.youtube.com/vi/Lfq6XD3-aUw/0.jpg)](https://www.youtube.com/watch?v=Lfq6XD3-aUw)\n\nNotes\n=====\nThe manim-automata plugin currently relies on JFLAP files, future updates will enable the user to create automata without JFLAP.\n[JFLAP](https://www.jflap.org) is software for experimenting with formal languages topics.\n\nInstallation\n============\nTo install manim-automata plugin run:\n\n   pip install manim-automata\n\nTo see which version of manim-automata you have:\n\n    manim-automata\n\nor\n\n    pip list\n\n\nImporting\n=========\nTo use manim-automata in your project, you can:\n\n* Add ``from manim_automata import *`` to your script.\nOnce manim-automata has been imported, you can use the ManimAutomata class to create automata.\n\nHow To Use\n==========\n\n\n\n\nExample\n=======\n```python\nclass Automaton(MovingCameraScene):\n    def construct(self):\n        manim_automaton = ManimAutomaton(xml_file=\'example_machine.jff\')\n        \n        #Adjust camera frame to fit ManimAutomaton in scene\n        self.camera.frame_width = manim_automaton.width + 10\n        self.camera.frame_height = manim_automaton.height + 10\n        self.camera.frame.move_to(manim_automaton) \n\n\n        #Create an mobject version of input for the manim_automaton\n        automaton_input = manim_automaton.construct_automaton_input("110011")\n\n        #Position automaton_input on the screen to avoid overlapping.\n        automaton_input.shift(LEFT * 2)\n        automaton_input.shift(UP * 10)\n\n        self.play(\n                DrawBorderThenFill(manim_automaton),\n                FadeIn(automaton_input)\n            )\n\n        # Play all the animations generate from .play_string()\n        for sequence in manim_automaton.play_string(automaton_input):\n            for step in sequence:\n                self.play(step, run_time=1)\n```\nTo run the code and generate the video, run:\n\n* manim -pqh <name_of_script.py> Automaton\n\n\nXML file used:\n```\n<?xml version="1.0" encoding="UTF-8" standalone="no"?><!--Created with JFLAP 7.1.--><structure>\n\t<type>fa</type>\n\t<automaton>\n\t\t<!--The list of states.-->\n\t\t<state id="0" name="q0">\n\t\t\t<x>84.0</x>\n\t\t\t<y>122.0</y>\n\t\t\t<initial/>\n\t\t</state>\n\t\t<state id="1" name="q1">\n\t\t\t<x>218.0</x>\n\t\t\t<y>175.0</y>\n\t\t</state>\n\t\t<state id="2" name="q2">\n\t\t\t<x>386.0</x>\n\t\t\t<y>131.0</y>\n\t\t\t<final/>\n\t\t</state>\n\t\t<state id="3" name="q3">\n\t\t\t<x>227.0</x>\n\t\t\t<y>36.0</y>\n\t\t</state>\n\t\t<!--The list of transitions.-->\n\t\t<transition>\n\t\t\t<from>0</from>\n\t\t\t<to>1</to>\n\t\t\t<read>0</read>\n\t\t</transition>\n\t\t<transition>\n\t\t\t<from>0</from>\n\t\t\t<to>1</to>\n\t\t\t<read>1</read>\n\t\t</transition>\n\t\t<transition>\n\t\t\t<from>2</from>\n\t\t\t<to>3</to>\n\t\t\t<read>0</read>\n\t\t</transition>\n\t\t<transition>\n\t\t\t<from>1</from>\n\t\t\t<to>2</to>\n\t\t\t<read>1</read>\n\t\t</transition>\n\t\t<transition>\n\t\t\t<from>3</from>\n\t\t\t<to>0</to>\n\t\t\t<read>1</read>\n\t\t</transition>\n\t\t<transition>\n\t\t\t<from>3</from>\n\t\t\t<to>0</to>\n\t\t\t<read>0</read>\n\t\t</transition>\n\t</automaton>\n</structure>\n```\n\n',
    'author': 'Sean Nelson',
    'author_email': 'snelson01010@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/SeanNelsonIO/manim-automata',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
