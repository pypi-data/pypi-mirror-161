[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![PyPi version](https://badgen.net/pypi/v/pip/)](https://pypi.org/project/pip/)

# Smarter API for Python

This API allows communication between any python based Component on the [smarter.ai](https://www.smarter.ai/)
platform.

## User Installation

The latest released version are available at the Python Package Index (PyPI).

To install using pip:

```bash
pip install smarterai
```

## Usage

- For starters an account needs to be created at our platform. So visit our website and create an account
  at [smarter.ai](https://www.smarter.ai/).

- Then in order for the python code to be accessible for the [smarter.ai](https://www.smarter.ai/) platform, follow
  these steps:
    1. Visit the [Studio](https://studio.smarter.ai/digital_twin)
    2. Start a new [new Experiment](https://studio.smarter.ai/digital_twin/newExperiment)
    3. Chose a Full Pipeline Template.
    4. Follow the wizard.
    5. Go to Build -> Experiment Editor.
    6. From _Container: Environment_ Drag & drop a python component.
    7. From _Blank: Starter Templates_ Drag & drop Python Code Template on top of the added Environment component.
    8. Double-click on the Python Code Template newly added Component. 
    9. Edit/upload your code there.

- You can then start building your code by copy-pasting the code found in the examples below.

- The Python Component's interface needs to consist of the following:
    1. Import ```smarterai```:
        ```python
            from smarterai import *
        ```
    2. A class called ```SmarterComponent```.
    2. ```SmarterComponent``` should inherit from ```SmarterPlugin```:
        ```python
            class SmarterComponent(SmarterPlugin):
        ```
    3. The class should have a method ```invoke``` with the following signature:
        ```python
            def invoke(self, port: str, message: SmarterMessage, sender: SmarterSender) -> Optional[SmarterMessage]:
        ```

### Example 1

This is the basic interface for a python based component.

```python
from typing import Optional
from smarterai import SmarterPlugin, SmarterMessage, SmarterSender


class SmarterComponent(SmarterPlugin):
    def invoke(self, port: str, message: SmarterMessage, sender: SmarterSender) -> Optional[SmarterMessage]:
        print(f"Received the message '{message}' on port '{port}'")
        return
```

### Example 2

If your component needs initializing/booting before it starts running. Then a method ```boot``` needs to be defined.

```python
from typing import Optional
from smarterai import SmarterPlugin, SmarterMessage, SmarterSender


class SmarterComponent(SmarterPlugin):
    def __init__(self):
        self.port_fn_mapper = {'boot': self.boot}

    def boot(self, message: SmarterMessage, sender: SmarterSender) -> Optional[SmarterMessage]:
        # Write code here
        return

    def invoke(self, port: str, message: SmarterMessage, sender: SmarterSender) -> Optional[SmarterMessage]:
        print(f"Received the message '{message}' on port '{port}'")
        if port in self.port_fn_mapper:
            self.port_fn_mapper[port](message, sender)
        return
```

### Example 3

If your component needs to send messages to other components, then you can use sender.

```python
from typing import Optional
from smarterai import SmarterPlugin, SmarterMessage, SmarterSender


class SmarterComponent(SmarterPlugin):
    def __init__(self):
        self.port_fn_mapper = {'boot': self.boot, 'start': self.start}

    def boot(self, message: SmarterMessage, sender: SmarterSender) -> Optional[SmarterMessage]:
        # Write code here
        return

    def start(self, message: SmarterMessage, sender: SmarterSender) -> None:
        port = 'out'
        new_message = SmarterMessage({'name': 'Smarter AI'})
        sender.send_message(message=new_message, port=port)

    def invoke(self, port: str, message: SmarterMessage, sender: SmarterSender) -> Optional[SmarterMessage]:
        print(f"Received the message '{message}' on port '{port}'")
        if port in self.port_fn_mapper:
            self.port_fn_mapper[port](message, sender)
        return
```

### Example 4

If your component needs to set data to front-end patterns.

```python
from typing import Optional
from smarterai import SmarterPlugin, SmarterMessage, SmarterSender


class SmarterComponent(SmarterPlugin):
    def __init__(self):
        self.port_fn_mapper = {'boot': self.boot, 'start': self.start}

    def boot(self, message: SmarterMessage, sender: SmarterSender) -> Optional[SmarterMessage]:
        # Write code here
        return

    def start(self, message: SmarterMessage, sender: SmarterSender) -> None:
        pattern = "text_field"
        data = 'some value'
        sender.set_data(pattern=pattern, data=data)

    def invoke(self, port: str, message: SmarterMessage, sender: SmarterSender) -> Optional[SmarterMessage]:
        print(f"Received the message '{message}' on port '{port}'")
        if port in self.port_fn_mapper:
            self.port_fn_mapper[port](message, sender)
        return
```

## Credits

Authored by Nevine Soliman and Carlos Medina (smarter.ai - All rights reserved)