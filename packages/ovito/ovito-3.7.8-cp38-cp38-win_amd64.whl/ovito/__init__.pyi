"""This module defines the :py:class:`Scene` class, which serves as a "universe" or context for all actions
performed by a script. The global scene object is accessible as module-level variable :py:data:`ovito.scene`.
The scene manages a list of :py:class:`Pipeline` objects, which will be visible in images and videos
when rendering the scene through a :py:class:`Viewport`. Furthermore, you can save the entire
scene definition including all pipelines to a :file:`.ovito` session state file, which can be opened in the graphical OVITO application."""
__all__ = ['version', 'version_string', 'scene', 'Scene', 'enable_logging']
from typing import Tuple, Optional, Any, Union, Mapping, MutableMapping, Sequence, MutableSequence
import ovito.pipeline

class Scene:
    """This class encompasses all data of an OVITO program session (basically everything that gets saved in a ``.ovito`` state file). It manages the list of objects (i.e. :py:class:`Pipeline` instances) that are part of the three-dimensional scene and which will show up in rendered images. 

From a script's point of view, there exists exactly one universal instance of this class at any time, which is accessible through the :py:data:`ovito.scene` module-level variable. A script cannot create another :py:class:`Scene` instance by itself."""

    @property
    def pipelines(self) -> MutableSequence[ovito.pipeline.Pipeline]:
        """The list of :py:class:`Pipeline` objects that are currently part of the three-dimensional scene.
Only pipelines in this list will display their output data in the viewports and in rendered images. You can add or remove a pipeline either by calling
its :py:meth:`add_to_scene` or :py:meth:`remove_from_scene` methods or by directly manipulating this
list using the standard Python ``append()`` and ``del`` statements:

```python
  from ovito import scene
  from ovito.io import import_file
  
  pipeline = import_file('input/simulation.dump')
  
  # Insert the pipeline into the visualization scene.
  pipeline.add_to_scene()
  # It's now part of the 'scene.pipelines' list.
  assert(pipeline in scene.pipelines)
  # If needed, we can take it out again.
  pipeline.remove_from_scene()
```"""
        ...

    @property
    def selected_pipeline(self) -> Optional[ovito.pipeline.Pipeline]:
        """The :py:class:`Pipeline` currently selected in the OVITO desktop application,
or ``None`` if no pipeline is selected. Typically, this is the last pipeline that was added to the scene using
`Pipeline.add_to_scene()`.

This field can be useful for macro scripts running in the context of an interactive OVITO session, 
which perform some action on the currently selected pipeline such as inserting a modifier."""
        ...

    def save(self, filename: str) -> None:
        """Saves the scene to a :file:`.ovito` session state file. The scene comprises the definition of all pipelines currently in the :py:attr:`Scene.pipelines` list as well as the modifiers and visual elements that are part of these pipelines. This function works like the *Save Session State As* function of the OVITO desktop application. 

.. note::

  Only :py:class:`Pipeline` objects for which `add_to_scene()` was called will be included in the session state file.   Pipelines that have not been added to the scene's :py:attr:`~Scene.pipelines` list will be left out. 

:param str filename: Output file path

The saved session state may be restored again from disk by 

  * calling the :py:meth:`Scene.load` method,
  * using the :command:`-o` command line option of the :program:`ovitos` interpreter, or
  * opening the saved state file with the OVITO desktop application. 

After loading the state file back from disk, the global :py:attr:`Scene.pipelines` list will contain again all pipeline objects that were part of the scene at the time it was saved. See also the section :py:ref:`saving_loading_pipelines`."""
        ...

    def load(self, filename: str) -> None:
        """Loads the pipeline(s) stored in a .ovito session state file. This function works like the *Load Session State* function of the graphical OVITO application. It can load session state files that were produced with the interactive OVITO application or which have been written by the :py:meth:`Scene.save` method. 

:param str filename: File path of the .ovito session file to load


After the state file has been loaded, the :py:attr:`pipelines` list will be populated with exact copies of the data pipelines that were part of the scene when it was saved. See also :pythis section for more information."""
        ...

def enable_logging() -> None:
    """Call this function at the beginning of your Python script to activate logging of otherwise unnoticeable operations performed by OVITO. Subsequently, when it performs long-running work or computations, OVITO will print messages to ``stderr`` indicating the current activity, e.g. file I/O, modifier execution, and image rendering."""
    ...
version: Tuple[int, int, int]
'A module-level attribute reporting the OVITO program version number.'
version_string: str
'Module-level attribute reporting the OVITO program version (as a string).'
scene: Scene
'This module-level variable points to the global :py:class:`~ovito.Scene` object,\nwhich serves as context for all operations performed by the script. The :py:class:`~ovito.Scene` object\nrepresents the program state and provides access to the contents of the visualization scene'