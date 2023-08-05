"""This module contains classes related to data visualization and rendering.

Rendering:

  * :py:class:`Viewport`

Rendering engines:

  * :py:class:`OpenGLRenderer`
  * :py:class:`TachyonRenderer`
  * :py:class:`OSPRayRenderer`

Data visualization elements:

  * :py:class:`DataVis` (base class for all visual elements)
  * :py:class:`BondsVis`
  * :py:class:`DislocationVis`
  * :py:class:`ParticlesVis`
  * :py:class:`SimulationCellVis`
  * :py:class:`SurfaceMeshVis`
  * :py:class:`TrajectoryVis`
  * :py:class:`TriangleMeshVis`
  * :py:class:`VectorVis`
  * :py:class:`VoxelGridVis`

Viewport overlays:

  * :py:class:`ViewportOverlay` (base class for all overlay types)
  * :py:class:`ColorLegendOverlay`
  * :py:class:`CoordinateTripodOverlay`
  * :py:class:`PythonViewportOverlay`
  * :py:class:`TextLabelOverlay`"""
__all__ = ['Viewport', 'OpenGLRenderer', 'DataVis', 'CoordinateTripodOverlay', 'PythonViewportOverlay', 'TextLabelOverlay', 'ViewportOverlay', 'TriangleMeshVis', 'SimulationCellVis', 'ColorLegendOverlay', 'SurfaceMeshVis', 'VoxelGridVis', 'ParticlesVis', 'VectorVis', 'BondsVis', 'TrajectoryVis', 'DislocationVis', 'OSPRayRenderer', 'TachyonRenderer']
from typing import Tuple, Optional, Any, Union, Iterator, Mapping, MutableMapping, Sequence, MutableSequence, Callable
import enum
import builtins
import numpy.typing
import ovito
import ovito.modifiers
import ovito.pipeline
import PySide6.QtCore
import PySide6.QtGui
import PySide6.QtWidgets
Color = Tuple[float, float, float]
Vector3 = Tuple[float, float, float]

class OpenGLRenderer:
    """The standard OpenGL-based renderer.

This is the default built-in rendering engine that is also used by OVITO to render the contents of the interactive viewports. Since it accelerates the generation of images by using the computer's graphics hardware, it is very fast. See the corresponding user manual page for more information on this rendering engine. 

Note that this renderer requires OpenGL graphics support, and Python scripts may be running in environments where it is not available. A typical example for such situations are remote SSH connections, which can prevent OVITO from accessing the X window and OpenGL systems. In this case, the OpenGL renderer will refuse to work and you have to use one of the software-based rendering engines instead. See the :py:meth:`Viewport.render_image` method."""

    @property
    def antialiasing_level(self) -> int:
        """A positive integer controlling the level of supersampling. If 1, no supersampling is performed. For larger values, the image in rendered at a higher resolution and then scaled back to the output size to reduce aliasing artifacts.

:Default: ``3``"""
        ...

class TachyonRenderer:
    """This is one of the software-based rendering backends of OVITO. Tachyon is an open-source raytracing engine integrated into OVITO.

An instance of this class can be passed to the :py:meth:`Viewport.render_image` or :py:meth:`Viewport.render_anim` methods. 

Tachyon can render scenes with ambient occlusion lighting, semi-transparent objects, and depth-of-field focal blur. See the corresponding user manual page for more information on this rendering backend."""

    @property
    def ambient_occlusion(self) -> bool:
        """Enables ambient occlusion shading. Enabling this lighting technique mimics some of the effects that occur under conditions of omnidirectional diffuse illumination, e.g. outdoors on an overcast day.

:Default: ``True``"""
        ...

    @property
    def ambient_occlusion_brightness(self) -> float:
        """Controls the brightness of the sky light source used for ambient occlusion.

:Default: ``0.8``"""
        ...

    @property
    def ambient_occlusion_samples(self) -> int:
        """Ambient occlusion is implemented using a Monte Carlo technique. This parameters controls the number of samples to compute. A higher sample count leads to a more even shading, but requires more computation time.

:Default: ``12``"""
        ...

    @property
    def antialiasing(self) -> bool:
        """Enables supersampling to reduce aliasing effects.

:Default: ``True``"""
        ...

    @property
    def antialiasing_samples(self) -> int:
        """The number of supersampling rays to generate per pixel to reduce aliasing effects.

:Default: ``12``"""
        ...

    @property
    def aperture(self) -> float:
        """Controls the aperture of the camera, which is used for depth-of-field rendering.

:Default: ``0.01``"""
        ...

    @property
    def depth_of_field(self) -> bool:
        """This flag enables depth-of-field rendering.

:Default: ``False``"""
        ...

    @property
    def direct_light(self) -> bool:
        """Enables the parallel light source, which is positioned at an angle behind the camera.

:Default: ``True``"""
        ...

    @property
    def direct_light_intensity(self) -> float:
        """Controls the brightness of the directional light source.

:Default: ``0.9``"""
        ...

    @property
    def focal_length(self) -> float:
        """Controls the focal length of the camera, which is used for depth-of-field rendering.

:Default: ``40.0``"""
        ...

    @property
    def shadows(self) -> bool:
        """Enables cast shadows for the directional light source.

:Default: ``True``"""
        ...

class OSPRayRenderer:
    """This is one of the software-based rendering backends of OVITO, which can generate images with higher fidelity than the standard :py:class:`OpenGLRenderer`. Typically, you create an instance of this class and pass it to the :py:meth:`Viewport.render_image` or :py:meth:`Viewport.render_anim` methods. 

OSPRay can render scenes with ambient occlusion lighting, semi-transparent objects, and depth-of-field focal blur. For technical details of the supported rendering algorithms and parameters, see the `www.ospray.org <https://www.ospray.org>`__ website. See also the corresponding user manual page for more information on this rendering engine."""

    @property
    def ambient_brightness(self) -> float:
        """Controls the radiance of the ambient light. 

:Default: ``0.8``"""
        ...

    @property
    def ambient_light_enabled(self) -> bool:
        """Enables the ambient light, which surrounds the scene and illuminates it from infinity with constant radiance. 

:Default: ``True``"""
        ...

    @property
    def aperture(self) -> float:
        """The aperture radius controls how blurred objects will appear that are out of focus if :py:attr:`dof_enabled` is set. 

:Default: ``0.5``"""
        ...

    @property
    def denoising_enabled(self) -> bool:
        """Enables the application of a denoising filter to the rendered image to reduce Monte Carlo noise inherent to stochastic ray tracing methods like path tracing. 

:Default: ``True``"""
        ...

    @property
    def direct_light_angular_diameter(self) -> float:
        """Specifies the apparent size (angle in radians) of the default directional light source. Setting the angular diameter to a value greater than zero yields soft shadow. 

:Default: ``numpy.radians(10.0)``"""
        ...

    @property
    def direct_light_enabled(self) -> bool:
        """Enables the default directional light source that is positioned behind the camera and is pointing roughly along the viewing direction. The brightness of the light source is controlled by the :py:attr:`direct_light_intensity` parameter. 

:Default: ``True``"""
        ...

    @property
    def direct_light_intensity(self) -> float:
        """The intensity of the default directional light source. The light source must be enabled by setting :py:attr:`direct_light_enabled`. 

:Default: ``1.0``"""
        ...

    @property
    def dof_enabled(self) -> bool:
        """Enables the depth-of-field effect (focal blur). Only objects exactly at the distance from the camera specified by the :py:attr:`focal_length` will appear sharp when depth-of-field rendering is enabled. Objects closer to or further from the camera will appear blurred. The strength of the effect is controlled by the :py:attr:`aperture` parameter. 

:Default: ``False``"""
        ...

    @property
    def focal_length(self) -> float:
        """Only objects exactly at this distance from the camera will appear sharp when :py:attr:`dof_enabled` is set. Objects closer to or further from the camera will appear blurred. 

:Default: ``40.0``"""
        ...

    @property
    def material_shininess(self) -> float:
        """Specular Phong exponent value for the default material. Usually in the range between 2.0 and 10,000. 

:Default: ``10.0``"""
        ...

    @property
    def material_specular_brightness(self) -> float:
        """Controls the specular reflectivity of the default material. 

:Default: ``0.02``"""
        ...

    @property
    def max_ray_recursion(self) -> int:
        """The maximum number of recursion steps during raytracing. Normally, 1 or 2 is enough, but when rendering semi-transparent objects, a larger recursion depth is needed. 

:Default: ``10``"""
        ...

    @property
    def refinement_iterations(self) -> int:
        """The OSPRay renderer supports a feature called adaptive accumulation, which is a progressive rendering method. During each rendering pass, the rendered image is progressively refined. This parameter controls the number of iterations until the refinement stops. 

:Default: ``4``"""
        ...

    @property
    def samples_per_pixel(self) -> int:
        """The number of raytracing samples computed per pixel. Larger values can help to reduce aliasing artifacts. 

:Default: ``2``"""
        ...

    @property
    def sky_albedo(self) -> float:
        """Controls the ground reflectance affecting the sky-sun light source. The light source must be enabled first by setting :py:attr:`sky_light_enabled`. Valid parameter range is [0.0 - 1.0].

:Default: ``0.3``"""
        ...

    @property
    def sky_brightness(self) -> float:
        """The intensity of the sky-sun light source. The light source must be enabled first by setting :py:attr:`sky_light_enabled`. 

:Default: ``2.0``"""
        ...

    @property
    def sky_light_enabled(self) -> bool:
        """Enables the sky/sun light source that mimics the light coming from the sky and the sun in an outdoor scene. The brightness of the sky is controlled by the :py:attr:`sky_brightness` parameter. 

:Default: ``False``"""
        ...

    @property
    def sky_turbidity(self) -> float:
        """Controls atmospheric turbidity due to particles affecting the sky-sun light source. The light source must be enabled first by setting :py:attr:`sky_light_enabled`. Valid parameter range is [1.0 - 10.0].

:Default: ``3.0``"""
        ...
Renderer = Union[OpenGLRenderer, TachyonRenderer, OSPRayRenderer]

class ViewportOverlay:
    """Abstract base class for viewport :py:attr:`overlays` and :py:attr:`underlays`, which render two-dimensional graphics on top of (or behind) the three-dimensional scene. Examples are :py:class:`CoordinateTripodOverlay`, :py:class:`TextLabelOverlay` and :py:class:`ColorLegendOverlay`. You can also implement your own viewport overlay in Python by using the :py:class:`PythonViewportOverlay` class."""

    @property
    def enabled(self) -> bool:
        """Controls whether the overlay gets rendered. An overlay can be hidden by setting its :py:attr:`enabled` property to ``False``. 

:Default: ``True``"""
        ...

class ColorLegendOverlay(ViewportOverlay):
    """Base: :py:class:`ovito.vis.ViewportOverlay`

This viewport layer renders a color legend over the image, which defines the meaning of the colors of depicted objects.
You can attach an instance of this :py:class:`ViewportOverlay` to a :py:class:`Viewport` by adding it to the viewport's 
:py:attr:`overlays` or :py:attr:`underlays` collections.

The :py:class:`ColorLegendOverlay` can render the color spectrum of a :py:class:`ColorCodingModifier` on top of the three-dimensional 
scene, with text labels indicating the range of corresponding numeric values. For this, the source color coding modifier must be specified by setting the :py:attr:`.modifier` field
of the viewport layer:

```python
  from ovito.io import import_file
  from ovito.vis import ColorLegendOverlay, Viewport
  from ovito.modifiers import ColorCodingModifier
  from ovito.qt_compat import QtCore
  
  # Prepare a data pipeline containing a ColorCodingModifier:
  pipeline = import_file("input/simulation.dump")
  color_mod = ColorCodingModifier(property = 'peatom')
  pipeline.modifiers.append(color_mod)
  pipeline.add_to_scene()
  
  # Configure the viewport overlay and link it to the ColorCodingModifier:
  overlay = ColorLegendOverlay(
      modifier = color_mod,
      title = 'Potential energy per atom:',
      alignment = QtCore.Qt.AlignLeft ^ QtCore.Qt.AlignTop,
      orientation = QtCore.Qt.Vertical,
      offset_y = -0.04,
      font_size = 0.12,
      format_string = '%.2f eV')
  
  # Attach the overlay to a Viewport, which is going to be used for image rendering:
  viewport = Viewport(type = Viewport.Type.Top)
  viewport.overlays.append(overlay)
```

Alternatively, the viewport layer can render the discrete colors of a typed property, i.e. a :py:class:`Property` object with attached
:py:class:`ElementType` instances. This allows you to include the particle type names and their corresponding colors in a rendered image, or the structural 
types identified by the :py:class:`PolyhedralTemplateMatchingModifier`, for example:

```python
  viewport.overlays.append(ColorLegendOverlay(property = 'particles/Particle Type'))
  viewport.overlays.append(ColorLegendOverlay(property = 'particles/Structure Type'))
  viewport.overlays.append(ColorLegendOverlay(property = 'particles/bonds/Bond Type'))
```

Here, the :py:attr:`.property` parameter specifies the path to the :py:class:`Property` object whose discrete :py:attr:`types` the
color legend should visualize. The path string consists of the :py:attr:`identifier` of each nested :py:class:`DataObject`
container separated by slashes. In case there are multiple data pipelines in the current scene, the color legend layer will use the first one yielding a 
:py:class:`DataCollection` containing the denoted property data path."""

    @builtins.property
    def alignment(self) -> PySide6.QtCore.Qt.Alignment:
        """Selects the corner of the viewport where the color bar is displayed (anchor position). This must be a valid `Qt.AlignmentFlag value <https://doc.qt.io/qtforpython/PySide6/QtCore/Qt.html#PySide6.QtCore.PySide6.QtCore.Qt.AlignmentFlag>`__ as shown in the code example above. 

:Default: ``QtCore.Qt.AlignHCenter ^ QtCore.Qt.AlignBottom``"""
        ...

    @builtins.property
    def aspect_ratio(self) -> float:
        """The aspect ratio of the color bar. Larger values make it more narrow. 

:Default: ``8.0``"""
        ...

    @builtins.property
    def border_color(self) -> Color:
        """The line color of the border painted around the color map. This is used only if :py:attr:`border_enabled` is set.

:Default: ``(0.0, 0.0, 0.0)``"""
        ...

    @builtins.property
    def border_enabled(self) -> bool:
        """Enables the painting of a border line around color map. 

:Default: ``False``"""
        ...

    @builtins.property
    def font(self) -> str:
        """A string with comma-separated parameter values describing the font to be used for rendering the text labels of the viewport layer. The string must follow the specific form understood by the `QFont.fromString() <https://doc.qt.io/qtforpython/PySide6/QtGui/QFont.html#PySide2.QtGui.PySide2.QtGui.QFont.fromString>`__ method, for example ``'Arial,10,-1,5,75,0,0,0,0,0,Bold'``. 

Note that the font size parameter (10 in the example specification above) will be ignored by the viewport layer, because the size of text labels is already controlled by the :py:attr:`font_size` parameter."""
        ...

    @builtins.property
    def font_size(self) -> float:
        """The relative size of the font used for text labels.

:Default: ``0.1``"""
        ...

    @builtins.property
    def format_string(self) -> str:
        """The format string used with the `sprintf() <https://en.cppreference.com/w/cpp/io/c/fprintf>`__ function to generate the text representation of floating-point values. You can change this format string to control the number of decimal places or add units to the numeric values, for example. 

:Default: ``'%g'``"""
        ...

    @builtins.property
    def label1(self) -> str:
        """Sets the text string displayed at the upper end of the bar. If empty, the :py:attr:`end_value` of the :py:class:`ColorCodingModifier` is used. 

:Default: ``''``"""
        ...

    @builtins.property
    def label2(self) -> str:
        """Sets the text string displayed at the lower end of the bar. If empty, the :py:attr:`start_value` of the :py:class:`ColorCodingModifier` is used. 

:Default: ``''``"""
        ...

    @builtins.property
    def legend_size(self) -> float:
        """Controls the overall size of the color bar relative to the output image size. 

:Default: ``0.3``"""
        ...

    @builtins.property
    def modifier(self) -> Optional[ovito.modifiers.ColorCodingModifier]:
        """The :py:class:`ColorCodingModifier` for which the color legend should be rendered."""
        ...

    @builtins.property
    def offset_x(self) -> float:
        """This parameter allows to displace the color bar horizontally from its anchor position. The offset is specified as a fraction of the output image width.

:Default: ``0.0``"""
        ...

    @builtins.property
    def offset_y(self) -> float:
        """This parameter allows to displace the color bar vertically from its anchor position. The offset is specified as a fraction of the output image height.

:Default: ``0.0``"""
        ...

    @builtins.property
    def orientation(self) -> PySide6.QtCore.Orientation:
        """Selects the orientation of the color bar. This must be a valid `Qt.Orientation value <https://doc.qt.io/qtforpython/PySide6/QtCore/Qt.html#PySide6.QtCore.PySide6.QtCore.Qt.Orientation>`__ as shown in the code example above. 

:Default: ``QtCore.Qt.Horizontal``"""
        ...

    @builtins.property
    def outline_color(self) -> Color:
        """The text outline color. This is used only if :py:attr:`outline_enabled` is set.

:Default: ``(1.0, 1.0, 1.0)``"""
        ...

    @builtins.property
    def outline_enabled(self) -> bool:
        """Enables the painting of a font outline to make the text easier to read.

:Default: ``False``"""
        ...

    @builtins.property
    def text_color(self) -> Color:
        """The RGB color used for text labels.

:Default: ``(0.0, 0.0, 0.0)``"""
        ...

    @builtins.property
    def title(self) -> str:
        """The text displayed next to the color bar. If this string is empty, the title of the source :py:class:`Property` object is used instead. 

:Default: ``''``"""
        ...

    @builtins.property
    def property(self) -> str:
        """The data path of the typed :py:class:`Property` for which the color legend should be rendered. 

:Default: ``''``"""
        ...

class CoordinateTripodOverlay(ViewportOverlay):
    """Base: :py:class:`ovito.vis.ViewportOverlay`

Displays a coordinate tripod in rendered images. You can attach an instance of this class to a viewport by adding it to the viewport's :py:attr:`overlays` collection:

.. literalinclude:: ../example_snippets/coordinate_tripod_overlay.py"""

    class Style(enum.Enum):
        """AUTODOC_SKIP_MEMBER

Members:

  Flat

  Solid"""
        Flat = enum.auto()
        Solid = enum.auto()

    @property
    def alignment(self) -> PySide6.QtCore.Qt.Alignment:
        """Selects the corner of the viewport where the tripod is displayed. This must be a valid `Qt.AlignmentFlag value <https://doc.qt.io/qtforpython/PySide6/QtCore/Qt.html#PySide6.QtCore.PySide6.QtCore.Qt.AlignmentFlag>`__ value as shown in the example above.

:Default: ``QtCore.Qt.AlignLeft ^ QtCore.Qt.AlignBottom``"""
        ...

    @property
    def axis1_color(self) -> Color:
        """RGB display color of the first axis.

:Default: ``(1.0, 0.0, 0.0)``"""
        ...

    @property
    def axis1_dir(self) -> Vector3:
        """Vector specifying direction and length of first axis, expressed in the global Cartesian coordinate system.

:Default: ``(1.0, 0.0, 0.0)``"""
        ...

    @property
    def axis1_enabled(self) -> bool:
        """Enables the display of the first axis.

:Default: ``True``"""
        ...

    @property
    def axis1_label(self) -> str:
        """Text label for the first axis.

:Default: ``"x"``"""
        ...

    @property
    def axis2_color(self) -> Color:
        """RGB display color of the second axis.

:Default: ``(0.0, 0.8, 0.0)``"""
        ...

    @property
    def axis2_dir(self) -> Vector3:
        """Vector specifying direction and length of second axis, expressed in the global Cartesian coordinate system.

:Default: ``(0.0, 1.0, 0.0)``"""
        ...

    @property
    def axis2_enabled(self) -> bool:
        """Enables the display of the second axis.

:Default: ``True``"""
        ...

    @property
    def axis2_label(self) -> str:
        """Text label for the second axis.

:Default: ``"y"``"""
        ...

    @property
    def axis3_color(self) -> Color:
        """RGB display color of the third axis.

:Default: ``(0.2, 0.2, 1.0)``"""
        ...

    @property
    def axis3_dir(self) -> Vector3:
        """Vector specifying direction and length of third axis, expressed in the global Cartesian coordinate system.

:Default: ``(0.0, 0.0, 1.0)``"""
        ...

    @property
    def axis3_enabled(self) -> bool:
        """Enables the display of the third axis.

:Default: ``True``"""
        ...

    @property
    def axis3_label(self) -> str:
        """Text label for the third axis.

:Default: ``"z"``"""
        ...

    @property
    def axis4_color(self) -> Color:
        """RGB display color of the fourth axis.

:Default: ``(1.0, 0.0, 1.0)``"""
        ...

    @property
    def axis4_dir(self) -> Vector3:
        """Vector specifying direction and length of fourth axis, expressed in the global Cartesian coordinate system.

:Default: ``(0.7071, 0.7071, 0.0)``"""
        ...

    @property
    def axis4_enabled(self) -> bool:
        """Enables the display of the fourth axis.

:Default: ``False``"""
        ...

    @property
    def axis4_label(self) -> str:
        """Label for the fourth axis.

:Default: ``"w"``"""
        ...

    @property
    def font(self) -> str:
        """A string with comma-separated parameter values describing the font to be used for rendering the text labels of the viewport layer. The string must follow the specific form understood by the `QFont.fromString() <https://doc.qt.io/qtforpython/PySide6/QtGui/QFont.html#PySide2.QtGui.PySide2.QtGui.QFont.fromString>`__ method, for example ``'Arial,10,-1,5,75,0,0,0,0,0,Bold'``. 

Note that the font size parameter (10 in the example specification above) will be ignored by the viewport layer, because the size of text labels is already controlled by the :py:attr:`font_size` parameter."""
        ...

    @property
    def font_size(self) -> float:
        """The font size for rendering the text labels of the tripod. The font size is specified in terms of the tripod size.

:Default: ``0.4``"""
        ...

    @property
    def line_width(self) -> float:
        """Controls the width of axis arrows. The line width is specified relative to the tripod size.

:Default: ``0.06``"""
        ...

    @property
    def offset_x(self) -> float:
        """This parameter allows to displace the tripod horizontally. The offset is specified as a fraction of the output image width.

:Default: ``0.0``"""
        ...

    @property
    def offset_y(self) -> float:
        """This parameter allows to displace the tripod vertically. The offset is specified as a fraction of the output image height.

:Default: ``0.0``"""
        ...

    @property
    def outline_color(self) -> Color:
        """The outline color for text labels. This is used only if :py:attr:`outline_enabled` is set.

:Default: ``(1.0, 1.0, 1.0)``"""
        ...

    @property
    def outline_enabled(self) -> bool:
        """Enables the painting of a font outline to make the axis labels easier to read.

:Default: ``False``"""
        ...

    @property
    def size(self) -> float:
        """Scaling factor controlling the overall size of the tripod. The size is specified as a fraction of the output image height.

:Default: ``0.075``"""
        ...

    @property
    def style(self) -> Style:
        """Selects the visual style of the coordinate axis tripod.
Supported values are:

   * ``CoordinateTripodOverlay.Style.Flat`` (default) 
   * ``CoordinateTripodOverlay.Style.Solid``"""
        ...

class PythonViewportOverlay(ViewportOverlay):
    """Base: :py:class:`ovito.vis.ViewportOverlay`

This type of viewport overlay runs a custom Python script function every time an image of the viewport is rendered. The user-defined script function can paint arbitrary graphics on top of the three-dimensional scene. 

Note that instead of using a :py:class:`PythonViewportOverlay` it is also possible to directly manipulate the image returned by the :py:meth:`Viewport.render_image` method before saving the image to disk. A :py:class:`PythonViewportOverlay` is only necessary when rendering animations or if you want the overlay to be usable from in the graphical program version. 

You can attach the Python overlay to a viewport by adding it to the viewport's :py:attr:`overlays` collection:

```python
  from ovito.vis import PythonViewportOverlay, Viewport
  
  # Create a viewport:
  viewport = Viewport(type = Viewport.Type.Top)
  
  # The user-defined function that will paint on top of rendered images:
  def render_some_text(args: PythonViewportOverlay.Arguments):
      args.painter.drawText(10, 10, "Hello world")
  
  # Attach overlay function to viewport:
  viewport.overlays.append(PythonViewportOverlay(function = render_some_text))
```

The user-defined Python function must accept a single argument (named ``args`` in the example above). The system will pass in an instance of the :py:class:`.Arguments` class to the function, which contains various state information, including the current animation frame number and the viewport being rendered as well as a `QPainter <https://doc.qt.io/qtforpython/PySide6/QtGui/QPainter.html>`__ object, which the function should use to issue drawing calls."""

    class Arguments:
        """This data structure is passed to the user-defined ``render()`` function of the viewport overlay by the system. It carries context information about the frame being rendered and provides utility methods for projecting points from 3d to 2d space. Most importantly, it gives access to the :py:attr:`painter` object, which should be used by the ``render()`` function to issue drawing commands."""

        @property
        def fov(self) -> float:
            """The field of view of the viewport’s camera. For perspective projections, this is the frustum angle in the vertical direction (in radians). For orthogonal projections this is the visible range in the vertical direction (in world units)."""
            ...

        @property
        def frame(self) -> int:
            """The animation frame number being rendered (0-based)."""
            ...

        @property
        def is_perspective(self) -> bool:
            """Flag indicating whether the viewport uses a perspective projection or parallel projection."""
            ...

        @property
        def painter(self) -> PySide6.QtGui.QPainter:
            """The `QPainter <https://doc.qt.io/qtforpython/PySide6/QtGui/QPainter.html>`__ object, which provides painting methods for drawing on top of the image canvas."""
            ...

        @property
        def proj_tm(self) -> numpy.typing.ArrayLike:
            """The projection matrix. This 4x4 matrix transforms points from camera space to screen space."""
            ...

        @property
        def view_tm(self) -> numpy.typing.ArrayLike:
            """The affine camera transformation matrix. This 3x4 matrix transforms points/vectors from world space to camera space."""
            ...

        @property
        def scene(self) -> ovito.Scene:
            """The current three-dimensional :py:class:`~ovito.Scene` being rendered, including all visible data pipelines."""
            ...

        @property
        def size(self) -> Tuple[int, int]:
            """A tuple containing the width and height of the viewport image being rendered (in pixels). This may be a sub-region of the output image when rendering a multi-viewport layout."""
            ...

        @property
        def viewport(self) -> Viewport:
            """The :py:class:`Viewport` being rendered."""
            ...

        def project_point(self, world_xyz: Vector3) -> Optional[Tuple[float, float]]:
            """Projects a point, given in world-space coordinates, to screen space. This method can be used to determine where a 3d point would appear in the rendered image.

Note that the projected point may lay outside of the visible viewport region. Furthermore, for viewports with a perspective projection, the input point may lie behind the virtual camera. In this case no corresponding projected point in 2d screen space exists and the method returns ``None``. 

:param world_xyz: The (x,y,z) coordinates of the input point
:return: A (x,y) pair of pixel coordinates; or ``None`` if *world_xyz* is behind the viewer."""
            ...

        def project_size(self, world_xyz: Vector3, r: float) -> float:
            """Projects a size from 3d world space to 2d screen space. This method can be used to determine how large a 3d object, for example a sphere with the given radius *r*, would appear in the rendered image. 

Additionally to the size *r* to be projected, the method takes a coordinate triplet (x,y,z) as input. It specifies the location of the base point from where the distance is measured. 

:param world_xyz: The (x,y,z) world-space coordinates of the base point
:param r: The world-space size or distance to be converted to screen-space
:return: The computed screen-space size measured in pixels."""
            ...

    @property
    def function(self) -> Callable[[Arguments], Any]:
        """A reference to the Python function to be called every time the viewport is repainted or when an output image is rendered.

The user-defined function must accept exactly one argument as shown in the example above. The system will pass an :py:class:`.Arguments` object to the function, providing various contextual information on the current frame being rendered. 

Implementation note: Exceptions raised within the custom rendering function are *not* propagated to the calling context. 

:Default: ``None``"""
        ...

class TextLabelOverlay(ViewportOverlay):
    """Base: :py:class:`ovito.vis.ViewportOverlay`

Displays a text label in a viewport and in rendered images. You can attach an instance of this class to a viewport by adding it to the viewport's :py:attr:`overlays` collection:

```python
  from ovito.vis import TextLabelOverlay, Viewport
  from ovito.qt_compat import QtCore
  
  # Create the overlay:
  overlay = TextLabelOverlay(
      text = 'Some text',
      alignment = QtCore.Qt.AlignHCenter ^ QtCore.Qt.AlignBottom,
      offset_y = 0.1,
      font_size = 0.03,
      text_color = (0,0,0))
  
  # Attach the overlay to a newly created viewport:
  viewport = Viewport(type = Viewport.Type.Top)
  viewport.overlays.append(overlay)
```

Text labels can display dynamically computed values. See the :py:attr:`text` property for an example."""

    @property
    def alignment(self) -> PySide6.QtCore.Qt.Alignment:
        """Selects the corner of the viewport where the text is displayed (anchor position). This must be a valid `Qt.AlignmentFlag value <https://doc.qt.io/qtforpython/PySide6/QtCore/Qt.html#PySide6.QtCore.PySide6.QtCore.Qt.AlignmentFlag>`__ as shown in the example above. 

:Default: ``QtCore.Qt.AlignLeft ^ QtCore.Qt.AlignTop``"""
        ...

    @property
    def font(self) -> str:
        """A string with comma-separated parameter values describing the font to be used for rendering the text labels of the viewport layer. The string must follow the specific form understood by the `QFont.fromString() <https://doc.qt.io/qtforpython/PySide6/QtGui/QFont.html#PySide2.QtGui.PySide2.QtGui.QFont.fromString>`__ method, for example ``'Arial,10,-1,5,75,0,0,0,0,0,Bold'``. 

Note that the font size parameter (10 in the example specification above) will be ignored by the viewport layer, because the size of text labels is already controlled by the :py:attr:`font_size` parameter."""
        ...

    @property
    def font_size(self) -> float:
        """The font size, which is specified as a fraction of the output image height.

:Default: ``0.02``"""
        ...

    @property
    def format_string(self) -> str:
        """The format string used with the `sprintf() <https://en.cppreference.com/w/cpp/io/c/fprintf>`__ function to generate the text representation of global attributes (only floating-point values). You can change this format string to control the number of decimal places shown and switch between exponential and regular notation, for example. 

:Default: ``'%.6g'``"""
        ...

    @property
    def offset_x(self) -> float:
        """This parameter allows to displace the label horizontally from its anchor position. The offset is specified as a fraction of the output image width.

:Default: ``0.0``"""
        ...

    @property
    def offset_y(self) -> float:
        """This parameter allows to displace the label vertically from its anchor position. The offset is specified as a fraction of the output image height.

:Default: ``0.0``"""
        ...

    @property
    def outline_color(self) -> Color:
        """The text outline color. This is used only if :py:attr:`outline_enabled` is set.

:Default: ``(1.0, 1.0, 1.0)``"""
        ...

    @property
    def outline_enabled(self) -> bool:
        """Enables the painting of a font outline to make the text easier to read.

:Default: ``False``"""
        ...

    @property
    def source_pipeline(self) -> Optional[ovito.pipeline.Pipeline]:
        """The :py:class:`Pipeline` that is queried to obtain the attribute values referenced in the text string. See the :py:attr:`text` property for more information."""
        ...

    @property
    def text(self) -> str:
        """The text string to be rendered.

The string can contain placeholder references to dynamically computed attributes of the form ``[attribute]``, which will be replaced by their actual value before rendering the text label. Attributes are taken from the pipeline output of the :py:class:`Pipeline` assigned to the overlay's :py:attr:`source_pipeline` property. 

The following example demonstrates how to insert a text label that displays the number of currently selected particles: 

```python
  from ovito.io import import_file
  from ovito.vis import TextLabelOverlay, Viewport
  from ovito.modifiers import ExpressionSelectionModifier
  
  # Import a simulation dataset and select some atoms based on their potential energy:
  pipeline = import_file("input/simulation.dump")
  pipeline.add_to_scene()
  pipeline.modifiers.append(ExpressionSelectionModifier(expression="peatom > -4.2"))
  
  # Create the overlay. Note that the text string contains a reference
  # to an output attribute of the ExpressionSelectionModifier.
  overlay = TextLabelOverlay(text="Number of selected atoms: [ExpressionSelection.count]")
  # Specify the source of dynamically computed attributes.
  overlay.source_pipeline = pipeline
  
  # Attach overlay to a newly created viewport:
  viewport = Viewport(type=Viewport.Type.Top)
  viewport.overlays.append(overlay)
```

You can embed HTML and CSS markup elements in the string to further control the formatting and styling of the text. Note that only a `subset of the HTML standard <https://doc.qt.io/qt-6/richtext-html-subset.html>`__ is supported. 

:Default: ``"Text label"``"""
        ...

    @property
    def text_color(self) -> Color:
        """The text rendering color.

:Default: ``(0.0, 0.0, 0.5)``"""
        ...

class DataVis:
    """Abstract base class for visualization elements that are responsible for the visual appearance of data objects in the visualization. Some `DataObjects` are associated with a corresponding :py:class:`DataVis` element (see `DataObject.vis` property), making them *visual* data objects that appear in the viewports and in rendered images. 

See the :py:mod:`ovito.vis` module for the list of visual element types available in OVITO."""

    @property
    def enabled(self) -> bool:
        """Boolean flag controlling the visibility of the data. If set to ``False``, the data will not be visible in the viewports or in rendered images.

:Default: ``True``"""
        ...

    @property
    def title(self) -> str:
        """A custom title string assigned to the visual element, which will show in the pipeline editor of OVITO. 

:Default: ``''``"""
        ...

class SimulationCellVis(DataVis):
    """Base: :py:class:`ovito.vis.DataVis`

Controls the visual appearance of the simulation cell. 
An instance of this class is attached to the :py:class:`SimulationCell` object 
and can be accessed through its :py:attr:`vis` field. 
See also the corresponding user manual page for this visual element. 

The following example script demonstrates how to change the display line width and rendering color of the simulation cell 
loaded from an input simulation file:

.. literalinclude:: ../example_snippets/simulation_cell_vis.py"""

    @property
    def line_width(self) -> float:
        """The width of the simulation cell line (in simulation units of length).

:Default: 0.14% of the simulation box diameter"""
        ...

    @property
    def render_cell(self) -> bool:
        """Boolean flag controlling the cell's visibility in rendered images. If ``False``, the cell will only be visible in the interactive viewports. 

:Default: ``True``"""
        ...

    @property
    def rendering_color(self) -> Color:
        """The line color used when rendering the cell.

:Default: ``(0.0, 0.0, 0.0)``"""
        ...

class ParticlesVis(DataVis):
    """Base: :py:class:`ovito.vis.DataVis`

This type of visual element is responsible for rendering particles and is attached to every :py:class:`Particles` data object. 
You can access the element through the :py:attr:`vis` field of the data object and adjust its parameters to control the visual
appearance of particles in rendered images:

```python
  from ovito.io import import_file
  from ovito.vis import ParticlesVis
  
  pipeline = import_file("input/simulation.dump")
  pipeline.add_to_scene()
  
  vis_element = pipeline.source.data.particles.vis
  vis_element.shape = ParticlesVis.Shape.Square
```

See also the corresponding user manual page for more information on this visual element."""

    class Shape(enum.Enum):
        """AUTODOC_SKIP_MEMBER

Members:

  Sphere

  Box

  Circle

  Square

  Cylinder

  Spherocylinder

  Mesh

  Unspecified"""
        Unspecified = enum.auto()
        Sphere = enum.auto()
        Box = enum.auto()
        Circle = enum.auto()
        Square = enum.auto()
        Cylinder = enum.auto()
        Spherocylinder = enum.auto()
        Mesh = enum.auto()

    @property
    def radius(self) -> float:
        """The standard display radius of particles. This value is only used if no per-particle or per-type radii have been set. A per-type radius can be set via `ParticleType.radius`. An individual display radius can be assigned to each particle by setting the ``Radius`` particle property, e.g. using the :py:class:`ComputePropertyModifier`. 

:Default: 1.2"""
        ...

    @property
    def scaling(self) -> float:
        """Global scaling factor that is applied to every particle being rendered. 

:Default: 1.0"""
        ...

    @property
    def shape(self) -> Shape:
        """The kind of shape to use when rendering the particles. Supported modes are:

   * ``ParticlesVis.Shape.Sphere`` (default) 
   * ``ParticlesVis.Shape.Box``
   * ``ParticlesVis.Shape.Circle``
   * ``ParticlesVis.Shape.Square``
   * ``ParticlesVis.Shape.Cylinder``
   * ``ParticlesVis.Shape.Spherocylinder``


Mode ``Sphere`` includes ellipsoid and superquadric particle geometries, which are activated by the presence of the ``Aspherical Shape`` and ``Superquadric Roundness`` particle properties. Mode ``Box`` renders cubic as well as non-cubic boxes depending on the presence of the ``Aspherical Shape`` particle property. 

Note that this parameter controls the standard shape to be used for all particles. You can override this default setting on a per-particle type basis by setting the `ParticleType.shape` property to a different value."""
        ...

class BondsVis(DataVis):
    """Base: :py:class:`ovito.vis.DataVis`

A visualization element that renders cylindrical bonds between particles. 
An instance of this class is attached to every :py:class:`Bonds` data object 
and controls the visual appearance of the bonds in rendered images. 

See also the corresponding user manual page for this visual element. 
If you import a simulation file containing bonds, you can subsequently access the :py:class:`BondsVis` element 
through the :py:attr:`vis` field of the bonds data object, which is part in the data collection managed 
by the pipeline's :py:attr:`source` object:

```python
  pipeline = import_file('input/bonds.data.gz', atom_style='bond')
  pipeline.add_to_scene()
  bonds_vis = pipeline.source.data.particles.bonds.vis
  bonds_vis.width = 0.4
```

In cases where the :py:class:`Bonds` data is dynamically generated by a modifier, e.g. the :py:class:`CreateBondsModifier`, 
the :py:class:`BondsVis` element is managed by the modifier:

```python
  modifier = CreateBondsModifier(cutoff = 2.8)
  modifier.vis.flat_shading = True
  pipeline.modifiers.append(modifier)
```"""

    class ColoringMode(enum.Enum):
        """AUTODOC_SKIP_MEMBER

Members:

  Uniform

  ByBondType

  ByParticle"""
        Uniform = enum.auto()
        ByBondType = enum.auto()
        ByParticle = enum.auto()

    @property
    def color(self) -> Color:
        """The uniform color of bonds. This parameter is only used if :py:attr:`coloring_mode` is set to ``Uniform`` and if the bonds do not possess a bond property named ``Color``, i.e., explicit per-bond colors were not provided. 

:Default: ``(0.6, 0.6, 0.6)``"""
        ...

    @property
    def coloring_mode(self) -> ColoringMode:
        """Selects how the color of each bond is determined. Available modes:

  * ``BondsVis.ColoringMode.Uniform``: Use the specified :py:attr:`color` value to render all bonds.
  * ``BondsVis.ColoringMode.ByBondType``: Use each bond type's :py:attr:`color` to render the bonds.
  * ``BondsVis.ColoringMode.ByParticle``: Adopt the colors of the particles connect by the bonds.


.. note:: 

  If the :py:class:`Bonds` object being rendered contains the ``Color`` property, then the visual element will directly use these explicit per-bond RGB values   for rendering the bonds. The :py:attr:`coloring_mode` parameter is ignored in this case. 

:Default: ``BondsVis.ColoringMode.ByParticle``"""
        ...

    @property
    def flat_shading(self) -> bool:
        """Boolean flag that activates a flat-shaded representation of the bonds instead of the normal cylinder representation. 

:Default: ``False``"""
        ...

    @property
    def width(self) -> float:
        """The display width of bonds (in natural length units).

:Default: 0.4"""
        ...

class DislocationVis(DataVis):
    """Base: :py:class:`ovito.vis.DataVis`

Controls the visual appearance of dislocation lines extracted by a :py:class:`DislocationAnalysisModifier`. An instance of this class is attached to every :py:class:`DislocationNetwork` data object. 

See also the corresponding user manual page for more information on this visual element."""

    class ColoringMode(enum.Enum):
        """AUTODOC_SKIP_MEMBER

Members:

  ByDislocationType

  ByBurgersVector

  ByCharacter"""
        ByDislocationType = enum.auto()
        ByBurgersVector = enum.auto()
        ByCharacter = enum.auto()

    class Shading(enum.Enum):
        """A simple attribute-based namespace.

SimpleNamespace(**kwargs)"""
        Normal = enum.auto()
        Flat = enum.auto()

    @property
    def burgers_vector_color(self) -> Color:
        """The color of Burgers vector arrows.

:Default: ``(0.7, 0.7, 0.7)``"""
        ...

    @property
    def burgers_vector_scaling(self) -> float:
        """The scaling factor applied to displayed Burgers vectors. This can be used to exaggerate the arrow size.

:Default: ``1.0``"""
        ...

    @property
    def burgers_vector_width(self) -> float:
        """Specifies the width of Burgers vector arrows (in length units).

:Default: ``0.6``"""
        ...

    @property
    def coloring_mode(self) -> ColoringMode:
        """Selects the coloring mode for dislocation lines. 
Supported modes are:

   * ``DislocationVis.ColoringMode.ByDislocationType`` (default) 
   * ``DislocationVis.ColoringMode.ByBurgersVector``
   * ``DislocationVis.ColoringMode.ByCharacter``"""
        ...

    @property
    def line_width(self) -> float:
        """Controls the display width (in units of length of the simulation) of dislocation lines.

:Default: ``1.0``"""
        ...

    @property
    def shading(self) -> Shading:
        """The shading style used for the lines.
Possible values:

   * ``DislocationVis.Shading.Normal`` (default) 
   * ``DislocationVis.Shading.Flat``"""
        ...

    @property
    def show_burgers_vectors(self) -> bool:
        """Boolean flag that enables the display of Burgers vector arrows.

:Default: ``False``"""
        ...

    @property
    def show_line_directions(self) -> bool:
        """Boolean flag that enables the visualization of line directions.

:Default: ``False``"""
        ...

class SurfaceMeshVis(DataVis):
    """Base: :py:class:`ovito.vis.DataVis`

Controls the visual appearance of a :py:class:`SurfaceMesh` object, which is typically generated by modifiers such as 
:py:class:`ConstructSurfaceModifier` or :py:class:`CreateIsosurfaceModifier`. 
See also the corresponding user manual page for more information on this visual element."""

    class ColorMappingMode(enum.Enum):
        """AUTODOC_SKIP_MEMBER

Members:

  Uniform

  Vertex

  Face

  Region"""
        Uniform = enum.auto()
        Vertex = enum.auto()
        Face = enum.auto()
        Region = enum.auto()

    @property
    def cap_color(self) -> Color:
        """The RGB display color of the cap polygons at periodic boundaries.

:Default: ``(0.8, 0.8, 1.0)``"""
        ...

    @property
    def cap_transparency(self) -> float:
        """The level of transparency of the displayed cap polygons. The valid range is 0.0 -- 1.0  (fully opaque to fully transparent).

:Default: ``0.0``"""
        ...

    @property
    def color_mapping_gradient(self) -> ovito.modifiers.ColorCodingModifier.Gradient:
        """The color gradient for mapping scalar property values taken from the selected :py:attr:`color_mapping_property` to corresponding RGB color values (*color transfer function*). See the `ColorCodingModifier.gradient` parameter for a list of available color gradient types. 

:Default: ``ColorCodingModifier.Rainbow()``"""
        ...

    @property
    def color_mapping_interval(self) -> Tuple[float, float]:
        """Specifies the range of input values from the selected :py:attr:`color_mapping_property` getting mapped to corresponding RGB values by the selected :py:attr:`color_mapping_gradient`. The tuple defines the start and end of the linear interval that is translated to pseudo-colors by the color map. Input property values not within of the interval get mapped to the marginal colors of the selected color map. 

:Default: ``(0.0, 0.0)``"""
        ...

    @property
    def color_mapping_mode(self) -> ColorMappingMode:
        """Controls how the color of the surface is computed. Using pseudo-coloring you can visualize a local property of the surface. 

Available modes:

  * ``SurfaceMeshVis.ColorMappingMode.Uniform``: Uses :py:attr:`surface_color` for rendering the entire surface with a constant color (disables local pseudo-coloring).
  * ``SurfaceMeshVis.ColorMappingMode.Vertex``: Colors the surface based on a local property associated with the surface's :py:attr:`vertices`.
  * ``SurfaceMeshVis.ColorMappingMode.Face``: Colors the surface based on a local property associated with the surface's :py:attr:`faces`.
  * ``SurfaceMeshVis.ColorMappingMode.Region``: Colors the surface based on a local property associated with the surface's :py:attr:`regions`.


:Default: ``SurfaceMeshVis.ColorMappingMode.Uniform``"""
        ...

    @property
    def color_mapping_property(self) -> str:
        """The name of the property to be used for coloring the mesh to visualize the local values of this property on the surface. If the :py:class:`Property` has several components, then the name must be followed by a component name, e.g. ``'Orientation.X'``. Whether the property is taken from the :py:attr:`vertices`, :py:attr:`faces`, or :py:attr:`regions` of the :py:class:`SurfaceMesh` being rendered is determined by the selected :py:attr:`color_mapping_mode`. 

Numeric values from the source property are mapped to corresponding RGB-based pseudo-colors by first normalizing them according to the specified :py:attr:`color_mapping_interval` and then applying the selected :py:attr:`color_mapping_gradient`. 

Note that, if the ``Color`` property is defined on the surface's :py:attr:`vertices`, :py:attr:`faces`, or :py:attr:`regions`, then the visual element directly uses these explicit RGB values to render the surface. No color mapping takes place in this case and the :py:attr:`color_mapping_property`, :py:attr:`color_mapping_mode` and :py:attr:`surface_color` parameters are all ignored. 

:Default: ``''``"""
        ...

    @property
    def highlight_edges(self) -> bool:
        """Activates the highlighted rendering of the polygonal edges of the mesh.

:Default: ``False``"""
        ...

    @property
    def reverse_orientation(self) -> bool:
        """Flips the orientation of the surface. This affects the generation of cap polygons as well.

:Default: ``False``"""
        ...

    @property
    def show_cap(self) -> bool:
        """Controls the visibility of cap polygons, which are created at the intersection of the surface mesh with periodic box boundaries.

:Default: ``True``"""
        ...

    @property
    def smooth_shading(self) -> bool:
        """Enables smooth shading of the triangulated surface mesh.

:Default: ``True``"""
        ...

    @property
    def surface_color(self) -> Color:
        """The RGB display color of the surface mesh. Used only if :py:attr:`color_mapping_mode` is set to uniform coloring. 

:Default: ``(1.0, 1.0, 1.0)``"""
        ...

    @property
    def surface_transparency(self) -> float:
        """The level of transparency of the displayed surface. The valid range is 0.0 -- 1.0 (fully opaque to fully transparent).

:Default: ``0.0``"""
        ...

class TrajectoryVis(DataVis):
    """Base: :py:class:`ovito.vis.DataVis`

Controls the visual appearance of particle trajectory lines. An instance of this class is attached 
to every :py:class:`TrajectoryLines` data object. 

You typically create trajectory lines by inserting the :py:class:`GenerateTrajectoryLinesModifier`
into a data pipeline. The modifier owns a :py:class:`TrajectoryVis` element, which is used for 
visualizing the generated trajectory lines. You can access it through the modifier's :py:attr:`vis` field."""

    class Shading(enum.Enum):
        """AUTODOC_SKIP_MEMBER

Members:

  Normal

  Flat"""
        Normal = enum.auto()
        Flat = enum.auto()

    @property
    def color(self) -> Color:
        """The uniform color to be used for rendering the trajectory lines. This parameter is ignored if pseudo-coloring of the lines has been activated by setting a :py:attr:`color_mapping_property`. 

:Default: ``(0.6, 0.6, 0.6)``"""
        ...

    @property
    def color_mapping_gradient(self) -> ovito.modifiers.ColorCodingModifier.Gradient:
        """The color gradient used to map scalar property values from the selected :py:attr:`color_mapping_property` to corresponding RGB output values (also called *color transfer function*). See the `ColorCodingModifier.gradient` parameter for a list of available color gradient types. 

:Default: ``ColorCodingModifier.Rainbow()``"""
        ...

    @property
    def color_mapping_interval(self) -> Tuple[float, float]:
        """Specifies the range of input values from the selected :py:attr:`color_mapping_property` getting mapped to corresponding RGB values by the selected :py:attr:`color_mapping_gradient`. The tuple defines the start and end of the linear interval that is translated to pseudo-colors by the color map. Input property values not within of the interval get mapped to the marginal colors of the selected color map. 

:Default: ``(0.0, 0.0)``"""
        ...

    @property
    def color_mapping_property(self) -> str:
        """The name of the :py:class:`TrajectoryLines` property to be used for pseudo-coloring the lines according to the scalar values of this property. If the :py:class:`Property` consists of several vector components, then the name must be followed by a specific component name, e.g. ``'Velocity.Z'``. 

Typically, this parameter should be set to the name of the particle property which was sampled during line tracing by the :py:class:`GenerateTrajectoryLinesModifier`. See its :py:attr:`sample_particle_property` parameter for an example. 

Numeric values from the selected source property are mapped to corresponding RGB values by first normalizing them according to the specified :py:attr:`color_mapping_interval` and then applying the selected :py:attr:`color_mapping_gradient`. 

.. note:: 

  If the :py:class:`TrajectoryLines` object being rendered contains the ``Color`` property, then the visual element directly uses these explicit RGB values   to render the trajectory lines. No color mapping takes place in this case and the :py:attr:`color_mapping_property` and :py:attr:`color` parameters are both ignored. 

:Default: ``''``"""
        ...

    @property
    def shading(self) -> Shading:
        """The shading style used for trajectory lines.
Possible values:

   * ``TrajectoryVis.Shading.Normal`` 
   * ``TrajectoryVis.Shading.Flat`` (default)"""
        ...

    @property
    def upto_current_time(self) -> bool:
        """If ``True``, trajectory lines are only rendered up to the particle positions at the current animation time. Otherwise, the complete trajectory lines are displayed.

:Default: ``False``"""
        ...

    @property
    def width(self) -> float:
        """The display width of trajectory lines.

:Default: 0.2"""
        ...

    @property
    def wrapped_lines(self) -> bool:
        """If ``True``, the continuous trajectory lines will automatically be wrapped back into the simulation box during rendering. Thus, they will be shown as several discontinuous segments if they cross periodic boundaries of the simulation box. 

:Default: ``False``"""
        ...

class TriangleMeshVis(DataVis):
    """Base: :py:class:`ovito.vis.DataVis`

Controls the visual appearance of a :py:class:`TriangleMesh`. 
See also the corresponding user manual page for more information on this visual element."""

    @property
    def backface_culling(self) -> bool:
        """Controls whether triangle faces facing away from the viewer are not rendered. 

:Default: ``False``"""
        ...

    @property
    def color(self) -> Color:
        """The uniform RGB color of the triangle mesh, which is used for rendering if the mesh's faces or vertices have no local colors associated with them. RGB color components must be in the range 0--1.

:Default: ``(0.85, 0.85, 1.0)``"""
        ...

    @property
    def highlight_edges(self) -> bool:
        """Highlights the polygonal edges of the mesh by rendering a wireframe lines along those edges that have been marked as visible.

:Default: ``False``"""
        ...

    @property
    def transparency(self) -> float:
        """The degree of semi-transparency of the rendered mesh. Valid parameter range is 0.0 -- 1.0.

:Default: ``0.0``"""
        ...

class VectorVis(DataVis):
    """Base: :py:class:`ovito.vis.DataVis`

This type of visual element is responsible for rendering arrows to visualize per-particle vector quantities. 
An instance of this class is typically attached to a :py:class:`Property` data object that represents a vectorial quantity, e.g. the ``Force`` and the ``Displacement`` particle properties. 
See also the corresponding user manual page for a description of this visual element. 

The parameters of the vector visual element let you control the visual appearance of the arrows in rendered images. 
For the standard particle properties ``Force``, ``Dipole`` and ``Displacement``, OVITO automatically 
attaches a :py:class:`VectorVis` element to these properties and you can access it through their :py:attr:`vis` field: 

```python
  pipeline = import_file('input/simulation.dump')
  pipeline.add_to_scene()
  vector_vis = pipeline.source.data.particles.forces.vis
  vector_vis.color = (1,0,0)
  vector_vis.enabled = True  # This activates the display of arrows
```

In the example above, the ``Force`` particle property was loaded from the input simulation file, 
and the code accesses the corresponding :py:class:`Property` data object in the source data collection of the pipeline. 

Some modifiers dynamically generate new vector particle properties. For instance, the :py:class:`CalculateDisplacementsModifier` 
generates the ``Displacement`` property and will automatically attach a new :py:class:`VectorVis` element to it. 
In this case, the visual element is managed by the modifier and may be configured as needed: 

```python
  modifier = CalculateDisplacementsModifier()
  pipeline.modifiers.append(modifier)
  modifier.vis.enabled = True  # This activates the display of displacement vectors
  modifier.vis.flat_shading = False
```

If you write your own modifier function in Python for computing a vector particle property, and you want to visualize these vectors 
as arrows, you need to create the :py:class:`VectorVis` element programmatically and attached it to the :py:class:`Property` generated 
by your user-defined modifier function. For example: 

```python
  from ovito.vis import VectorVis
  import numpy
  
  # Set up the visual element outside of the modifier function:
  vector_vis = VectorVis(
      alignment = VectorVis.Alignment.Center, 
      color = (1.0, 0.0, 0.4))
  
  def my_modifier_function(frame, data):
      vector_data = numpy.random.random_sample(size=(data.particles.count, 3))
      my_prop = data.particles_.create_property('My Property', data=vector_data)
      my_prop.vis = vector_vis  # Attach the visual element to output property
```"""

    class Alignment(enum.Enum):
        """AUTODOC_SKIP_MEMBER

Members:

  Base

  Center

  Head"""
        Base = enum.auto()
        Center = enum.auto()
        Head = enum.auto()

    @property
    def alignment(self) -> Alignment:
        """Controls the positioning of arrows with respect to the particles.
Possible values:

   * ``VectorVis.Alignment.Base`` (default) 
   * ``VectorVis.Alignment.Center``
   * ``VectorVis.Alignment.Head``"""
        ...

    @property
    def color(self) -> Color:
        """The uniform display color of arrows. This parameter is *not* used if pseudo-color mapping is enabled through the :py:attr:`color_mapping_property` option or when the ``Vector Color`` property was set for the particles. 

:Default: ``(1.0, 1.0, 0.0)``"""
        ...

    @property
    def color_mapping_gradient(self) -> ovito.modifiers.ColorCodingModifier.Gradient:
        """The color gradient used to map scalar property values from the selected :py:attr:`color_mapping_property` to corresponding RGB output values (*color transfer function*). See the `ColorCodingModifier.gradient` parameter for a list of available color gradient types. 

:Default: ``ColorCodingModifier.Rainbow()``"""
        ...

    @property
    def color_mapping_interval(self) -> Tuple[float, float]:
        """Specifies the range of input values from the selected :py:attr:`color_mapping_property` getting mapped to corresponding RGB values by the selected :py:attr:`color_mapping_gradient`. The tuple defines the start and end of the linear interval that is translated to pseudo-colors by the color map. Input property values not within of the interval get mapped to the marginal colors of the selected color map. 

:Default: ``(0.0, 0.0)``"""
        ...

    @property
    def color_mapping_property(self) -> str:
        """The name of the :py:class:`Particles` property to be used for coloring the vector glyphs. If the :py:class:`Property` has several components, then the name must be followed by a component name, e.g. ``'Displacement.Z'``. 

Numeric values from the selected source property are mapped to corresponding RGB values by first normalizing them according to the specified :py:attr:`color_mapping_interval` and then applying the selected :py:attr:`color_mapping_gradient`. 

Note that, if the :py:class:`Particles` object being rendered contains the ``Vector Color`` property, then the visual element directly uses these RGB values to render the vector glyphs. No color mapping takes place in this case and the :py:attr:`color_mapping_property` and :py:attr:`color` parameters are both ignored. 

:Default: ``''``"""
        ...

    @property
    def flat_shading(self) -> bool:
        """Switches between a flat rendering style for the arrows and a three-dimensional representation. 

:Default: ``True``"""
        ...

    @property
    def offset(self) -> Vector3:
        """Additional offset by which all arrows are displaced. This can be used to move the arrows in front of or behind the particles and avoid occlusions. 

:Default: ``(0.0, 0.0, 0.0)``"""
        ...

    @property
    def reverse(self) -> bool:
        """Boolean flag controlling the reversal of arrow directions.

:Default: ``False``"""
        ...

    @property
    def scaling(self) -> float:
        """The uniform scaling factor applied to arrow glyphs. 

:Default: 1.0"""
        ...

    @property
    def transparency(self) -> float:
        """The level of semi-transparency for rendering the arrows. The valid parameter range is 0.0 -- 1.0 (fully opaque to fully transparent).

:Default: 0.0"""
        ...

    @property
    def width(self) -> float:
        """Controls the width of arrows (in simulation units of length).

:Default: 0.5"""
        ...

class VoxelGridVis(DataVis):
    """Base: :py:class:`ovito.vis.DataVis`

This visual element controls the appearance of a :py:class:`VoxelGrid` data object, which is typically generated by the 
:py:class:`SpatialBinningModifier` or imported directly from files containing volumetric data. The visual element is responsible for rendering 
the outer boundaries of the grid, i.e., showing only the voxel cells at the surface but not in the interior of the grid volume.

See also the corresponding user manual page for further information on this visual element."""

    @property
    def color_mapping_gradient(self) -> ovito.modifiers.ColorCodingModifier.Gradient:
        """The color gradient used to map scalar property values from the selected :py:attr:`color_mapping_property` to corresponding RGB output values (also called *color transfer function*). See the `ColorCodingModifier.gradient` parameter for a list of available color gradient types. 

:Default: ``ColorCodingModifier.Rainbow()``"""
        ...

    @property
    def color_mapping_interval(self) -> Tuple[float, float]:
        """Specifies the range of input values from the selected :py:attr:`color_mapping_property` getting mapped to corresponding RGB values by the selected :py:attr:`color_mapping_gradient`. The tuple defines the start and end of the linear interval that is translated to pseudo-colors by the color map. Input property values not within of the interval get mapped to the marginal colors of the selected color map. 

:Default: ``(0.0, 0.0)``"""
        ...

    @property
    def color_mapping_property(self) -> str:
        """The name of the :py:class:`VoxelGrid` scalar property to be used for coloring the grid cells. If the :py:class:`Property` has several components, then the name must be followed by a component name, e.g. ``'Velocity.Z'``. 

Numeric values from the selected source property are mapped to corresponding RGB cell colors by first normalizing them according to the specified :py:attr:`color_mapping_interval` and then applying the selected :py:attr:`color_mapping_gradient`. 

Note that, if the :py:class:`VoxelGrid` being rendered contains the ``Color`` property, then the visual element directly uses these RGB values to render the grid cells. No color mapping takes place in this case and the :py:attr:`color_mapping_property` parameter is ignored. 

:Default: ``''``"""
        ...

    @property
    def highlight_grid_lines(self) -> bool:
        """Controls the rendering of grid lines separating the voxel cells.

:Default: ``True``"""
        ...

    @property
    def interpolate_colors(self) -> bool:
        """Controls whether the (pseudo)colors of the voxel cells visible on the boundary of the grid are smoothly interpolated between neighboring cells. 

:Default: ``False``"""
        ...

    @property
    def transparency(self) -> float:
        """The level of transparency of the displayed grid surface. The valid parameter range is 0.0 -- 1.0 (fully opaque to fully transparent).

:Default: ``0.0``"""
        ...

class Viewport(DataVis):
    """A viewport is a "window" to the three-dimensional scene, showing the scene from the point of view of a virtual camera. 

The virtual camera's position and orientation are given by the :py:attr:`camera_pos` and :py:attr:`camera_dir` properties. Additionally, the :py:attr:`type` field allows you to switch between perspective and parallel projection modes or reset the camera to one of the standard axis-aligned orientations (top, left, front, etc.). The :py:meth:`.zoom_all` method repositions the camera automatically such that the entire scene becomes fully visible within the viewport. See also the documentation of the Adjust View dialog of OVITO to learn more about these camera-related settings. 

After the viewport's virtual camera has been set up, you can render an image or movie using the :py:meth:`.render_image` and :py:meth:`.render_anim` methods. For example: 

```python
  from ovito.io import import_file
  from ovito.vis import Viewport, TachyonRenderer
  
  pipeline = import_file('input/simulation.dump')
  pipeline.add_to_scene()
  
  vp = Viewport(type = Viewport.Type.Ortho, camera_dir = (2, 1, -1))
  vp.zoom_all()
  vp.render_image(filename='output/simulation.png', 
                  size=(320, 240), 
                  renderer=TachyonRenderer())
```

Furthermore, so-called *overlays* may be added to a viewport. Overlays are function objects that draw additional two-dimensional graphics or text on top of or behind the rendered scene, e.g. coordinate axes or a color legend. See the documentation of the :py:attr:`overlays` and :py:attr:`underlays` lists for more information."""

    class Type(enum.Enum):
        """AUTODOC_SKIP_MEMBER

Members:

  Top

  Bottom

  Front

  Back

  Left

  Right

  Ortho

  Perspective

  SceneNode

  NONE

  TOP

  BOTTOM

  FRONT

  BACK

  LEFT

  RIGHT

  ORTHO

  PERSPECTIVE"""
        Perspective = enum.auto()
        Ortho = enum.auto()
        Top = enum.auto()
        Bottom = enum.auto()
        Front = enum.auto()
        Back = enum.auto()
        Left = enum.auto()
        Right = enum.auto()

    @property
    def camera_dir(self) -> Vector3:
        """The viewing direction vector of the viewport's camera."""
        ...

    @property
    def camera_pos(self) -> Vector3:
        """The position of the viewport's camera in the three-dimensional scene."""
        ...

    @property
    def camera_up(self) -> Vector3:
        """Direction vector specifying which coordinate axis will point upward in rendered images. Set this parameter to a non-zero vector in order to rotate the camera around the viewing direction and align the vertical direction in rendered images with a different simulation coordinate axis. If set to ``(0,0,0)``, then the upward axis is determined by the current user settings set in OVITO's application settings dialog (z-axis by default). 

:Default: ``(0.0, 0.0, 0.0)``"""
        ...

    @property
    def fov(self) -> float:
        """The field of view of the viewport's camera. For perspective projections this is the camera's angle in the vertical direction (in radians). For orthogonal projections this is the visible range in the vertical direction (in world units)."""
        ...

    @property
    def overlays(self) -> MutableSequence[ViewportOverlay]:
        """The list of :py:class:`ViewportOverlay` objects currently attached to this viewport. Overlays render two-dimensional graphics on top of the three-dimensional scene. See the following overlay types for more information:

   * :py:class:`TextLabelOverlay`
   * :py:class:`ColorLegendOverlay`
   * :py:class:`CoordinateTripodOverlay`
   * :py:class:`PythonViewportOverlay`


To attach a new overlay to the viewport, use the list's ``append()`` method:

```python
  from ovito.vis import Viewport, CoordinateTripodOverlay
  
  vp = Viewport(type = Viewport.Type.Ortho)
  tripod = CoordinateTripodOverlay(size = 0.07)
  vp.overlays.append(tripod)
```

The viewport also has an :py:attr:`underlays` list. :py:class:`ViewportOverlay` objects inserted into that list will be rendered *behind* the 3d objects of the scene."""
        ...

    @property
    def underlays(self) -> MutableSequence[ViewportOverlay]:
        """The list of :py:class:`ViewportOverlay` objects currently attached to this viewport. They render two-dimensional graphics *behind* the three-dimensional scene. See the :py:attr:`overlays` list for further information."""
        ...

    @property
    def type(self) -> Type:
        """Specifies the projection type of the viewport. The following standard projections are available:

  * ``Viewport.Type.Perspective``
  * ``Viewport.Type.Ortho``
  * ``Viewport.Type.Top``
  * ``Viewport.Type.Bottom``
  * ``Viewport.Type.Front``
  * ``Viewport.Type.Back``
  * ``Viewport.Type.Left``
  * ``Viewport.Type.Right``

The first two types (``Perspective`` and ``Ortho``) allow you to set up custom views with arbitrary camera orientations."""
        ...

    def create_qt_widget(self, parent: Optional[PySide6.QtWidgets.QWidget]=None) -> PySide6.QtWidgets.QWidget:
        """Creates an interactive visual widget displaying the three-dimensional scene as seen through this virtual viewport.
The method creates an interactive window accepting mouse inputs from the user similar to the viewport windows 
of the OVITO desktop application. You can use this method to develop custom user interfaces based on the Qt cross-platform framework 
that integrate OVITO's functionality and display the output of a data pipeline.

:param parent: An optional Qt widget that should serve as parent of the newly created viewport widget. 
:returns: A new `QWidget <https://doc.qt.io/qtforpython/PySide6/QtWidgets/QWidget.html>`__ displaying the three-dimensional scene as seen through the virtual viewport.

The Qt widget returned by this method is linked to this :py:class:`Viewport` instance. 
Any changes your Python script subsequently makes to the non-visual :py:class:`Viewport` instance,
for example setting :py:attr:`camera_pos` or :py:attr:`camera_dir`, will automatically be reflected by the 
visual viewport widget. Vice versa will interactions of the user with the viewport widget
automatically lead to changes of the corresponding fields of the :py:class:`Viewport` instance.

The following short example program demonstrates the use of the :py:meth:`create_qt_widget` method. Please see the 
`Qt for Python <https://doc.qt.io/qtforpython-5/>`__ documentation for more information on how to create graphical 
user interfaces using the Qt framework.

```python
  import sys, os
  # Future versions of OVITO will use Qt6 & PySide6, older versions use Qt5 & PySide2.
  # Please pick the right PySide version for import.
  if os.getenv('QT_API') == 'pyside6': 
      from PySide6.QtCore import QEventLoop, QTimer
      from PySide6.QtWidgets import QApplication
  else: 
      from PySide2.QtCore import QEventLoop, QTimer
      from PySide2.QtWidgets import QApplication
  
  # Create a global Qt application object - unless we are running inside the 'ovitos' interpreter, 
  # which automatically initializes a Qt application object.
  if not QApplication.instance():
      myapp = QApplication(sys.argv)
  
  # Note: Import the ovito package AFTER the QApplication object
  # has been created. Otherwise, Ovito would automatically create its own 
  # QCoreApplication object, which won't let us display GUI widgets.
  from ovito.io import import_file
  from ovito.vis import Viewport
  
  # Import model and add it to visualization scene.
  pipeline = import_file('input/simulation.dump')
  pipeline.add_to_scene()
  
  # Create a virtual Viewport.
  vp = Viewport(type=Viewport.Type.Perspective, camera_dir=(2, 1, -1))
  
  # Create a visible GUI widget associated with the viewport.
  widget = vp.create_qt_widget()
  widget.resize(500, 400)
  widget.setWindowTitle('OVITO Viewport Demo')
  widget.show()
  vp.zoom_all((widget.width(), widget.height()))
  
  # Shut down application when the user closes the viewport widget.
  widget.destroyed.connect(QApplication.instance().quit)
  
  # Start the Qt event loop.
  if 'myapp' in locals():
      # When a standard Python interpreter is used to run this script, start the 
      # application's main event loop to begin UI event processing.
      sys.exit(myapp.exec_()) 
  else:
      # When running this script with the 'ovitos' interpreter, a Qt event loop is already active.
      # Start a nested event loop then, just for this little demo program.
      eventLoop = QEventLoop()
      widget.destroyed.connect(eventLoop.quit) # Stop event loop when user closes the viewport widget.
      eventLoop.exec_()
```"""
        ...

    def render_anim(self, filename: str, size: Tuple[int, int]=(640, 480), fps: int=10, background: Color=(1.0, 1.0, 1.0), renderer: Optional[Renderer]=None, range: Optional[Tuple[int, int]]=None, every_nth: int=1, layout: Optional[Sequence[Tuple[Viewport, Tuple[float, float, float, float]]]]=None) -> None:
        """Renders an animation sequence.

:param str filename: The filename under which the rendered animation should be saved.
                     Supported video formats are: :file:`.avi`, :file:`.mp4`, :file:`.mov` and :file:`.gif`.
                     Alternatively, an image format may be specified (:file:`.png`, :file:`.jpeg`).
                     In this case, a series of image files will be produced, one for each frame, which
                     may be combined into an animation using an external video encoding tool of your choice.
:param size: The resolution of the movie in pixels.
:param fps: The number of frames per second of the encoded movie. This determines the playback speed of the animation.
:param background: An RGB triplet in the range [0,1] specifying the background color of the rendered movie.
:param renderer: The rendering engine to use. If none is specified, either OpenGL or Tachyon are used,
                 depending on the availability of OpenGL in the script execution context.
:param range: The interval of frames to render, specified in the form ``(from,to)``.
              Frame numbering starts at 0. If no interval is specified, the entire animation is rendered, i.e.
              frame 0 through (`FileSource.num_frames`-1).
:param every_nth: Frame skipping interval in case you don't want to render every frame of a very long animation.
:param layout: Optional definition of a multi-viewport layout to be rendered into the output image. 

See also the :py:meth:`.render_image` method for a more detailed discussion of some of these parameters."""
        ...

    def render_image(self, size: Tuple[int, int]=(640, 480), frame: int=0, filename: Optional[str]=None, background: Color=(1.0, 1.0, 1.0), alpha: bool=False, renderer: Optional[Renderer]=None, crop: bool=False, layout: Optional[Sequence[Tuple[Viewport, Tuple[float, float, float, float]]]]=None) -> PySide6.QtGui.QImage:
        """Renders an image of the viewport's view.

:param size: A pair of integers specifying the horizontal and vertical dimensions of the output image in pixels.
:param int frame: The animation frame to render. Numbering starts at 0. See the `FileSource.num_frames` property for the number of loaded animation frames.
:param str filename: The file path under which the rendered image should be saved (optional).
                     Supported output formats are: :file:`.png`, :file:`.jpeg` and :file:`.tiff`.
:param background: A triplet of RGB values in the range [0,1] specifying the background color of the rendered image.
:param alpha: This option makes the background transparent so that the rendered image may later be superimposed on a different backdrop.
              When using this option, make sure to save the image in the PNG format in order to preserve the generated transparency information.
:param renderer: The rendering engine to use. If set to ``None``, either OpenGL or Tachyon are used,
                 depending on the availability of OpenGL in the current execution context.
:param crop: This option cuts away border areas of the rendered image filled with the background color; the resulting image may thus turn out smaller than the requested *size*. 
:param layout: Optional definition of a multi-viewport layout to be rendered into the output image. The layout must be provided as a list of :py:class:`Viewport` objects
               and corresponding rectangular areas, which determine where each viewport's picture appears within the composed output image. 
               Please make use of OVITO Pro's code generation function to learn how to construct the *layout* argument. 
:returns: A `QImage <https://doc.qt.io/qtforpython/PySide6/QtGui/QImage.html>`__ object containing the rendered picture.

Populating the scene

Before rendering an image using this method, you should make sure the three-dimensional contains some
visible objects. Typically this involves calling the `Pipeline.add_to_scene()`
method on a pipeline to insert its output data into the scene::

   pipeline = import_file('simulation.dump')
   pipeline.add_to_scene()

Selecting a rendering engine

OVITO supports several different rendering backends for producing pictures of the three-dimensional scene:

    * :py:class:`OpenGLRenderer`
    * :py:class:`TachyonRenderer`
    * :py:class:`OSPRayRenderer`

Each of these backends exhibits specific parameters that control the image quality and other aspect of the image
generation process. Typically, you would create an instance of one of these renderer classes, configure it and pass
it to the :py:meth:`!render_image()` method:

```python
  vp.render_image(filename='output/simulation.png', 
                  size=(320,240),
                  background=(0,0,0), 
                  renderer=TachyonRenderer(ambient_occlusion=False, shadows=False))
```

Note that the :py:class:`OpenGLRenderer` backend may not be available when you are executing the script in a
headless environment, e.g. on a remote HPC cluster without X display and OpenGL support.

Post-processing images

If the ``filename`` parameter is omitted, the method does not save the rendered image to disk.
This gives you the opportunity to paint additional graphics on top before saving the
`QImage <https://doc.qt.io/qtforpython/PySide6/QtGui/QImage.html>`__ later using its ``save()`` method:

```python
  from ovito.vis import Viewport, TachyonRenderer
  from ovito.qt_compat import QtGui
  
  # Render an image of the three-dimensional scene:
  vp = Viewport(type=Viewport.Type.Ortho, camera_dir=(2, 1, -1))
  vp.zoom_all()
  image = vp.render_image(size=(320,240), renderer=TachyonRenderer())
  
  # Paint on top of the rendered image using Qt's drawing functions:
  painter = QtGui.QPainter(image)
  painter.drawText(10, 20, "Hello world!")
  del painter
  
  # Save image to disk:
  image.save("output/image.png")
```

As an alternative to the direct method demonstrated above, you can also make use of a :py:class:`PythonViewportOverlay`
to paint custom graphics on top of rendered images."""
        ...

    def zoom_all(self, size: Tuple[int, int]=(640, 480)) -> None:
        """Repositions the viewport camera such that all objects in the scene become completely visible.
The current orientation (:py:attr:`camera_dir`) of the viewport's camera is maintained but
the :py:attr:`camera_pos` and :py:attr:`fov` parameters are adjusted by this method.

:param size: Size in pixels of the image that is going to be renderer from this viewport.
             This information is used to compute the aspect ratio of the viewport rectangle into which 
             the visible objects should be fitted. The tuple should match the *size* argument being passed
             to :py:meth:`render_image`.

Note that this method uses an axis-aligned bounding box computed at frame 0 of the
loaded trajectory enclosing all visible objects to position the viewport camera. 
Make sure to call `Pipeline.add_to_scene()` prior
to this method to insert some visible object(s) to the scene first."""
        ...