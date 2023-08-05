"""This module contains object types that are part of OVITO's data pipeline system.

Pipelines:

  * :py:class:`Pipeline`
  * :py:class:`Modifier` (base class)

Data sources:

  * :py:class:`StaticSource`
  * :py:class:`FileSource`
  * :py:class:`PythonScriptSource`"""
__all__ = ['Pipeline', 'Modifier', 'StaticSource', 'FileSource', 'PythonScriptSource', 'ModifierInterface', 'ReferenceConfigurationModifier']
from typing import Tuple, Optional, Any, Union, Mapping, MutableMapping, Sequence, MutableSequence, Callable, List
import ovito.data
import ovito.modifiers
import enum
import abc

class ModifierInterface:
    """A HasTraits subclass which behaves like HasStrictTraits but
also enables the features of Abstract Base Classes (ABC). See the
'abc' module in the standard library for more information."""

    class InputSlot:

        @property
        def num_frames(self) -> int:
            ...

        def compute(self, frame: Optional[int]=None) -> ovito.data.DataCollection:
            ...
    extra_input_slots: int = 0

    @abc.abstractmethod
    def modify(self, data: ovito.data.DataCollection, *, frame: int, input_slots: List[ovito.modifiers.PythonScriptModifier.InputSlot], data_cache: ovito.data.DataCollection, **kwargs):
        ...

class StaticSource:
    """Serves as a data :py:attr:`~Pipeline.source` for a :py:class:`Pipeline`. 
A :py:class:`StaticSource` manages a :py:class:`DataCollection`, which it will pass to the :py:class:`Pipeline` as input data. 
One typically initializes a :py:class:`StaticSource` with a collection of data objects, then wiring it to a :py:class:`Pipeline` as follows: 

.. literalinclude:: ../example_snippets/static_source.py"""

    def compute(self, frame: Optional[int]=None) -> ovito.data.DataCollection:
        """Returns a copy of the :py:class:`DataCollection` stored in this source's :py:attr:`data` field. 

:param frame: This parameter is ignored, because the data of a :py:class:`StaticSource` is not time-dependent.
:return: A new :py:class:`DataCollection` containing the data stored in this :py:class:`StaticSource`."""
        ...

    @property
    def data(self) -> Optional[ovito.data.DataCollection]:
        """The :py:class:`DataCollection` managed by this object, which will be fed to the pipeline. 

:Default: ``None``"""
        ...

class FileSource:
    """This object type serves as a :py:attr:`Pipeline.source` and takes care of reading the input data for a :py:class:`Pipeline` from an external file. 

You normally do not need to create an instance of this class yourself; the :py:func:`import_file` function does it for you and wires the fully configured :py:class:`FileSource` to the new :py:attr:`Pipeline`. However, if needed, the :py:meth:`FileSource.load` method allows you to load a different input file later on and replace the input of the existing pipeline with a new dataset: 

```python
  from ovito.io import import_file
  
  # Create a new pipeline with a FileSource:
  pipeline = import_file('input/first_file.dump')
  
  # Get the data from the first file:
  data1 = pipeline.compute()
  
  # Use FileSource.load() method to replace the pipeline's input with a different file 
  pipeline.source.load('input/second_file.dump')
  
  # Now the pipeline gets its input data from the new file:
  data2 = pipeline.compute()
```

Furthermore, you will encounter other :py:class:`FileSource` objects in conjunction with certain modifiers that need secondary input data from a separate file. The :py:class:`CalculateDisplacementsModifier`, for example, manages its own :py:class:`FileSource` for loading reference particle positions from a separate input file. Another example is the :py:class:`LoadTrajectoryModifier`, which employs its own separate :py:class:`FileSource` instance to load the particle trajectories from disk and combine them with the topology data previously loaded by the main :py:class:`FileSource` of the data pipeline. 

Data access

The :py:class:`FileSource` class provides two ways of accessing the data that is loaded from the external input file(s). For read-only access to the data, the :py:meth:`FileSource.compute` method should be called. It loads the data of a specific frame from the input simulation trajectory and returns it as a new :py:class:`DataCollection` object: 

```python
  # This creates a new Pipeline with an attached FileSource.
  pipeline = import_file('input/simulation.dump')
  
  # Request data of animation frame 0 from the FileSource.
  data = pipeline.source.compute(0)
  print(data.particles.positions[...])
```

To modify or amend the :py:class:`DataCollection` that was loaded by the :py:class:`FileSource`, you should insert a :ref:`user-defined modifier function <writing_custom_modifiers>` into the pipeline. A typical use case is assigning the radii and names to particle types loaded from a simulation file that doesn't contain named atom types: 

```python
  pipeline = import_file('input/simulation.dump')
  
  # User-defined modifier function that assigns names and radii to numeric atom types:
  def setup_atom_types(frame, data):
      types = data.particles_.particle_types_
      types.type_by_id_(1).name = "Cu"
      types.type_by_id_(1).radius = 1.35
      types.type_by_id_(2).name = "Zr"
      types.type_by_id_(2).radius = 1.55
  
  pipeline.modifiers.append(setup_atom_types)
```"""

    def compute(self, frame: Optional[int]=None) -> ovito.data.DataCollection:
        """Requests data from this data source. The :py:class:`FileSource` will load it from the external file if needed.

The optional *frame* parameter determines the frame to retrieve, which must be in the range 0 through (:py:attr:`num_frames`-1).
If no frame number is specified, the current time slider position is used (will always be frame 0 for scripts not running in the context of an interactive OVITO session).

The :py:class:`FileSource` uses a caching mechanism to keep the data for one or more frames in memory. Thus, invoking :py:meth:`compute`
repeatedly to retrieve the same frame will typically be very fast.

:param int frame: The source frame to retrieve.
:return: A new :py:class:`DataCollection` containing the loaded data."""
        ...

    def load(self, location: Union[str, Sequence[str]], **params) -> None:
        """Sets a new input file, from which this data source will retrieve its data from.

The function accepts additional keyword arguments, which are forwarded to the format-specific file reader.
For further information, please see the documentation of the :py:func:`import_file` function,
which has the same function interface as this method.

:param str location: The local file(s) or remote URL to load."""
        ...

    @property
    def data(self) -> Optional[ovito.data.DataCollection]:
        """This field provides access to the internal :py:class:`DataCollection`, i.e. the master copy of the data loaded from the input file (at frame 0)."""
        ...

    @property
    def num_frames(self) -> int:
        """This read-only attribute reports the number of frames found in the input file or sequence of input files. The data for the individual frames can be obtained using the :py:meth:`.compute` method."""
        ...

    @property
    def source_path(self) -> Union[str, Sequence[str]]:
        """This read-only attribute returns the path(s) or URL(s) of the file(s) where this :py:class:`FileSource` retrieves its input data from.
You can change the source path by calling :py:meth:`.load`."""
        ...

class PythonScriptSource:
    """Example:

.. literalinclude:: ../example_snippets/python_script_source.py"""

    @property
    def function(self) -> Optional[Callable[[int, ovito.data.DataCollection], Any]]:
        """The Python function to be called each time the data pipeline is evaluated by the system.

The function must have a signature as shown in the example above. The *frame* parameter specifies the current animation frame number at which the data pipeline is being evaluated. The :py:class:`DataCollection` *data* is initially empty should be populated with data objects by the user-defined source function. 

:Default: ``None``"""
        ...

class Modifier:
    """This is the base class for all modifier types in OVITO. See the :py:mod:`ovito.modifiers` module for a list of concrete modifier types that can be inserted into a data :py:class:`Pipeline`."""

    @property
    def enabled(self) -> bool:
        """Controls whether the modifier is applied to the data. Disabled modifiers are skipped during evaluation of a data pipeline. 

:Default: ``True``"""
        ...

class ReferenceConfigurationModifier(Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

This is the common base class of analysis modifiers that perform some kind of comparison
of the current particle configuration with a reference configuration. For example,
the :py:class:`CalculateDisplacementsModifier`, the :py:class:`AtomicStrainModifier`
and the :py:class:`WignerSeitzAnalysisModifier` are modifier types that require
a reference configuration as additional input.

Constant and sliding reference configurations

The :py:class:`ReferenceConfigurationModifier` base class provides various fields that
allow you to specify the reference particle configuration. By default, frame 0 of the currently loaded
simulation sequence is used as reference. You can select any other frame with the :py:attr:`reference_frame` field.
Sometimes an incremental analysis is desired, instead of a fixed reference configuration. That means the sliding reference configuration and the current configuration
are separated along the time axis by a constant period (*delta t*). The incremental analysis mode is activated by
setting the :py:attr:`use_frame_offset` flag and specifying the desired :py:attr:`frame_offset`.

External reference configuration file

By default, the reference particle positions are obtained by evaluating the same data pipeline that also
provides the current particle positions, i.e. which the modifier is part of. That means any modifiers preceding this modifier in the pipeline
will also act upon the reference particle configuration, but not modifiers that follow in the pipeline.

Instead of taking it from the same data pipeline, you can explicitly provide a reference configuration by loading it from a separate data file.
To this end the :py:attr:`reference` field contains a :py:class:`FileSource` object and you can
use its :py:meth:`load` method to load the reference particle positions from a separate file.

Handling of periodic boundary conditions and cell deformations

Certain analysis modifiers such as the :py:class:`CalculateDisplacementsModifier` and the :py:class:`AtomicStrainModifier`
calculate the displacements particles experienced between the reference and the current configuration.
Since particle coordinates in periodic simulation cells are often stored in a *wrapped* form,
calculating the displacement vectors is non-trivial when particles have crossed the periodic boundaries.
By default, the *minimum image convention* is used in these cases, but you can turn if off by
setting :py:attr:`minimum_image_convention` to ``False``, for example if the input particle coordinates
are given in unwrapped form.

Furthermore, if the simulation cell of the reference and the current configuration are different, it makes
a slight difference whether displacements are calculated in the reference or in the current frame.
The :py:attr:`affine_mapping` property controls the type of coordinate mapping that is used."""

    class AffineMapping(enum.Enum):
        """AUTODOC_SKIP_MEMBER

Members:

  Off

  ToReference

  ToCurrent"""
        Off = enum.auto()
        ToReference = enum.auto()
        ToCurrent = enum.auto()

    @property
    def affine_mapping(self) -> AffineMapping:
        """Selects the type of affine deformation applied to the particle coordinates of either the reference or the current configuration prior to the actual analysis computation. Must be one of the following modes:
 * ``ReferenceConfigurationModifier.AffineMapping.Off``
 * ``ReferenceConfigurationModifier.AffineMapping.ToReference``
 * ``ReferenceConfigurationModifier.AffineMapping.ToCurrent``


When affine mapping is disabled (``AffineMapping.Off``), particle displacement vectors are simply calculated from the difference of current and reference positions, irrespective of the cell shape the reference and current configuration. Note that this can introduce a small geometric error if the shape of the periodic simulation cell changes considerably. The mode ``AffineMapping.ToReference`` applies an affine transformation to the current configuration such that all particle positions are first mapped to the reference cell before calculating the displacement vectors. The last option, ``AffineMapping.ToCurrent``, does the reverse: it maps the reference particle positions to the deformed cell before calculating the displacements. 

:Default: ``ReferenceConfigurationModifier.AffineMapping.Off``"""
        ...

    @property
    def frame_offset(self) -> int:
        """The relative frame offset when using a sliding reference configuration (if :py:attr:`use_frame_offset` == ``True``). Negative frame offsets correspond to reference configurations that precede the current configuration in time. 

:Default: ``-1``"""
        ...

    @property
    def minimum_image_convention(self) -> bool:
        """If ``False``, then displacements are calculated from the particle coordinates in the reference and the current configuration as is. Note that in this case the calculated displacements of particles that have crossed a periodic simulation cell boundary will be wrong if their coordinates are stored in a wrapped form. If ``True``, then the minimum image convention is applied when calculating the displacements of particles that have crossed a periodic boundary. 

:Default: ``True``"""
        ...

    @property
    def reference(self) -> FileSource:
        """A pipeline :py:attr:`source` object that provides the reference particle positions. By default this field is ``None``, in which case the modifier obtains the reference particle positions from data pipeline it is part of. You can explicitly assign a data source object such as a :py:class:`FileSource` or a :py:class:`StaticSource` to this field to specify an explicit reference configuration. 

```python
  # The modifier that requires a reference config:
  mod = CalculateDisplacementsModifier()
  
  # Load the reference config from a separate input file.
  mod.reference = FileSource() # Note: You may have to import FileSource from the ovito.pipeline module. 
  mod.reference.load('input/simulation.0.dump')
```

:Default: ``None``"""
        ...

    @property
    def reference_frame(self) -> int:
        """The frame number to use as reference configuration. Ignored if :py:attr:`use_frame_offset` is set.

:Default: ``0``"""
        ...

    @property
    def use_frame_offset(self) -> bool:
        """Determines whether a sliding reference configuration is taken at a constant time offset (specified by :py:attr:`frame_offset`) relative to the current frame. If ``False``, a constant reference configuration is used (set by the :py:attr:`reference_frame` parameter) irrespective of the current frame.

:Default: ``False``"""
        ...

class Pipeline:
    """This class encapsulates a data pipeline, consisting of a *data source* and a chain of zero or more *modifiers*, 
which manipulate the data on the way through the pipeline. 

Pipeline creation

Every pipeline has a *data source*, which loads or dynamically generates the input data entering the 
pipeline. This source is accessible through the :py:attr:`Pipeline.source` field and may be replaced with a different kind of source object if needed. 
For pipelines created by the :py:func:`import_file` function, the data source is automatically set to be a 
:py:class:`FileSource` object, which loads the input data 
from the external file and feeds it into the pipeline. Another kind of data source is the 
:py:class:`StaticSource`, which can be used if you want to programmatically specify the input data for the pipeline 
instead of loading it from a file. 

The modifiers that are part of the pipeline are accessible through the :py:attr:`Pipeline.modifiers` field. 
This list is initially empty and you can populate it with the modifier types found in the :py:mod:`ovito.modifiers` module. 
Note that it is possible to employ the same :py:class:`Modifier` instance in more than one pipeline. And it is 
okay to use the same data source object for several pipelines, letting them process the same input data. 

Pipeline evaluation

Once the pipeline is set up, its computation results can be requested by calling :py:meth:`.compute()`, which means that the input data will be loaded/generated by the :py:attr:`source` 
and all modifiers of the pipeline are applied to the data one after the other. The :py:meth:`.compute()` method 
returns a new :py:class:`DataCollection` storing the data objects produced by the pipeline. 
Under the hood, an automatic caching system ensures that unnecessary file accesses and computations are avoided. 
Repeatedly calling :py:meth:`compute` will not trigger a recalculation of the pipeline's results unless you 
alter the pipeline's data source, the chain of modifiers, or a modifier's parameters.

Usage example

The following code example shows how to create a new pipeline by importing an MD simulation file and inserting a :py:class:`SliceModifier` to
cut away some of the particles. Finally, the total number of remaining particles is printed.

```python
  from ovito.io import import_file
  from ovito.modifiers import SliceModifier
  
  # Import a simulation file. This creates a Pipeline object.
  pipeline = import_file('input/simulation.dump')
  
  # Insert a modifier that operates on the data:
  pipeline.modifiers.append(SliceModifier(normal=(0,0,1), distance=0))
  
  # Compute the effect of the slice modifier by evaluating the pipeline.
  output = pipeline.compute()
  print("Remaining particle count:", output.particles.count)
```

If you would like to access the unmodified input data of the pipeline, i.e. *before* it has been processed by any of the modifiers,
you can call the :py:meth:`FileSource.compute` method instead:

```python
  # Access the pipeline's input data provided by the FileSource:
  input = pipeline.source.compute()
  print("Input particle count:", input.particles.count)```

Data visualization

If you intend to produce graphical renderings of a output data produced by a pipeline,
you must make the pipeline part of the current three-dimensional scene by calling the :py:meth:`Pipeline.add_to_scene` method.

Data export

To export the generated data of the pipeline to an output file, simply call the :py:func:`ovito.io.export_file` function with the pipeline."""

    def __init__(self) -> None:
        ...

    def add_to_scene(self) -> None:
        """Inserts the pipeline into the three-dimensional scene by appending it to the :py:attr:`ovito.Scene.pipelines` list.
The visual representation of the pipeline's output data will appear in rendered images and in the interactive viewports of the
graphical OVITO program.

You can remove the pipeline from the scene again using :py:meth:`.remove_from_scene`."""
        ...

    def remove_from_scene(self) -> None:
        """Removes the visual representation of the pipeline from the scene by deleting it from the :py:attr:`ovito.Scene.pipelines` list.
The output data of the pipeline will disappear from the viewports."""
        ...

    def compute(self, frame: Optional[int]=None) -> ovito.data.DataCollection:
        """Computes and returns the results of this data pipeline.

This method requests an evaluation of the pipeline and blocks while the input data is being obtained from the
data :py:attr:`source` and all modifiers are applied to the data. If you invoke the :py:meth:`compute` method repeatedly
without changing the pipeline between calls, the method may serve subsequent requests by immediately returning a cached pipeline output.

The optional *frame* parameter specifies the animation time at which the pipeline should be evaluated. Frame numbering starts at 0.
If you don't specify a frame number, the current time slider position of OVITO is used; or frame 0 when execution doesn't take place in an interactive OVITO session.

The :py:meth:`compute` method raises a ``RuntimeError`` if the pipeline could not be successfully evaluated for some reason.
This may happen due to invalid modifier settings or file I/O errors, for example.

:param int frame: The animation frame number at which the pipeline should be evaluated.
:returns: A :py:class:`DataCollection` produced by the data pipeline.

.. note::
   
   This method creates a static snapshot of the results of the current pipeline.
   The returned :py:class:`DataCollection` will *not* reflect any changes you subsequently make 
   to the pipeline or the modifiers. You have to invoke :py:meth:`compute` again if you want updated results.

.. note::

   The returned :py:class:`DataCollection` behaves like an independent copy of the pipeline's output data.
   If you make changes to the objects in the :py:class:`DataCollection`, the changes will *not*
   be visible to the modifiers within the pipeline nor will they be persistent, i.e., subsequent calls to :py:meth:`compute`
   will *not* produce data collections containing the same changes. 
   
   If your intention is to change the data before it gets passed to the modifiers in the pipeline, insert a 
   :ref:`user-defined modifier function <writing_custom_modifiers>` into the pipeline, which lets you manipulate the 
   :py:class:`DataCollection` before subsequent modifiers in the downstream pipeline see it."""
        ...

    @property
    def modifiers(self) -> MutableSequence[Modifier]:
        """The sequence of modifiers in the pipeline.

This list contains any modifiers that are applied to the input data provided by the pipeline's data :py:attr:`source`. You
can add and remove modifiers as needed using standard Python ``append()`` and ``del`` operations. The
head of the list represents the beginning of the pipeline, i.e. the first modifier receives the data from the
data :py:attr:`source`, manipulates it and passes the results on to the second modifier in the list and so forth.

Example: Adding a new modifier to the end of a data pipeline::

   pipeline.modifiers.append(WrapPeriodicImagesModifier())"""
        ...

    @property
    def source(self) -> Union[FileSource, StaticSource, PythonScriptSource, None]:
        """The object that provides the data entering the pipeline. This typically is a :py:class:`FileSource` instance if the pipeline was created by a call to :py:func:`import_file`. You can assign a new source to the pipeline if needed. See the :py:mod:`ovito.pipeline` module for a list of available pipeline source types. Note that you can even make several pipelines share the same source object."""
        ...