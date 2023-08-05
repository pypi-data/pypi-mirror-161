"""This module contains all modifiers available in OVITO. See the introduction to learn more
about modifiers and their role in the data pipeline system. The following table lists the Python names of all modifier types that can be instantiated.
Please consult the OVITO user manual for a more in-depth description of what
each of these modifiers does.

============================================== =========================================
Python class name                              User interface name
============================================== =========================================
:py:class:`AcklandJonesModifier`               :guilabel:`Ackland-Jones analysis`
:py:class:`AffineTransformationModifier`       :guilabel:`Affine transformation`
:py:class:`AmbientOcclusionModifier`           :guilabel:`Ambient occlusion`
:py:class:`AssignColorModifier`                :guilabel:`Assign color`
:py:class:`AtomicStrainModifier`               :guilabel:`Atomic strain`
:py:class:`BondAnalysisModifier`               :guilabel:`Bond analysis`
:py:class:`CalculateDisplacementsModifier`     :guilabel:`Displacement vectors`
:py:class:`CentroSymmetryModifier`             :guilabel:`Centrosymmetry parameter`
:py:class:`ChillPlusModifier`                  :guilabel:`Chill+`
:py:class:`ClearSelectionModifier`             :guilabel:`Clear selection`
:py:class:`ClusterAnalysisModifier`            :guilabel:`Cluster analysis`
:py:class:`ColorByTypeModifier`                :guilabel:`Color by type`
:py:class:`ColorCodingModifier`                :guilabel:`Color coding`
:py:class:`CombineDatasetsModifier`            :guilabel:`Combine datasets`
:py:class:`CommonNeighborAnalysisModifier`     :guilabel:`Common neighbor analysis`
:py:class:`ComputePropertyModifier`            :guilabel:`Compute property`
:py:class:`ConstructSurfaceModifier`           :guilabel:`Construct surface mesh`
:py:class:`CoordinationAnalysisModifier`       :guilabel:`Coordination analysis`
:py:class:`CoordinationPolyhedraModifier`      :guilabel:`Coordination polyhedra`
:py:class:`CreateBondsModifier`                :guilabel:`Create bonds`
:py:class:`CreateIsosurfaceModifier`           :guilabel:`Create isosurface`
:py:class:`DeleteSelectedModifier`             :guilabel:`Delete selected`
:py:class:`DislocationAnalysisModifier`        :guilabel:`Dislocation analysis (DXA)`
:py:class:`ElasticStrainModifier`              :guilabel:`Elastic strain calculation`
:py:class:`ExpandSelectionModifier`            :guilabel:`Expand selection`
:py:class:`ExpressionSelectionModifier`        :guilabel:`Expression selection`
:py:class:`FreezePropertyModifier`             :guilabel:`Freeze property`
:py:class:`GenerateTrajectoryLinesModifier`    :guilabel:`Generate trajectory lines`
:py:class:`GrainSegmentationModifier`          :guilabel:`Grain segmentation`
:py:class:`HistogramModifier`                  :guilabel:`Histogram`
:py:class:`IdentifyDiamondModifier`            :guilabel:`Identify diamond structure`
:py:class:`InvertSelectionModifier`            :guilabel:`Invert selection`
:py:class:`LoadTrajectoryModifier`             :guilabel:`Load trajectory`
:py:class:`PolyhedralTemplateMatchingModifier` :guilabel:`Polyhedral template matching`
:py:class:`PythonScriptModifier`               :guilabel:`Python script`
:py:class:`ReplicateModifier`                  :guilabel:`Replicate`
:py:class:`SelectTypeModifier`                 :guilabel:`Select type`
:py:class:`SliceModifier`                      :guilabel:`Slice`
:py:class:`SmoothTrajectoryModifier`           :guilabel:`Smooth trajectory`
:py:class:`SpatialBinningModifier`             :guilabel:`Spatial binning`
:py:class:`SpatialCorrelationFunctionModifier` :guilabel:`Spatial correlation function`
:py:class:`TimeAveragingModifier`              :guilabel:`Time averaging`
:py:class:`TimeSeriesModifier`                 :guilabel:`Time series`
:py:class:`UnwrapTrajectoriesModifier`         :guilabel:`Unwrap trajectories`
:py:class:`VoronoiAnalysisModifier`            :guilabel:`Voronoi analysis`
:py:class:`VoroTopModifier`                    :guilabel:`VoroTop analysis`
:py:class:`WignerSeitzAnalysisModifier`        :guilabel:`Wigner-Seitz defect analysis`
:py:class:`WrapPeriodicImagesModifier`         :guilabel:`Wrap at periodic boundaries`
============================================== =========================================

*Note that some modifiers of the graphical version of OVITO are missing from this list and are not accessible from Python scripts.
That is because they perform simple operations that can be accomplished equally well or even easier using other means in Python.*"""
__all__ = ['PythonScriptModifier', 'TimeAveragingModifier', 'TimeSeriesModifier', 'SliceModifier', 'AffineTransformationModifier', 'ClearSelectionModifier', 'InvertSelectionModifier', 'ColorCodingModifier', 'AssignColorModifier', 'DeleteSelectedModifier', 'SelectTypeModifier', 'HistogramModifier', 'ScatterPlotModifier', 'ReplicateModifier', 'ExpressionSelectionModifier', 'FreezePropertyModifier', 'ManualSelectionModifier', 'ComputePropertyModifier', 'CombineDatasetsModifier', 'ColorByTypeModifier', 'CreateIsosurfaceModifier', 'AmbientOcclusionModifier', 'WrapPeriodicImagesModifier', 'ExpandSelectionModifier', 'StructureIdentificationModifier', 'CommonNeighborAnalysisModifier', 'AcklandJonesModifier', 'CreateBondsModifier', 'CentroSymmetryModifier', 'ClusterAnalysisModifier', 'CoordinationAnalysisModifier', 'CalculateDisplacementsModifier', 'AtomicStrainModifier', 'WignerSeitzAnalysisModifier', 'VoronoiAnalysisModifier', 'IdentifyDiamondModifier', 'LoadTrajectoryModifier', 'PolyhedralTemplateMatchingModifier', 'CoordinationPolyhedraModifier', 'SmoothTrajectoryModifier', 'GenerateTrajectoryLinesModifier', 'UnwrapTrajectoriesModifier', 'ChillPlusModifier', 'ConstructSurfaceModifier', 'CoordinationNumberModifier', 'InterpolateTrajectoryModifier', 'SpatialBinningModifier', 'BondAnalysisModifier', 'SpatialCorrelationFunctionModifier', 'DislocationAnalysisModifier', 'ElasticStrainModifier', 'GrainSegmentationModifier', 'VoroTopModifier']
from typing import NamedTuple, Tuple, Optional, Any, Union, Iterator, AbstractSet, Mapping, MutableMapping, Sequence, MutableSequence, NamedTuple, Callable
import ovito.vis
import ovito.pipeline
import ovito.data
import numpy
import numpy.typing
import enum
import builtins

class StructureIdentificationModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

Abstract base class for all modifiers in OVITO that analyze the local neighborhood of particles to 
identify structural motives or crystalline structures. It contains parameter fields that are
common to all these modifiers:

  * :py:class:`AcklandJonesModifier`
  * :py:class:`ChillPlusModifier`
  * :py:class:`CommonNeighborAnalysisModifier`
  * :py:class:`IdentifyDiamondModifier`
  * :py:class:`PolyhedralTemplateMatchingModifier`
  * :py:class:`VoroTopModifier`"""

    @property
    def color_by_type(self) -> bool:
        """Controls the coloring of particles by the modifier to indicate their identified structure type. See the documentation of the :py:attr:`structures` list on how to change the colors representing the different structure types recognized by the modifier. 

:Default: ``True``"""
        ...

    @property
    def only_selected(self) -> bool:
        """Set this to ``True`` to perform the analysis on selected particles only. Particles that are *not* selected will be treated as if they did not exist and are assigned to the "OTHER" structure category. Use a :py:class:`SelectTypeModifier` in your pipeline, for example, to restrict the structure identification to a sub-lattice formed by one species of particles in a multi-component system. 

:Default: ``False``"""
        ...

    @property
    def structures(self) -> Sequence[ovito.data.ElementType]:
        """A list of :py:class:`ElementType` instances managed by this modifier, one for each recognized structural type. You can modify the type objects in this list to adjust the coloring and to turn the identification of certain structural types on or off. The ordering of the :py:class:`ParticleType` objects in this list corresponds to the numeric type IDs defined by the concrete structure identification modifiers. In the following code snippets, the :py:class:`CommonNeighborAnalysisModifier` serves as an example. 

Your can change the color of a type by setting its :py:attr:`color` property to a new RGB value:: 

   modifier = CommonNeighborAnalysisModifier()
   modifier.structures[CommonNeighborAnalysisModifier.Type.FCC].color = (0.2, 1.0, 0.8)
   modifier.structures[CommonNeighborAnalysisModifier.Type.HCP].color = (0.0, 0.4, 1.0)


To turn the identification of a particular structure type on or off, you set its :py:attr:`enabled` property:: 

   modifier.structures[CommonNeighborAnalysisModifier.Type.BCC].enabled = False
   modifier.structures[CommonNeighborAnalysisModifier.Type.ICO].enabled = True




."""
        ...

class AcklandJonesModifier(StructureIdentificationModifier):
    """Base: :py:class:`ovito.modifiers.StructureIdentificationModifier`

This modifier analyzes the local neighborhood of each particle to identify simple crystalline structures.
The structure identification is performed using the bond-angle classification method proposed by Ackland and Jones.
See the corresponding user manual page
for more information on this modifier.

Note that this class inherits several important parameter fields from its :py:class:`StructureIdentificationModifier`
base class.

Modifier inputs:

.. list-table::
    :widths: auto
    :header-rows: 1

    * - Particle properties
      -
    * - ``Position``
      - The input coordinates of the particles.
    * - ``Selection``
      - The selection state of the input particles. Only needed if :py:attr:`~StructureIdentificationModifier.only_selected` is ``True``.

Modifier outputs:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Particle properties
      -
    * - ``Structure Type``
      - The structure type computed by the algorithm for each particle, encoded as an integer value:

        ============= =========================================================
        Numeric id    Python constant
        ============= =========================================================
        0             ``AcklandJonesModifier.Type.OTHER``
        1             ``AcklandJonesModifier.Type.FCC``
        2             ``AcklandJonesModifier.Type.HCP``
        3             ``AcklandJonesModifier.Type.BCC``
        4             ``AcklandJonesModifier.Type.ICO``
        ============= =========================================================
    * - ``Color``
      - Particle coloring to indicate the identified structure type for each particle; only if :py:attr:`~StructureIdentificationModifier.color_by_type` is ``True``.
        See the :py:attr:`~StructureIdentificationModifier.structures` array on how to customize the colors.

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Global attributes
      -
    * - ``AcklandJones.counts.OTHER``
      - Number of particles not matching any of the recognized structure types.
    * - ``AcklandJones.counts.FCC``
      - Number of particles identified as face-centered cubic.
    * - ``AcklandJones.counts.HCP``
      - Number of particles identified as hexagonal close packed.
    * - ``AcklandJones.counts.BCC``
      - Number of particles identified as body-centered cubic.
    * - ``AcklandJones.counts.ICO``
      - Number of particles identified as icosahedral.

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Data tables
      -
    * - ``structures``
      - A bar chart with the particle counts for each structure type identified by the modifier.
        You can retrieve this :py:class:`DataTable` from the `DataCollection.tables` dictionary."""
    pass

class AffineTransformationModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

This modifier applies an affine transformation to data elements in order to move, rotate, shear or scale them.
See also the corresponding user manual page for more information.

Inputs:

The modifier can operate on any combination of the following data elements:

.. list-table::
    :widths: auto
    :header-rows: 1

    * - Data element specifier
      - Description
    * - ``particles``
      - Transforms the ``Position`` particle property.
    * - ``vector_properties``
      - Transforms the vectorial particle properties ``Velocity``, ``Force``, and ``Displacement``.
    * - ``cell``
      - Transforms the :py:class:`SimulationCell`.
    * - ``surfaces``
      - Transforms the vertices of all :py:class:`SurfaceMesh` and :py:class:`TriangleMesh` objects.
    * - ``dislocations``
      - Transforms all dislocation lines in a :py:class:`DislocationNetwork`.
    * - ``voxels``
      - Transforms the spatial :py:attr:`domain` of all :py:class:`VoxelGrid` objects.

The modifier will act on all of these by default. You can restrict the transform to a subset of data objects by setting the :py:attr:`operate_on` field.

Examples:

The following code applies a simple shear transformation to all particle coordinates. The shear transformation is specified
as a 3x3 matrix with ones on the matrix diagonal and an off-diagonal element that is non-zero.
No translation is applied to the particles. Thus all elements in the fourth column of the extended 3x4 affine transformation 
matrix are set to zero:

    ```python
  xy_shear = 0.05
  mod = AffineTransformationModifier(
          operate_on = {'particles'}, # Transform particles but not the box.
          transformation = [[1, xy_shear, 0, 0],
                            [0,        1, 0, 0],
                            [0,        0, 1, 0]])
```

Note that the modifier itself only supports static transformations, which
remain constant over the entire trajectory. However, is possible to employ the :py:class:`AffineTransformationModifier`
in a :ref:`user-defined modifier function <writing_custom_modifiers>`, which calculates the transformation matrix dynamically
at each animation frame: 

    ```python
  import numpy as np
  
  def rotate(frame, data):
      theta = np.deg2rad(frame * 5.0)  # time-dependent angle of rotation
      tm = [[np.cos(theta), -np.sin(theta), 0, 0],
            [np.sin(theta),  np.cos(theta), 0, 0],
            [            0,              0, 1, 0]]
      # Execute AffineTransformationModifier as a sub-operation:
      data.apply(AffineTransformationModifier(transformation = tm))
  
  pipeline.modifiers.append(rotate)
```"""

    @property
    def only_selected(self) -> bool:
        """Controls whether the modifier should transform only the subset of currently selected elements (e.g. selected particles). For data object types that do not support selections, e.g. the simulation cell, this option has no effect. 

:Default: ``False``"""
        ...

    @property
    def operate_on(self) -> AbstractSet[str]:
        """A set of strings specifying the kinds of data elements this modifier should act on. By default, the set includes all types of data elements supported by the modifier. 

:Default: ``{'particles', 'vector_properties', 'cell', 'surfaces', 'dislocations', 'voxels'}``"""
        ...

    @property
    def reduced_coords(self) -> bool:
        """Controls whether the translation vector (fourth column of the :py:attr:`.transformation` matrix) is specified in reduced cell coordinates or in absolute Cartesian coordinates. 

If set to ``False``, the modifier applies the transformation :math:`\\mathbf{x}' =  \\mathbf{M} \\cdot \\mathbf{x} + \\mathbf{t}` to Cartesian input points :math:`\\mathbf{x}`. Here, :math:`\\mathbf{M}` refers to the 3x3 linear part of the affine :py:attr:`.transformation` matrix and :math:`\\mathbf{t}` to the translational part (fourth matrix column). 

If set to ``True``, the modifier applies the transformation :math:`\\mathbf{x}' =  \\mathbf{M} \\cdot (\\mathbf{x} + \\mathbf{H} \\cdot \\mathbf{t})`. Here, :math:`\\mathbf{H}` refers to the 3x3 cell matrix formed by the three edge vectors of the simulation cell. 

Note that this option only applies if :py:attr:`relative_mode` is active. 

:Default: ``False``"""
        ...

    @property
    def relative_mode(self) -> bool:
        """Selects the operation mode of the modifier.

If set to ``True``, the modifier transforms data elements by applying the specified :py:attr:`transformation` matrix.

If set to ``False``, the modifier determines the effective transformation dynamically based on the current shape of the :py:class:`SimulationCell` and the specified :py:attr:`target_cell` matrix. The old cell will be mapped to the new shape using an appropriate affine transformation. 

:Default: ``True``"""
        ...

    @property
    def target_cell(self) -> numpy.typing.ArrayLike:
        """This 3x4 matrix specifies the target cell shape. It is only used if :py:attr:`relative_mode` == ``False``. 

The first three columns of the matrix specify the three edge vectors of the target cell. The fourth column specifies the origin vector of the target cell. 

The following code shows how to scale the simulation box, whose shape may vary with simulation time, back to the initial shape at frame 0, including the cell's contents. As a result, the output dataset generated by the modifier will have a constant simulation cell size. 

```python
  pipeline = import_file("input/simulation.*.dump")
  modifier = AffineTransformationModifier(
          relative_mode = False,
          target_cell = pipeline.compute(0).cell[...]
  )
  pipeline.modifiers.append(modifier)
```"""
        ...

    @property
    def transformation(self) -> numpy.typing.ArrayLike:
        """The 3x4 transformation matrix to apply to input elements. The first three matrix columns define the linear part of the transformation. The fourth column specifies the translation vector. 

Note that this matrix describes a *relative* transformation and is used only if :py:attr:`relative_mode` == ``True``. See the :py:attr:`.reduced_coords` field for a definition of the precise coordinate transformation that is specified by this matrix. 

:Default: ``[[1,0,0,0], [0,1,0,0], [0,0,1,0]]``"""
        ...

class AmbientOcclusionModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

Performs a quick lighting calculation to modulate the brightness of particles according to the degree of occlusion by other particles.
See the corresponding user manual page for more information.

This modifier should always be inserted at the end of a data pipeline, after particle filtering and coloring is done. 
It can help to improve the visual appearance of complex particle structures which are rendered with the default
:py:class:`OpenGLRenderer`. It is *not* needed when using other renderer, which perform the ambient occlusion 
calculation on the fly during image rendering.

Inputs:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Particle properties
      -
    * - ``Position``
      - The input coordinates of the particles.
    * - ``Color``
      - The original per-particle colors.

Outputs:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Particle properties
      -
    * - ``Color``
      - The new per-particle colors, which have been modulated by the occlusion factor computed by the modifier for each particle."""

    @property
    def buffer_resolution(self) -> int:
        """A positive integer controlling the resolution of the internal render buffer, which is used to compute how much light each particle receives. For large datasets, where the size of particles is small compared to the simulation dimensions, a higher buffer resolution should be used.

:Valid range: [1, 4]
:Default: ``3``"""
        ...

    @property
    def intensity(self) -> float:
        """Controls the strength of the shading effect. 

:Valid range: [0.0, 1.0]
:Default: ``0.7``"""
        ...

    @property
    def sample_count(self) -> int:
        """The number of light exposure samples to compute. More samples give a more even light distribution but take longer to compute.

:Default: ``40``"""
        ...

class AssignColorModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

This modifier assigns a uniform color to all selected data elements.
See also the corresponding user manual page for more information.
The modifier can operate on different data elements:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Data element
      -
    * - ``particles``
      - Sets the ``Color`` property of selected particles.
    * - ``vectors``
      - Sets the ``Vector Color`` property of selected particles.
    * - ``bonds``
      - Sets the ``Color`` property of selected bonds.
    * - ``surface_vertices``
      - Sets the ``Color`` property of selected vertices of a :py:class:`SurfaceMesh` structure.
    * - ``surface_faces``
      - Sets the ``Color`` property of selected faces of a :py:class:`SurfaceMesh` structure.
    * - ``surface_regions``
      - Sets the ``Color`` property of selected spatial regions of a :py:class:`SurfaceMesh` structure.

By default the modifier will act on particles. You can change this by setting the :py:attr:`operate_on` field.
The modifier uses the input :py:class:`Property` named ``Selection`` to determine which subset of data elements should
be assigned the specified :py:attr:`color`. Data elements whose ``Selection`` property is zero, keep their current color. 
In case the ``Selection`` property does not exist at all, the modifier assigns the color to every data element.

OVITO provides various modifiers for creating selections: :py:class:`SelectTypeModifier`, :py:class:`ExpressionSelectionModifier`,
:py:class:`SliceModifier`, :py:class:`InvertSelectionModifier`.

Examples

Select some particles with the :py:class:`SelectTypeModifier` and give them a new color:

    ```python
  pipeline.modifiers.append(SelectTypeModifier(types={1,3}))
  pipeline.modifiers.append(AssignColorModifier(color=(1.0, 0.3, 0.3)))
```

Use the :py:class:`CalculateDisplacementsModifier` to calculate the atomic displacement vectors and visualize them
as arrows in rendered images. Particularly large displacement arrows can be highlighted using the :py:class:`AssignColorModifier`:

    ```python
  # Calculate and visualize atomic displacement vectors:
  modifier = CalculateDisplacementsModifier()
  modifier.vis.enabled = True
  pipeline.modifiers.append(modifier)
  
  # Select particles with large displacement magnitudes:
  pipeline.modifiers.append(ExpressionSelectionModifier(expression='DisplacementMagnitude > 1.2'))
  # Highlight large displacement vectors using a special color: 
  pipeline.modifiers.append(AssignColorModifier(operate_on='vectors', color=(0.0, 0.9, 1.0)))
```"""

    @property
    def color(self) -> ovito.vis.Color:
        """The RGB color that will be assigned to all selected elements by the modifier.

:Default: ``(0.3, 0.3, 1.0)``"""
        ...

    @property
    def operate_on(self) -> str:
        """Selects the kind of data elements this modifier should operate on. Supported values are: ``'particles'``, ``'bonds'``, ``'vectors'``, ``'surface_vertices'``, ``'surface_faces'``, ``'surface_regions'``. 

:Default: ``'particles'``"""
        ...

class AtomicStrainModifier(ovito.pipeline.ReferenceConfigurationModifier):
    """Base: :py:class:`ovito.pipeline.ReferenceConfigurationModifier`

Computes the atomic-level deformation with respect to a reference configuration.
See the corresponding user manual page
for more information.

The modifier is a subclass of :py:class:`ReferenceConfigurationModifier`, which provides
the programming interface for specifying the reference configuration and how particle displacements get calculated.
By default, frame 0 of the processed simulation sequence is used as static reference configuration.

Outputs:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Particle properties
      -
    * - ``Shear Strain``
      - The von Mises shear strain invariant of the computed atomic Green-Lagrangian strain tensor.
    * - ``Volumetric Strain``
      - One third of the trace of the computed atomic Green-Lagrangian strain tensor.
    * - ``Strain Tensor``
      - The six components of the symmetric Green-Lagrangian strain tensor. Only if :py:attr:`output_strain_tensors` was set to ``True``.
    * - ``Deformation Gradient``
      - The nine components of the atomic deformation gradient tensor. Only if :py:attr:`output_deformation_gradients` was set to ``True``.
    * - ``Stretch Tensor``
      - The six components of the symmetric right stretch tensor U in the polar decomposition F=RU. Only if :py:attr:`output_stretch_tensors` was set to ``True``.
    * - ``Rotation``
      - The atomic microrotation obtained from the polar decomposition F=RU as a 4-component quaternion. Only if :py:attr:`output_rotations` was set to ``True``.
    * - ``Nonaffine Squared Displacement``
      - The D\\ :sup:`2`\\ :sub:`min` measure of Falk & Langer, which describes the non-affine part of the local deformation. Only if :py:attr:`output_nonaffine_squared_displacements` was set to ``True``.
    * - ``Selection``
      -  Set to a non-zero value for particles for which the modifier failed to determine a local deformation tensor, because they do not have enough neighbors
         within the specified :py:attr:`cutoff` distance. Only if :py:attr:`select_invalid_particles` was set to ``True``.
         The selected particles without valid deformation values can subsequently be removed using a :py:class:`DeleteSelectedModifier`.

.. list-table::
    :widths: auto
    :header-rows: 1

    * - Global attributes
      -
    * - ``AtomicStrain.invalid_particle_count``
      - Number of particles for which the modifier could not compute a deformation tensor, because they do not have enough neighbors
        within the specified :py:attr:`cutoff` distance. You typically should increase the cutoff distance if this value is non-zero."""

    @property
    def cutoff(self) -> float:
        """The spatial range up to which neighboring atoms will be taken into account to calculate the local strain measure.

:Default: ``3.0``"""
        ...

    @property
    def output_deformation_gradients(self) -> bool:
        """Controls the output of the per-particle deformation gradient tensors. If ``False``, the computed tensors are not output as a particle property to save memory.

:Default: ``False``"""
        ...

    @property
    def output_nonaffine_squared_displacements(self) -> bool:
        """Enables the computation of the squared magnitude of the non-affine part of the atomic displacements. The computed values are output in the ``"Nonaffine Squared Displacement"`` particle property.

:Default: ``False``"""
        ...

    @property
    def output_rotations(self) -> bool:
        """Controls the calculation of the per-particle rotations.

:Default: ``False``"""
        ...

    @property
    def output_strain_tensors(self) -> bool:
        """Controls the output of the per-particle strain tensors. If ``False``, the computed strain tensors are not output as a particle property to save memory.

:Default: ``False``"""
        ...

    @property
    def output_stretch_tensors(self) -> bool:
        """Controls the calculation of the per-particle stretch tensors.

:Default: ``False``"""
        ...

    @property
    def select_invalid_particles(self) -> bool:
        """If ``True``, the modifier selects the particle for which the local strain tensor could not be computed (because of an insufficient number of neighbors within the cutoff).

:Default: ``True``"""
        ...

class BondAnalysisModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

Computes the bond angle distribution and the bond length distribution for the particle system with bonds.
See the corresponding user manual page for more information on this modifier.

The input for this modifier must contain a :py:class:`Bonds` data object with the bond topology information,
which may either be loaded from the simulation file or by first inserting the :py:class:`CreateBondsModifier`
into the pipeline.

The modifier outputs the computed bond length and bond angle histograms as two :py:class:`DataTable` objects,
which may be exported to an output text file using the :py:func:`export_file` function or retrieved 
from the pipeline's output data collection, see the `DataCollection.tables` dictionary
and the code examples following below. 

Inputs:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Particle properties
      -
    * - ``Position``
      - The coordinates of the input particles.
    * - ``Particle Type``
      - Required if :py:attr:`partition` is set to ``ByParticleType``.
    * - ``Selection``
      - Required if :py:attr:`partition` is set to ``ByParticleSelection``.

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Bond properties
      -
    * - ``Topology``
      - The input bonds list.
    * - ``Bond Type``
      - Required if :py:attr:`partition` is set to ``ByBondType``.
    * - ``Selection``
      - Required if :py:attr:`partition` is set to ``ByBondSelection``.

Outputs:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - :py:class:`DataTable`
      -
    * - ``bond-angle-distr``
      - The bond angle distribution histogram computed by the modifier. 
    * - ``bond-length-distr``
      - The bond length distribution histogram computed by the modifier. 

Examples:

The following Python script demonstrates how to load a particle system (without bond topology) from a file, 
create the bond topology using OVITO's :py:class:`CreateBondsModifier`, and then compute
the bond angle distribution. Finally, the histogram is written to an output text file using the :py:func:`export_file` function.

```python
  from ovito.io import import_file, export_file
  from ovito.modifiers import BondAnalysisModifier, CreateBondsModifier
  
  # Set up data pipeline:
  pipeline = import_file('input/simulation.dump')
  pipeline.modifiers.append(CreateBondsModifier(cutoff = 3.2))
  pipeline.modifiers.append(BondAnalysisModifier(bins = 100))
  
  # Export bond angle distribution to an output text file.
  export_file(pipeline, 'output/bond_angles.txt', 'txt/table', key='bond-angle-distr')
  
  # Convert bond length histogram to a NumPy array and print it to the terminal.
  data = pipeline.compute()
  print(data.tables['bond-length-distr'].xy())
```

The script above computes the instantaneous distribution for the initial frame in the simulation file only.
To compute an average bond angle distribution for the entire MD trajectory, you can make use of the 
:py:class:`TimeAveragingModifier`:

.. literalinclude:: ../example_snippets/bond_analysis_modifier_averaging.py"""

    class Partition(enum.Enum):
        """AUTODOC_SKIP_MEMBER

Members:

  Off

  ByBondType

  ByBondSelection

  ByParticleType

  ByParticleSelection"""
        Off = enum.auto()
        ByBondType = enum.auto()
        ByBondSelection = enum.auto()
        ByParticleType = enum.auto()
        ByParticleSelection = enum.auto()

    @property
    def bins(self) -> int:
        """The number of bins in the length and angle histograms generated by the modifier. 

:Default: ``180``"""
        ...

    @property
    def cosine_mode(self) -> bool:
        """If set to ``True``, the modifier will calculate the distribution of the cosines of the bond angles instead of the angles themselves, and the bond angle histogram output by the modifier will then extend over the value interval [-1, +1] instead of [0, 180] degrees. 

:Default: ``False``"""
        ...

    @property
    def length_cutoff(self) -> float:
        """Maximum bond length at which the bond length distribution gets truncated. Together with the :py:attr:`bins` parameter, this value determines the bin size of the bond length histogram output by the modifier. 

Note that this parameter does not affect the computation of the bond angle distribution. All bonds are included in the angle distribution, even if their length exceeds the cutoff. 

:Default: ``4.0``"""
        ...

    @property
    def partition(self) -> Partition:
        """This mode parameter instructs the modifier to split the bond length and bond angle distributions into partial distributions, one for each particle or bond type combination. Available partitioning modes are: 

   * ``BondAnalysisModifier.Partition.Off``
   * ``BondAnalysisModifier.Partition.ByBondType``
   * ``BondAnalysisModifier.Partition.ByBondSelection``
   * ``BondAnalysisModifier.Partition.ByParticleType``
   * ``BondAnalysisModifier.Partition.ByParticleSelection``


If partitioning is turned on, the :py:attr:`y` property array of the two :py:class:`DataTable` histograms computed by the modifier will have multiple vector components, one for each partial distribution. The follow code example shows how to access the partial histograms: 

```python
  from ovito.io import import_file
  from ovito.modifiers import BondAnalysisModifier
  
  # Load LAMMPS data file with bonds and compute bond angle distribution partitioned by bond type:
  pipeline = import_file('input/input.data', atom_style='bond')
  pipeline.modifiers.append(BondAnalysisModifier(partition=BondAnalysisModifier.Partition.ByBondType))
  data = pipeline.compute()
  
  # Retrieve y-property array from output DataTable:
  histogram = data.tables['bond-angle-distr'].y
  
  # Print the individual columns of the vector-valued property array:
  for column, name in enumerate(histogram.component_names):
      print("Angle distribution for bond types:", name)
      print(histogram[:,column])
```

:Default: ``BondAnalysisModifier.Partition.Off``"""
        ...

class CalculateDisplacementsModifier(ovito.pipeline.ReferenceConfigurationModifier):
    """Base: :py:class:`ovito.pipeline.ReferenceConfigurationModifier`

Computes the displacement vectors of particles with respect to a reference configuration.
See the corresponding user manual page
for more information.

The modifier is a subclass of :py:class:`ReferenceConfigurationModifier`, which provides
the programming interface for specifying the reference configuration and how particle displacements get calculated.
By default, frame 0 of the processed simulation sequence is used as static reference configuration.

Outputs:

.. list-table::
    :widths: 35 65
    :header-rows: 1

    * - Particle properties
      -
    * - ``Displacement``
      - The computed displacement vectors.
    * - ``Displacement Magnitude``
      - The length of the computed displacement vectors."""

    @property
    def vis(self) -> ovito.vis.VectorVis:
        """A :py:class:`VectorVis` element controlling the visual representation of the computed displacement vectors. Note that the computed displacement vectors are hidden by default. You can enable the visualization of arrows as follows: 

```python
  modifier = CalculateDisplacementsModifier()
  modifier.vis.enabled = True
  modifier.vis.color = (0.8, 0.0, 0.5)
```"""
        ...

class CentroSymmetryModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

Computes the centrosymmetry parameter (CSP) of each particle, which is a measure of the local lattice disorder
around a particle in centrosymmetric crystal lattices.
See the corresponding user manual page
for more information.

Inputs:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Particle properties
      -
    * - ``Position``
      - The input coordinates of the particles.

Outputs:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Particle properties
      -
    * - ``Centrosymmetry``
      - The non-negative CSP value computed for each particle. Values close to zero mean neighboring
        particles are in a perfect centrosymmetric arrangement."""

    class Mode(enum.Enum):
        """AUTODOC_SKIP_MEMBER

Members:

  Conventional

  Matching"""
        Conventional = enum.auto()
        Matching = enum.auto()

    @property
    def mode(self) -> Mode:
        """Selects how pair-wise opposite neighbors should be picked during the CSP calculation. Valid modes are:

  * ``CentroSymmetryModifier.Mode.Conventional``
  * ``CentroSymmetryModifier.Mode.Matching``


See the user manual for more information on these two modes. 

:Default: ``CentroSymmetryModifier.Mode.Conventional``"""
        ...

    @property
    def num_neighbors(self) -> int:
        """The number of nearest neighbors to take into account for the computation, e.g. 

  * 12 for FCC crystals
  * 8 for BCC crystals


:Default: ``12``"""
        ...

    @property
    def only_selected(self) -> bool:
        """Set this to ``True`` to perform the analysis only on the sub-set of currently selected particles. Particles that are *not* selected will be treated as if they did not exist. That means they won't be considered in the centrosymmetry calculation of the surrounding particles and their own centrosymmetry value will be zero. Use a :py:class:`SelectTypeModifier` in your pipeline, for example, to restrict the centrosymmetry analysis to a sub-lattice formed by one species of particles in a multi-component system. 

:Default: ``False``"""
        ...

class ChillPlusModifier(StructureIdentificationModifier):
    """Base: :py:class:`ovito.modifiers.StructureIdentificationModifier`

Analyzes the local neighborhood of each particle to identify different structural arrangements of water molecules.
The structure identification is performed using the CHILL+ algorithm.
See the corresponding user manual page
for more information.

Note that this class inherits several important parameter fields from its :py:class:`StructureIdentificationModifier`
base class.

Modifier inputs:

.. list-table::
    :widths: auto
    :header-rows: 1

    * - Particle properties
      -
    * - ``Position``
      - The input coordinates of the particles.
    * - ``Selection``
      - The selection state of the input particles. Only needed if :py:attr:`~StructureIdentificationModifier.only_selected` is ``True``.

Modifier outputs:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Particle properties
      -
    * - ``Structure Type``
      - The structure type computed by the algorithm for each particle, encoded as an integer value:

        ============= =========================================================
        Numeric id    Python constant
        ============= =========================================================
        0             ``ChillPlusModifier.Type.OTHER``
        1             ``ChillPlusModifier.Type.HEXAGONAL_ICE``
        2             ``ChillPlusModifier.Type.CUBIC_ICE``
        3             ``ChillPlusModifier.Type.INTERFACIAL_ICE``
        4             ``ChillPlusModifier.Type.HYDRATE``
        5             ``ChillPlusModifier.Type.INTERFACIAL_HYDRATE``
        ============= =========================================================
    * - ``Color``
      - Particle coloring to indicate the identified structure type for each particle; only if :py:attr:`~StructureIdentificationModifier.color_by_type` is ``True``.
        See the :py:attr:`~StructureIdentificationModifier.structures` array on how to customize the colors.

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Global attributes
      -
    * - ``ChillPlus.counts.OTHER``
      - Number of particles not matching any of the known structure types.
    * - ``ChillPlus.counts.HEXAGONAL_ICE``
      - Number of particles identified as hexagonal ice.
    * - ``ChillPlus.counts.CUBIC_ICE``
      - Number of particles identified as cubic ice.
    * - ``ChillPlus.counts.INTERFACIAL_ICE``
      - Number of particles identified as interfacial ice.
    * - ``ChillPlus.counts.HYDRATE``
      - Number of particles identified as hydrate.
    * - ``ChillPlus.counts.INTERFACIAL_HYDRATE``
      - Number of particles identified as interfacial hydrate.

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Data tables
      -
    * - ``structures``
      - A bar chart with the particle counts for each structure type identified by the modifier.
        You can retrieve this :py:class:`DataTable` from the `DataCollection.tables` dictionary."""

    @property
    def cutoff(self) -> float:
        """The cutoff distance for bonds between water molecules. 

:Default: ``3.5``"""
        ...

class ClearSelectionModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

This modifier clears the current selection by removing the ``Selection`` property from a :py:class:`PropertyContainer`
such that subsequent modifiers in the pipeline won't see it.
See also the corresponding user manual page for more information.
The modifier can operate on different kinds of data elements:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Data element
      -
    * - ``particles``
      - Removes the ``Selection`` property of particles.
    * - ``bonds``
      - Removes the ``Selection`` property of bonds.
    * - ``voxels``
      - Removes the ``Selection`` property of voxel grid cells.

By default the modifier will act on particles. You can change this by setting the :py:attr:`operate_on` field."""

    @property
    def operate_on(self) -> str:
        """Selects the kind of data elements this modifier should operate on. Supported values are: ``'particles'``, ``'bonds'``, ``'voxels'``. 

:Default: ``'particles'``"""
        ...

class ClusterAnalysisModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

This modifier groups particles into disconnected clusters based on a selectable connectivity criterion.
See the corresponding user manual page
for more information.

Outputs:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Particle properties
      -
    * - ``Cluster``
      - The 1-based numeric ID of the cluster each particle was assigned to by the modifier.

.. list-table::
    :widths: auto
    :header-rows: 1

    * - Global attributes
      -
    * - ``ClusterAnalysis.cluster_count``
      - Total number of clusters produced by the modifier. Cluster IDs range from 1 to this number.
    * - ``ClusterAnalysis.largest_size``
      - Number of particles in the largest cluster (cluster ID 1). Only computed if :py:attr:`sort_by_size` is set to ``True``.

.. list-table::
    :widths: 15 85
    :header-rows: 1

    * - :py:class:`DataTable`
      -
    * - ``clusters``
      - The list of clusters identified by the modifier. 
        You can retrieve this :py:class:`DataTable` from the `DataCollection.tables` dictionary.
        It consists of several data columns, each being a separate :py:class:`Property` object:

          * ``Cluster Identifier``: The numeric ID of each identified cluster (1-based).
          * ``Cluster Size``: The number of particles in each identified cluster.
          * ``Center of Mass``: The XYZ coordinates of the center of mass of each cluster (only if :py:attr:`compute_com` is set).
          * ``Radius of Gyration``: The radius of gyration of each cluster (only if :py:attr:`compute_gyration` is set) in simulation units of length.
          * ``Gyration Tensor``: The gyration tensor of each cluster (only if :py:attr:`compute_gyration` is set) in simulation units of length squared.
            The tensors are stored as vectors with six components [XX, YY, ZZ, XY, XZ, YZ].

Example:

The following example code demonstrates how to export the data table generated by the modifier to a text file and how to access the
information from Python.

.. literalinclude:: ../example_snippets/cluster_analysis_modifier.py"""

    class NeighborMode(enum.Enum):
        """AUTODOC_SKIP_MEMBER

Members:

  CutoffRange

  Bonding"""
        CutoffRange = enum.auto()
        Bonding = enum.auto()

    @property
    def cluster_coloring(self) -> bool:
        """Enables the coloring of particles based on their assignment to clusters. Each cluster is represented by a unique random color. 

:Default: ``False``"""
        ...

    @property
    def compute_com(self) -> bool:
        """Enables the computation of the center of mass of each cluster. The center coordinates will be output as an extra column named ``Center of Mass`` in the ``clusters`` data table. 

:Default: ``False``"""
        ...

    @property
    def compute_gyration(self) -> bool:
        """Enables the computation of the radius of gyration and the gyration tensor of each cluster. Both quantities will be output as auxiliary properties to the ``clusters`` data table, see above. 

:Default: ``False``"""
        ...

    @property
    def cutoff(self) -> float:
        """The cutoff distance used by the algorithm to form clusters of connected particles. This parameter is only used when :py:attr:`neighbor_mode` is set to ``CutoffRange``; otherwise it is ignored. 

:Default: ``3.2``"""
        ...

    @property
    def neighbor_mode(self) -> NeighborMode:
        """Selects the neighboring criterion for the clustering algorithm. Valid values are: 

  * ``ClusterAnalysisModifier.NeighborMode.CutoffRange``
  * ``ClusterAnalysisModifier.NeighborMode.Bonding``


In the first mode (``CutoffRange``), the clustering algorithm treats pairs of particles as neighbors which are within a certain range of each other given by the parameter :py:attr:`cutoff`. 

In the second mode (``Bonding``), particles which are connected by bonds are combined into clusters. Bonds between particles can either be loaded from the input simulation file or dynamically created using for example the :py:class:`CreateBondsModifier` or the :py:class:`VoronoiAnalysisModifier`. 

:Default: ``ClusterAnalysisModifier.NeighborMode.CutoffRange``"""
        ...

    @property
    def only_selected(self) -> bool:
        """Lets the modifier perform the analysis only for selected particles. In this case, particles which are not selected are treated as if they did not exist and will be assigned cluster ID 0. 

:Default: ``False``"""
        ...

    @property
    def sort_by_size(self) -> bool:
        """Enables the sorting of clusters by size (in descending order). Cluster 1 will be the largest cluster, cluster 2 the second largest, and so on.

:Default: ``False``"""
        ...

    @property
    def unwrap_particles(self) -> bool:
        """Enables the "unwrapping" of particle coordinates in order to make clusters contiguous that are cut by a periodic simulation cell boundary. 

:Default: ``False``"""
        ...

class ColorByTypeModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

Assigns colors to data elements to visualize the discrete per-element values of a typed property, e.g. the residue type or structural type of particles.
See also the corresponding user manual page for more information.
The modifier can operate on different data elements:

.. list-table::
    :widths: 20 80
    :header-rows: 1

    * - Data elements
      -
    * - ``particles``
      - Colors :py:class:`Particles` according to a typed particle property.
    * - ``bonds``
      - Colors :py:class:`Bonds` according to a typed bond property.
    * - ``voxels``
      - Colors :py:class:`VoxelGrid` cells according to a typed property.

By default the modifier will act on particles. You can change this by setting the :py:attr:`operate_on` field.

The modifier's :py:attr:`property` field names the input property according to which the data elements will be colored.
It must be a so-called *typed property*, which means the :py:class:`Property` object has a list of :py:class:`ElementType`
instances attached in its :py:attr:`types` field, defining the mapping of integer values in the property array to element type colors.
Each :py:class:`ElementType` instance associates one numeric :py:attr:`id` with
a corresponding :py:attr:`color`.

Output:

The modifier sets the ``Color`` property of the data elements it operates on. When rendering a picture,
this property determines the visual color of the individual objects.

Examples:

```python
  from ovito.io import import_file
  from ovito.modifiers import ColorByTypeModifier
  
  # Load a GROMACS file, which contains the 'Residue Type' particle property.
  pipeline = import_file("input/1AKI.gro")
  pipeline.add_to_scene()
  
  # Print a table of all residue types defined in the dataset:
  for residue_type in pipeline.compute().particles['Residue Type'].types:
      print(residue_type.id, residue_type.name, residue_type.color)
  
  # Apply the ColorByTypeModifier, giving particles a color based on 
  # the value of their 'Residue Type' property:
  pipeline.modifiers.append(ColorByTypeModifier(
      operate_on='particles', 
      property='Residue Type'))
```

One way to change the colors of the element types is to prepend the :py:class:`ColorByTypeModifier` in the pipeline with a :ref:`user-defined modifier function <writing_custom_modifiers>`
configuring the :py:class:`ElementType` instances that are attached to the typed :py:class:`Property`:

```python
  def setup_residue_colors(frame, data):
      residues = data.particles_['Residue Type_']
      residues.type_by_name_('LYS').color = (1.0, 0.0, 1.0)
      residues.type_by_name_('GLU').color = (0.0, 0.5, 1.0)
  pipeline.modifiers.insert(0, setup_residue_colors)
```

Implementation:

The :py:class:`ColorByTypeModifier` is functionally equivalent to (but more efficient than) the following :ref:`user-defined modifier function <writing_custom_modifiers>`:

```python
  def color_by_type(frame, data, property_name='Residue Type'):
      input_property = data.particles[property_name]
      output_colors = data.particles_.create_property('Color')
      for index, type_id in enumerate(input_property):
          element_type = input_property.type_by_id(type_id)
          output_colors[index] = element_type.color
```"""

    @property
    def clear_selection(self) -> bool:
        """Controls whether the current element selection is cleared to reveal the assigned colors in the interactive viewports of OVITO, which may otherwise be masked by the highlighting of selected elements. This option only has an effect if the :py:attr:`.only_selected` option is also turned on. Otherwise the modifier never clears the current element selection. 

:Default: ``True``"""
        ...

    @property
    def only_selected(self) -> bool:
        """If ``True``, only selected data elements will be assigned a color by the modifier and the colors of unselected elements will be preserved; if ``False``, all data elements will be colored.

:Default: ``False``"""
        ...

    @property
    def operate_on(self) -> str:
        """Controls the kind of data elements that are being colored by this modifier. Supported values are: ``'particles'``, ``'bonds'``, ``'voxels'``. 

:Default: ``'particles'``"""
        ...

    @property
    def property(self) -> str:
        """The name of the typed property to use as input; must be an integer property with attached :py:class:`ElementType` instances. 

For particles, typical input properties are ``'Particle Type'``, ``'Residue Type'`` or ``'Structure Type'``. When coloring bonds, the ``'Bond Type'`` property is an example for a typed property. 

:Default: ``'Particle Type'``"""
        ...

class ColorCodingModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

Colors elements to visualize one of their properties.
See also the corresponding user manual page for more information.
The modifier can operate on different data elements:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Data element
      -
    * - ``particles``
      - Assigns a local color to particles by setting their ``Color`` property.
    * - ``vectors``
      - Colors the vector arrows associated with particles by setting their ``Vector Color`` property.
    * - ``bonds``
      - Assigns a local color to bonds by setting their ``Color`` property.
    * - ``voxels``
      - Colors the cells of a :py:class:`VoxelGrid`.
    * - ``surface_vertices``
      - Colors the vertices of a :py:class:`SurfaceMesh` object.
    * - ``surface_faces``
      - Colors the faces of a :py:class:`SurfaceMesh` object.
    * - ``surface_regions``
      - Colors the volumetric regions of a :py:class:`SurfaceMesh` object.
    * - ``trajectories``
      - Assigns a local color to the sampling points of a :py:class:`TrajectoryLines` object.

By default the modifier will act on particles. You can change this by setting the :py:attr:`operate_on` field.

Example:

```python
  pipeline.modifiers.append(ColorCodingModifier(
      property = 'Potential Energy',
      gradient = ColorCodingModifier.Hot()
  ))
```

If, as in the example above, the :py:attr:`start_value` and :py:attr:`end_value` parameters are not explicitly specified,
then modifier will automatically adjust the mapping interval to fully cover the range of input property values 
(dynamically for each trajectory frame).

The :py:class:`ColorLegendOverlay` may be used in conjunction with a :py:class:`ColorCodingModifier`
to include a color legend in rendered images."""

    class Gradient:

        def __init__(self, color_array: numpy.typing.ArrayLike) -> None:
            """Initialize self.  See help(type(self)) for accurate signature."""
            ...

    class BlueWhiteRed(Gradient):

        def __init__() -> None:
            ...

    class Grayscale(Gradient):

        def __init__() -> None:
            ...

    class Hot(Gradient):

        def __init__() -> None:
            ...

    class Jet(Gradient):

        def __init__() -> None:
            ...

    class Magma(Gradient):

        def __init__() -> None:
            ...

    class Rainbow(Gradient):

        def __init__() -> None:
            ...

    class Viridis(Gradient):

        def __init__() -> None:
            ...

    class Image(Gradient):

        def __init__(self, imagefile: str) -> None:
            """Initialize self.  See help(type(self)) for accurate signature."""
            ...

    @builtins.property
    def auto_adjust_range(self) -> bool:
        """Controls the automatic adjustment of the modifier's mapping interval to always cover the full range of input values. If turned on (the default), the modifier adaptively adjusts the value-to-color mapping to the current min/max range of input values (at the current timestep). If turned off, the mapping is fixed and is determined by the :py:attr:`start_value` and :py:attr:`end_value` parameters of the modifier. 

Setting the :py:attr:`start_value` or :py:attr:`end_value` parameters to some value implicitly changes :py:attr:`auto_adjust_range` to ``False``. Furthermore, note that the automatic range is always determined over the complete set of input elements irrespective of the :py:attr:`only_selected` option. 

:Default: ``True``"""
        ...

    @builtins.property
    def end_value(self) -> float:
        """This parameter determines, together with :py:attr:`start_value`, the linear mapping of input property values to colors. It is only used if :py:attr:`auto_adjust_range` is turned off, which happens automatically as soon as you assign some value to this modifier parameter. 

:Default: ``0.0``"""
        ...

    @builtins.property
    def gradient(self) -> Gradient:
        """The color gradient used to map normalized property values to colors. Available gradient types are:

 * ``ColorCodingModifier.BlueWhiteRed()``
 * ``ColorCodingModifier.Grayscale()``
 * ``ColorCodingModifier.Hot()``
 * ``ColorCodingModifier.Jet()``
 * ``ColorCodingModifier.Magma()``
 * ``ColorCodingModifier.Rainbow()`` (default)
 * ``ColorCodingModifier.Viridis()``
 * ``ColorCodingModifier.Gradient(Nx3 array)``
 * ``ColorCodingModifier.Image("<image file path>")``

The ``Gradient`` constructor lets you define your own coloring scheme and takes an array of dimensions *N* x 3 containing a table of colors (RGB values in the range [0-1]). The color coding modifier will linearly interpolate between the *N* colors of the table. 
The ``Image`` constructor expects the path to an image file on disk, which will be used to create a custom color gradient from the first row of pixels in the image.

Code example:

```python
  color_table = [
      (1.0, 0.0, 0.0),  # red
      (1.0, 1.0, 0.0),  # yellow
      (1.0, 1.0, 1.0)   # white
  ]
  modifier = ColorCodingModifier(
      property = 'Position.X',
      gradient = ColorCodingModifier.Gradient(color_table)
  )
```"""
        ...

    @builtins.property
    def only_selected(self) -> bool:
        """If ``True``, only selected elements will be affected by the modifier and the existing colors of unselected elements will be preserved; if ``False``, all elements will be colored.

:Default: ``False``"""
        ...

    @builtins.property
    def operate_on(self) -> str:
        """Selects the kind of data elements this modifier should operate on. Supported values are: ``'particles'``, ``'bonds'``, ``'vectors'``, ``'voxels'``, ``'surface_vertices'``, ``'surface_faces'``, ``'surface_regions'``, ``'trajectories'``. 

:Default: ``'particles'``"""
        ...

    @builtins.property
    def property(self) -> str:
        """The name of the input property that should be used to color elements. 

When the input property has multiple components, then a component name must be appended to the property base name, e.g. ``"Velocity.X"``."""
        ...

    @builtins.property
    def start_value(self) -> float:
        """This parameter determines, together with :py:attr:`end_value`, the linear mapping of input property values to colors. It is only used if :py:attr:`auto_adjust_range` is turned off, which happens automatically as soon as you assign some value to this modifier parameter. 

:Default: ``0.0``"""
        ...

class CombineDatasetsModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

This modifier loads a set of particles from a separate simulation file and merges them into the primary dataset.
See also the corresponding user manual page for more information.

Example:

.. literalinclude:: ../example_snippets/combine_datasets_modifier.py"""

    @property
    def source(self) -> ovito.pipeline.FileSource:
        """A :py:class:`FileSource` that provides the set of particles to be merged. You can call its :py:meth:`load` function to load a data file as shown in the code example above."""
        ...

class CommonNeighborAnalysisModifier(StructureIdentificationModifier):
    """Base: :py:class:`ovito.modifiers.StructureIdentificationModifier`

This modifier analyzes the local neighborhood of each particle to identify simple crystalline structures.
The structure identification is performed using the Common Neighbor Analysis (CNA) method.
See the corresponding user manual page
for more information on this modifier and the structure identification algorithm it implements.

Note that this class inherits several important parameter fields from its :py:class:`StructureIdentificationModifier`
base class.

Modifier inputs:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Particle properties
      -
    * - ``Position``
      - The input coordinates of the particles. They are not used if :py:attr:`mode` is set to ``BondBased``.
    * - ``Selection``
      - The selection state of the input particles. Only needed if :py:attr:`~StructureIdentificationModifier.only_selected` is set to ``True``.

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Bond properties
      -
    * - ``Topology``
      - The input bond topology; required only if :py:attr:`mode` is set to ``BondBased``.

Modifier outputs:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Particle properties
      -
    * - ``Structure Type``
      - The structure type computed by the algorithm for each particle, encoded as an integer value:

        ============= =========================================================
        Numeric id    Python constant
        ============= =========================================================
        0             ``CommonNeighborAnalysisModifier.Type.OTHER``
        1             ``CommonNeighborAnalysisModifier.Type.FCC``
        2             ``CommonNeighborAnalysisModifier.Type.HCP``
        3             ``CommonNeighborAnalysisModifier.Type.BCC``
        4             ``CommonNeighborAnalysisModifier.Type.ICO``
        ============= =========================================================
    * - ``Color``
      - Particle coloring to indicate the identified structure type for each particle; only if :py:attr:`~StructureIdentificationModifier.color_by_type` is ``True``.
        See the :py:attr:`~StructureIdentificationModifier.structures` array on how to customize the colors.

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Global attributes
      -
    * - ``CommonNeighborAnalysis.counts.OTHER``
      - Number of particles not matching any of the recognized structure types.
    * - ``CommonNeighborAnalysis.counts.FCC``
      - Number of particles identified as face-centered cubic.
    * - ``CommonNeighborAnalysis.counts.HCP``
      - Number of particles identified as hexagonal close packed.
    * - ``CommonNeighborAnalysis.counts.BCC``
      - Number of particles identified as body-centered cubic.
    * - ``CommonNeighborAnalysis.counts.ICO``
      - Number of particles identified as icosahedral.

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Data tables
      -
    * - ``structures``
      - A bar chart with the particle counts for each structure type identified by the modifier.
        You can retrieve this :py:class:`DataTable` from the `DataCollection.tables` dictionary."""

    class Mode(enum.Enum):
        """AUTODOC_SKIP_MEMBER

Members:

  FixedCutoff

  AdaptiveCutoff

  IntervalCutoff

  BondBased"""
        FixedCutoff = enum.auto()
        AdaptiveCutoff = enum.auto()
        IntervalCutoff = enum.auto()
        BondBased = enum.auto()

    @property
    def cutoff(self) -> float:
        """The cutoff radius used for the conventional common neighbor analysis. This parameter is only used if :py:attr:`mode` is ``CommonNeighborAnalysisModifier.Mode.FixedCutoff``.

:Default: ``3.2``"""
        ...

    @property
    def mode(self) -> Mode:
        """Selects the algorithm type. One of the following constants:

  * ``CommonNeighborAnalysisModifier.Mode.FixedCutoff``
  * ``CommonNeighborAnalysisModifier.Mode.AdaptiveCutoff``
  * ``CommonNeighborAnalysisModifier.Mode.IntervalCutoff``
  * ``CommonNeighborAnalysisModifier.Mode.BondBased``


:Default: ``CommonNeighborAnalysisModifier.Mode.AdaptiveCutoff``"""
        ...

class ComputePropertyModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

Evaluates a user-defined math expression for every input element and stores the results in an output property.
See also the corresponding user manual page for more information.
The modifier can operate on different data elements:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Data element
      -
    * - ``particles``
      - Computes a particle property.
    * - ``bonds``
      - Computes a bond property.
    * - ``voxels``
      - Computes a voxel grid property.

By default the modifier will act on particles. You can change this by setting the :py:attr:`operate_on` field.

Example:

```python
  pipeline.modifiers.append(ComputePropertyModifier(
      output_property = 'Color',
      expressions = ['Position.X / CellSize.X', '0.0', '0.5']
  ))
```

Note that a :py:class:`PythonScriptModifier` may sometimes be a better choice than this modifier to
set a property to computed values, in particular when the computation involves complex indexing operations or conditions."""

    @property
    def cutoff_radius(self) -> float:
        """The cutoff radius up to which neighboring particles are visited to compute :py:attr:`neighbor_expressions`.
This parameter is only used if :py:attr:`operate_on` is set to ``'particles'`` and the :py:attr:`neighbor_expressions`
field has been set.

:Default: 3.0"""
        ...

    @property
    def expressions(self) -> Tuple[str]:
        """A tuple of strings containing the math expressions to compute, one for each vector component of the selected output property. If the output property is scalar, the list must comprise one expression string. 

See the corresponding user manual page for a description of the expression syntax. 

:Default: ``('0', )``"""
        ...

    @property
    def neighbor_expressions(self) -> Tuple[str]:
        """The tuple of strings containing the math expressions for the per-neighbor terms, one for each vector component of the output particle property.
If the output property is scalar, the tuple must comprise one string only.

The neighbor expressions are only evaluated for each neighbor particle and the value is added to the output property of the central particle.
Neighbor expressions are only evaluated if :py:attr:`operate_on` is set to ``'particles'``.

:Default: ``()``"""
        ...

    @property
    def only_selected(self) -> bool:
        """If ``True``, the property is only computed for currently selected elements. In this case, the property values of unselected elements will be preserved if the output property already exists. 

:Default: ``False``"""
        ...

    @property
    def operate_on(self) -> str:
        """Selects the kind of data elements this modifier should operate on. Supported values are: ``'particles'``, ``'bonds'``, ``'voxels'``. 

:Default: ``'particles'``"""
        ...

    @property
    def output_property(self) -> str:
        """The name of the output property which the computed values will be assigned to. 

:Default: ``'My property'``"""
        ...

class ConstructSurfaceModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

Constructs the geometric surface of the solid region formed by point-like particles. The modifier generates
a :py:class:`SurfaceMesh`, which is a closed manifold consisting of triangular elements. It can further compute the
surface area and the volume of the region enclosed by the surface mesh as well as empty pores in the interior of the
filled region. See the corresponding user manual page
for more information.

Basic usage example:

```python
  from ovito.io import import_file
  from ovito.modifiers import ConstructSurfaceModifier
  
  pipeline = import_file("input/simulation.dump")
  pipeline.modifiers.append(ConstructSurfaceModifier(radius = 2.9))
  data = pipeline.compute()
  surface_mesh = data.surfaces['surface']
```

Alpha-shape method:

The modifier supports two different construction methods for the surface, which are selected by setting the :py:attr:`method`
parameter. The ``AlphaShape`` method uses a Delaunay tessellation constructed on the basis of the input particle coordinates
to identify volume elements that cannot fully accommodate a virtual probe sphere of a given radius and which are thus classified as being
part of the filled (or solid) region. The :py:attr:`radius` parameter controls the size of the virtual probe sphere and determines how 
much detail of the morphology are resolved during the surface construction. A larger radius leads to a surface with fewer details, 
reflecting only coarse features of the surface morphology. A small radius, on the other hand, will resolve finer surface features and 
small pores in the interior of a solid, for example.

See `[A. Stukowski, JOM 66 (2014), 399-407] <http://dx.doi.org/10.1007/s11837-013-0827-5>`_ for a description of the alpha-shape surface 
construction algorithm. Please cite this paper when publishing analysis results obtained with the help of OVITO.

Gaussian density method:

The second surface construction method supported by the modifier is based on the smeared-out representation of the point-like 
particles as overlapping Gaussian distribution functions centered on each particle site. The density field has local maximums  
at the particle centers and decays to zero far away from any particles. The surface mesh representation is then constructed as an isosurface
of the Gaussian density field, with the threshold :py:attr:`isolevel` chosen such that the resulting surface roughly represents the finite diameters of the input
particle spheres. 

```python
  pipeline.modifiers.append(ConstructSurfaceModifier(
      method = ConstructSurfaceModifier.Method.GaussianDensity,
      radius_scaling = 1.2,
      isolevel = 0.5))
```

Volume analysis:

The ``AlphaShape`` method provides the option to compute volume and surface area of the solid region formed by the input particles.
Furthermore, it allows identifying pores inside the solid and to compute their respective volumes and interior surface areas. 
To enable this extra calculation step, set :py:attr:`identify_regions` to ``True``. The modifier will output various
aggregate values such as the total surface area and the pore volume fraction as global attributes, 
see the table below.

```python
  pipeline.modifiers.append(ConstructSurfaceModifier(
      method = ConstructSurfaceModifier.Method.AlphaShape,
      radius = 2.9,
      identify_regions = True))
  
  data = pipeline.compute()
  print("Surface area: %f" % data.attributes['ConstructSurfaceMesh.surface_area'])
  print("Solid volume: %f" % data.attributes['ConstructSurfaceMesh.filled_volume'])
```

Outputs:

.. list-table::
    :widths: auto
    :header-rows: 1

    * - Surface
      -
    * - :py:class:`SurfaceMesh`
      - The surface mesh computed by the modifier. You can access it through the :py:attr:`surfaces`
        dictionary in the output :py:class:`DataCollection` under the lookup key ``"surface"``, see the
        code example below.

The following output attributes will only be computed if :py:attr:`identify_regions` is turned on:

.. list-table::
    :widths: auto
    :header-rows: 1

    * - Global attributes
      -
    * - ``ConstructSurfaceMesh.surface_area``
      - The total surface area in squared simulation units of length. 
        Includes only interfaces between empty and filled regions if they modifier identifies internal boundaries (filled-filled interfaces).
    * - ``ConstructSurfaceMesh.specific_surface_area``
      - The total surface area divided by the simulation cell volume (in reciprocal units of length).
    * - ``ConstructSurfaceMesh.filled_volume``
      - The total volume of the filled region(s) bounded by the surface in cubic simulation units of length.
    * - ``ConstructSurfaceMesh.empty_volume``
      - The total volume of the empty region(s) in cubic simulation units of length. Includes interior pores as well as the overlap of the infinite exterior region
        with the simulation box volume in case of a finite system with open boundary conditions.
    * - ``ConstructSurfaceMesh.filled_fraction``
      - Total volume of filled regions divided by the simulation box volume (unitless).
    * - ``ConstructSurfaceMesh.empty_fraction``
      - Total volume of empty regions divided by the simulation box volume (unitless).
    * - ``ConstructSurfaceMesh.filled_region_count``
      - Integer number of disconnected volumetric regions filled with particles.
    * - ``ConstructSurfaceMesh.empty_region_count``
      - Integer number of disconnected empty regions (voids).
    * - ``ConstructSurfaceMesh.cell_volume``
      - The total volume of the simulation box in cubic simulation units of length. Equal to `SimulationCell.volume`.

The following particle properties may be computed by the modifier:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Particle properties
      -
    * - ``Selection``
      - Will be set to 1 by the modifier for particles right at the surface of a filled region, and 0 for interior particles
        or isolated particles not forming any solid. Computed only if the :py:attr:`select_surface_particles` option is turned on.
    * - ``Surface Distance``
      - The computed distance of each particle from the closest point on the geometric surface. 
        This property is only computed if the :py:attr:`compute_distances` option is turned on.
    * - ``Region``
      - Index of the spatial region (see `SurfaceMesh.regions`) each particle is located in. 
        This property is only computed if the :py:attr:`map_particles_to_regions` option is turned on."""

    class Method(enum.Enum):
        """AUTODOC_SKIP_MEMBER

Members:

  AlphaShape

  GaussianDensity"""
        AlphaShape = enum.auto()
        GaussianDensity = enum.auto()

    @property
    def compute_distances(self) -> bool:
        """This option activates the calculation of distances of the particles from the constructed surface. The computed distance of each particle is measured to the closest point on the surface mesh. The modifier will output the computed distance values as a new particle property named ``Surface Distance``. 

Note that the computation of distances for all particles is a very expensive operation, which can take a long time for systems with many particles or a complex surface. To select surface particles, i.e. those particles which are located exactly on the surface, it may be more efficient to use the modifier's :py:attr:`select_surface_particles` option instead. 

:Default: ``False``"""
        ...

    @property
    def grid_resolution(self) -> int:
        """Specifies the number of grid cells along the longest dimension of the simulation cell when generating the Gaussian density grid. This parameter thus also controls the level of detail of the of the final surface mesh, which is constructed as an isosurface from the density grid data. 

The parameter is only used if ``GaussianDensity`` is selected as construction :py:attr:`method`.

:Default: ``50``"""
        ...

    @property
    def identify_regions(self) -> bool:
        """This option lets the modifier identify individual volumetric regions (filled with particles or empty) and compute their volumes and surface areas. 

Identifying volumetric regions is only supported by the ``AlphaShape`` surface construction :py:attr:`method`. For other construction methods, this option will be ignored. 

:Default: ``False``"""
        ...

    @property
    def isolevel(self) -> float:
        """The threshold value used for constructing the isosurface from the Gaussian density field. This parameter is only used if the selected construction :py:attr:`method` is set to ``GaussianDensity``. 

:Default: ``0.6``"""
        ...

    @property
    def method(self) -> Method:
        """Selects the algorithm for constructing the surface mesh from the input particles. The following methods are supported:


 * ``ConstructSurfaceModifier.Method.AlphaShape``
 * ``ConstructSurfaceModifier.Method.GaussianDensity``


If the default alpha-shape method is selected, you should set the :py:attr:`radius` parameter to specify the size of the virtual probe sphere, which determines the level of detail of the resulting surface. 

:Default: ``ConstructSurfaceModifier.Method.AlphaShape``"""
        ...

    @property
    def only_selected(self) -> bool:
        """If ``True``, the modifier acts only on selected particles and ignores other particles; if ``False``, the modifier constructs the surface around all particles.

:Default: ``False``"""
        ...

    @property
    def radius(self) -> float:
        """The radius of the virtual probe sphere used in the alpha-shape surface construction algorithm. This parameter is only used by the modifier if :py:attr:`method` is set to the default mode ``AlphaShape``. 

A rule of thumb is that the radius parameter should be slightly larger than the typical distance between nearest neighbor particles. 

:Default: ``4.0``"""
        ...

    @property
    def radius_scaling(self) -> float:
        """Scaling factor applied to the input particle radii when constructing the Gaussian density field for surface generation. This parameter is only used if the selected construction :py:attr:`method` is set to ``GaussianDensity``. The optional scaling serves as a way to increase the spatial extent of the Gaussian function centered on each particle site and to increase the overlap between the Gaussians, yielding a more connected isosurface. 

:Default: ``1.0``"""
        ...

    @property
    def select_surface_particles(self) -> bool:
        """This option lets the modifier select those particles that are part of the constructed geometric surface. This provides a simply way of identifying surface atoms or particles. If the flag is set to ``True``, the modifier will create the ``Selection`` particle property, assigning a value of 1 to surface particles and 0 to bulk particles. This particle selection may then be used in subsequent operations in the data pipeline. 

Selecting surface particles is only supported by the ``AlphaShape`` construction :py:attr:`method`. For other construction methods, the setting is ignored and the modifier does not create a particle selection. 

An alternative way of selecting particles that are located near the surface is to use the :py:attr:`compute_distances` option of the modifier. While the :py:attr:`select_surface_particles` option lets you identify particles located exactly on the geometric surface, the :py:attr:`compute_distances` option lets you define a distance threshold, selecting also particles slightly away from the surface. 

:Default: ``False``"""
        ...

    @property
    def smoothing_level(self) -> int:
        """The number of times the smoothing procedure is applied to the generated surface mesh. This parameter is only used by the modifier if :py:attr:`method` is set to the default mode ``AlphaShape``. 

Note that the smoothing level does only affect the computed surface area but not the solid volume. That is because the solid volume is computed before smoothing the mesh. (Smoothing is supposed to be volume preserving.)

:Default: ``8``"""
        ...

    @property
    def transfer_properties(self) -> bool:
        """This option lets the modifier copy the property values of the particles over to the vertices of the generated surface mesh. 

Note: If the Gaussian density method is used, only particle properties of data type ``Float`` will be transferred to the surface. Integer properties will be skipped, because the algorithm has to blend the property values of several particles in order to compute the value at each surface vertex. In case of the alpha-shape method, all properties are transferred, including integer properties, because there is a one-to-one mapping between input particles and output mesh vertices. 

:Default: ``False``"""
        ...

    @property
    def map_particles_to_regions(self) -> bool:
        """Tells the modifier to attribute each input particle to one of the spatial :py:attr:`regions` of the output :py:class:`SurfaceMesh`. 

This option generates a new per-particle property named ``Region`` specifying the indices of the spatial regions the particles are located it. A particle located exactly on the boundary between a filled and an empty region is always attributed to the filled region. Note, however, that a particle located fully inside an empty region will be attributed to that empty region. 

The mapping of particles to regions happens *before* the surface smoothing stage, which means particles may appear slightly outside of the region they were attributed to, because the vertices of the final surface mesh are displaced by the smoothing procedure. You can turn surface smoothing off by setting :py:attr:`smoothing_level` to 0. 

The modifier will try to assign all particles to spatial regions - even the unselected ones when the :py:attr:`only_selected` option is turned on and the surface is being constructed only for a subset of the particles. 

The :py:attr:`map_particles_to_regions` option is only supported by the ``AlphaShape`` surface construction :py:attr:`method`. Furthermore, the :py:attr:`identify_regions` option must be turned on; or otherwise this option has no effect. 

Usage example:

```python
  # Construct surface mesh around the subset of currently selected particles.
  pipeline.modifiers.append(ConstructSurfaceModifier(radius = 5.0, smoothing_level = 0, 
      only_selected = True, identify_regions = True, map_particles_to_regions = True))
  data = pipeline.compute()
  
  # Count particles located inside solid regions of the surface mesh (region property "Filled" is 1). 
  particle_regions = data.particles['Region']
  regions_table = data.surfaces['surface'].regions
  n = numpy.count_nonzero(regions_table['Filled'][particle_regions])
```

:Default: ``False``"""
        ...

    @property
    def vis(self) -> ovito.vis.SurfaceMeshVis:
        """The :py:class:`SurfaceMeshVis` element controlling the visual appearance of the generated surface in rendered images and animations."""
        ...

class CoordinationAnalysisModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

Computes coordination number of each particle and the radial distribution function (RDF) for the entire system.
See the corresponding user manual page
for more information.

Inputs:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Particle properties
      -
    * - ``Position``
      - The input coordinates of the particles.
    * - ``Particle Type``
      - Required if :py:attr:`partial` is set to ``True``.
    * - ``Selection``
      - The selection state of the input particles. Only needed if :py:attr:`only_selected` is set to ``True``.

Outputs:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Particle properties
      -
    * - ``Coordination``
      - The number of neighbors of each particle.

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - :py:class:`DataTable`
      -
    * - ``coordination-rdf``
      - The RDF computed by the modifier. You can retrieve the RDF data through the :py:attr:`tables`
        dictionary of the output :py:class:`DataCollection` under the lookup key ``"coordination-rdf"``, see the
        code examples below.

Examples:

The following batch script demonstrates how to load a particle configuration, compute the RDF using the modifier
and export the data to a text file:

```python
  from ovito.io import import_file
  from ovito.modifiers import CoordinationAnalysisModifier
  
  # Load a particle dataset, apply the modifier, and evaluate pipeline.
  pipeline = import_file("input/simulation.dump")
  modifier = CoordinationAnalysisModifier(cutoff = 5.0, number_of_bins = 200)
  pipeline.modifiers.append(modifier)
  data = pipeline.compute()
  
  # Print the computed g(r) function values.
  print(data.tables['coordination-rdf'].xy())
```

The following code demonstrates how to use the :py:class:`TimeAveragingModifier` to compute the RDF for every frame of an MD simulation and 
generate a time-averaged RDF histogram. Finally, the RDF histogram is written to an output file.

.. literalinclude:: ../example_snippets/coordination_analysis_modifier_averaging.py"""

    @property
    def cutoff(self) -> float:
        """Specifies the cutoff distance for the coordination number calculation and also the range up to which the modifier calculates the RDF. 

:Default: ``3.2``"""
        ...

    @property
    def number_of_bins(self) -> int:
        """The number of histogram bins to use when computing the RDF.

:Default: ``200``"""
        ...

    @property
    def only_selected(self) -> bool:
        """Restricts the calculation to currently selected particles. Unselected particles will be treated as if they did not exist and their ``Coordination`` value is set to zero when this option is enabled. 

:Default: ``False``"""
        ...

    @property
    def partial(self) -> bool:
        """This modifier option requests the calculation of element-specific (partial) RDFs. The resulting RDF table will contain one tabulated g(r) function for each pair-wise combination of particle types in the input. This code example demonstrates how to access the partial RDFs computed by the modifier: 

```python
  from ovito.io import import_file
  from ovito.modifiers import CoordinationAnalysisModifier
  
  # Load input data.
  pipeline = import_file("input/simulation.dump")
  
  # Print the list of input particle types.
  # They are represented by ParticleType objects attached to the 'Particle Type' particle property.
  for t in pipeline.compute().particles.particle_types.types:
      print("Type %i: %s" % (t.id, t.name))
  
  # Calculate partial RDFs:
  pipeline.modifiers.append(CoordinationAnalysisModifier(cutoff=5.0, number_of_bins=100, partial=True))
  
  # Access the output DataTable:
  rdf_table = pipeline.compute().tables['coordination-rdf']
  
  # The y-property of the data points of the DataTable is now a vectorial property.
  # Each vector component represents one partial RDF.
  rdf_names = rdf_table.y.component_names
  
  # Print a list of partial g(r) functions.
  for component, name in enumerate(rdf_names):
      print("g(r) for pair-wise type combination %s:" % name)
      print(rdf_table.y[:,component])
  
  # The DataTable.xy() method yields everthing as one combined NumPy table.
  # This includes the 'r' values in the first array column, followed by the
  # tabulated g(r) partial functions in the remaining columns. 
  print(rdf_table.xy())
```

:Default: ``False``"""
        ...

class CoordinationPolyhedraModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

Constructs coordination polyhedra around selected particles for visualization purposes.
See the corresponding user manual page
for more information. A coordination polyhedron is the convex hull constructed from the neighbor atoms
of some central atom.

In order to tell the modifier which input particles should be surrounded by a coordination polyhedron,
the central particles must be selected first. The particle selection can be created by inserting a 
:py:class:`SelectTypeModifier` into the data pipeline prior to this modifier. 

The modifier furthermore requires input bonds connecting a central particle with its neighbors 
to define which atoms the algorithm should use in the construction of the convex hulls.
You can insert the :py:class:`CreateBondsModifier` prior to this modifier to let OVITO dynamically generate
neighbor bonds between particles.

Example:

```python
  # Import simulation dataset and add it to the scene:
  pipeline = import_file("input/simulation.0.dump")
  pipeline.add_to_scene()
  
  # Select all atoms of species type 1. They will form the centers of the polyhedra.
  pipeline.modifiers.append(SelectTypeModifier(types={1}))
  # Create bonds between nearby atoms.
  pipeline.modifiers.append(CreateBondsModifier(cutoff=3.0))
  # Let the modifier construct the coordination polyhedra around selected atoms.
  modifier = CoordinationPolyhedraModifier()
  pipeline.modifiers.append(modifier)
  
  # Optional: Configure visual appearance of the polyhedra and make them semi-transparent.
  modifier.vis.surface_transparency = 0.4
  modifier.vis.highlight_edges = True
```

Modifier inputs:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Particle properties
      -
    * - ``Selection``
      - Determines the subset of particles for which coordination polyhedra should be constructed.
        You can select all particles of certain chemical type(s) by first inserting a :py:class:`SelectTypeModifier` into the pipeline.

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Bond properties
      -
    * - ``Topology``
      - The bonds list, which is used to determine the set of bonded neighbor particles serving as vertices
        for the construction of a coordination polyhedron around some central particle. 
        You can let OVITO create the bond topology by inserting a :py:class:`CreateBondsModifier` into the pipeline first.

Modifier outputs:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Polyhedral mesh
      -
    * - ``coord-polyhedra``
      - The polyhedral :py:class:`SurfaceMesh` generated by the modifier. You can retrieve it from the :py:attr:`surfaces`
        dictionary of the :py:class:`DataCollection`."""

    @property
    def vis(self) -> ovito.vis.SurfaceMeshVis:
        """The :py:class:`SurfaceMeshVis` element controlling the visual appearance of the generated polyhedra in rendered images and animations."""
        ...

class CreateBondsModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

Creates bonds between nearby particles.
See the corresponding user manual page
for more information.

Inputs:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Particle properties
      -
    * - ``Position``
      - The xyz coordinates of the input particles.
    * - ``Particle Type``
      - The particle type information, which is used only if :py:attr:`mode` is set to ``VdWRadius`` or ``Pairwise``.
    * - ``Molecule Identifier``
      - The assignment of atoms to molecules, which is used only if :py:attr:`intra_molecule_only` is set to ``True``.

Outputs:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Bond properties
      -
    * - ``Topology``
      - The modifier will create new bond topology entries and append them to the property arrays in an existing :py:class:`Bonds`
        object; or it creates a new :py:class:`Bonds` instance if necessary.
    * - ``Periodic Image``
      - Stores the transitions of each bond through the faces of a periodic simulation cell if the bond connects
        two particles from different periodic images of the system.
    * - ``Bond Type``
      - The type ID information that is assigned to newly created bonds according to the modifier's :py:attr:`bond_type` field.

.. list-table::
    :widths: auto
    :header-rows: 1

    * - Global attributes
      -
    * - ``CreateBonds.num_bonds``
      - The number of bonds that exists after the modifier's operation."""

    class Mode(enum.Enum):
        """AUTODOC_SKIP_MEMBER

Members:

  Uniform

  Pairwise

  VdWRadius"""
        Uniform = enum.auto()
        VdWRadius = enum.auto()
        Pairwise = enum.auto()

    @property
    def bond_type(self) -> ovito.data.BondType:
        """The :py:class:`BondType` that will be assigned to the newly created bonds. This lets you control the display color of the new bonds."""
        ...

    @property
    def cutoff(self) -> float:
        """The upper cutoff distance for the creation of bonds between particles. This parameter is only used if :py:attr:`mode` is ``Uniform``. 

:Default: ``3.2``"""
        ...

    @property
    def intra_molecule_only(self) -> bool:
        """If this option is set to true, the modifier will create bonds only between atoms that belong to the same molecule (i.e. which have the same molecule ID assigned to them).

:Default: ``False``"""
        ...

    @property
    def lower_cutoff(self) -> float:
        """The minimum bond length. No bonds will be created between particles whose distance is below this threshold. 

:Default: ``0.0``"""
        ...

    @property
    def mode(self) -> Mode:
        """Controls the cutoff criterion for creating bonds. Valid cutoff modes are:

  * ``CreateBondsModifier.Mode.Uniform``
  * ``CreateBondsModifier.Mode.VdWRadius``
  * ``CreateBondsModifier.Mode.Pairwise``


Mode ``Uniform`` uses a single uniform :py:attr:`cutoff` distance for creating bonds, which is independent of the types of the particles. Mode ``VdWRadius`` uses a distance cutoff that is derived from the :py:attr:`vdw_radius` (Van der Waals radius) of the :py:class:`ParticleType` of the two particles involved. Mode ``Pairwise`` lets you specify a separate cutoff distance for each pairwise combination of particle types using the :py:meth:`set_pairwise_cutoff` method. 

:Default: ``CreateBondsModifier.Mode.Uniform``"""
        ...

    @property
    def prevent_hh_bonds(self) -> bool:
        """Controls whether the modifier should *not* generate bonds between pairs of hydrogen atoms. This flag only applies if :py:attr:`.mode` is set to ``VdWRadius`` and the van der Waals radii of the atom types are used for generating pair-wise bonds. A particle is considered a hydrogen atom if its :py:class:`ParticleType`'s name is ``'H'``. 

:Default: ``True``"""
        ...

    @property
    def vis(self) -> ovito.vis.BondsVis:
        """The :py:class:`BondsVis` object controlling the visual appearance of the bonds created by this modifier."""
        ...

    def get_pairwise_cutoff(self, type_a: Union[int, str], type_b: Union[int, str]) -> float:
        """Returns the pair-wise cutoff distance that was previously set for a specific pair of particle types using the :py:meth:`set_pairwise_cutoff` method. 

:param str,int type_a: The :py:attr:`name` or numeric :py:attr:`id` of the first particle type
:param str,int type_b: The :py:attr:`name` or numeric :py:attr:`id` of the second particle type
:return: The cutoff distance set for the type pair. Returns zero if no cutoff has been set for the pair."""
        ...

    def set_pairwise_cutoff(self, type_a: Union[int, str], type_b: Union[int, str], cutoff: float) -> None:
        """Sets the cutoff range for creating bonds between a specific pair of particle types. This information is only used if :py:attr:`mode` is set to ``Pairwise``.

:param str,int type_a: The :py:attr:`name` or numeric :py:attr:`id` of the first particle type
:param str,int type_b: The :py:attr:`name` or numeric :py:attr:`id` of the second particle type
:param float cutoff: The cutoff distance to be used by the modifier for the type pair


If you want no bonds to be created between a pair of types, set the corresponding cutoff radius to zero (which is the default)."""
        ...

class CreateIsosurfaceModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

Constructs an isosurface for a scalar field defined on a three-dimensional :py:class:`VoxelGrid`.
See the corresponding user manual page
for more information on this modifier.

The modifier takes an existing :py:class:`VoxelGrid` as input, for example a charge density
field loaded from an input simulation file or a three-dimensional voxel grid dynamically 
computed by the :py:class:`SpatialBinningModifier`. The input voxel grid for the isosurface
must be specified by setting the :py:attr:`operate_on` field to the string ``'voxels:'`` followed by the
:py:attr:`identifier` of the input voxel grid. Furthermore, you need to specify 
the name of the field :py:class:`Property` for which to construct the isosurface, because
multiple fields may be defined on the same voxel grid.

    ```python
  # Import a charge density field from a VASP calculation:
  pipeline = import_file("input/CHGCAR.nospin.gz")
  pipeline.add_to_scene()
  
  # The identifier of the imported VoxelGrid is 'charge-density',
  # and the field property defined on the grid is named 'Charge density'.
  print(pipeline.source.data.grids['charge-density'])
  
  # Set up the isosurface modifier:
  modifier = CreateIsosurfaceModifier(
      operate_on = 'voxels:charge-density', 
      property = 'Charge density',
      isolevel = 0.00014)
  pipeline.modifiers.append(modifier)
  
  # Adjust visual appearance of the isosurface in rendered images:
  modifier.vis.show_cap = False
  modifier.vis.surface_transparency = 0.4
```

The following example demonstrates how to construct an isosurface for a dynamically computed field by
the :py:class:`SpatialBinningModifier`:

    ```python
  pipeline.modifiers.append(SpatialBinningModifier(
      property = 'Particle Type',
      direction = SpatialBinningModifier.Direction.XYZ, 
      bin_count = (30, 30, 30),
      reduction_operation = SpatialBinningModifier.Operation.Mean
  ))
  pipeline.modifiers.append(CreateIsosurfaceModifier(
      operate_on = 'voxels:binning', 
      property = 'Particle Type',
      isolevel = 1.5
  ))
```

Modifier outputs:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - :py:class:`SurfaceMesh`
      -
    * - ``isosurface``
      - The :py:class:`SurfaceMesh` constructed by the modifier. You can retrieve it from the :py:attr:`surfaces`
        dictionary of the pipeline's output :py:class:`DataCollection`.

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - :py:class:`DataTable`
      -
    * - ``isosurface-histogram``
      - A histogram of the input field values. You can retrieve this :py:class:`DataTable` from the :py:attr:`tables`
        dictionary of the pipeline's output :py:class:`DataCollection`."""

    @builtins.property
    def isolevel(self) -> float:
        """The value at which to create the isosurface.

:Default: ``0.0``"""
        ...

    @builtins.property
    def operate_on(self) -> str:
        """Specifies the :py:class:`VoxelGrid` this modifier should operate on. Set this to the prefix string ``'voxels:'`` followed by the :py:attr:`identifier` of the grid. 

Note: You can use the Python statement ``print(pipeline.compute().grids)`` to find out what the identifiers of the voxel :py:attr:`grids` in your data pipeline are. 

:Default: ``'voxels:'``"""
        ...

    @builtins.property
    def property(self) -> str:
        """The name of the :py:class:`Property` in the selected input :py:class:`VoxelGrid` for which to construct the isosurface. Note that this must be a scalar property. If the input grid property is a vector property, you need to explicitly specify which vector component to use, e.g. ``'Dipole Orientation.Z'``."""
        ...

    @builtins.property
    def transfer_values(self) -> str:
        """This option lets the modifier copy auxiliary properties of the voxel field (aside from the field quantity for which the isosurface is being constructed) over to the vertices of the generated isosurface mesh. The local field value at each isosurface vertex is computed from the voxel values using trilinear interpolation. Subsequently, the :py:class:`ColorCodingModifier` can be used to color the generated isosurface based on some secondary field quantity, for example. 

:Default: ``False``"""
        ...

    @builtins.property
    def vis(self) -> ovito.vis.SurfaceMeshVis:
        """The :py:class:`SurfaceMeshVis` controlling the visual appearance of the generated isosurface in rendered images."""
        ...

class DeleteSelectedModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

This modifier deletes the currently selected elements.
See also the corresponding user manual page for more information.

Inputs:

The modifier can operate on any combination of the following data elements:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Data element
      -
    * - ``particles``
      - Deletes all particles with a non-zero value of the ``Selection`` property.
    * - ``bonds``
      - Deletes all bonds with a non-zero value of the ``Selection`` property.
    * - ``surface_regions``
      - Deletes all selected spatial regions (including the corresponding mesh faces) from a :py:class:`SurfaceMesh`.

By default the modifier will act on all data element types simultaneously. You can restrict it to a subset by setting the :py:attr:`operate_on` field."""

    @property
    def operate_on(self) -> AbstractSet[str]:
        """A set of strings specifying the kinds of data elements this modifier should operate on. By default the set contains all data element types supported by the modifier. 

:Default: ``{'particles', 'bonds', 'surface_regions'}``"""
        ...

class DislocationAnalysisModifier(StructureIdentificationModifier):
    """Base: :py:class:`ovito.modifiers.StructureIdentificationModifier`

This analysis modifier extracts all dislocations in a crystal and converts them to continuous line segments.
The computational method behind this is called *Dislocation Extraction Algorithm* (DXA) and is described
in the paper `[MSMSE 20 (2012), 085007] <http://stacks.iop.org/0965-0393/20/085007>`__.
See also the corresponding user manual page for this modifier.

The extracted dislocation lines are output as a :py:class:`DislocationNetwork` object by the modifier
and can be accessed through the `DataCollection.dislocations` field
after the modification pipeline has been evaluated. This is demonstrated in the example script below.

Furthermore, you can use the :py:func:`export_file` function to write the dislocation lines
to a so-called CA file. The CA file format is described on this page
of the OVITO user manual.

Inputs:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Particle properties
      -
    * - ``Position``
      - The coordinates of the input particles.
    * - ``Selection``
      - The selection state of the input particles. Only needed if :py:attr:`~StructureIdentificationModifier.only_selected` is ``True``.

Outputs:

.. list-table::
    :widths: auto
    :header-rows: 1

    * - Dislocations
      -
    * - :py:class:`DislocationNetwork`
      - The dislocation lines found by the modifier. You can access this data object through the :py:attr:`dislocations`
        field of the output :py:class:`DataCollection`, see the
        code example below.

.. list-table::
    :widths: auto
    :header-rows: 1

    * - Global attributes
      -
    * - ``DislocationAnalysis.total_line_length``
      - Total length of all dislocation lines found by the DXA (in simulation units).
    * - ``DislocationAnalysis.length.1/n<ijk>``
      - A set of attributes indicating the length of dislocations broken down by Burgers vector type.
        For example, the attribute ``DislocationAnalysis.length.1/6<112>`` specifies the total line length of Shockley partials found by the DXA.
    * - ``DislocationAnalysis.length.other``
      - Total length of dislocation lines with an unusual Burgers vector that do not belong to any of the predefined standard dislocation types.
    * - ``DislocationAnalysis.cell_volume``
      - The volume of the input simulation cell. You can use it to calculate the dislocation density from the line length.
    * - ``DislocationAnalysis.counts.OTHER``
      - Number of particles not matching any of the known structural types.
    * - ``DislocationAnalysis.counts.FCC``
      - Number of particles identified as face-centered cubic structure.
    * - ``DislocationAnalysis.counts.HCP``
      - Number of particles identified as hexagonal close packed structure.
    * - ``DislocationAnalysis.counts.BCC``
      - Number of particles identified as body-centered cubic structure.
    * - ``DislocationAnalysis.counts.CubicDiamond``
      - Number of particles identified as cubic diamond structure.
    * - ``DislocationAnalysis.counts.HexagonalDiamond``
      - Number of particles identified as hexagonal diamond structure.

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Particle properties
      -
    * - ``Structure Type``
      - The structure type assigned to each particle by the CNA sub-algorithm, encoded as an integer value:

        ============= =========================================================
        Value         Python constant
        ============= =========================================================
        0             ``DislocationAnalysisModifier.Lattice.Other``
        1             ``DislocationAnalysisModifier.Lattice.FCC``
        2             ``DislocationAnalysisModifier.Lattice.HCP``
        3             ``DislocationAnalysisModifier.Lattice.BCC``
        4             ``DislocationAnalysisModifier.Lattice.CubicDiamond``
        5             ``DislocationAnalysisModifier.Lattice.HexagonalDiamond``
        ============= =========================================================
    * - ``Color``
      - A per-particle color representing the identified structure type (only if :py:attr:`~StructureIdentificationModifier.color_by_type` is ``True``).
    * - ``Cluster``
      - The ID of the cluster each atom has been assigned to. A "cluster" is a contiguous group of atoms, all being of the same
        crystalline structure type. Non-crystalline atoms are assigned to cluster ID 0.

Example:

```python
  from ovito.io import import_file, export_file
  from ovito.modifiers import DislocationAnalysisModifier
  from ovito.data import DislocationNetwork
  
  import ovito
  ovito.enable_logging()
  
  pipeline = import_file("input/simulation.dump")
  
  # Extract dislocation lines from a crystal with diamond structure:
  modifier = DislocationAnalysisModifier()
  modifier.input_crystal_structure = DislocationAnalysisModifier.Lattice.CubicDiamond
  pipeline.modifiers.append(modifier)
  data = pipeline.compute()
  
  total_line_length = data.attributes['DislocationAnalysis.total_line_length']
  cell_volume = data.attributes['DislocationAnalysis.cell_volume']
  print("Dislocation density: %f" % (total_line_length / cell_volume))
  
  # Print list of dislocation lines:
  print("Found %i dislocation segments" % len(data.dislocations.segments))
  for segment in data.dislocations.segments:
      print("Segment %i: length=%f, Burgers vector=%s" % (segment.id, segment.length, segment.true_burgers_vector))
      print(segment.points)
  
  # Export dislocation lines to a CA file:
  export_file(pipeline, "output/dislocations.ca", "ca")
  
  # Or export dislocations to a ParaView VTK file:
  export_file(pipeline, "output/dislocations.vtk", "vtk/disloc")
```"""

    class Lattice(enum.Enum):
        """AUTODOC_SKIP_MEMBER

Members:

  Other

  FCC

  HCP

  BCC

  CubicDiamond

  HexagonalDiamond"""
        FCC = enum.auto()
        HCP = enum.auto()
        BCC = enum.auto()
        CubicDiamond = enum.auto()
        HexagonalDiamond = enum.auto()

    @property
    def circuit_stretchability(self) -> int:
        """The number of steps by which a Burgers circuit can stretch while it is being advanced along a dislocation line.

:Default: ``9``"""
        ...

    @property
    def color_by_type(self) -> bool:
        """Controls whether the modifier assigns a color to each particle based on the identified structure type. 

:Default: ``True``"""
        ...

    @property
    def defect_mesh_smoothing_level(self) -> int:
        """Specifies the number of iterations of the surface smoothing algorithm to perform when post-processing the extracted defect mesh.

:Default: ``8``"""
        ...

    @property
    def defect_vis(self) -> ovito.vis.SurfaceMeshVis:
        """The :py:class:`SurfaceMeshVis` element controlling the visual representation of the generated defect mesh."""
        ...

    @property
    def disloc_vis(self) -> ovito.vis.DislocationVis:
        """The :py:class:`DislocationVis` element controlling the visual representation of the generated dislocation lines."""
        ...

    @property
    def input_crystal_structure(self) -> Lattice:
        """The type of crystal to analyze. Must be one of: 

  * ``DislocationAnalysisModifier.Lattice.FCC``
  * ``DislocationAnalysisModifier.Lattice.HCP``
  * ``DislocationAnalysisModifier.Lattice.BCC``
  * ``DislocationAnalysisModifier.Lattice.CubicDiamond``
  * ``DislocationAnalysisModifier.Lattice.HexagonalDiamond``


:Default: ``DislocationAnalysisModifier.Lattice.FCC``"""
        ...

    @property
    def line_coarsening_enabled(self) -> bool:
        """Flag that enables the coarsening of extracted dislocation lines, which reduces the number of sample points along the lines.

:Default: ``True``"""
        ...

    @property
    def line_point_separation(self) -> float:
        """Sets the desired distance between successive sample points along the dislocation lines, measured in multiples of the interatomic spacing. This parameter controls the amount of coarsening performed during post-processing of dislocation lines.

:Default: ``2.5``"""
        ...

    @property
    def line_smoothing_enabled(self) -> bool:
        """Flag that enables the smoothing of extracted dislocation lines after they have been coarsened.

:Default: ``True``"""
        ...

    @property
    def line_smoothing_level(self) -> int:
        """The number of iterations of the line smoothing algorithm to perform.

:Default: ``1``"""
        ...

    @property
    def only_perfect_dislocations(self) -> bool:
        """This flag controls whether the algorithm should extract only perfect dislocations (and no partial dislocations, which is normally done for FCC/HCP and diamond lattices). Make sure you set the :py:attr:`circuit_stretchability` parameter to a high value when activating this option, because large Burgers circuits are needed to identify dissociated dislocations with a wide core. 

:Default: ``False``"""
        ...

    @property
    def only_selected(self) -> bool:
        """Set this to ``True`` to perform the analysis on selected particles only. Particles that are not selected will be treated as if they did not exist. Use the :py:class:`SelectTypeModifier`, for example, to restrict the crystal structure identification to a sub-lattice formed by one species of particles in a multi-component system. 

:Default: ``False``"""
        ...

    @property
    def trial_circuit_length(self) -> int:
        """The maximum length of trial Burgers circuits constructed by the DXA to discover dislocations. The length is specified in terms of the number of atom-to-atom steps.

:Default: ``14``"""
        ...

class ElasticStrainModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

This modifier computes the atomic-level elastic strain and deformation gradient tensors in crystalline systems.
See also the corresponding user manual page for this modifier.

The modifier first performs an identification of the local crystal structure and stores the results in the ``Structure Type`` particle
property. Possible structure type values are listed under the :py:attr:`input_crystal_structure` property.
Atoms that do not form a crystalline structure or which are part of defects are assigned the special type ``OTHER`` (=0).
For these atoms the local elastic deformation cannot be computed.

If :py:attr:`calculate_deformation_gradients` is set to true, the modifier outputs a new particle property named ``Elastic Deformation Gradient``,
which contains the per-atom elastic deformation gradient tensors. Each tensor has nine components stored in column-major order.
Atoms for which the elastic deformation gradient could not be determined (i.e. which are classified as ``OTHER``) will be assigned the null tensor.

If :py:attr:`calculate_strain_tensors` is set to true, the modifier outputs a new particle property named ``Elastic Strain``,
which contains the per-atom elastic strain tensors. Each symmetric strain tensor has six components stored in the order XX, YY, ZZ, XY, XZ, YZ.
Atoms for which the elastic strain tensor could not be determined (i.e. which are classified as ``OTHER``) will be assigned the null tensor.

Furthermore, the modifier generates a particle property ``Volumetric Strain``, which stores the trace divided by three of the local elastic strain tensor.
Atoms for which the elastic strain tensor could not be determined (i.e. which are classified as ``OTHER``) will be assigned a value of zero.

Inputs:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Particle properties
      -
    * - ``Position``
      - The coordinates of the input particles.
    * - ``Selection``
      - The selection state of the input particles. Only needed if :py:attr:`~StructureIdentificationModifier.only_selected` is ``True``.

Outputs:


.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Particle properties
      -
    * - ``Elastic Deformation Gradient``
      - The computed per-atom elastic deformation gradient tensors.
        Each tensor consists of 9 components stored in column-major order.
        All components will be set to zero for atoms for which no elastic deformation tensor could be determined (because they were classified as ``OTHER``).
        This output property is only generated if :py:attr:`calculate_deformation_gradients` is set to ``True``.
    * - ``Elastic Strain``
      - The computed per-atom elastic strain tensor.
        Each symmetric strain tensor has six components stored in the order XX, YY, ZZ, XY, XZ, YZ.
        All components will be set to zero for atoms for which no elastic strain tensor could be determined (because they were classified as ``OTHER``).
        This output property is only generated if :py:attr:`calculate_strain_tensors` is set to ``True``.
    * - ``Volumetric Strain``
      - Scalar particle property which is set to one third of the trace of the computed local elastic strain tensor.
        Atoms for which no elastic strain tensor could be determined (because they were classified as ``OTHER``) will
        have a volumetric strain value of zero.
    * - ``Structure Type``
      - The structure type determined by the algorithm for each particle, encoded as an integer value:

        ============= =========================================================
        Value         Python constant
        ============= =========================================================
        0             ``ElasticStrainModifier.Lattice.OTHER``
        1             ``ElasticStrainModifier.Lattice.FCC``
        2             ``ElasticStrainModifier.Lattice.HCP``
        3             ``ElasticStrainModifier.Lattice.BCC``
        4             ``ElasticStrainModifier.Lattice.CubicDiamond``
        5             ``ElasticStrainModifier.Lattice.HexagonalDiamond``
        ============= =========================================================
    * - ``Color``
      - A per-particle color representing the identified structure type (only if :py:attr:`~StructureIdentificationModifier.color_by_type` is ``True``).
    * - ``Cluster``
      - The ID of the cluster each atom has been assigned to. A "cluster" is a contiguous group of atoms, all being of the same
        crystalline structure type. Non-crystalline atoms are assigned the invalid cluster ID 0."""

    class Lattice(enum.Enum):
        """A simple attribute-based namespace.

SimpleNamespace(**kwargs)"""
        FCC = enum.auto()
        HCP = enum.auto()
        BCC = enum.auto()
        CubicDiamond = enum.auto()
        HexagonalDiamond = enum.auto()

    @property
    def axial_ratio(self) -> float:
        """The *c/a* ratio of the ideal unit cell for crystals with hexagonal symmetry.

:Default: ``sqrt(8/3)``"""
        ...

    @property
    def calculate_deformation_gradients(self) -> bool:
        """Flag that enables the output of the calculated elastic deformation gradient tensors. The per-particle tensors will be stored in a new particle property named ``Elastic Deformation Gradient`` with nine components (stored in column-major order). Particles for which the local elastic deformation cannot be calculated, are assigned the null tensor. 

:Default: ``False``"""
        ...

    @property
    def calculate_strain_tensors(self) -> bool:
        """Flag that enables the calculation and out of the elastic strain tensors. The symmetric strain tensors will be stored in a new particle property named ``Elastic Strain`` with six components (XX, YY, ZZ, XY, XZ, YZ). 

:Default: ``True``"""
        ...

    @property
    def input_crystal_structure(self) -> Lattice:
        """The type of crystal to analyze. Must be one of: 

  * ``ElasticStrainModifier.Lattice.FCC``
  * ``ElasticStrainModifier.Lattice.HCP``
  * ``ElasticStrainModifier.Lattice.BCC``
  * ``ElasticStrainModifier.Lattice.CubicDiamond``
  * ``ElasticStrainModifier.Lattice.HexagonalDiamond``


:Default: ``ElasticStrainModifier.Lattice.FCC``"""
        ...

    @property
    def lattice_constant(self) -> float:
        """Lattice constant (*a*:sub:`0`) of the ideal unit cell.

:Default: ``1.0``"""
        ...

    @property
    def push_strain_tensors_forward(self) -> bool:
        """Selects the frame in which the elastic strain tensors are calculated. 

If true, the *Eulerian-Almansi* finite strain tensor is computed, which measures the elastic strain in the global coordinate system (spatial frame). 

If false, the *Green-Lagrangian* strain tensor is computed, which measures the elastic strain in the local lattice coordinate system (material frame). 

:Default: ``True``"""
        ...

class ExpandSelectionModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

Expands the current particle selection by selecting particles that are neighbors of already selected particles.
See the corresponding user manual page for more information.

Inputs:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Particle properties
      -
    * - ``Selection``
      - The selection state of the input particles.
    * - ``Position``
      - The coordinates of the input particles (only used if :py:attr:`mode` is ``Cutoff`` or ``Nearest``).

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Bond properties
      -
    * - ``Topology``
      - The list of bonds (only used if :py:attr:`mode` is ``Bonded``).

Outputs:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Particle properties
      -
    * - ``Selection``
      - The output particle selection."""

    class ExpansionMode(enum.Enum):
        """AUTODOC_SKIP_MEMBER

Members:

  Cutoff

  Nearest

  Bonded"""
        Cutoff = enum.auto()
        Nearest = enum.auto()
        Bonded = enum.auto()

    @property
    def cutoff(self) -> float:
        """The maximum distance up to which particles are selected around already selected particles. This parameter is only used if :py:attr:`mode` is set to ``ExpansionMode.Cutoff``.

:Default: ``3.2``"""
        ...

    @property
    def iterations(self) -> int:
        """Controls how many iterations of the modifier are executed. This can be used to select neighbors of neighbors up to a certain recursive depth.

:Default: ``1``"""
        ...

    @property
    def mode(self) -> ExpansionMode:
        """Selects the mode of operation, i.e., how the modifier extends the selection around already selected particles. Valid values are:

  * ``ExpandSelectionModifier.ExpansionMode.Cutoff``
  * ``ExpandSelectionModifier.ExpansionMode.Nearest``
  * ``ExpandSelectionModifier.ExpansionMode.Bonded``


:Default: ``ExpandSelectionModifier.ExpansionMode.Cutoff``"""
        ...

    @property
    def num_neighbors(self) -> int:
        """The number of nearest neighbors to select around each already selected particle. This parameter is only used if :py:attr:`mode` is set to ``ExpansionMode.Nearest``.

:Default: ``1``"""
        ...

class ExpressionSelectionModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

Selects data elements, e.g. particles, based on a user-defined Boolean expression. 
This modifier can be inserted into a :py:class:`Pipeline` to create a selection
set. which subsequent modifiers in the pipeline can operate on.

See also the corresponding user manual page for more information on this modifier.
The modifier can select different kinds of data elements depending on the value of its :py:attr:`operate_on` property:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Operate on
      - Description
    * - ``particles`` (default)
      - Selects particles based on a user-defined criterion.
    * - ``bonds``
      - Selects bonds based on a user-defined criterion.
    * - ``surface_regions``
      - Selects volumetric regions of a :py:class:`SurfaceMesh` based on a user-defined criterion.

Outputs:

The modifier sets or updates the value of the ``Selection`` property of each data element: 1 if 
the expression evaluates to true for an element; 0 otherwise.

.. list-table::
    :widths: auto
    :header-rows: 1

    * - Global attributes
      -
    * - ``ExpressionSelection.count``
      - The number of data elements (particles/bonds) that have been selected by the modifier.

Usage example:

The following code example demonstrates how to select all atoms whose potential energy 
exceeds a threshold value of -3.6 eV. After executing the pipeline, the number of atoms that got selected
may be queried by inspecting the global attribute ``ExpressionSelection.count``,
which was created by the modifier as summarized output:

```python
  pipeline.modifiers.append(ExpressionSelectionModifier(expression = 'PotentialEnergy > -3.6'))
  data = pipeline.compute()
  print(data.attributes['ExpressionSelection.count'])
```

Note that, in many cases, the :py:class:`ExpressionSelectionModifier` class can be replaced with an equivalent
:ref:`user-defined modifier function <writing_custom_modifiers>` creating the selection directly.
The example above can be reimplemented without a :py:class:`ExpressionSelectionModifier` as follows:

```python
  def select_atoms(frame, data):
      sel = data.particles['Potential Energy'] > -3.6
      data.particles_.create_property('Selection', data=sel)
  pipeline.modifiers.append(select_atoms)
  data = pipeline.compute()
  print(numpy.count_nonzero(data.particles['Selection']))
```

In this second version, the selection criterion is specified in terms of a native Python expression operating on a NumPy array
containing particle property values, which means you are no longer limited to the simple language supported by :py:class:`ExpressionSelectionModifier`.
NumPy expressions allow you to directly and efficiently compute the ``Selection`` property array and thereby establish the output selection set.

Furthermore, if you just want to count the number of particles that fulfill a certain criterion, it may not even be necessary to create a selection. 
You can directly use NumPy's `count_nonzero() <https://numpy.org/doc/stable/reference/generated/numpy.count_nonzero.html>`__
function to determine the number of particles for which some Boolean expression evaluates to true:

```python
  data = pipeline.compute()
  print(numpy.count_nonzero(data.particles['Potential Energy'] > -3.6))
```"""

    @property
    def expression(self) -> str:
        """The Boolean expression to be evaluated by the modifier for each data element, formatted as a Python string. The expression syntax is documented in :ref:`OVITO's user manual <manual:particles.modifiers.expression_select>`; it is *not* regular Python syntax. The string's contents will be parsed by OVITO's integrated math expression interpreter (`muparser <https://beltoforion.de/en/muparser/>`__). 

.. note::

  Keep in mind that the Boolean expression is subject to special syntax rules.   Because variable identifiers cannot contain spaces, spaces occurring in particle property names must be omitted.   For example, the particle property `Potential Energy` must be referred to as ``PotentialEnergy`` in the expression string. 

Note that you can incorporate the values of regular Python variables in the expression simply by using Python's `string formatting <https://docs.python.org/3/tutorial/inputoutput.html#formatted-string-literals>`__ technique, e.g. 

```python
  threshold = float(sys.argv[1])
  pipeline.modifiers.append(ExpressionSelectionModifier(expression = f"ShearStrain>{threshold}"))
```

The generated string that the modifier sees contains just a constant literal in place of the original Python variable reference. Furthermore, it is possible to update the expression string *after* the modifier was inserted into the pipeline. Re-evaluating the data pipeline will recompute the selection, letting you perform several calculations in a for-loop, for example: 

```python
  modifier = ExpressionSelectionModifier()
  pipeline.modifiers.append(modifier)
  for threshold in numpy.arange(0.0, 1.0, 0.05):
      modifier.expression = f"ShearStrain>{threshold}"
      data = pipeline.compute()
      print(threshold, data.attributes['ExpressionSelection.count'])
```"""
        ...

    @property
    def operate_on(self) -> str:
        """Selects the kind of data elements this modifier should operate on. One of the following strings: ``'particles'``, ``'bonds'``, ``'surface_regions'``. 

:Default: ``'particles'``"""
        ...

class FreezePropertyModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

This modifier copies the values of a source property from some reference animation frame (frame 0 by default) to the current animation frame.
It allows preserving a particle or bond property that would otherwise change with time.
See also the corresponding user manual page for more information.
The modifier can operate on different data elements:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Data element
      -
    * - ``particles``
      - Freezes a particle property.
    * - ``bonds``
      - Freezes a bond property.
    * - ``voxels``
      - Freezes a voxel grid property.

By default the modifier will operate on a particle property. You can change this by setting the :py:attr:`operate_on` field.

Example:

.. literalinclude:: ../example_snippets/freeze_property_modifier.py
   :emphasize-lines: 12-14"""

    @property
    def destination_property(self) -> str:
        """The name of the output property that should be created by the modifier. It may be the same as :py:attr:`source_property`. If the destination property already exists in the modifier's input, the values are overwritten."""
        ...

    @property
    def freeze_at(self) -> int:
        """The animation frame number at which to freeze the input property's values. 

:Default: ``0``"""
        ...

    @property
    def operate_on(self) -> str:
        """Selects the kind of properties this modifier should operate on. Supported values are: ``'particles'``, ``'bonds'``, ``'voxels'``. 

:Default: ``'particles'``"""
        ...

    @property
    def source_property(self) -> str:
        """The name of the input property that should be evaluated by the modifier on the animation frame specified by :py:attr:`freeze_at`."""
        ...

class GenerateTrajectoryLinesModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

This modifier periodically samples the time-dependent positions of particles to produce a :py:class:`TrajectoryLines` object.
The modifier is typically used to visualize the paths of motion of particles as continuous curves.
See the corresponding user manual page for more information.

Note that inserting the modifier into the pipeline is not sufficient to visualize the lines.
The line tracing (i.e. the sampling of the particle positions over the entire simulation trajectory) must be explicitly 
triggered by calling the modifier's :py:meth:`.generate` method as in the following code example:

.. literalinclude:: ../example_snippets/trajectory_lines.py"""

    @property
    def frame_interval(self) -> Optional[Tuple[int, int]]:
        """The animation frame interval over which the particle positions are sampled to generate the trajectory lines. Set this to a tuple of two integers to specify the first and the last animation frame; or use ``None`` to generate trajectory lines over the entire animation sequence.

:Default: ``None``"""
        ...

    @property
    def only_selected(self) -> bool:
        """Controls whether trajectory lines should only by generated for currently selected particles.

:Default: ``True``"""
        ...

    @property
    def sample_particle_property(self) -> str:
        """Name of the particle property to sample along the generated trajectory lines. 

This option transfers the specified particle property to the trajectory line vertices. In other words, the time-dependent input property of the particles becomes a position-dependent property of the generated trajectory lines. The sampled values will become available in the :py:class:`TrajectoryLines` object and may subsequently be used for pseudo-coloring the trajectory lines. See also the `TrajectoryVis.color_mapping_property` option. 

The following code example demonstrates how to color trajectory lines based on the velocity magnitude of the particles at the corresponding simulation times: 


```python
  from ovito.io import *
  from ovito.modifiers import *
  from ovito.vis import *
  import numpy
  
  # Import an MD simulation trajectory. The snapshots stored in the trajectory file contain the instantaneous 
  # particle velocities (vector property "Velocity") at each timestep and OVITO automatically
  # computes the scalar velocities (particle property "Velocity Magnitude") during file import.
  pipeline = import_file('../../../ovito/tests/files/GSD/trajectory.gsd')
  
  # Turn off the display of particles.
  pipeline.compute().particles.vis.enabled = False
  
  # Generate trajectory lines:
  modifier = GenerateTrajectoryLinesModifier(only_selected = False)
  modifier.sample_particle_property = 'Velocity Magnitude'
  
  # Insert modifier into the pipeline before calling generate(), because it needs access to the pipeline's data.
  pipeline.modifiers.append(modifier)
  modifier.generate()
  
  # Configure trajectory line visualization:
  modifier.vis.width = 0.1
  modifier.vis.shading = TrajectoryVis.Shading.Normal
  
  # Locally color the trajectory lines based on the 'Velocity Magnitude' property, which was transferred 
  # from the particles to the trajectory line vertices.
  modifier.vis.color_mapping_property = 'Velocity Magnitude'
  
  # To determine the correct min/max value range for pseudo-coloring, we need to access the
  # array of property values associated with the generated trajectory lines:
  velocity_magnitudes = pipeline.compute().trajectories['Velocity Magnitude']
  modifier.vis.color_mapping_interval = (numpy.amin(velocity_magnitudes), numpy.amax(velocity_magnitudes))
  
  # Insert pipeline into the scene to make the trajectory lines visible in rendered images.
  pipeline.add_to_scene()
```

:Default: ``''``"""
        ...

    @property
    def sampling_frequency(self) -> int:
        """Length of the animation frame intervals at which the particle positions should be sampled.

:Default: ``1``"""
        ...

    @property
    def unwrap_trajectories(self) -> bool:
        """Controls whether trajectory lines should be automatically unwrapped at the box boundaries when the particles cross a periodic boundary.

:Default: ``True``"""
        ...

    @property
    def vis(self) -> ovito.vis.TrajectoryVis:
        """The :py:class:`TrajectoryVis` element controlling the visual appearance of the trajectory lines created by this modifier."""
        ...

    def generate(self) -> None:
        """Generates the trajectory lines by sampling the positions of the particles from the upstream pipeline in regular animation time intervals. Make sure you call this method *after* the modifier has been inserted into the pipeline and all its parameters have been configured."""
        ...

class GrainSegmentationModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

This analysis modifier identifies the individual grains in a polycrystalline microstructure.
See the corresponding user manual page for 
more information on this modifier.

Inputs:

.. list-table::
    :widths: auto
    :header-rows: 1

    * - Particle properties
      -
    * - ``Position``
      - The input coordinates of the particles.
    * - ``Structure Type``
      - The local structure types computed by the :py:class:`PolyhedralTemplateMatchingModifier`.
    * - ``Orientation``
      - The local lattice orientations computed by the :py:class:`PolyhedralTemplateMatchingModifier`.

Outputs:

.. list-table::
    :widths: auto
    :header-rows: 1

    * - Particle properties
      -
    * - ``Grain``
      - The numeric identifier of the grain a particle has been assigned to by the algorithm.
    * - ``Color``
      - A per-particle color representing either the grain (if :py:attr:`color_particles` is ``True``) or the identified PTM structure type.

.. list-table::
    :widths: auto
    :header-rows: 1

    * - Global attributes
      -
    * - ``GrainSegmentation.grain_count``
      - Number of grains that have been found by the algorithm.

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - :py:class:`DataTable`
      -
    * - ``grains``
      - A data table containing the list of grains found by the algorithm.
    * - ``grains-merge``
      - A scatter plot of the ordered cluster merge steps computed by the grain segmentation algorithm."""

    class Algorithm(enum.Enum):
        """AUTODOC_SKIP_MEMBER

Members:

  GraphClusteringAuto

  GraphClusteringManual

  MinimumSpanningTree"""
        GraphClusteringAuto = enum.auto()
        GraphClusteringManual = enum.auto()
        MinimumSpanningTree = enum.auto()

    @property
    def algorithm(self) -> Algorithm:
        """Selects the cluster merge algorithm to use. One of the following constants:

  * ``GrainSegmentationModifier.Algorithm.GraphClusteringAuto``
  * ``GrainSegmentationModifier.Algorithm.GraphClusteringManual``
  * ``GrainSegmentationModifier.Algorithm.MinimumSpanningTree``


:Default: ``GrainSegmentationModifier.Algorithm.GraphClusteringAuto``"""
        ...

    @property
    def color_particles(self) -> bool:
        """Controls whether the modifier colors atoms according to the grains they have been assigned to. 

:Default: ``True``"""
        ...

    @property
    def handle_stacking_faults(self) -> bool:
        """Controls whether the algorithm should handle stacking faults and coherent twin boundaries explicitly. If turned off, atoms with cubic and hexagonal crystal structure will simply be treated as separate phases and will never be merged into the same grain. 

:Default: ``True``"""
        ...

    @property
    def merging_threshold(self) -> float:
        """Specifies the maximum graph edge contraction distance and determines the resulting number and sizes of grains. A lower threshold produces more (and smaller) grains; a larger threshold produces fewer (and larger) grains. 

This parameter is ignored if :py:attr:`algorithm` is ``GraphClusteringAuto``, in which case the merging threshold is automatically determined by the algorithm to give optimal segmentation results. 

:Default: ``0.0``"""
        ...

    @property
    def min_grain_size(self) -> int:
        """Minimum number of atoms in a grain. Crystallite clusters smaller than this threshold get dissolved during the grain segmentation and their atoms are merged into neighboring grains. 

:Default: ``100``"""
        ...

    @property
    def orphan_adoption(self) -> bool:
        """Controls the merging of non-crystalline atoms (e.g. grain boundary atoms) into adjacent grains. 

:Default: ``True``"""
        ...

class HistogramModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

Generates a histogram of a property, i.e. the distribution of its per-element values.
See also the corresponding user manual page for more information.
The modifier can operate on different types of data elements:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Data element
      -
    * - ``particles``
      - Computes the histogram for a particle property.
    * - ``bonds``
      - Computes the histogram for a bond property.
    * - ``voxels``
      - Computes the histogram for a voxel grid property.

By default the modifier will operate on a particle property. You can change this by setting the :py:attr:`operate_on` field.

The value range of the histogram is determined automatically from the minimum and maximum values of the selected property
unless :py:attr:`fix_xrange` is set to ``True``. In this case the range of the histogram is controlled by the
:py:attr:`xrange_start` and :py:attr:`xrange_end` parameters.

Example:

.. literalinclude:: ../example_snippets/histogram_modifier.py"""

    @builtins.property
    def bin_count(self) -> int:
        """The number of histogram bins.

:Default: ``200``"""
        ...

    @builtins.property
    def fix_xrange(self) -> bool:
        """Controls how the value range of the histogram is determined. If set to ``False``, the interval and bin widths are chosen automatically by the modifier to include all input values. If set to ``True``, the histogram's value range may be specified explicitly by setting :py:attr:`xrange_start` and :py:attr:`xrange_end`.

:Default: ``False``"""
        ...

    @builtins.property
    def only_selected(self) -> bool:
        """If ``True``, the histogram is computed only on the basis of currently selected particles or bonds. You can use this to restrict histogram calculation to a subset of input particles/bonds. 

:Default: ``False``"""
        ...

    @builtins.property
    def operate_on(self) -> str:
        """Selects the kind of data elements this modifier should operate on. Supported values are: ``'particles'``, ``'bonds'``, ``'voxels'``. 

:Default: ``'particles'``"""
        ...

    @builtins.property
    def property(self) -> str:
        """The name of the input property for which to compute the histogram. For vector properties a component name must be appended in the string, e.g. ``"Velocity.X"``. 

:Default: ``''``"""
        ...

    @builtins.property
    def xrange_end(self) -> float:
        """If :py:attr:`fix_xrange` is true, then this parameter controls the upper end of the value interval covered by the histogram. Input values higher than this range limit will be discarded from the computed histogram. 

:Default: ``0.0``"""
        ...

    @builtins.property
    def xrange_start(self) -> float:
        """If :py:attr:`fix_xrange` is true, then this parameter controls the lower end of the value interval covered by the histogram.Input values lower than this range limit will be discarded from the computed histogram. 

:Default: ``0.0``"""
        ...

class IdentifyDiamondModifier(StructureIdentificationModifier):
    """Base: :py:class:`ovito.modifiers.StructureIdentificationModifier`

Analyzes the local neighborhood of each particle to identify cubic or hexagonal diamond lattices.
See the corresponding user manual page
for more information.

Note that this class inherits several important parameter fields from its :py:class:`StructureIdentificationModifier`
base class.

Modifier inputs:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Particle properties
      -
    * - ``Position``
      - The input coordinates of the particles.
    * - ``Selection``
      - The selection state of the input particles. Only needed if :py:attr:`~StructureIdentificationModifier.only_selected` is ``True``.

Modifier outputs:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Particle properties
      -
    * - ``Structure Type``
      - The structure type computed by the algorithm for each particle, encoded as an integer value:

        ============= =========================================================
        Numeric id    Python constant
        ============= =========================================================
        0             ``IdentifyDiamondModifier.Type.OTHER``
        1             ``IdentifyDiamondModifier.Type.CUBIC_DIAMOND``
        2             ``IdentifyDiamondModifier.Type.CUBIC_DIAMOND_FIRST_NEIGHBOR``
        3             ``IdentifyDiamondModifier.Type.CUBIC_DIAMOND_SECOND_NEIGHBOR``
        4             ``IdentifyDiamondModifier.Type.HEX_DIAMOND``
        5             ``IdentifyDiamondModifier.Type.HEX_DIAMOND_FIRST_NEIGHBOR``
        6             ``IdentifyDiamondModifier.Type.HEX_DIAMOND_SECOND_NEIGHBOR``
        ============= =========================================================
    * - ``Color``
      - Particle coloring to indicate the identified structure type for each particle; only if :py:attr:`~StructureIdentificationModifier.color_by_type` is ``True``.
        See the :py:attr:`~StructureIdentificationModifier.structures` array on how to customize the colors.

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Global attributes
      -
    * - ``IdentifyDiamond.counts.OTHER``
      - Number of particles not matching any of the recognized structure types.
    * - ``IdentifyDiamond.counts.CUBIC_DIAMOND``
      - Number of particles identified as fully coordinated cubic diamond.
    * - ``IdentifyDiamond.counts.CUBIC_DIAMOND_FIRST_NEIGHBOR``
      - Number of particles identified as partially coordinated cubic diamond.
    * - ``IdentifyDiamond.counts.CUBIC_DIAMOND_SECOND_NEIGHBOR``
      - Number of particles identified as partially coordinated cubic diamond.
    * - ``IdentifyDiamond.counts.HEX_DIAMOND``
      - Number of particles identified as fully coordinated hexagonal diamond.
    * - ``IdentifyDiamond.counts.HEX_DIAMOND_FIRST_NEIGHBOR``
      - Number of particles identified as partially coordinated hexagonal diamond.
    * - ``IdentifyDiamond.counts.HEX_DIAMOND_SECOND_NEIGHBOR``
      - Number of particles identified as partially coordinated hexagonal diamond.

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Data tables
      -
    * - ``structures``
      - A bar chart with the particle counts for each structure type identified by the modifier.
        You can retrieve this :py:class:`DataTable` from the `DataCollection.tables` dictionary."""
    pass

class InvertSelectionModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

This modifier inverts the current data element selection.
See also the corresponding user manual page for more information.
The modifier can operate on different kinds of data elements:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Data element
      -
    * - ``particles``
      - Inverts the values of the ``Selection`` particle property.
    * - ``bonds``
      - Inverts the values of the ``Selection`` bond property.
    * - ``voxels``
      - Inverts the values of the ``Selection`` voxel grid property.

By default the modifier will act on particles. You can change this by setting the :py:attr:`operate_on` field."""

    @property
    def operate_on(self) -> str:
        """Selects the kind of data elements this modifier should operate on. Supported values are: ``'particles'``, ``'bonds'``, ``'voxels'``. 

:Default: ``'particles'``"""
        ...

class LoadTrajectoryModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

This modifier loads trajectories of particles from a separate simulation file.
See also the corresponding user manual page for this modifier.

The typical use case for this modifier is when the topology of a molecular system (i.e. the definition of atom types, bonds, etc.) is
stored separately from the trajectories of atoms. In this case you should load the topology file first using :py:func:`import_file`.
Then create and apply the :py:class:`LoadTrajectoryModifier` to the topology dataset, which loads the trajectory file.
The modifier will replace the static atom positions from the topology dataset with the time-dependent positions from the trajectory file.

Example:

```python
  from ovito.io import import_file
  from ovito.modifiers import LoadTrajectoryModifier
  
  # Load static topology data from a LAMMPS data file.
  pipeline = import_file('input/input.data', atom_style='bond')
  
  # Load atom trajectories from separate LAMMPS dump file.
  traj_mod = LoadTrajectoryModifier()
  traj_mod.source.load('input/trajectory.dump')
  print("Number of frames: ", traj_mod.source.num_frames)
  
  # Insert modifier into data pipeline.
  pipeline.modifiers.append(traj_mod)
```

Furthermore, it is possible to let the modifier load varying bond topologies
for each trajectory frame from a LAMMPS `dump local <https://docs.lammps.org/dump.html>`__ file:

```python
  bonds_mod = LoadTrajectoryModifier()
  bonds_mod.source.load('input/bonds.dump.local', 
      columns = [None, 'Bond Type', 'Particle Identifiers.1', 'Particle Identifiers.2', 'Length', 'Energy'])
  pipeline.modifiers.append(bonds_mod)
```

Here, the ``columns`` function parameter specifies the mapping of data columns in the imported dump file to corresponding
target bond properties within OVITO. The dump local file :file:`bonds.dump.local` contains six data columns 
and has been produced by the following LAMMPS commands::

   compute 1 all property/local btype batom1 batom2
   compute 2 all bond/local dist engpot
   dump bonds all local 100 bonds.dump.local index c_1[1] c_1[2] c_1[3] c_2[1] c_2[2]"""

    @property
    def source(self) -> ovito.pipeline.FileSource:
        """A :py:class:`FileSource` that provides the trajectories of particles. You can call its :py:meth:`load` function to load a simulation trajectory file as shown in the code example above."""
        ...

class PolyhedralTemplateMatchingModifier(StructureIdentificationModifier):
    """Base: :py:class:`ovito.modifiers.StructureIdentificationModifier`

This modifier analyzes the local neighborhood of each particle to identify common structural motives and crystalline structures.
The structure identification is based on the Polyhedral Template Matching (PTM) algorithm.
See the corresponding user manual page
for more information. The PTM algorithm is able to compute local crystal orientations, elastic lattice strains, and can identify 
local chemical orderings in binary compounds.

Note that this modifier inherits several important parameter fields from the :py:class:`StructureIdentificationModifier`
base class.

Modifier inputs:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Particle properties
      -
    * - ``Position``
      - The input coordinates of the particles.
    * - ``Particle Type``
      - The chemical types of the input particles; only used if :py:attr:`output_ordering` is ``True``.
    * - ``Selection``
      - The selection state of the input particles; only used if :py:attr:`~StructureIdentificationModifier.only_selected` is ``True``.

Modifier outputs:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Particle properties
      -
    * - ``Structure Type``
      - The structure type computed by the algorithm for each particle, encoded as an integer value:

        ============= ========================================================= =============
        Numeric id    Python constant                                           Initial state
        ============= ========================================================= =============
        0             ``PolyhedralTemplateMatchingModifier.Type.OTHER``         
        1             ``PolyhedralTemplateMatchingModifier.Type.FCC``           enabled
        2             ``PolyhedralTemplateMatchingModifier.Type.HCP``           enabled
        3             ``PolyhedralTemplateMatchingModifier.Type.BCC``           enabled
        4             ``PolyhedralTemplateMatchingModifier.Type.ICO``           disabled
        5             ``PolyhedralTemplateMatchingModifier.Type.SC``            disabled
        6             ``PolyhedralTemplateMatchingModifier.Type.CUBIC_DIAMOND`` disabled
        7             ``PolyhedralTemplateMatchingModifier.Type.HEX_DIAMOND``   disabled
        8             ``PolyhedralTemplateMatchingModifier.Type.GRAPHENE``      disabled
        ============= ========================================================= =============

        The algorithm only identifies enabled structure types; see :py:attr:`~StructureIdentificationModifier.structures` array for details.
    * - ``RMSD``
      - The per-particle RMSD values computed by the PTM algorithm.
        Only if :py:attr:`output_rmsd` is set.
    * - ``Interatomic Distance``
      - The per-particle local atomic distances computed by the PTM algorithm.
        Only if :py:attr:`output_interatomic_distance` is set.
    * - ``Orientation``
      - The local lattice orientations computed by the PTM algorithm, encoded as quaternions.
        Only if :py:attr:`output_orientation` is set.
    * - ``Elastic Deformation Gradient``
      - The per-particle elastic deformation gradient tensors computed by the PTM algorithm (3x3 components).
        Only if :py:attr:`output_deformation_gradient` is set.
    * - ``Ordering Type``
      - The local chemical ordering type determined by the PTM algorithm, encoded as an integer value.
        Only if :py:attr:`output_ordering` is set.

        ============= =========================================================
        Numeric id    Python constant
        ============= =========================================================
        0             ``PolyhedralTemplateMatchingModifier.OrderingType.OTHER``
        1             ``PolyhedralTemplateMatchingModifier.OrderingType.PURE``
        2             ``PolyhedralTemplateMatchingModifier.OrderingType.L10``
        3             ``PolyhedralTemplateMatchingModifier.OrderingType.L12_A``
        4             ``PolyhedralTemplateMatchingModifier.OrderingType.L12_B``
        5             ``PolyhedralTemplateMatchingModifier.OrderingType.B2``
        6             ``PolyhedralTemplateMatchingModifier.OrderingType.ZINCBLENDE_WURTZITE``
        7             ``PolyhedralTemplateMatchingModifier.OrderingType.BORON_NITRIDE``
        ============= =========================================================
    * - ``Color``
      - Particle coloring to indicate the identified structure type for each particle; only if :py:attr:`~StructureIdentificationModifier.color_by_type` is ``True``.
        See the :py:attr:`~StructureIdentificationModifier.structures` array on how to customize the colors.

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Global attributes
      -
    * - ``PolyhedralTemplateMatching.counts.OTHER``
      - Number of particles not matching any of the recognized structural types.
    * - ``PolyhedralTemplateMatching.counts.FCC``
      - Number of particles identified as face-centered cubic structure.
    * - ``PolyhedralTemplateMatching.counts.HCP``
      - Number of particles identified as hexagonal close packed structure.
    * - ``PolyhedralTemplateMatching.counts.BCC``
      - Number of particles identified as body-centered cubic structure.
    * - ``PolyhedralTemplateMatching.counts.ICO``
      - Number of particles identified as icosahedral structure.
    * - ``PolyhedralTemplateMatching.counts.SC``
      - Number of particles identified as simple cubic structure.
    * - ``PolyhedralTemplateMatching.counts.CUBIC_DIAMOND``
      - Number of particles identified as cubic diamond structure.
    * - ``PolyhedralTemplateMatching.counts.HEX_DIAMOND``
      - Number of particles identified as hexagonal diamond structure.
    * - ``PolyhedralTemplateMatching.counts.GRAPHENE``
      - Number of particles identified as 2d graphene structure.

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Data tables
      -
    * - ``structures``
      - A bar chart with the particle counts for each structure type identified by the modifier.
        You can retrieve this :py:class:`DataTable` from the `DataCollection.tables` dictionary.
    * - ``ptm-rmsd``
      - A histogram with the RMSD value distribution computed by the modifier.
        You can retrieve this :py:class:`DataTable` from the `DataCollection.tables` dictionary."""

    @property
    def output_deformation_gradient(self) -> bool:
        """Boolean flag that controls whether the modifier outputs the computed per-particle elastic deformation gradients as a new particle property named ``Elastic Deformation Gradient``.The elastic deformation gradient describes the local deformation and rigid-body rotation of the crystal with respect to an ideal reference lattice configuration. See the OVITO user manual for details. 

:Default: ``False``"""
        ...

    @property
    def output_interatomic_distance(self) -> bool:
        """Boolean flag that controls whether the modifier outputs the computed per-particle interatomic distance as a new particle property named ``Interatomic Distance``.

:Default: ``False``"""
        ...

    @property
    def output_ordering(self) -> bool:
        """Boolean flag that controls whether the modifier should identify local ordering types and output them as a new particle property named ``Ordering Type``. 

:Default: ``False``"""
        ...

    @property
    def output_orientation(self) -> bool:
        """Boolean flag that controls whether the modifier outputs the computed per-particle lattice orientations as a new particle property named ``Orientation``. The lattice orientation is specified in terms of a quaternion that describes the rotation of the crystal with respect to a reference lattice orientation. See the OVITO user manual for details. 

:Default: ``False``"""
        ...

    @property
    def output_rmsd(self) -> bool:
        """Boolean flag that controls whether the modifier outputs the computed per-particle RMSD values as a new particle property named ``RMSD``.

:Default: ``False``"""
        ...

    @property
    def rmsd_cutoff(self) -> float:
        """The maximum allowed root mean square deviation for positive structure matches. If this threshold value is non-zero, template matches that yield a RMSD value above the cutoff are classified as "Other". This can be used to filter out spurious template matches (false positives). 

:Default: ``0.1``"""
        ...

class PythonScriptModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

Allows you to insert a user-defined Python function into a data pipeline. 

This class makes it possible to implement new modifier functions in the Python language which can participate in OVITO's 
data pipeline system and which can be used just like OVITO's built-in modifiers. 
You can learn more about the usage of this class in the :ref:`writing_custom_modifiers` section.

Example:

.. literalinclude:: ../example_snippets/python_script_modifier.py"""

    @property
    def function(self) -> Optional[Callable[[int, ovito.data.DataCollection], Any]]:
        """The Python function to be called each time the data pipeline is evaluated by the system.

The function must have a signature as shown in the example above. The *frame* parameter specifies the current animation frame number at which the data pipeline is being evaluated. The :py:class:`DataCollection` *data* initially holds the input data objects of the modifier, which were produced by the upstream part of the data pipeline. The user-defined modifier function is free modify the data collection and the data objects stored in it. 

:Default: ``None``"""
        ...

class ReplicateModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

This modifier replicates all particles, bonds and other elements of a system to visualize periodic images.
See also the corresponding user manual page for more information.

Inputs:

The modifier can operate on any combination of the following data elements:

.. list-table::
    :widths: auto
    :header-rows: 1

    * - Data element
      -
    * - ``particles``
      - Duplicates :py:class:`Particles` and :py:class:`Bonds`.
    * - ``surfaces``
      - Duplicates the mesh geometry of :py:class:`SurfaceMesh` objects.
    * - ``voxels``
      - Duplicates the voxel elements of :py:class:`VoxelGrid` objects.
    * - ``dislocations``
      - Duplicates dislocation lines in a :py:class:`DislocationNetwork`.

By default the modifier will operate on all of these. You can restrict it to a subset by setting the :py:attr:`operate_on` field."""

    @property
    def adjust_box(self) -> bool:
        """Controls whether the simulation cell is resized. If ``True``, the simulation cell is accordingly extended to fit the replicated data. If ``False``, the original simulation cell size (containing only the primary image of the system) is maintained. 

:Default: ``True``"""
        ...

    @property
    def num_x(self) -> bool:
        """A positive integer specifying the number of copies to generate in the *x* direction (including the existing primary image).

:Default: ``1``"""
        ...

    @property
    def num_y(self) -> bool:
        """A positive integer specifying the number of copies to generate in the *y* direction (including the existing primary image).

:Default: ``1``"""
        ...

    @property
    def num_z(self) -> bool:
        """A positive integer specifying the number of copies to generate in the *z* direction (including the existing primary image).

:Default: ``1``"""
        ...

    @property
    def operate_on(self) -> AbstractSet[str]:
        """A set of strings specifying the kinds of data elements this modifier should operate on. By default the set contains all data element types supported by the modifier. 

:Default: ``{'particles', 'voxels', 'surfaces', 'dislocations'}``"""
        ...

    @property
    def unique_ids(self) -> bool:
        """If ``True``, the modifier automatically generates new unique IDs for each copy of particles. Otherwise, the replica will keep the same IDs as the original particles, which is typically not what you want. 

Note: This option has no effect if the input particles do not already have numeric IDs (i.e. the ``'Particle Identifier'`` property does not exist). 

:Default: ``True``"""
        ...

class SelectTypeModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

Selects data elements of a certain type or types (e.g. all atoms of a chemical species).
See also the corresponding user manual page for more information.
The modifier can operate on different data elements:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Data element
      -
    * - ``particles``
      - Selects all particles of a certain type.
    * - ``bonds``
      - Selects all bonds of a certain type.

By default the modifier will act on particles. You can change this by setting the :py:attr:`operate_on` field.

Outputs:

.. list-table::
    :widths: auto
    :header-rows: 1

    * - Global attributes
      -
    * - ``SelectType.num_selected``
      - The number of data elements (particles/bonds) that have been selected by the modifier.

Example:

.. literalinclude:: ../example_snippets/select_type_modifier.py"""

    @builtins.property
    def operate_on(self) -> str:
        """Controls the kind of data elements this modifier should select. Supported values are: ``'particles'``, ``'bonds'``. 

:Default: ``'particles'``"""
        ...

    @builtins.property
    def property(self) -> str:
        """The name of the property to use as input; must be an integer property. 

For selecting particles, possible input properties are ``'Particle Type'`` and ``'Structure Type'``, for example. For selecting bonds, ``'Bond Type'`` is a typical input property. 

:Default: ``'Particle Type'``"""
        ...

    @builtins.property
    def types(self) -> AbstractSet[Union[str, int]]:
        """The ``set`` of types to select. You can add numeric type *IDs* or type *names* to this set. 
Type names will automatically be translated into corresponding numeric type IDs by the modifier.
Thus, it is not necessary for you to look up the numeric ID for a type name using `Property.type_by_name()`.
For example, to select all atoms belonging to the type named 'Cu':

```python
  modifier = SelectTypeModifier(property = 'Particle Type', types = {'Cu'})
```

When using the :py:class:`SelectTypeModifier` to select *structural* types, you can directly use the predefined numeric constants for the structures, e.g.:

```python
  # Let the CNA modifier identify the structural type of each particle:
  pipeline.modifiers.append(CommonNeighborAnalysisModifier())
  # Select all FCC and HCP particles:
  modifier = SelectTypeModifier(property = 'Structure Type')
  modifier.types = { CommonNeighborAnalysisModifier.Type.FCC,
                     CommonNeighborAnalysisModifier.Type.HCP }
  pipeline.modifiers.append(modifier)
```

:Default: ``set([])``"""
        ...

class SliceModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

Deletes or selects data elements located within a semi-infinite region bounded by a plane or within a slab bounded by a pair of parallel planes.
See also the corresponding user manual page for more information.

Inputs:

The modifier can operate on any combination of the following data elements:

.. list-table::
    :widths: auto
    :header-rows: 1

    * - Data element
      -
    * - ``particles``
      - Deletes (or selects) particles.
    * - ``surfaces``
      - Cuts the mesh geometry of a :py:class:`SurfaceMesh`.
    * - ``voxels``
      - Creates a cross-sectional cut of a :py:class:`VoxelGrid`.
    * - ``dislocations``
      - Cuts dislocation lines of a :py:class:`DislocationNetwork`.

By default the modifier will act on all of these. You can restrict it to a subset by setting the :py:attr:`operate_on` field.
Furthermore, you can restrict the operation to only selected particles by setting the :py:attr:`only_selected` option.

The :py:attr:`select` option lets you select all elements on one side of the plane instead of deleting them.
Currently, the selection mode works only for :py:class:`Particles` or :py:class:`SurfaceMesh` vertices,
which get selected by setting their ``Selection`` particle property to 1."""

    @property
    def distance(self) -> float:
        """The distance of the slicing plane from the origin (along its normal vector).Its interpretation depends on whether :py:attr:`miller` mode is enabled or not. 

:Default: ``0.0``"""
        ...

    @property
    def gridslice_vis(self) -> ovito.vis.SurfaceMeshVis:
        """The :py:class:`SurfaceMeshVis` controlling the visual appearance of the cross-sectional slice being extracted from a :py:class:`VoxelGrid` by the modifier. The visual element is only used if :py:attr:`operate_on` includes ``'voxels'`` and the input data collection contains a :py:class:`VoxelGrid`."""
        ...

    @property
    def inverse(self) -> bool:
        """Reverses the sense of the slicing plane.

:Default: ``False``"""
        ...

    @property
    def miller(self) -> bool:
        """Controls whether the :py:attr:`.normal` vector and the :py:attr:`.distance` parameter are given in terms of the reciprocal cell vectors. 

If enabled, the modifier will interpret the components of the :py:attr:`.normal` vector as Miller indices :math:`hkl`. Note that the indices do not have to be integer. The :attr:`.distance` parameter measures the (signed) offset of the plane from the simulation cell origin. It is specified in terms of the interplanar spacing :math:`d_{\\mathrm{hkl}}`, which depends on the simulation cell vectors and the Miller indices :math:`hkl`. 

If Miller index mode is off, the :py:attr:`.normal` vector is specified in the Cartesian simulation coordinate system. The :attr:`.distance` from the origin (0,0,0) is measured in simulation units of length along the normal vector. 

The :py:attr:`.slab_width` parameter is always specified in real-space units. 

:Default: ``False``"""
        ...

    @property
    def normal(self) -> ovito.vis.Vector3:
        """The normal vector of the slicing plane. Its interpretation depends on whether :py:attr:`miller` mode is enabled or not. 

:Default: ``(1.0, 0.0, 0.0)``"""
        ...

    @property
    def only_selected(self) -> bool:
        """Controls whether the modifier should act only on currently selected data elements (e.g. selected particles).

:Default: ``False``"""
        ...

    @property
    def operate_on(self) -> AbstractSet[str]:
        """A set of strings specifying the kinds of data elements this modifier should operate on. By default the set contains all data element types supported by the modifier. 

:Default: ``{'particles', 'surfaces', 'voxels', 'dislocations'}``"""
        ...

    @property
    def plane_vis(self) -> ovito.vis.TriangleMeshVis:
        """The :py:class:`TriangleMeshVis` controlling the visual appearance of the cutting plane in rendered images. The visual element is only used when :py:attr:`render_plane` has been set to ``True`` to visualize the mathematical plane of the modifier as a visible polygon."""
        ...

    @property
    def render_plane(self) -> bool:
        """Controls whether the modifier should produce renderable geometry to visualize the cutting plane. The visual appearance of the plane can be adjusted through the :py:attr:`plane_vis` element. 

:Default: ``False``"""
        ...

    @property
    def select(self) -> bool:
        """If ``True``, the modifier selects data elements instead of deleting them.

:Default: ``False``"""
        ...

    @property
    def slab_width(self) -> float:
        """The thickness of the slab to cut (in simulation units of length). If zero, the modifier cuts away everything on one side of the cutting plane.

:Default: ``0.0``"""
        ...

class SmoothTrajectoryModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

This modifier smoothens the particle motion by averaging the particle positions from several successive snapshots of a simulation trajectory.
It can be used to create smooth-looking animations from a relatively coarse sequence of simulation snapshots
and reduce fluctuations or thermal vibrations in particle trajectories.
See also the corresponding user manual page for this modifier.

Note: Make sure you insert this modifier at the beginning of a data pipeline, in particular before any other modifiers that 
delete or filter particles, because needs to see the complete particle system in order to perform the trajectory smoothing."""

    @property
    def minimum_image_convention(self) -> bool:
        """If this option is set, the modifier will automatically detect when particles cross a simulation box boundary in between two successive simulation frames and computes the unwrapped displacements correctly. You should leave this option activated unless the input particle coordinates are already in unwrapped form. 

:Default: ``True``"""
        ...

    @property
    def window_size(self) -> int:
        """Controls how many input animation frames to take into account when calculating the time-averaged particle coordinates. The modifier uses a sliding time window of the given size that is centered around the current animation time. A window size of 1 disables smoothing. 

:Default: ``1``"""
        ...

class SpatialBinningModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

This modifier maps the particles to a bin grid and applies a reduction operation (mean, sum, min, max, etc.) to some property of 
the particles located within each spatial bin. The modifier outputs a one-, two- or three-dimensional grid of field values. 
See also the corresponding user manual page for more information on this modifier. 

The :py:attr:`direction` parameter of the modifier selects the dimensionality of the bin grid and the 
spatial direction(s) along which the grid cells are oriented. The :py:attr:`bin_count` parameter controls the resolution
of the generated grid, which always covers the entire :py:class:`SimulationCell`.
Finally, you have to specify the input particle property which should be transferred to the grid cell by setting the modifier's
:py:attr:`property` field to the name of an existing particle property. 

If the dimensionality of the selected output grid is one-dimensional, then the modifier will generate a :py:class:`DataTable` object
containing the computed bin values along the selected spatial :py:attr:`direction`. The data table may later be retrieved from the 
:py:attr:`tables` dictionary of the pipeline's output :py:class:`DataCollection` 
under the look-up key ``'binning'``.

If the dimensionality of the selected output grid is two- or three-dimensional, then the modifier will generate a :py:class:`VoxelGrid` object.
The generated voxel grid may later be retrieved from the :py:attr:`grids` dictionary of the pipeline's output 
:py:class:`DataCollection` under the look-up key ``'binning'``.

Examples

The following example shows how to calculate the gradient of the ``Velocity.X`` field along the spatial Z-axis.
For this, we use the :py:attr:`first_derivative` option, which lets the modifier compute the first derivative of the 
data points using a finite differences scheme.

```python
  pipeline.modifiers.append(SpatialBinningModifier(
      property = 'Velocity.X',
      direction = SpatialBinningModifier.Direction.Z, 
      bin_count = 80,
      reduction_operation = SpatialBinningModifier.Operation.Mean,
      first_derivative = True
  ))
```

The output :py:class:`DataTable` can then be exported to an output file using OVITO's :py:func:`export_file`
function or printed to the console:

```python
  export_file(pipeline, 'output/velocity_profile.txt', 'txt/table', key='binning')
  data = pipeline.compute()
  print(data.tables['binning'].xy())
```

The following example demonstrates how to compute a three-dimensional :py:class:`VoxelGrid` of the particle number density.
Since the :py:class:`SpatialBinningModifier` always requires some input particle property, we first employ the 
:py:class:`ComputePropertyModifier` to give all particles a new property with the uniform value 1, which can then
serve as input property for the binning:

```python
  pipeline.modifiers.append(ComputePropertyModifier(expressions=['1'], output_property='Unity'))
  
  pipeline.modifiers.append(SpatialBinningModifier(
      property = 'Unity',
      direction = SpatialBinningModifier.Direction.XYZ, 
      bin_count = (100, 100, 100),
      reduction_operation = SpatialBinningModifier.Operation.SumVol
  ))
```

The resulting :py:class:`VoxelGrid` may now be exported to an output file, for example in the VTK format:

```python
  export_file(pipeline, 'output/density.vtk', 'vtk/grid', key='binning')
```

Or it can serve as input for subsequent modifiers in your data pipeline, for example the :py:class:`CreateIsosurfaceModifier`."""

    class Direction(enum.Enum):
        """AUTODOC_SKIP_MEMBER

Members:

  X

  Y

  Z

  XY

  XZ

  YZ

  XYZ"""
        X = enum.auto()
        Y = enum.auto()
        Z = enum.auto()
        XY = enum.auto()
        XZ = enum.auto()
        YZ = enum.auto()
        XYZ = enum.auto()

    class Operation(enum.Enum):
        """AUTODOC_SKIP_MEMBER

Members:

  Mean

  Sum

  SumVol

  Min

  Max"""
        Mean = enum.auto()
        Sum = enum.auto()
        SumVol = enum.auto()
        Min = enum.auto()
        Max = enum.auto()

    @builtins.property
    def bin_count(self) -> Tuple[int, ...]:
        """Specifies the number of bin cells to generate along each axis of the binning grid. You should assign a tuple containing one, two, or three positive integers to this parameter field, depending on the grid's dimensionality set by the :py:attr:`direction` parameter. 

Note that the entries in the tuple specify the number of bins along the grid's first, second, and third dimension and not along the spatial axes. For example, if the binning :py:attr:`direction` is ``Direction.YZ``, setting :py:attr:`bin_count` to ``(100, 50)`` will let the modifier generate a two-dimensional grid with 100 bins along the second simulation cell vector (spatial y-axis) and 50 bins along the third cell vector (z-axis) of the 3-dimensional simulation box. Examples:: 

   SpatialBinningModifier(direction=SpatialBinningModifier.Direction.Z, bin_count=100)
   SpatialBinningModifier(direction=SpatialBinningModifier.Direction.XZ, bin_count=(40, 80))
   SpatialBinningModifier(direction=SpatialBinningModifier.Direction.XYZ, bin_count=(80, 80, 80))


If you assign just a single number, or a tuple with fewer entries than required for the selected grid dimensionality, the bin count in any of the remaining grid dimensions will be implicitly set to 1. 

:Default: ``(50, 50, 20)``"""
        ...

    @builtins.property
    def direction(self) -> Direction:
        """Selects the alignment of the bins and the dimensionality of the grid. Possible values:

   * ``SpatialBinningModifier.Direction.X``
   * ``SpatialBinningModifier.Direction.Y``
   * ``SpatialBinningModifier.Direction.Z``
   * ``SpatialBinningModifier.Direction.XY``
   * ``SpatialBinningModifier.Direction.XZ``
   * ``SpatialBinningModifier.Direction.YZ``
   * ``SpatialBinningModifier.Direction.XYZ``

For modes ``X``, ``Y``, and ``Z``, the modifier will generate a one-dimensional grid with bins aligned perpendicular to the selected simulation cell vector. For modes ``XY``, ``XZ``, and ``YZ``, the modifier will generate a two-dimensional grid with bins aligned perpendicular to both selected simulation cell vectors (i.e. parallel to the third vector). In the last case (``XYZ``), the modifier generates a three-dimensional voxel grid. 

:Default: ``SpatialBinningModifier.Direction.X``"""
        ...

    @builtins.property
    def first_derivative(self) -> bool:
        """Set this to ``True`` to let the modifier numerically compute the first derivative of the binned data points using a finite differences approximation. This works only if binning is performed in a single :py:attr:`direction` (``Direction.X``, ``Direction.Y`` or ``Direction.Z``). 

:Default: ``False``"""
        ...

    @builtins.property
    def grid_vis(self) -> ovito.vis.VoxelGridVis:
        """The :py:class:`VoxelGridVis` element controlling the visual appearance of the 2d or 3d grid generated by the modifier in rendered images. The visual element is ignored if :py:attr:`direction` parameter is set to a 1-dimensional binning mode."""
        ...

    @builtins.property
    def only_selected(self) -> bool:
        """This option lets the modifier take into account only the currently selected particles. Unselected particles will be excluded from the binning process. You can use this option to restrict the calculation to a subset of particles. 

:Default: ``False``"""
        ...

    @builtins.property
    def property(self) -> str:
        """The name of the input particle :py:class:`Property` which the reduction operation should be applied to. This can be the name of one of the standard particle properties or of a user-defined particle property. 

If the input property is a vector property, a component name may be appended after a dot, e.g. ``"Velocity.X"``, to perform the reduction operation only on that specific vector component. The output will then be a scalar field. Otherwise, the reduction operation is applied to all vector components independently and the output will be a vector field or vector-valued function."""
        ...

    @builtins.property
    def reduction_operation(self) -> Operation:
        """Selects the reduction operation to be carried out. Supported parameter values are:

   * ``SpatialBinningModifier.Operation.Mean``
   * ``SpatialBinningModifier.Operation.Sum``
   * ``SpatialBinningModifier.Operation.SumVol``
   * ``SpatialBinningModifier.Operation.Min``
   * ``SpatialBinningModifier.Operation.Max``

The operation ``SumVol`` first computes the sum and then divides the result by the volume of the respective bin. It is intended to compute pressure (or stress) within each bin from the per-atom virial.

:Default: ``SpatialBinningModifier.Operation.Mean``"""
        ...

class SpatialCorrelationFunctionModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

This modifier calculates the spatial correlation function between two particle properties. See also the corresponding user manual page for this modifier. 

The algorithm uses the FFT to compute the convolution. It then computes a radial average in reciprocal and real space. This gives the correlation function up to half of the cell size. The modifier can additionally compute the short-ranged part of the correlation function from a direct summation over neighbors.

Usage example:

.. literalinclude:: ../example_snippets/correlation_function_modifier.py"""

    @property
    def apply_window(self) -> bool:
        """This flag controls whether non-periodic directions have a Hann window applied to them. Applying a window function is necessary to remove spurious oscillations and power-law scaling of the (implicit) rectangular window of the non-periodic domain. 

:Default: ``True``"""
        ...

    @property
    def direct_summation(self) -> bool:
        """Flag controlling whether the real-space correlation plot will show the result of a direct calculation of the correlation function, obtained by summing over neighbors. 

:Default: ``False``"""
        ...

    @property
    def grid_spacing(self) -> float:
        """Controls the approximate size of the FFT grid cell. The actual size is determined by the distance of the simulation cell faces which must contain an integer number of grid cells. 

:Default: ``3.0``"""
        ...

    @property
    def neighbor_bins(self) -> int:
        """This integer value controls the number of bins for the direct calculation of the real-space correlation function. 

:Default: ``50``"""
        ...

    @property
    def neighbor_cutoff(self) -> float:
        """This parameter determines the cutoff of the direct calculation of the real-space correlation function. 

:Default: ``5.0``"""
        ...

    @property
    def property1(self) -> str:
        """The name of the first input particle property for which to compute the correlation, P1. For vector properties a component name must be appended in the string, e.g. ``"Velocity.X"``. 

:Default: ``''``"""
        ...

    @property
    def property2(self) -> str:
        """The name of the second particle property for which to compute the correlation, P2. If this is the same as :py:attr:`property1`, then the modifier will compute the autocorrelation. 

:Default: ``''``"""
        ...

class TimeAveragingModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

This modifier can compute the time average of one or more time-dependent input quantities by sampling them over all frames of the loaded trajectory.
The input quantities to be averaged can be any time-varying attribute or :py:class:`DataTable` generated on a frame-by-frame basis by 
another modifier in the OVITO data pipeline. Or it can be per-element values, for example particle properties.
See also the corresponding user manual page for more information on this modifier. 

Averaging scalar quantities:

The following code example demonstrates how to use the :py:class:`TimeAveragingModifier` to calculate the mean value of
a scalar quantity that changes with simulation time. In this example, the :py:class:`CreateBondsModifier` is 
added to the pipeline to dynamically create bonds between the moving particles (thus, the number of created bonds will change with time). 
The modifier reports the number of bonds that have been created in the current simulation frame as an output attribute named ``'CreateBonds.num_bonds'``. 
This varying attribute is then selected as the input quantity to be averaged by the following :py:class:`TimeAveragingModifier`, 
which in turn outputs the time-averaged value it computes as a new attribute named ``'CreateBonds.num_bonds (Average)'``. 
This value can be retrieved from the :py:class:`DataCollection` produced by `Pipeline.compute()`.
Note that is does not matter at which simulation time we evaluate the data pipeline -- the mean number of bonds is a static quantity and remains
constant over the entire trajectory.

```python
  pipeline = import_file('input/trajectory.dump')
  pipeline.modifiers.append(CreateBondsModifier(cutoff=2.9))
  pipeline.modifiers.append(TimeAveragingModifier(operate_on='attribute:CreateBonds.num_bonds'))
  data = pipeline.compute()
  print(data.attributes['CreateBonds.num_bonds (Average)'])
```

Averaging data tables:

Some analysis modifiers of OVITO output their results as :py:class:`DataTable` objects, which can represent
histograms or distributions functions. For example, the :py:class:`CoordinationAnalysisModifier` computes
the radial pair distribution function (RDF) of a particle system for the current simulation time and outputs it as a data table
named ``'coordination-rdf'``. We can have the :py:class:`TimeAveragingModifier` compute the time average of this varying 
distribution function over all frames of the loaded trajectory: 

```python
  pipeline = import_file('input/trajectory.dump')
  pipeline.modifiers.append(CoordinationAnalysisModifier(cutoff=6.0, number_of_bins=50))
  pipeline.modifiers.append(TimeAveragingModifier(operate_on='table:coordination-rdf'))
  data = pipeline.compute()
  print(data.tables['coordination-rdf[average]'].xy())
```

Note that, in case of data tables, the output table's :py:attr:`identifier` is given the suffix ``[average]``
by the :py:class:`TimeAveragingModifier`. 

An average of a :py:class:`DataTable` can only be computed if the table's x-axis :py:attr:`interval` does not vary with time and
the :py:attr:`x`-coordinates of the data points remain fixed. That's because the modifier simply averages the time-varying y-coordinate of each data point.
Thus, to generate a histogram :py:class:`DataTable` using the :py:class:`HistogramModifier` that is suitable for time averaging,  
you will have to activate the :py:attr:`HistogramModifier.fix_xrange` option.

Averaging properties:

The modifier can time-average properties that belong to a :py:class:`Particles` object, :py:class:`VoxelGrid`, 
or other type of :py:class:`PropertyContainer`. When setting the :py:attr:`operate_on` field, you need to specify 
the container's identifier and the name of the property to average:

```python
  pipeline.modifiers.append(TimeAveragingModifier(operate_on='property:particles/Coordination'))
  data = pipeline.compute()
  print(data.particles['Coordination Average'][...])
```

Note that the output :py:attr:`Property` is given the suffix ``'Average'`` by the :py:class:`TimeAveragingModifier`."""

    @property
    def interval(self) -> Optional[Tuple[int, int]]:
        """The animation frame interval over which the input trajectory is sampled to compute the average. You can set this to a pair of integers specifying the first and the last frame of the averaging interval; or assign ``None`` to let the modifier compute the average over the entire trajectory. 

For example, to restrict the average to the second half of the loaded simulation trajectory, you can specify the frame interval based on the `FileSource.num_frames` value: 

```python
  modifier.interval = (pipeline.source.num_frames//2, pipeline.source.num_frames-1)
```

:Default: ``None``"""
        ...

    @property
    def operate_on(self) -> str:
        """Selects the input quantity to be averaged by this modifier. Supported values for this field are: 

  * ``'attribute:<NAME>'``
  * ``'table:<ID>'``
  * ``'property:<CONTAINER>/<PROPERTY>'``


Here, ``<NAME>`` refers to the name of a global attribute to be averaged. ``<ID>`` is the :py:attr:`identifier` of the :py:class:`DataTable` to be averaged, ``<CONTAINER>`` is the :py:attr:`identifier` of a :py:class:`PropertyContainer` and ``<PROPERTY>`` the :py:attr:`name` of the :py:class:`Property` in that container, which should be averaged. Note that the :py:class:`Particles` property container has the standard identifier ``'particles'``. Its :py:class:`Bonds` child container is referenced by the hierarchical identifier ``'particles/bonds'``. 

Furthermore, it is possible to let the modifier average multiple input quantities in one pass by specifying a list of input references of the kind described above. The following code demonstrates how to compute the time averages of two global attributes: 

```python
  pipeline.modifiers.append(TimeAveragingModifier(
      operate_on = ('attribute:CommonNeighborAnalysis.counts.FCC', 
                    'attribute:CommonNeighborAnalysis.counts.BCC')
  ))
  data = pipeline.compute()
  print(data.attributes['CommonNeighborAnalysis.counts.FCC (Average)'])
  print(data.attributes['CommonNeighborAnalysis.counts.BCC (Average)'])
```

:Default: ``''``"""
        ...

    @property
    def sampling_frequency(self) -> int:
        """Animation step interval at which the quantity to be averaged is sampled from the input trajectory. You can set this to a larger value to perform a coarser sampling and reduce the total number of trajectory frames that need to be loaded into memory. 

:Default: ``1``"""
        ...

class TimeSeriesModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

This modifier samples a varying input quantity computed by the data pipeline over all frames of the loaded trajectory
to produce a time series, which can then be plotted to visualize the time evolution of the quantity.
See also the corresponding user manual page for more information on this modifier. 

The modifier takes one or more global attributes as input, samples their values over the simulation trajectory, 
and outputs the generated time series as a new :py:class:`DataTable` with the identifier ``time-series``. 

```python
  pipeline = import_file('input/trajectory.dump')
  pipeline.modifiers.append(ConstructSurfaceModifier(radius = 1.9))
  pipeline.modifiers.append(TimeSeriesModifier(operate_on = 'ConstructSurfaceMesh.surface_area'))
  data = pipeline.compute()
  print(data.tables['time-series'].xy())
```

This code samples the value of the global attribute ``ConstructSurfaceMesh.surface_area``, which is computed by the :py:class:`ConstructSurfaceModifier`
for each frame of the loaded simulation trajectory. The result is a static :py:class:`DataTable` with the number of rows equal to the number
of trajectory frames, which is inserted by the :py:class:`TimeSeriesModifier` into the pipeline's output data collection.

Note that you do not need the :py:class:`TimeSeriesModifier` in order to output a global attribute to a text file as a function of time.
This can be accomplished simply by calling the :py:func:`export_file` function, which can automatically sample an attribute's value 
and write it to the output file one line per frame:

```python
  pipeline = import_file('input/trajectory.dump')
  pipeline.modifiers.append(ConstructSurfaceModifier(radius = 1.9))
  export_file(pipeline, 'output/surface_area.txt', 
      format='txt/attr', 
      columns=["SourceFrame", "ConstructSurfaceMesh.surface_area"],
      multiple_frames=True)
```"""

    @property
    def interval(self) -> Optional[Tuple[int, int]]:
        """The interval of animation frames over which the input trajectory is sampled to generate the time series. You can set this to a pair of integers specifying the first and the last frame of the sampling interval; or assign ``None`` to let the modifier generate the time series over the entire trajectory. 

For example, to restrict the time series to the first half of the loaded simulation trajectory, you can specify the frame interval based on the `FileSource.num_frames` value: 

```python
  modifier.interval = (0, pipeline.source.num_frames//2)
```

:Default: ``None``"""
        ...

    @property
    def operate_on(self) -> str:
        """Specifies the name of the input global attribute to be sampled by the modifier. The attribute must be generated by the trajectory file reader or dynamically computed by a modifier in the upstream data pipeline. 

You can also specify several global attributes as a Python tuple of strings. Then the modifier will simultaneously sample each of the input attributes and produce a :py:class:`DataTable` with a vector data column containing the set of time series. 

```python
  pipeline.modifiers.append(TimeSeriesModifier(
      operate_on = ('ConstructSurfaceMesh.surface_area',
                    'ConstructSurfaceMesh.filled_volume')))
  data = pipeline.compute()
  series = data.tables['time-series'].y
  print("Surface area:", series[:,0])
  print("Solid volume:", series[:,1])
```

:Default: ``''``"""
        ...

    @property
    def sampling_frequency(self) -> int:
        """Animation interval at which the attribute(s) is sampled from the input trajectory. You can set this to a larger value to perform a coarser sampling and reduce the total number of trajectory frames that need to be loaded/computed. 

:Default: ``1``"""
        ...

    @property
    def time_attribute(self) -> str:
        """The name of a global attribute that should be queried by the modifier to obtain the time-axis coordinates of the data samples. If set to an empty string (the default), the modifier uses the animation frame number as time axis. You can alternatively tell the modifier to use the ``Timestep`` or ``Time`` global attributes, which are created by some file readers based on the information found in the input trajectory, in order to plot the selected input attribute as a function of  MD timestep number or physical simulation time. 

:Default: ``''``"""
        ...

class UnwrapTrajectoriesModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

This modifier determines when particles cross through the periodic boundaries of the simulation cell and unwraps the particle coordinates in order to make the trajectories continuous. As a result of this operation, particle trajectories will no longer fold back into the simulation cell and instead lead outside the cell. 

Note that, to unwrap the particle coordinates, the modifier may have to step through all frames of the input simulation trajectory to detect jumps in the trajectories. This will not be necessary, however, if the ``Periodic Image`` particle property has been loaded from the input simulation file, because then the modifier can directly use this information to unwrap the particle coordinates. 

.. literalinclude:: ../example_snippets/unwrap_trajectories.py"""
    pass

class VoroTopModifier(StructureIdentificationModifier):
    """Base: :py:class:`ovito.modifiers.StructureIdentificationModifier`

"This modifier uses the Voronoi cell topology of particles to characterize their local structural environments
"[`Lazar, Han, Srolovitz, PNAS 112:43 (2015) <http://dx.doi.org/10.1073/pnas.1505788112>`__].
See the corresponding user manual page
for more information on this modifier. Note that this modifier inherits several important parameter fields 
from its :py:class:`StructureIdentificationModifier` base class.

The Voronoi cell of a particle is the region of space closer to it than to any other particle. 
The topology of the Voronoi cell is the manner in which its faces are connected, and describes 
the manner in which a particle's neighbors are arranged.  The topology of a Voronoi cell can be 
completely described in a vector of integers called a *Weinberg vector* 
[`Weinberg, IEEE Trans. Circuit Theory 13:2 (1966) <http://dx.doi.org/10.1109/TCT.1966.1082573>`__]. 

This modifier requires loading a *filter*, which specifies structure types and associated 
Weinberg vectors.  Filters for several common structures can be obtained from the 
`VoroTop <https://www.vorotop.org/download.html>`__ website. 
The modifier calculates the Voronoi cell topology of each particle, uses the provided 
filter to determine the structure type, and stores the results in the ``Structure Type`` particle property. 
This allows the user to subsequently select particles  of a certain structural type, e.g. by using the 
:py:class:`SelectTypeModifier`. 

This method is well-suited for analyzing finite-temperature systems, including those heated to 
their bulk melting temperatures. This robust behavior relieves the need to quench a sample 
(such as by energy minimization) prior to analysis. 
Further information about the Voronoi topology approach for local structure analysis, as well 
as additional filters, can be found on the `VoroTop webpage <https://www.vorotop.org/>`__."""

    @property
    def filter_file(self) -> str:
        """Path to the filter definition file used by the modifier. Filters files are available from the `VoroTop <https://www.vorotop.org/download.html>`__ website. 

:Default: ``''``"""
        ...

    @property
    def use_radii(self) -> bool:
        """If ``True``, the modifier computes the poly-disperse Voronoi tessellation, which takes into account the radii of particles. Otherwise a mono-disperse Voronoi tessellation is computed, which is independent of the particle sizes. 

:Default: ``False``"""
        ...

class VoronoiAnalysisModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

Computes the atomic volumes and coordination numbers using a Voronoi tessellation of the particle system.
See the corresponding user manual page for more information.
See :ref:`example_compute_voronoi_indices` for a code example demonstrating the use of this modifier.

Inputs:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Particle properties
      -
    * - ``Position``
      - The coordinates of the input particles.
    * - ``Radius``
      - Per-particle radii are used if :py:attr:`use_radii` is set to ``True``.
    * - ``Particle Type``
      - Per-type radii are used if :py:attr:`use_radii` is set to ``True`` and ``Radius`` property is not present.
    * - ``Selection``
      - The selection state of the input particles. Only needed if :py:attr:`only_selected` is set to ``True``.

Outputs:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Particle properties
      -
    * - ``Atomic Volume``
      - The computed volume of each particle's Voronoi polyhedron.
    * - ``Coordination``
      - The number of faces of each particle's Voronoi polyhedron.
    * - ``Voronoi Index``
      - The index vector of each Voronoi polyhedron. Only computed if :py:attr:`compute_indices` is set to ``True``.
    * - ``Max Face Order``
      - The maximum number of edges in any face of a particle's Voronoi polyhedron. Only if :py:attr:`compute_indices` is set to ``True``.

.. list-table::
    :widths: auto
    :header-rows: 1

    * - Global attributes
      -
    * - ``Voronoi.max_face_order``
      - Indicates the maximum number of edges of any face in the computed Voronoi tessellation (ignoring edges and faces that fall below the area/length thresholds).

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Bond properties
      -
    * - ``Topology``
      - The connectivity information of newly created :py:class:`Bonds` (one bond for each Voronoi face). Only if :py:attr:`generate_bonds` is set to ``True``."""

    @property
    def bonds_vis(self) -> ovito.vis.BondsVis:
        """The :py:class:`BondsVis` object controlling the visual appearance of the bonds generated by the modifier if :py:attr:`generate_bonds` is set to ``True``."""
        ...

    @property
    def compute_indices(self) -> bool:
        """If ``True``, the modifier calculates the Voronoi indices of particles. The modifier stores the computed indices in a vector particle property named ``Voronoi Index``. The *i*-th component of this property will contain the number of faces of the Voronoi cell that have *i* edges. Thus, the first two components of the per-particle vector will always be zero, because the minimum number of edges a polygon can have is three. 

:Default: ``False``"""
        ...

    @property
    def edge_threshold(self) -> float:
        """Specifies the minimum length an edge must have to be considered in the Voronoi index calculation. Edges that are shorter than this threshold will be ignored when counting the number of edges of a Voronoi face. The threshold parameter is an absolute value in units of length of your input data. 

:Default: ``0.0``"""
        ...

    @property
    def face_threshold(self) -> float:
        """Specifies a minimum area for individual Voronoi faces in terms of an absolute area. The algorithm will ignore any face of a Voronoi polyhedron with an area smaller than this threshold when computing the coordination number and the Voronoi index of a particle. The threshold parameter is an absolute area given in units of length squared (in whatever units your input data is given). 

Note that this absolute area threshold and the :py:attr:`relative_face_threshold` are applied simultaneously. 

:Default: ``0.0``"""
        ...

    @property
    def generate_bonds(self) -> bool:
        """Controls whether the modifier outputs the nearest neighbor bonds. The modifier will generate a bond for every pair of adjacent atoms that share a face of the Voronoi tessellation. No bond will be created if the face's area is below the :py:attr:`face_threshold` or if the face has less than three edges that are longer than the :py:attr:`edge_threshold`.

:Default: ``False``"""
        ...

    @property
    def generate_polyhedra(self) -> bool:
        """Controls whether the modifier outputs the computed Voronoi cells as a polyhedral :py:class:`SurfaceMesh` object. 

:Default: ``False``"""
        ...

    @property
    def mesh_vis(self) -> ovito.vis.SurfaceMeshVis:
        """The :py:class:`SurfaceMeshVis` object controlling the visual appearance of the polyhedral mesh generated by the modifier if :py:attr:`generate_polyhedra` is set to ``True``."""
        ...

    @property
    def only_selected(self) -> bool:
        """Lets the modifier perform the analysis only for selected particles. Particles that are currently not selected will be treated as if they did not exist.

:Default: ``False``"""
        ...

    @property
    def relative_face_threshold(self) -> float:
        """Specifies a minimum area for Voronoi faces in terms of a fraction of total area of the Voronoi polyhedron surface. The algorithm will ignore any face of a Voronoi polyhedron with an area smaller than this threshold when computing the coordination number and the Voronoi index of particles. The threshold parameter is specified as a fraction of the total surface area of the Voronoi polyhedron the faces belong to. For example, a threshold value of 0.01 would remove those faces from the analysis with an area less than 1% of the total area of the polyhedron surface. 

Note that this relative threshold and the absolute :py:attr:`face_threshold` are applied simultaneously. 

:Default: ``0.0``"""
        ...

    @property
    def use_radii(self) -> bool:
        """If ``True``, the modifier computes the poly-disperse Voronoi tessellation, which takes into account the radii of particles. Otherwise a mono-disperse Voronoi tessellation is computed, which is independent of the particle sizes. 

:Default: ``False``"""
        ...

class WignerSeitzAnalysisModifier(ovito.pipeline.ReferenceConfigurationModifier):
    """Base: :py:class:`ovito.pipeline.ReferenceConfigurationModifier`

Performs the Wigner-Seitz cell analysis to identify point defects in a crystal.
See the corresponding user manual page for more information.

Defects are identified with respect to a perfect reference crystal configuration.
By default, frame 0 of the current simulation sequence is used as reference configuration.
The modifier inherits from the :py:class:`ReferenceConfigurationModifier` class, which provides
further settings that control the definition of the reference configuration.

Outputs:

.. list-table::
    :widths: 20 80
    :header-rows: 1

    * - Particle properties
      -
    * - ``Occupancy``
      - The computed site occupation numbers, one for each particle in the reference configuration.

.. list-table::
    :widths: auto
    :header-rows: 1

    * - Global attributes
      -
    * - ``WignerSeitz.vacancy_count``
      - The total number of vacant sites (having ``Occupancy`` == 0).
    * - ``WignerSeitz.interstitial_count``
      - The total number of of interstitial atoms. This is equal to the sum of occupancy numbers of all non-empty sites minus the number of non-empty sites.

Example:

The ``Occupancy`` particle property generated by the Wigner-Seitz algorithm allows to select specific types of point defects, e.g.
antisites, using OVITO's selection tools. One option is to use the :py:class:`ExpressionSelectionModifier` to pick
sites having a certain occupancy. The following script exemplarily demonstrates the use of a custom :py:class:`PythonScriptModifier` to
select and count A-sites occupied by B-atoms in a binary system with two atom types (A=1 and B=2).

.. literalinclude:: ../example_snippets/wigner_seitz_example.py"""

    @property
    def output_displaced(self) -> bool:
        """Specifies whether the modifier should output the atoms of the current configuration or replace them with the sites from the reference configuration. 

By default, the modifier throws away all atoms of the current configuration and outputs the atomic sites from the reference configuration instead. Thus, in this default mode, you will obtain information about how many atoms occupy each site from the reference configuration. If, however, you are more interested in visualizing the physical atoms that are currently occupying the sites (instead of the sites being occupied), then you should activate this modifier option. If set to true, the modifier will maintain the input atoms from the current configuration. The ``Occupancy`` property generated by the modifier will now pertain to the atoms instead of the sites, with the following new meaning: The occupancy number now counts how many atoms in total are occupying the same site as the atom the property refers to does. Furthermore, the modifier will in this mode output another property named ``Site Type``, which reports for each atom the type of the reference site it was assigned to by the W-S algorithm. 

:Default: ``False``"""
        ...

    @property
    def per_type_occupancies(self) -> bool:
        """A flag controlling whether the modifier should compute occupancy numbers on a per-particle-type basis. 

If false, only the total occupancy number is computed for each reference site, which counts the number of particles that occupy the site irrespective of their types. If true, then the ``Occupancy`` property computed by the modifier becomes a vector property with *N* components, where *N* is the number of particle types defined in the system. Each component of the ``Occupancy`` property counts the number of particles of the corresponding type that occupy the site. For example, the property component ``Occupancy.1`` contains the number of particles of type 1 that occupy a site. 

:Default: ``False``"""
        ...

class WrapPeriodicImagesModifier(ovito.pipeline.Modifier):
    """Base: :py:class:`ovito.pipeline.Modifier`

This modifier maps particles located outside of the simulation cell back into the cell by "wrapping" their coordinates 
around at the periodic boundaries of the :py:class:`SimulationCell`. 
See also the corresponding user manual page for this modifier. 
This modifier has no configurable parameters."""
    pass