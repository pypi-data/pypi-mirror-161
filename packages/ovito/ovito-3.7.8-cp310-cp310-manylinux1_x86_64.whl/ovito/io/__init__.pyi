"""This module provides two high-level functions for reading and data files:

    * :py:func:`import_file`
    * :py:func:`export_file`"""
__all__ = ['import_file', 'export_file', 'FileReaderInterface']
from typing import Tuple, Optional, Any, Union, Iterator, Mapping, MutableMapping, Sequence, MutableSequence
import ovito.pipeline
import ovito.data
import abc

def import_file(location: Union[str, Sequence[str]], **params) -> ovito.pipeline.Pipeline:
    """Imports data from an external file.

This Python function corresponds to the *Load File* menu command in OVITO's
user interface. The format of the imported file is automatically detected (see list of supported formats).
Depending on the file's format, additional keyword parameters may be required
to specify how the data should be interpreted. These keyword parameters are documented below.

:param location: The file to import. This can be a local file path or a remote *sftp://* or *https://* URL.
:returns: The new :py:class:`Pipeline` that has been created for the imported data.

The function creates and returns a new :py:class:`Pipeline` object, which uses the contents of the
external data file as input. The pipeline will be wired to a :py:class:`FileSource`, which
reads the input data from the external file and passes it on to the pipeline. You can access the
data by calling the `Pipeline.compute()` method or, alternatively,
`FileSource.compute()` on the data :py:attr:`source`.
As long as the new :py:class:`Pipeline` contains no modifiers yet, both methods will return the same data.

Note that the :py:class:`Pipeline` is not automatically inserted into the three-dimensional scene.
That means the loaded data won't appear in rendered images or the interactive viewports of OVITO by default.
For that to happen, you need to explicitly insert the pipeline into the scene by calling its :py:meth:`add_to_scene` method if desired.

Furthermore, note that you can re-use the returned :py:class:`Pipeline` if you want to load a different
data file later on. Instead of calling :py:func:`import_file` again to load another file,
you can use the `pipeline.source.load(...)` method to replace the input file
of the already existing pipeline.

File data columns

When importing simple-format XYZ files or legacy *binary* LAMMPS dump files, the mapping of file columns
to particle properties in OVITO must be specified using the ``columns`` keyword parameter::

    pipeline = import_file('file.xyz', columns =
        ['Particle Identifier', 'Particle Type', 'Position.X', 'Position.Y', 'Position.Z'])

The number of column strings must match the actual number of data columns in the input file.
See this table for standard particle property names. Alternatively, you can specify
user-defined names for file columns that should be read as custom particle properties by OVITO.
For vector properties, the component name must be appended to the property's base name as demonstrated for the ``Position`` property in the example above.
To ignore a file column during import, use ``None`` as entry in the ``columns`` list.

For LAMMPS dump files or extended-format XYZ files, OVITO automatically determines a reasonable column-to-property mapping, but you may override it using the
``columns`` keyword. This can make sense, for example, if the file columns containing the particle coordinates
do not follow the standard naming scheme ``x``, ``y``, and ``z`` (as is the case when importing time-averaged atomic positions computed by LAMMPS, for example).

Frame sequences

OVITO automatically detects if the imported file contains multiple data frames (timesteps).
Alternatively (and additionally), it is possible to load a sequence of files in the same directory by using the ``*`` wildcard character
in the filename. Note that ``*`` may appear only once, only in the filename component of the path, and only in place of numeric digits.
Furthermore, it is possible to pass an explicit list of file paths to the :py:func:`import_file` function, which will be loaded
as an animatable sequence. All variants can be combined. For example, to load two file sets from different directories as one
consecutive sequence::

   import_file('sim.xyz')     # Load all frames contained in the given file
   import_file('sim.*.xyz')   # Load 'sim.0.xyz', 'sim.100.xyz', 'sim.200.xyz', etc.
   import_file(['sim_a.xyz', 'sim_b.xyz'])  # Load an explicit list of snapshot files
   import_file(['dir_a/sim.*.xyz',
                'dir_b/sim.*.xyz']) # Load several file sequences from different directories

The number of frames found in the input file(s) is reported by the :py:attr:`num_frames` attribute of the pipeline's :py:class:`FileSource`
You can step through the frames with a ``for``-loop as follows:

```python
  from ovito.io import import_file
  
  # Import a sequence of files.
  pipeline = import_file('input/simulation.*.dump')
  
  # Loop over all frames of the sequence.
  for frame_index in range(pipeline.source.num_frames):    
  
      # Calling FileSource.compute() loads the requested frame
      # from the sequence into memory and returns the data as a new
      # DataCollection:
      data = pipeline.source.compute(frame_index)
  
      # The source path and the index of the current frame
      # are attached as attributes to the data collection:
      print('Frame source:', data.attributes['SourceFile'])
      print('Frame index:', data.attributes['SourceFrame'])
      
      # Accessing the loaded frame data, e.g the particle positions:
      print(data.particles.positions[...])
```

LAMMPS atom style

When loading a LAMMPS data file, the atom style may have to be specified using the ``atom_style`` keyword parameter unless the file contains
a hint string, which allows OVITO to detect the style automatically. Data files written by the LAMMPS ``write_data`` command or by OVITO contain such a hint, for example.
For data files not containing a hint, the atom style must be specified explicitly as in these examples::

   import_file('full_model.data', atom_style = 'full')
   import_file('hybrid_model.data', atom_style = 'hybrid', atom_substyles = ('template', 'charge'))

Particle ordering

Particles are read and stored by OVITO in the same order as they are listed in the input file.
Some file formats contain unique particle identifiers or tags which allow OVITO to track individual particles
over time even if the storage order changes from frame to frame. OVITO will automatically make use of that
information where appropriate without touching the original storage order. However, in some situations it may be
desirable to explicitly have the particles sorted with respect to the IDs. You can request this
reordering by passing the ``sort_particles=True`` option to :py:func:`import_file`. Note that this option
is without effect if the input file contains no particle identifiers.

Topology and trajectory files

Some simulation codes write a *topology* file and separate *trajectory* file. The former contains only static information like the bonding
between atoms, the atom types, etc., which do not change during a simulation run, while the latter stores the varying data (primarily
the atomic trajectories). To load such a topology-trajectory pair of files, first read the topology file with
the :py:func:`import_file` function, then insert a :py:class:`LoadTrajectoryModifier` into the returned :py:class:`Pipeline`
to also load the trajectory data.

Explicit file format specification

Normally, OVITO detects the format of the imported file(s) automatically. In rare cases, however, the auto-detection mechanism may fail.
Then you can explicitly specify the file format to  assume using the ``input_format`` keyword parameter. It must be set to one of the following 
supported format identifiers: 
``"ca"``, ``"castep/cell"``, ``"castep/md"``, ``"cfg"``, ``"cif"``, ``"dlpoly"``, ``"fhi-aims"``, ``"fhi-aims/log"``, ``"galamost"``, 
``"gaussian/cube"``, ``"gro"``, ``"gsd/hoomd"``, ``"imd"``, ``"lammps/data"``, ``"lammps/dump"``, ``"lammps/dump/bin"``, ``"lammps/dump/local"``, 
``"mmcif"``, ``"netcdf/amber"``, ``"obj"``, ``"oxdna"``, ``"paradis"``, ``"parcas"``, ``"pdb"``, ``"quantumespresso"``, ``"reaxff/bonds"``, 
``"stl"``, ``"vasp"``, ``"vtk/legacy/mesh"``, ``"vtk/pvd"``, ``"vtk/vti/grid"``, ``"vtk/vtm"``, ``"vtk/vtp/mesh"``, ``"vtk/vtp/particles"``, 
``"vtk/vts/grid"``, ``"xsf"``, ``"xtc"``, ``"xyz"``. 

.. seealso::

    - :ref:`manual:file_formats.input.lammps_data`
    - :ref:`manual:file_formats.input.lammps_dump`
    - :ref:`manual:file_formats.input.lammps_dump_local`
    - :ref:`manual:file_formats.input.reaxff`
    - :ref:`manual:file_formats.input.xyz`"""
    ...

def export_file(data: Union[ovito.pipeline.Pipeline, ovito.data.DataObject, None], file: str, format: str, **params) -> None:
    """Writes data to an output file. See section :ref:`file_output_overview` for an overview.

:param data: The object to be exported. See available options below.
:param str file: The output file path.
:param str format: The kind of file to write. See available options below.
:param params: Optional keyword arguments depending on the selected format. 

Data to be exported

The following things are acceptable as first argument:

:py:class:`Pipeline`
    If you provide a data pipeline, the dynamically computed output of the pipeline is exported. Since pipelines support evaluation at different animation times,
    a sequence of frames can be exported by passing the keyword argument ``multiple_frames=True``, see below.

:py:class:`DataCollection`
    If you specify a data collection, the static snapshot stored in the collection is exported. 
    Note that it depends on the selected file format which objects from the data collection will be exported.

:py:class:`DataObject`
    If you specify a single data object, e.g. a :py:class:`DataTable` or :py:class:`SurfaceMesh`,
    just that one object is exported. The behavior is similar to providing a :py:class:`DataCollection` 
    containing a single data object.

`None`
    In this case the output of all data pipelines in the current visualization scene (see :py:attr:`ovito.Scene.pipelines` list) 
    is exported to a single file. This option is only supported for the POV-Ray export format, which stores a full scene 
    description.

Additional keyword parameters, as documented below, let you select the aspects of a dataset to be written to the output file.
For instance, for some file formats the ``columns`` keyword controls the set of particle properties to be saved.

Output filename

The parameter *file* specifies the path of the output file. If the filename ends with the suffix `.gz`,
the output file will be compressed using the zlib library to save disk space (works only for text-based file formats).

If a wildcard "*" character appears in the filename, then one file per animation frame is written and the "*" character is replaced 
with the frame number. This feature is typically used in conjunction with the ``multiple_frames=True`` option, see below.

Output formats

The parameter *format* selects the kind of file to write:

============================= ======================================================================== 
Format string                 Description              
============================= ======================================================================== 
``"txt/attr"``                Export global attributes to a text file (see below)
``"txt/table"``               Export a :py:class:`DataTable` to a text file
``"lammps/dump"``             LAMMPS text-based dump format
``"lammps/data"``             LAMMPS data format
``"imd"``                     IMD format
``"vasp"``                    POSCAR format
``"xyz"``                     XYZ format
``"fhi-aims"``                FHI-aims format
``"gsd/hoomd"``               GSD format used by the HOOMD simulation code
``"netcdf/amber"``            Binary format for MD data following the `AMBER format convention <https://ambermd.org/netcdf/nctraj.pdf>`__
``"vtk/trimesh"``             `ParaView VTK format <https://www.vtk.org/VTK/img/file-formats.pdf>`__ for exporting :py:class:`SurfaceMesh` objects
``"vtk/disloc"``              `ParaView VTK format <https://www.vtk.org/VTK/img/file-formats.pdf>`__ for exporting :py:class:`DislocationNetwork` objects
``"vtk/grid"``                `ParaView VTK format <https://www.vtk.org/VTK/img/file-formats.pdf>`__ for exporting :py:class:`VoxelGrid` objects
``"ca"``                      :ref:`Text-based format for storing dislocation lines <manual:particles.modifiers.dislocation_analysis.fileformat>`
``"povray"``                  `POV-Ray <https://www.povray.org/>`__ scene format
============================= ========================================================================

Depending on the selected output format, additional keyword arguments may be passed to :py:func:`export_file` as documented in the following sections.

File columns

For the output formats *lammps/dump*, *xyz*, *imd*, and *netcdf/amber* you must specify the set of particle properties to export
by providing the ``columns`` keyword parameter::

    export_file(pipeline, "output.xyz", "xyz", columns =
      ["Particle Identifier", "Particle Type", "Position.X", "Position.Y", "Position.Z"])

In case of vector properties, one of the property's :py:attr:`component_names` must be appended 
to the base name, e.g. `Position.Z` or `Atomic Strain.XY`. See the list of standard particle properties.

.. tip::

    If you are not sure which particle properties are available for export, you can print the list of properties 
    produced by your current data pipeline to the console::

       print(pipeline.compute().particles)

Exporting several simulation frames

By default, only the current animation frame (frame 0 by default) is exported.
To export a different trajectory frame, pass the ``frame`` keyword parameter to the :py:func:`export_file` function.
Alternatively, you can export all frames of the animation sequence at once by specifying ``multiple_frames=True``. 
More refined control is possible through the keyword arguments ``start_frame``, ``end_frame``, and ``every_nth_frame``.

Some file formats such as *lammps/dump*, *xyz*, *gsd/hoomd* or *netcdf/amber* can store all frames of the exported trajectory 
in a single output file. For other formats, or if you prefer one file per frame, you must pass a filename pattern 
to :py:func:`export_file`. The specified output filename must contain a ``*`` wildcard character as in the following example, 
which will be replaced with the animation frame number during export::

    export_file(pipeline, "output.*.dump", "lammps/dump", multiple_frames=True)

This is equivalent to an explicit for-loop that exports the frames one by one to a series of files::

    for i in range(pipeline.source.num_frames):
        export_file(pipeline, f"output.{i}.dump", "lammps/dump", frame=i)

Floating-point number precision

For text-based file formats, you can specify the desired formatting precision for floating-point values using the
``precision`` keyword parameter. The default output precision is 10 digits; the maximum is 17.

LAMMPS atom style

When writing files in the *lammps/data* format, the LAMMPS atom style "atomic" is used by default. If you want to output
a data file with a different `LAMMPS atom style <https://docs.lammps.org/atom_style.html>`__, specify it using the ``atom_style`` keyword parameter::

    export_file(pipeline, "output.data", "lammps/data", atom_style="bond")
    export_file(pipeline, "output.data", "lammps/data", atom_style="hybrid", atom_substyles=("template", "charge"))

If at least one :py:class:`ParticleType` of the exported model has a non-zero :py:attr:`mass` value,
OVITO writes a ``Masses`` section to the LAMMPS data file. You can suppress it by passing ``omit_masses=True`` to the export function.
Furthermore, the keyword argument ``ignore_identifiers=True`` replaces any existing atom IDs (particle property `Particle Identifier`) 
with a contiguous sequence of numbers during file export.

**VASP (POSCAR) format**

When exporting to the *vasp* file format, OVITO will output atomic positions and velocities in Cartesian coordinates by default.
You can request output in reduced cell coordinates by specifying the ``reduced`` keyword parameter::

    export_file(pipeline, "structure.poscar", "vasp", reduced=True)

Global attributes

The *txt/attr* file format allows you to write global quantities computed by the data pipeline to a text file.
For example, here is how you export the number of FCC atoms identified by a :py:class:`CommonNeighborAnalysisModifier`
as a function of simulation time to a simple text file::

    export_file(pipeline, "data.txt", "txt/attr",
        columns=["Timestep", "CommonNeighborAnalysis.counts.FCC"],
        multiple_frames=True)

.. tip::

    If you are not sure which global attributes are available for export, you can print the list of :py:attr:`attributes`
    produced by your current data pipeline to the console::

       print(pipeline.compute().attributes)"""
    ...

class FileReaderInterface:
    """A HasTraits subclass which behaves like HasStrictTraits but
also enables the features of Abstract Base Classes (ABC). See the
'abc' module in the standard library for more information."""

    @abc.abstractmethod
    def parse(self, data: ovito.data.DataCollection, **kwargs):
        ...