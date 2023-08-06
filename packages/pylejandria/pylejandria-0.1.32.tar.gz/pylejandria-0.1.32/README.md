# **PYLEJANDRIA**
<img src="https://www.traveldepartment.com/media/23634/career-icons-training-and-development.png"
     alt="HTML image alt text"
     title="Optional image title"
     align="right"
     width="100px"
/>

Javier and I were bored of sending us scripts and functions by whatsapp, so we decided to make a compilation of the *most useful functions*, even create some together. The project is called **PyLejandria** thanks to the library of Alexandria, where it is said that a colossal amount of knowledge resided. The project is not at all serious, but we will try to do the best we can with our current level of programming.

# **MODULES**
* **GUI**
    * Compilation of widgets that take as a basis the widgets of tkinter, can add functions to make simple interfaces in a very simple way without losing flexibility or having new widgets.

* **MATH**
    * Set of functions and classes that facilitate mathematics in python, we are aware that there are specialized libraries, but the idea of this module is that it is easy and fast access.

* **MODULE**
    * A simple module consisting of an init function to easily generate a new python package. It could in the future be part of a complete tool to maintain packages.

* **TOOLS**
    * Set of everyday functions, mostly for debugging, consists of variables, functions and classes that make the interaction of the program with the terminal simpler, but without needing a user interface.

* **UPLOAD**
    * Module with graphical interface for the management of python packages, has tools for easierly upload the package to GitHub and PyPi, allows you to decide whether to upload to a GitHub repository automatically detecting if the package has one, in addition to not uploading to PyPi in case we only want to update the repository.

# **DOWNLOAD**
`pip install pylejandria` or copy from [PyPi](https://pypi.org/project/pylejandria/).

# **HELP**

* ## **Script**
    If you need help you can import the package and use the example function, it will open an interface that will show you all the attributes of the module and its description. This are the following examples, in this case we will see the help of the "gui" module

    ```python
    # Import the module
    from pylejandria import gui

    # Run the example if we run the script directly
    if __name__ == '__main__':
        gui.example()
    ```
    
* ## **Terminal**
    Open your favorite terminal and run the following commands
    ```bash
    # Import the module
    from pylejandria import gui

    # Run the example
    gui.example()
    ```

# **TK FILES**
***Tk files*** are cascade files that wrap around the interface system of the [**tkinter**](https://docs.python.org/es/3/library/tkinter.html) module. The idea is to have a structure similar to [**kivy**](https://www.geeksforgeeks.org/python-kivy-kv-file/) or [**QML**](https://es.wikipedia.org/wiki/QML) files, it also has a system of styles with a format similar to [**CSS**](https://www.w3schools.com/Css/). The main idea of this format is to create separate interfaces from the functional file, for a better organization and have the possibility of editing the interface from the code since it is a text file. It should be noted that you should know about the tkinter module.

This is the **minimal configuration** for a simple window.

We start with a "Tk", which is the base widget of tkinter, then with an extra level of indentation we state the properties that we want. Here is the syntax.

It is important to **pay attention to the spaces**, since at the moment the project is in the initial phases and **there are no considerations towards these cases**. This could change in the future.
* **For simple properties**
    * property_name: property_value
* **To call functions of the widget we start the name with a "."**
    * .function_name: function_value
```
Tk
    .geometry: '500x500'
    .title: 'Simple UI'
    bg: '#181818'
```

To run the tk file we use this simple code, what it does is import the load of the function from the pylejandria.gui module, then we create a window variable that will store the window built from the given file, we also pass the "__file\__" as the second parameter, this is necessary in case we have functions for our interface,   otherwise we can skip it. (But it is recommended to use it in any case.)

```python
# Import load from pylejandria.gui module
from pylejandria.gui import load

# Use this if statement, is important to avoid recursive imports
if __name__ == '__main__':
    window = load('gui.tk', __file__)
    window.mainloop()
```

Now let's see a more complex example to implement functions and the id system. Here is the new syntax.

* **To call a function start the function's name with a "$" then the name**
    * For example: $change
* **To reference an id start the id with a "#" then the id**
    * For example: #topleft_frame
* **If the function needs arguments then we pass them using "()" around the elements and each value with a " | "**. *(Notice the spacing)*
    * For example: $change **(#topleft_frame | "#ff0000" | "#800000")**
* **References**.
    * **self**: refers to the widget itself.
    * **self.master**: refers to the parent of the widget.
    * **self[property]**: refers to the given property of the widget itself.
    * Any other value **must follow python´s syntax**.
        * For example: '#ff0000', [self, self.master, self['bg']]

**.tk file**
```
Tk
    .title: 'Simple UI'
    bg: '#181818'
    Frame
        bg: '#323232'
        .pack: {}
        Frame
            id: 'topleft_frame'
            bg: '#ff0000'
            width: 200
            height: 200
            .grid: {'row': 0, 'column': 0, 'padx': (50, 0), 'pady': (50, 0)}
        Frame
            id: 'topright_frame'
            bg: '#ffff00'
            width: 200
            height: 200
            .grid: {'row': 0, 'column': 1, 'padx': 50, 'pady': (50, 0)}
        Frame
            id: 'bottomleft_frame'
            bg: '#00ffff'
            width: 200
            height: 200
            .grid: {'row': 1, 'column': 0, 'padx': (50, 0), 'pady': 50}
        Frame
            id: 'bottomright_frame'
            bg: '#00ff00'
            width: 200
            height: 200
            .grid: {'row': 1, 'column': 1, 'padx': 50, 'pady': 50}
    Frame
        bg: 'gray'
        .pack: {}
        Button
            text: 'change top left'
            command: $change(#topleft_frame | '#ff0000' | '#800000')
            .grid: {'row': 0, 'column': 0}
        Button
            text: 'change top right'
            command: $change(#topright_frame | '#ffff00' | '#808000')
            .grid: {'row': 0, 'column': 1}
        Button
            text: 'change bottom left'
            command: $change(#bottomleft_frame | '#00ffff' | '#008080')
            .grid: {'row': 0, 'column': 2}
        Button
            text: 'change bottom right'
            command: $change(#bottomright_frame | '#00ff00' | '#008000')
            .grid: {'row': 0, 'column': 3}
```
**.py file**
```python
# Import load from pylejandria.gui module
from pylejandria.gui import load

# Define the change function, this will be called by the buttons
def change(widget: tk.Widget, color1: str, color2: str) -> None:
    """
    Change the color of the background of the widget based on its current
    color. If the current color is equal to the first color then we choose the
    second one and viceversa.
    """
    widget['bg'] = color1 if widget['bg'] == color2 else color2

# Use this if statement, is important to avoid recursive imports
if __name__ == '__main__':    
    window = load(path, __file__)
    window.mainloop()
```

# **CREDITS**
| **Name**         | **User**         |
| ---------------- | ---------------- |
| Armando Chaparro | TheCodingStudent |

# **LICENSE**
[PyLejandria](https://github.com/TheCodingStudent/pylejandria) by Armando Chaparro is licensed under a [MIT License](https://mit-license.org/). See LICENSE.md.

Copyright © 2022 [Armando Chaparro](https://github.com/TheCodingStudent)