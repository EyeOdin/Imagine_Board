# Tela is a Krita plugin for a Canvas Tool Box
# Copyright (C) 2021  Ricardo Jeremias.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


#region Imports

# Python Module
import datetime
import inspect
import xml
import zipfile
# Krita Module
from krita import *
# PyQt5 Modules
from PyQt5 import QtWidgets, QtCore, QtGui, uic
# Modules
from .tela_modulo import *

#endregion
#region Global Variables

# Tela
EXTENSION_NAME = "Tela"

# time constants
segundo = 1 # null
minuto = 60 # seconds
hora = 60 # minutes
dia = 24 # hours
mes = 30.4167 # days
ano = 12 # moths
sec_segundo = segundo
sec_minuto = minuto * sec_segundo
sec_hora = hora * sec_minuto
sec_dia = dia * sec_hora
sec_mes = mes * sec_dia
sec_ano = ano * sec_mes

#endregion


class Tela_Extension( Extension ):
    """
    Tela ToolBox
    """

    #region Initialize

    def __init__( self, parent ):
        super().__init__( parent )
    def setup( self ):
        self.User_Interface()
        self.Variables()
        self.Modules()
        self.Updater()

    def User_Interface( self ):
        # Operating System
        self.OS = str( QSysInfo.kernelType() ) # WINDOWS=winnt & LINUX=linux
        if self.OS == "winnt": # Unlocks icons in Krita for Menu Mode
            QApplication.setAttribute( Qt.AA_DontShowIconsInMenus, False )
        # Path Name
        self.directory_plugin = str( os.path.dirname( os.path.realpath( __file__ ) ) )
        # Information
        url_information = os.path.join( self.directory_plugin, "information.ui" )
        self.ui_information = uic.loadUi( url_information, QWidget() )
        # Guide
        url_guide = os.path.join( self.directory_plugin, "guide.ui" )
        self.ui_guide = uic.loadUi( url_guide, QWidget() )
        # Color Picker
        url_color_picker = os.path.join( self.directory_plugin, "color_picker.ui" )
        self.ui_color_picker = uic.loadUi( url_color_picker, QWidget() )
        # Shelf Action Manage
        url_manage_shelf = os.path.join( self.directory_plugin, "manage_shelf.ui" )
        self.ui_manage_shelf = uic.loadUi( url_manage_shelf, QWidget() )
        self.ui_manage_shelf.setWindowTitle( "Manage Shelf Action" )
    def Variables( self ):
        # Variables
        ki = Krita.instance()

        # Version
        krita_version = ki.version()
        major = int( krita_version[0] )
        minor = int( krita_version[2] )
        self.krita_version = ( major == 5 and minor >= 3 ) or (  major >= 6 ) # comic tool is new in version 5.3

        # None Variables
        self.qmenu = None
        self.stacked_widget = None
        self.qmdiarea = None
        self.window_list = list()

        # State
        self.state_canvas = False

        # Animation
        self.animation_frame = None
        self.check_timer = 2000
        self.anim_ctime = 0
        self.anim_stime = 0
        self.anim_etime = 100

        # Vector
        icon_select_tool        = ki.icon( "select" )
        icon_text_tool          = ki.icon( "draw-text" )
        icon_edit_tool          = ki.icon( "shape_handling" )
        icon_calligraphy_tool   = ki.icon( "calligraphy" )
        icon_comic_tool         = ki.icon( "tool_comic_panel" )
        # Brush
        icon_freehand_brush     = ki.icon( "krita_tool_freehand" )
        icon_line_brush         = ki.icon( "krita_tool_line" )
        icon_rectangle_brush    = ki.icon( "krita_tool_rectangle" )
        icon_ellipse_brush      = ki.icon( "krita_tool_ellipse" )
        icon_polygon_brush      = ki.icon( "krita_tool_polygon" )
        icon_polyline_brush     = ki.icon( "polyline" )
        icon_bezier_brush       = ki.icon( "krita_draw_path" )
        icon_path_brush         = ki.icon( "krita_tool_freehandvector" )
        icon_dynamic_brush      = ki.icon( "krita_tool_dyna" )
        icon_multi_brush        = ki.icon( "krita_tool_multihand" )
        # Transform
        icon_transform_tool     = ki.icon( "krita_tool_transform" )
        icon_move_tool          = ki.icon( "krita_tool_move" )
        icon_crop_tool          = ki.icon( "tool_crop" )
        # Color
        icon_gradient_tool      = ki.icon( "krita_tool_gradient" )
        icon_sampler_tool       = ki.icon( "krita_tool_color_sampler" )
        icon_colorize_tool      = ki.icon( "krita_tool_lazybrush" )
        icon_patch_tool         = ki.icon( "krita_tool_smart_patch" )
        icon_fill_tool          = ki.icon( "krita_tool_color_fill" )
        icon_enclose_tool       = ki.icon( "krita_tool_enclose_and_fill" )
        # Overlay
        icon_assistant_tool     = ki.icon( "krita_tool_assistant" )
        icon_measure_tool       = ki.icon( "krita_tool_measure" )
        icon_reference_tool     = ki.icon( "krita_tool_reference_images" )
        # Select
        icon_rectangle_select   = ki.icon( "tool_rect_selection" )
        icon_elliptical_select  = ki.icon( "tool_elliptical_selection" )
        icon_polygon_select     = ki.icon( "tool_polygonal_selection" )
        icon_freehand_select    = ki.icon( "tool_outline_selection")
        icon_contiguous_select  = ki.icon( "tool_contiguous_selection" )
        icon_color_select       = ki.icon( "tool_similar_selection")
        icon_bezier_select      = ki.icon( "tool_path_selection")
        icon_magnetic_select    = ki.icon( "tool_magnetic_selection" )
        # Camera
        icon_zoom_tool          = ki.icon( "tool_zoom" )
        icon_pan_tool           = ki.icon( "tool_pan" )
        # Mirror Fix
        self.icon_mirrorfix = "wraparound"

        # Toolbox ( name, pykrita, qicon )
        self.tool = {
            "vector" : {
                "select_tool"        : [ "Select",      "InteractionTool",                   icon_select_tool,        0 ],
                "text_tool"          : [ "Text",        "SvgTextTool",                       icon_text_tool,          1 ],
                "edit_tool"          : [ "Edit",        "PathTool",                          icon_edit_tool,          2 ],
                "calligraphy_tool"   : [ "Calligraphy", "KarbonCalligraphyTool",             icon_calligraphy_tool,   3 ],
                # "comic_tool"         : [ "Comic",       "KritaShape/KisToolKnife",           icon_comic_tool,         4 ],
                },
            "brush" : {
                "freehand_brush"     : [ "Freehand",    "KritaShape/KisToolBrush",           icon_freehand_brush,     0 ],
                "line_brush"         : [ "Line",        "KritaShape/KisToolLine",            icon_line_brush,         1 ],
                "rectangle_brush"    : [ "Rectangle",   "KritaShape/KisToolRectangle",       icon_rectangle_brush,    2 ],
                "ellipse_brush"      : [ "Ellipse",     "KritaShape/KisToolEllipse",         icon_ellipse_brush,      3 ],
                "polygon_brush"      : [ "Polygon",     "KisToolPolygon",                    icon_polygon_brush,      4 ],
                "polyline_brush"     : [ "Polyline",    "KisToolPolyline",                   icon_polyline_brush,     5 ],
                "bezier_brush"       : [ "Bezier",      "KisToolPath",                       icon_bezier_brush,       6 ],
                "path_brush"         : [ "Path",        "KisToolPencil",                     icon_path_brush,         7 ],
                "dynamic_brush"      : [ "Dynamic",     "KritaShape/KisToolDyna",            icon_dynamic_brush,      8 ],
                "multi_brush"        : [ "Multibrush",  "KritaShape/KisToolMultiBrush",      icon_multi_brush,        9 ],
                },
            "transform" : {
                "transform_tool"     : [ "Transform",   "KisToolTransform",                  icon_transform_tool,     0 ],
                "move_tool"          : [ "Move",        "KritaTransform/KisToolMove",        icon_move_tool,          1 ],
                "crop_tool"          : [ "Crop",        "KisToolCrop",                       icon_crop_tool,          2 ],
                },
            "color" : {
                "gradient_tool"      : [ "Gradient",    "KritaFill/KisToolGradient",         icon_gradient_tool,      0 ],
                "sampler_tool"       : [ "Sampler",     "KritaSelected/KisToolColorSampler", icon_sampler_tool,       1 ],
                "colorize_tool"      : [ "Colorize",    "KritaShape/KisToolLazyBrush",       icon_colorize_tool,      2 ],
                "patch_tool"         : [ "Patch",       "KritaShape/KisToolSmartPatch",      icon_patch_tool,         3 ],
                "fill_tool"          : [ "Fill",        "KritaFill/KisToolFill",             icon_fill_tool,          4 ],
                "enclose_tool"       : [ "Enclose",     "KisToolEncloseAndFill",             icon_enclose_tool,       5 ],
                },
            "overlay" : {
                "assistant_tool"     : [ "Assistant",   "KisAssistantTool",                  icon_assistant_tool,     0 ],
                "measure_tool"       : [ "Measure",     "KritaShape/KisToolMeasure",         icon_measure_tool,       1 ],
                "reference_tool"     : [ "Reference",   "ToolReferenceImages",               icon_reference_tool,     2 ],
                },
            "select" : {
                "rectangle_select"   : [ "Rectangle",   "KisToolSelectRectangular",          icon_rectangle_select,   0 ],
                "elliptical_select"  : [ "Elliptical",  "KisToolSelectElliptical",           icon_elliptical_select,  1 ],
                "polygon_select"     : [ "Polygon",     "KisToolSelectPolygonal",            icon_polygon_select,     2 ],
                "freehand_select"    : [ "Freehand",    "KisToolSelectOutline",              icon_freehand_select,    3 ],
                "contiguous_select"  : [ "Contiguous",  "KisToolSelectContiguous",           icon_contiguous_select,  4 ],
                "color_select"       : [ "Color",       "KisToolSelectSimilar",              icon_color_select,       5 ],
                "bezier_select"      : [ "Bezier",      "KisToolSelectPath",                 icon_bezier_select,      6 ],
                "magnetic_select"    : [ "Magnetic",    "KisToolSelectMagnetic",             icon_magnetic_select,    7 ],
                },
            "camera" : {
                "zoom_tool"          : [ "Zoom",        "ZoomTool",                          icon_zoom_tool,          0 ],
                "pan_tool"           : [ "Pan",         "PanTool",                           icon_pan_tool,           1 ],
                },
        }
        if self.krita_version == True: # Krita 5.3 and above have a extra tool
            self.tool["vector"]["comic_tool"] = [ "Comic", "KritaShape/KisToolKnife", icon_comic_tool, 4 ]

        # Operation holds the favorite tools before starting
        self.operation = {
            "vector"    : "InteractionTool",
            "brush"     : "KritaShape/KisToolBrush",
            "transform" : "KisToolTransform",
            "color"     : "KritaSelected/KisToolColorSampler",
            "overlay"   : "ToolReferenceImages",
            "select"    : "KisToolSelectOutline",
            "camera"    : "PanTool",
        }

        # Krita
        self.krita_toolbox = list()  # ToolBox ( Install Event Filter )
        self.krita_eraser = None
        self.krita_action = list()
        self.krita_icon = list()

        # Tool Box Widget
        self.menu_vector = None
        self.menu_brush = None
        self.menu_transform = None
        self.menu_color = None
        self.menu_overlay = None
        self.menu_select = None
        self.menu_camera = None
        # Progress Bar Widget
        self.progress_bar = None
        # Actions Widget
        self.menu_mirror_fix = None
        self.menu_color_picker = None
        # Widgets Widget
        self.menu_tela = None

        # Index
        self.index_vector = "select_tool"
        self.index_brush = "freehand_brush"
        self.index_transform = "transform_tool"
        self.index_color = "sampler_tool"
        self.index_overlay = "reference_tool"
        self.index_select = "freehand_select"
        self.index_camera = "pan_tool"

        # Shelf
        self.shelf_action = list()
        self.shelf_preset = list()
        self.shelf_size = QSize( 25, 25 )
        self.shelf_margin = 30
        self.search_action = list()
        self.search_icon = list()
        # Resources
        self.resource_preset = list()

        # State Tela
        self.show_animation = False
        self.show_option = False
        self.show_extra = False
        self.show_information = False
        self.show_guide = False
        self.show_colorpicker = False
        self.hide_tela = False

        # Pushbutton Size
        self.pba = 35
        self.pbb = 28
        self.pbc = 20
        self.pbs = 5
        # Menu Margin
        self.mx = 10
        self.my = 10
        self.mi = 23 # 23 is the expected height of a self.qmenu item on windows at least

        # Menu
        self.press_time = 500 # 1000=1sec
        self.menu_hold = None

        # Color Picker Module
        self.pigmento_picker = None
        self.pigmento_picker_pyid = "pykrita_pigment_o_picker_docker"

        # ProgressBar
        self.krita_progress_bar_id = "ProgressBar"
        self.krita_progress_bar_module = None

        # Color Picker
        self.qpixmap_list = list()
        self.hue = 360 # 360
        self.svl = 255 # 255
        self.wheel_space = None # HSV HSL HCY ARD
        self.s1 = 0 # 0-360
        self.s2 = 0 # 0-255
        self.s3 = 0 # 0-255
        self.cor = None # Pigment.o color object

        # Icons
        self.icon_anim_cache = "clear"
        self.icon_anim_cleanup = "broken-preset"
        self.icon_mirrorfix = "wraparound"

        # Information
        self.work_hours = 0

        # Guides
        self.guide_mirror_h = False
        self.guide_mirror_v = False
        self.guide_list_h = list()
        self.guide_list_v = list()
        self.guide_ruler = False
        self.guide_snap = False
        self.guide_show = False
        self.guide_lock = False

        # Snap
        self.snap_all = False
    def Modules( self ):
        #region Notifier

        self.notifier = Krita.instance().notifier()
        self.notifier.applicationClosing.connect( self.Application_Closing )
        self.notifier.configurationChanged.connect( self.Configuration_Changed )
        self.notifier.imageClosed.connect( self.Image_Closed )
        self.notifier.imageCreated.connect( self.Image_Created )
        self.notifier.imageSaved.connect( self.Image_Saved )
        self.notifier.viewClosed.connect( self.View_Closed )
        self.notifier.viewCreated.connect( self.View_Created )
        self.notifier.windowCreated.connect( self.Window_Created )
        self.notifier.windowIsBeingCreated.connect( self.Window_IsBeingCreated )

        #endregion
        #region Color Picker

        self.color_display = Color_Display( self.ui_color_picker.color_display )
        self.color_panel = Color_Panel( self.ui_color_picker.color_panel )
        self.color_panel.SIGNAL_PREVIEW.connect( self.Color_Panel_Preview )
        self.color_panel.SIGNAL_APPLY.connect( self.Color_Panel_Apply )

        #endregion
    def Updater( self ):
        # Variables
        self.anim_delta = 0
        # QTimer
        self.qtimer_pulse = QtCore.QTimer( self )
        self.qtimer_pulse.timeout.connect( self.Update_Cycle )

    #endregion
    #region Management

    # Kritarc
    def Kritarc_Read( self, group, key, default, mode ):
        value = Krita.instance().readSetting( group, key, "" )
        invalid = [ "", None ]
        if value not in invalid:
            value = mode( value )
        else:
            value = default
            self.Kritarc_Write( group, key, default )
        return value
    def Kritarc_Write( self, group, key, value ):
        Krita.instance().writeSetting( group, key, str( value ) )

    # Warnnings
    def Message_Float( self, operation, message, icon ):
        ki = Krita.instance()
        string = f"TELA | { operation } { message }"
        try:ki.activeWindow().activeView().showFloatingMessage( string, ki.icon( icon ), 5000, 0 )
        except:pass
    # Math
    def Limit_Range( self, value, mini, maxi, minifix=0, maxifix=0 ):
        if value <= mini:   value = mini + minifix
        if value >= maxi:   value = maxi + maxifix
        return value
    # Canvas
    def Check_Canvas( self ):
        # Variables
        ki = Krita.instance()
        view = ki.activeWindow().activeView()
        canvas = view.canvas()
        # Return
        if ( canvas != None ) and ( view != None ): return True
        else:                                       return False
    # Progress Bar
    def ProgressBar_StyleSheet( self, percentage, background ):
        style_sheet = str()
        style_sheet += "QProgressBar { background-color: " + background + "; border-radius: 0px; }"
        style_sheet += "QProgressBar::chunk { background-color: " + percentage + "; }"
        return style_sheet

    # Troubleshooting
    def Inspect( self ):
        functions = list()
        ins = inspect.stack()
        for item in ins:
            functions.append( item[3] )
        QtCore.qDebug( f"Inspect = { functions }" )

    #endregion
    #region Widgets

    # Tela
    def Tela_Display( self ):
        # Main Window
        self.stacked_widget = self.window.qwindow().centralWidget()
        self.qmdiarea = self.stacked_widget.findChild( QMdiArea )
        self.qmdiarea.installEventFilter( self )

        # Display
        self.Interface_Create( self.qmdiarea )
        self.Geometry_Tela( self.show_animation, self.show_option, self.show_extra, self.hide_tela )

        # Progress_Bar
        self.Connect_Progress_Bar()

        # Color Picker
        self.ui_color_picker.setParent( self.qmdiarea )
        self.ui_color_picker.hide()
        # Information
        self.ui_information.setParent( self.qmdiarea )
        self.ui_information.hide()
        # Guide
        self.ui_guide.setParent( self.qmdiarea )
        self.ui_guide.hide()

        # Import Pigment.o module
        if self.pigmento_picker == None:
            self.Import_Pigment_O()
    def Tela_Button( self ):
        qwindow = Krita.instance().activeWindow().qwindow()
        # Vector Checks
        self.button_select_tool         = qwindow.findChild( QToolButton, self.tool["vector"]["select_tool"][1] )
        self.button_text_tool           = qwindow.findChild( QToolButton, self.tool["vector"]["text_tool"][1] )
        self.button_edit_tool           = qwindow.findChild( QToolButton, self.tool["vector"]["edit_tool"][1] )
        self.button_calligraphy_tool    = qwindow.findChild( QToolButton, self.tool["vector"]["calligraphy_tool"][1] )
        if self.krita_version == True:
            self.button_comic_tool      = qwindow.findChild( QToolButton, self.tool["vector"]["comic_tool"][1] )
        # Brush Checks
        self.button_freehand_brush      = qwindow.findChild( QToolButton, self.tool["brush"]["freehand_brush"][1] )
        self.button_line_brush          = qwindow.findChild( QToolButton, self.tool["brush"]["line_brush"][1] )
        self.button_rectangle_brush     = qwindow.findChild( QToolButton, self.tool["brush"]["rectangle_brush"][1] )
        self.button_ellipse_brush       = qwindow.findChild( QToolButton, self.tool["brush"]["ellipse_brush"][1] )
        self.button_polygon_brush       = qwindow.findChild( QToolButton, self.tool["brush"]["polygon_brush"][1] )
        self.button_polyline_brush      = qwindow.findChild( QToolButton, self.tool["brush"]["polyline_brush"][1] )
        self.button_bezier_brush        = qwindow.findChild( QToolButton, self.tool["brush"]["bezier_brush"][1] )
        self.button_path_brush          = qwindow.findChild( QToolButton, self.tool["brush"]["path_brush"][1] )
        self.button_dynamic_brush       = qwindow.findChild( QToolButton, self.tool["brush"]["dynamic_brush"][1] )
        self.button_multi_brush         = qwindow.findChild( QToolButton, self.tool["brush"]["multi_brush"][1] )
        # Transform Checks
        self.button_transform_tool      = qwindow.findChild( QToolButton, self.tool["transform"]["transform_tool"][1] )
        self.button_move_tool           = qwindow.findChild( QToolButton, self.tool["transform"]["move_tool"][1] )
        self.button_crop_tool           = qwindow.findChild( QToolButton, self.tool["transform"]["crop_tool"][1] )
        # Color Checks
        self.button_gradient_tool       = qwindow.findChild( QToolButton, self.tool["color"]["gradient_tool"][1] )
        self.button_sampler_tool        = qwindow.findChild( QToolButton, self.tool["color"]["sampler_tool"][1] )
        self.button_colorize_tool       = qwindow.findChild( QToolButton, self.tool["color"]["colorize_tool"][1] )
        self.button_patch_tool          = qwindow.findChild( QToolButton, self.tool["color"]["patch_tool"][1] )
        self.button_fill_tool           = qwindow.findChild( QToolButton, self.tool["color"]["fill_tool"][1] )
        self.button_enclose_tool        = qwindow.findChild( QToolButton, self.tool["color"]["enclose_tool"][1] )
        # Overlay Checks
        self.button_assistant_tool      = qwindow.findChild( QToolButton, self.tool["overlay"]["assistant_tool"][1] )
        self.button_measure_tool        = qwindow.findChild( QToolButton, self.tool["overlay"]["measure_tool"][1] )
        self.button_reference_tool      = qwindow.findChild( QToolButton, self.tool["overlay"]["reference_tool"][1] )
        # Selection Checks
        self.button_rectangle_select    = qwindow.findChild( QToolButton, self.tool["select"]["rectangle_select"][1] )
        self.button_elliptical_select   = qwindow.findChild( QToolButton, self.tool["select"]["elliptical_select"][1] )
        self.button_polygon_select      = qwindow.findChild( QToolButton, self.tool["select"]["polygon_select"][1] )
        self.button_freehand_select     = qwindow.findChild( QToolButton, self.tool["select"]["freehand_select"][1] )
        self.button_contiguous_select   = qwindow.findChild( QToolButton, self.tool["select"]["contiguous_select"][1] )
        self.button_color_select        = qwindow.findChild( QToolButton, self.tool["select"]["color_select"][1] )
        self.button_bezier_select       = qwindow.findChild( QToolButton, self.tool["select"]["bezier_select"][1] )
        self.button_magnetic_select     = qwindow.findChild( QToolButton, self.tool["select"]["magnetic_select"][1] )
        # Camera Checks
        self.button_zoom_tool           = qwindow.findChild( QToolButton, self.tool["camera"]["zoom_tool"][1] )
        self.button_pan_tool            = qwindow.findChild( QToolButton, self.tool["camera"]["pan_tool"][1] )
    def Tela_Filter_Install( self ):
        # Variables
        app = QApplication.instance()
        list_widget = app.allWidgets()
        list_key = list()
        # Krita
        key_a = self.tool.keys()
        for a in key_a:
            key_b = self.tool[a].keys()
            for b in key_b:
                item = self.tool[a][b][1]
                list_key.append( item )
        # Krita Toolbox
        for widget in list_widget:
            name = widget.objectName()
            if name in list_key:
                self.krita_toolbox.append( widget )
                widget.installEventFilter( self )
        # Krita Eraser
        for widget in list_widget:
            try:
                text = widget.text()
                if text == "Set eraser mode":
                    self.krita_eraser = widget
                    widget.installEventFilter( self )
                    break
            except:
                pass

        # Tela
        self.ui_color_picker.installEventFilter( self )
    def Tela_Load( self ):
        # Kritarc
        show_animation = self.Kritarc_Read( EXTENSION_NAME, "show_animation", self.show_animation, eval )
        show_option    = self.Kritarc_Read( EXTENSION_NAME, "show_option",    self.show_option,    eval )
        show_extra     = self.Kritarc_Read( EXTENSION_NAME, "show_extra",     self.show_extra,     eval )
        hide_tela      = self.Kritarc_Read( EXTENSION_NAME, "hide_tela",      self.hide_tela,      eval )
        # Tela Button
        self.menu_tela.blockSignals( True )
        self.menu_tela.setChecked( hide_tela )
        self.menu_tela.blockSignals( False )
        # Geometry
        self.Geometry_Tela( show_animation, show_option, show_extra, hide_tela )
        # Resources
        self.shelf_action = self.Kritarc_Read( EXTENSION_NAME, "shelf_action", self.shelf_action, eval )
        self.shelf_preset = self.Kritarc_Read( EXTENSION_NAME, "shelf_preset", self.shelf_preset, eval )
    # Tool
    def Tool_Update( self ):
        # Canvas
        check_canvas = self.Check_Canvas()
        if check_canvas == True:
            # Group
            if   self.button_select_tool.isChecked():           self.Tool_Apply( "vector",    "select_tool",       self.menu_vector )
            elif self.button_text_tool.isChecked():             self.Tool_Apply( "vector",    "text_tool",         self.menu_vector )
            elif self.button_edit_tool.isChecked():             self.Tool_Apply( "vector",    "edit_tool",         self.menu_vector )
            elif self.button_calligraphy_tool.isChecked():      self.Tool_Apply( "vector",    "calligraphy_tool",  self.menu_vector )
            elif self.krita_version and self.button_comic_tool.isChecked():
                self.Tool_Apply( "vector", "comic_tool", self.menu_vector )
            # Brush Checks
            elif self.button_freehand_brush.isChecked():        self.Tool_Apply( "brush",     "freehand_brush",    self.menu_brush )
            elif self.button_line_brush.isChecked():            self.Tool_Apply( "brush",     "line_brush",        self.menu_brush )
            elif self.button_rectangle_brush.isChecked():       self.Tool_Apply( "brush",     "rectangle_brush",   self.menu_brush )
            elif self.button_ellipse_brush.isChecked():         self.Tool_Apply( "brush",     "ellipse_brush",     self.menu_brush )
            elif self.button_polygon_brush.isChecked():         self.Tool_Apply( "brush",     "polygon_brush",     self.menu_brush )
            elif self.button_polyline_brush.isChecked():        self.Tool_Apply( "brush",     "polyline_brush",    self.menu_brush )
            elif self.button_bezier_brush.isChecked():          self.Tool_Apply( "brush",     "bezier_brush",      self.menu_brush )
            elif self.button_path_brush.isChecked():            self.Tool_Apply( "brush",     "path_brush",        self.menu_brush )
            elif self.button_dynamic_brush.isChecked():         self.Tool_Apply( "brush",     "dynamic_brush",     self.menu_brush )
            elif self.button_multi_brush.isChecked():           self.Tool_Apply( "brush",     "multi_brush",       self.menu_brush )
            # Transform Checks
            elif self.button_transform_tool.isChecked():        self.Tool_Apply( "transform", "transform_tool",    self.menu_transform )
            elif self.button_move_tool.isChecked():             self.Tool_Apply( "transform", "move_tool",         self.menu_transform )
            elif self.button_crop_tool.isChecked():             self.Tool_Apply( "transform", "crop_tool",         self.menu_transform )
            # Color Checks
            elif self.button_gradient_tool.isChecked():         self.Tool_Apply( "color",     "gradient_tool",     self.menu_color )
            elif self.button_sampler_tool.isChecked():          self.Tool_Apply( "color",     "sampler_tool",      self.menu_color )
            elif self.button_colorize_tool.isChecked():         self.Tool_Apply( "color",     "colorize_tool",     self.menu_color )
            elif self.button_patch_tool.isChecked():            self.Tool_Apply( "color",     "patch_tool",        self.menu_color )
            elif self.button_fill_tool.isChecked():             self.Tool_Apply( "color",     "fill_tool",         self.menu_color )
            elif self.button_enclose_tool.isChecked():          self.Tool_Apply( "color",     "enclose_tool",      self.menu_color )
            # Overlay Checks
            elif self.button_assistant_tool.isChecked():        self.Tool_Apply( "overlay",   "assistant_tool",    self.menu_overlay )
            elif self.button_measure_tool.isChecked():          self.Tool_Apply( "overlay",   "measure_tool",      self.menu_overlay )
            elif self.button_reference_tool.isChecked():        self.Tool_Apply( "overlay",   "reference_tool",    self.menu_overlay )
            # Selection Checks
            elif self.button_rectangle_select.isChecked():      self.Tool_Apply( "select",    "rectangle_select",  self.menu_select )
            elif self.button_elliptical_select.isChecked():     self.Tool_Apply( "select",    "elliptical_select", self.menu_select )
            elif self.button_polygon_select.isChecked():        self.Tool_Apply( "select",    "polygon_select",    self.menu_select )
            elif self.button_freehand_select.isChecked():       self.Tool_Apply( "select",    "freehand_select",   self.menu_select )
            elif self.button_contiguous_select.isChecked():     self.Tool_Apply( "select",    "contiguous_select", self.menu_select )
            elif self.button_color_select.isChecked():          self.Tool_Apply( "select",    "color_select",      self.menu_select )
            elif self.button_bezier_select.isChecked():         self.Tool_Apply( "select",    "bezier_select",     self.menu_select )
            elif self.button_magnetic_select.isChecked():       self.Tool_Apply( "select",    "magnetic_select",   self.menu_select )
            # Camera Checks
            elif self.button_zoom_tool.isChecked():             self.Tool_Apply( "camera",    "zoom_tool",         self.menu_camera )
            elif self.button_pan_tool.isChecked():              self.Tool_Apply( "camera",    "pan_tool",          self.menu_camera )
            # Error
            else:self.Message_Float( "ERROR", "new tool present ?", "broken-preset" )
            # Clean
            self.Geometry_Tela( self.show_animation, self.show_option, self.show_extra, self.hide_tela )
    def Tool_Apply( self, mode, tool, widget ):
        # Variables
        operation = self.tool[mode][tool][1]
        qicon = self.tool[mode][tool][2]
        if mode == "vector":    self.index_vector = tool
        if mode == "brush":     self.index_brush = tool
        if mode == "transform": self.index_transform = tool
        if mode == "color":     self.index_color = tool
        if mode == "overlay":   self.index_overlay = tool
        if mode == "select":    self.index_select = tool
        if mode == "camera":    self.index_camera = tool
        # Tool
        self.operation[mode] = operation
        # UI
        widget.setIcon( qicon )
        widget.setChecked( True )

    # Connect Krita UI with Tela
    def Connect_Progress_Bar( self ):
        self.krita_progress_bar = self.window.qwindow().statusBar().findChild( QProgressBar )
        self.krita_progress_bar.valueChanged.connect( self.Progress_Bar )

    # Interface
    def Interface_Create( self, parent ):
        #region Widgets

        # Variables
        bar = ( self.pba * 7 ) + ( self.pbs * 6 )

        # Animation
        self.anim_play          = QPushButton( "anim_play", parent )
        self.anim_onion         = QPushButton( "anim_onion", parent )
        self.anim_cache         = QPushButton( "anim_cache", parent )
        self.anim_cleanup       = QPushButton( "anim_cleanup", parent )
        self.anim_timeline      = QSlider( parent )
        # Tool Box
        self.menu_krita         = QPushButton( "menu_krita", parent )
        self.menu_vector        = QPushButton( "menu_vector", parent )
        self.menu_brush         = QPushButton( "menu_brush", parent )
        self.menu_transform     = QPushButton( "menu_transform", parent )
        self.menu_color         = QPushButton( "menu_color", parent )
        self.menu_overlay       = QPushButton( "menu_overlay", parent )
        self.menu_select        = QPushButton( "menu_select", parent )
        self.menu_camera        = QPushButton( "menu_camera", parent )
        self.menu_break         = QPushButton( "menu_break", parent )
        # Progress Bar
        self.progress_bar       = QProgressBar( parent )
        # Extras
        self.menu_information   = QPushButton( "menu_information", parent )
        self.menu_guide         = QPushButton( "menu_guide", parent )
        self.menu_color_picker  = QPushButton( "menu_color_picker", parent )
        self.menu_mirror_fix    = QPushButton( "menu_mirror_fix", parent )
        # Transform
        self.spt_free           = QPushButton( "spt_free", parent )
        self.spt_perspective    = QPushButton( "spt_perspective", parent )
        self.spt_warp           = QPushButton( "spt_warp", parent )
        self.spt_cage           = QPushButton( "spt_cage", parent )
        self.spt_liquify        = QPushButton( "spt_liquify", parent )
        self.spt_mesh           = QPushButton( "spt_mesh", parent )
        # Select
        self.sps_invert         = QPushButton( "sps_invert", parent )
        self.sps_all            = QPushButton( "sps_all", parent )
        self.sps_none           = QPushButton( "sps_none", parent )
        self.sps_overlay        = QPushButton( "sps_overlay", parent )
        # Hide
        self.menu_tela          = QPushButton( "hide", parent )

        # Animation
        self.Interface_Push_Button(  self.anim_play,         "anim_play",         self.pba, self.pbc, False, False, False )
        self.Interface_Push_Button(  self.anim_onion,        "anim_onion",        self.pba, self.pbc, False, False, False )
        self.Interface_Push_Button(  self.anim_cache,        "anim_cache",        self.pba, self.pbc, False, False, False )
        self.Interface_Push_Button(  self.anim_cleanup,      "anim_cleanup",      self.pba, self.pbc, False, False, False )
        self.Interface_Slider(       self.anim_timeline )
        # Tool Box
        self.Interface_Push_Button(  self.menu_krita,        "menu_krita",        self.pbc, self.pba, False, False, False )
        self.Interface_Push_Button(  self.menu_vector,       "menu_vector",       self.pba, self.pba, True,  True,  False )
        self.Interface_Push_Button(  self.menu_brush,        "menu_brush",        self.pba, self.pba, True,  True,  False )
        self.Interface_Push_Button(  self.menu_transform,    "menu_transform",    self.pba, self.pba, True,  True,  False )
        self.Interface_Push_Button(  self.menu_color,        "menu_color",        self.pba, self.pba, True,  True,  False )
        self.Interface_Push_Button(  self.menu_overlay,      "menu_overlay",      self.pba, self.pba, True,  True,  False )
        self.Interface_Push_Button(  self.menu_select,       "menu_select",       self.pba, self.pba, True,  True,  False )
        self.Interface_Push_Button(  self.menu_camera,       "menu_camera",       self.pba, self.pba, True,  True,  False )
        self.Interface_Push_Button(  self.menu_break,        "menu_break",        self.pbc, self.pba, False, False, False )
        # Progress Bar
        self.Interface_Progress_Bar( self.progress_bar,      "progress_bar",      bar,      self.pbs )
        # Extras
        self.Interface_Push_Button(  self.menu_information,  "menu_information",  self.pba, self.pba, True,  False, False )
        self.Interface_Push_Button(  self.menu_guide,        "menu_guide",        self.pba, self.pba, True,  False, False )
        self.Interface_Push_Button(  self.menu_color_picker, "menu_color_picker", self.pba, self.pba, True,  False, False )
        self.Interface_Push_Button(  self.menu_mirror_fix,   "menu_mirror_fix",   self.pba, self.pba, False, False, False )
        # Transform
        self.Interface_Push_Button(  self.spt_free,          "spt_free",          self.pba, self.pbb, False, False, False )
        self.Interface_Push_Button(  self.spt_perspective,   "spt_perspective",   self.pba, self.pbb, False, False, False )
        self.Interface_Push_Button(  self.spt_warp,          "spt_warp",          self.pba, self.pbb, False, False, False )
        self.Interface_Push_Button(  self.spt_cage,          "spt_cage",          self.pba, self.pbb, False, False, False )
        self.Interface_Push_Button(  self.spt_liquify,       "spt_liquify",       self.pba, self.pbb, False, False, False )
        self.Interface_Push_Button(  self.spt_mesh,          "spt_mesh",          self.pba, self.pbb, False, False, False )
        # Select
        self.Interface_Push_Button(  self.sps_invert,        "sps_invert",        self.pba, self.pbb, False, False, False )
        self.Interface_Push_Button(  self.sps_all,           "sps_all",           self.pba, self.pbb, False, False, False )
        self.Interface_Push_Button(  self.sps_none,          "sps_none",          self.pba, self.pbb, False, False, False )
        self.Interface_Push_Button(  self.sps_overlay,       "sps_overlay",       self.pba, self.pbb, False, False, False )
        # Hide
        self.Interface_Push_Button(  self.menu_tela,         "menu_tela",         50,       self.pbc, True,  False, True  )

        #endregion
        #region Connections

        # Animation
        self.anim_play.clicked.connect( self.Animation_Play )
        self.anim_onion.clicked.connect( self.Animation_Onion )
        self.anim_cache.clicked.connect( self.Animation_Cache )
        self.anim_cleanup.clicked.connect( self.Animation_Frame )
        self.anim_timeline.valueChanged.connect( self.Animation_Time )
        # Krita Menu
        self.menu_krita.pressed.connect( self.Hold_Krita )
        self.menu_krita.released.connect( self.Release_Krita )
        # Vector
        self.menu_vector.pressed.connect( self.Hold_Vector )
        self.menu_vector.released.connect( self.Release_Vector )
        # Brush
        self.menu_brush.pressed.connect( self.Hold_Brush )
        self.menu_brush.released.connect( self.Release_Brush )
        # Transform
        self.menu_transform.pressed.connect( self.Hold_Transform )
        self.menu_transform.released.connect( self.Release_Transform )
        # Color
        self.menu_color.pressed.connect( self.Hold_Color )
        self.menu_color.released.connect( self.Release_Color )
        # Overlay
        self.menu_overlay.pressed.connect( self.Hold_Overlay )
        self.menu_overlay.released.connect( self.Release_Overlay )
        # Select
        self.menu_select.pressed.connect( self.Hold_Select )
        self.menu_select.released.connect( self.Release_Select )
        # Camera
        self.menu_camera.pressed.connect( self.Hold_Camera )
        self.menu_camera.released.connect( self.Release_Camera )
        # Break
        self.menu_break.pressed.connect( self.Hold_Break )
        self.menu_break.released.connect( self.Release_Break )
        # Transform
        self.spt_free.clicked.connect( self.Transform_Free )
        self.spt_perspective.clicked.connect( self.Transform_Perspective )
        self.spt_warp.clicked.connect( self.Transform_Warp )
        self.spt_cage.clicked.connect( self.Transform_Cage )
        self.spt_liquify.clicked.connect( self.Transform_Liquify )
        self.spt_mesh.clicked.connect( self.Transform_Mesh )
        # Select
        self.sps_invert.clicked.connect( self.Select_Invert )
        self.sps_all.clicked.connect( self.Select_All )
        self.sps_none.clicked.connect( self.Select_None )
        self.sps_overlay.clicked.connect( self.Select_Overlay )
        # Extra Information
        self.menu_information.toggled.connect( self.Extra_Information )
        self.ui_information.info_title.textChanged.connect( self.Information_Save )
        self.ui_information.info_description.textChanged.connect( self.Information_Save )
        self.ui_information.info_subject.textChanged.connect( self.Information_Save )
        self.ui_information.info_keyword.textChanged.connect( self.Information_Save )
        self.ui_information.info_license.textChanged.connect( self.Information_Save )
        self.ui_information.menu_money_rate.valueChanged.connect( self.Money_Rate )
        self.ui_information.menu_money_total.valueChanged.connect( self.Money_Total )
        self.ui_information.info_contact.itemClicked.connect( self.Information_Copy )
        # Extra Guide
        self.menu_guide.toggled.connect( self.Extra_Guide )
        self.ui_guide.guide_mirror_h.toggled.connect( self.Guide_Mirror_Horizontal )
        self.ui_guide.guide_mirror_v.toggled.connect( self.Guide_Mirror_Vertical )
        self.ui_guide.guide_list_h.doubleClicked.connect( self.Guide_Value_Horizontal )
        self.ui_guide.guide_list_v.doubleClicked.connect( self.Guide_Value_Vertical )
        self.ui_guide.guide_ruler.toggled.connect( self.Guide_Ruler )
        self.ui_guide.guide_show.toggled.connect( self.Guide_Show )
        self.ui_guide.guide_snap.toggled.connect( self.Guide_Snap )
        self.ui_guide.guide_lock.toggled.connect( self.Guide_Lock )
        # Extra Color Picker
        self.menu_color_picker.toggled.connect( self.Extra_Color_Picker )
        self.ui_color_picker.s1.valueChanged.connect(   lambda: self.CS1_W( False ) )
        self.ui_color_picker.s1.sliderReleased.connect( lambda: self.CS1_W( True ) )
        self.ui_color_picker.s2.valueChanged.connect(   lambda: self.CS2_W( False ) )
        self.ui_color_picker.s2.sliderReleased.connect( lambda: self.CS2_W( True ) )
        self.ui_color_picker.s3.valueChanged.connect(   lambda: self.CS3_W( False ) )
        self.ui_color_picker.s3.sliderReleased.connect( lambda: self.CS3_W( True ) )
        # Hide
        self.menu_tela.toggled.connect( self.Hide_Tela )

        # Shelf
        self.ui_manage_shelf.shelf_remove.clicked.connect( self.Shelf_Remove )
        self.ui_manage_shelf.append_action.clicked.connect( self.Shelf_Action )
        self.ui_manage_shelf.append_icon.clicked.connect( self.Shelf_Icon )
        # Search
        self.ui_manage_shelf.search_action.textChanged.connect( self.Search_Action )
        self.ui_manage_shelf.search_icon.textChanged.connect( self.Search_Icon )

        #endregion
        #region Modules

        self.mirror_fix = MirrorFix_Button( self.menu_mirror_fix )
        self.mirror_fix.SIGNAL_SIDE.connect( self.MirrorFix_Side )
        self.mirror_fix.SIGNAL_NEUTRAL.connect( self.MirrorFix_Explanation )

        #endregion
        #region Theme

        # Style
        self.Style_Icon()
        self.Style_Theme()

        # Animation
        self.anim_play.setToolTip( "Play / Pause" )
        self.anim_onion.setToolTip( "Onion Skin" )
        self.anim_cache.setToolTip( "Clear Cache" )
        self.anim_cleanup.setToolTip( "Animation Cleanup" )
        # Tool Box
        self.menu_krita.setToolTip( "Krita Options" )
        self.menu_vector.setToolTip( "Vector" )
        self.menu_brush.setToolTip( "Brush" )
        self.menu_transform.setToolTip( "Transform" )
        self.menu_color.setToolTip( "Color" )
        self.menu_overlay.setToolTip( "Overlay" )
        self.menu_select.setToolTip( "Select" )
        self.menu_camera.setToolTip( "Camera" )
        self.menu_break.setToolTip( "Tela Options" )
        # Extras
        self.menu_information.setToolTip( "Information" )
        self.menu_guide.setToolTip( "Guide" )
        self.menu_color_picker.setToolTip( "Color Picker" )
        self.menu_mirror_fix.setToolTip( "Mirror Fix" )
        # Transform
        self.spt_free.setToolTip( "Free" )
        self.spt_perspective.setToolTip( "Perspective" )
        self.spt_warp.setToolTip( "Warp" )
        self.spt_cage.setToolTip( "Cage" )
        self.spt_liquify.setToolTip( "Liquify" )
        self.spt_mesh.setToolTip( "Mesh" )
        # Select
        self.sps_invert.setToolTip( "Invert" )
        self.sps_all.setToolTip( "Select All" )
        self.sps_none.setToolTip( "Deselect" )

        #endregion
    def Interface_Push_Button( self, button, name, pw, ph, check, exclusive, flat ):
        # Variables
        qsize = QSize( pw, ph )
        # QWidget
        button.setObjectName( name )
        button.setSizePolicy( QSizePolicy.Fixed, QSizePolicy.Fixed )
        button.setMinimumSize( qsize )
        button.setMaximumSize( qsize )
        button.setFocusPolicy( Qt.NoFocus )
        # QAbstract Button
        button.setText( "" )
        button.setCheckable( check )
        button.setAutoExclusive( exclusive )
        # QPushbutton
        button.setFlat( flat )
    def Interface_Progress_Bar( self, progress, name, pw, ph ):
        # Variables
        qsize = QSize( pw, ph )
        # QWidget
        progress.setObjectName( name )
        progress.setSizePolicy( QSizePolicy.Fixed, QSizePolicy.Fixed )
        progress.setMinimumSize( qsize )
        progress.setMaximumSize( qsize )
        progress.setFocusPolicy( Qt.NoFocus )
        # QProgress Bar
        progress.setMinimum( 0 )
        progress.setMaximum( 99 )
        progress.setValue( 0 )
        progress.setTextVisible( False )
    def Interface_Slider( self, slider ):
        slider.setOrientation( Qt.Horizontal )
        slider.setTickPosition( QSlider.TicksBelow )
    # Theme
    def Theme_Highlight( self, button, name, background, pen ):
        button.setStyleSheet( "#" + str( name ) + "::checked{ background-color : " + str( background ) + ";}" )
    def Theme_Slider( self, widget, handle, border, page_sub, page_add ):
        style_sheet = str()
        style_sheet += "QSlider::groove:horizontal { border: 1px solid; height: 2px; }"
        style_sheet += "QSlider::handle:horizontal { background-color: " + handle + "; width: 10px; height: 10px; margin: -5px 2px; border: 1px solid " + border + "; border-radius: 5px; }"
        style_sheet += "QSlider::sub-page:horizontal { background-color: " + page_sub + "; }" # Left Side
        style_sheet += "QSlider::add-page:horizontal { background-color: " + page_add + "; }" # Right Side
        widget.setStyleSheet( style_sheet )

    # Style
    def Style_Icon( self ):
        # Variables
        ki = Krita.instance()
        # Vector
        icon_select_tool = ki.icon( "select" )
        icon_text_tool = ki.icon( "draw-text" )
        icon_edit_tool = ki.icon( "shape_handling" )
        icon_calligraphy_tool = ki.icon( "calligraphy" )
        # Brush
        icon_freehand_brush = ki.icon( "krita_tool_freehand" )
        icon_line_brush = ki.icon( "krita_tool_line" )
        icon_rectangle_brush = ki.icon( "krita_tool_rectangle" )
        icon_ellipse_brush = ki.icon( "krita_tool_ellipse" )
        icon_polygon_brush = ki.icon( "krita_tool_polygon" )
        icon_polyline_brush = ki.icon( "polyline" )
        icon_bezier_brush = ki.icon( "krita_draw_path" )
        icon_path_brush = ki.icon( "krita_tool_freehandvector" )
        icon_dynamic_brush = ki.icon( "krita_tool_dyna" )
        icon_multi_brush = ki.icon( "krita_tool_multihand" )
        # Transform
        icon_transform_tool = ki.icon( "krita_tool_transform" )
        icon_move_tool = ki.icon( "krita_tool_move" )
        icon_crop_tool = ki.icon( "tool_crop" )
        # Color
        icon_gradient_tool = ki.icon( "krita_tool_gradient" )
        icon_sampler_tool = ki.icon( "krita_tool_color_sampler" )
        icon_colorize_tool = ki.icon( "krita_tool_lazybrush" )
        icon_patch_tool = ki.icon( "krita_tool_smart_patch" )
        icon_fill_tool = ki.icon( "krita_tool_color_fill" )
        icon_enclose_tool = ki.icon( "krita_tool_enclose_and_fill" )
        # Overlay
        icon_assistant_tool = ki.icon( "krita_tool_assistant" )
        icon_measure_tool = ki.icon( "krita_tool_measure" )
        icon_reference_tool = ki.icon( "krita_tool_reference_images" )
        # Select
        icon_rectangle_select = ki.icon( "tool_rect_selection" )
        icon_elliptical_select = ki.icon( "tool_elliptical_selection" )
        icon_polygon_select = ki.icon( "tool_polygonal_selection" )
        icon_freehand_select = ki.icon( "tool_outline_selection")
        icon_contiguous_select = ki.icon( "tool_contiguous_selection" )
        icon_color_select = ki.icon( "tool_similar_selection")
        icon_bezier_select = ki.icon( "tool_path_selection")
        icon_magnetic_select = ki.icon( "tool_magnetic_selection" )
        # Camera
        icon_zoom_tool = ki.icon( "tool_zoom" )
        icon_pan_tool = ki.icon( "tool_pan" )
        # Color Picker
        if self.pigmento_picker != None:    icon_color_picker = ki.icon( "krita_tool_ellipse" )
        else:                               icon_color_picker = ki.icon( "close-tab" )

        # Toolbox ( name, pykrita, qicon )
        self.tool["vector"]["select_tool"][2]       = icon_select_tool
        self.tool["vector"]["text_tool"][2]         = icon_text_tool
        self.tool["vector"]["edit_tool"][2]         = icon_edit_tool
        self.tool["vector"]["calligraphy_tool"][2]  = icon_calligraphy_tool
        # Brush
        self.tool["brush"]["freehand_brush"][2]     = icon_freehand_brush
        self.tool["brush"]["line_brush"][2]         = icon_line_brush
        self.tool["brush"]["rectangle_brush"][2]    = icon_rectangle_brush
        self.tool["brush"]["ellipse_brush"][2]      = icon_ellipse_brush
        self.tool["brush"]["polygon_brush"][2]      = icon_polygon_brush
        self.tool["brush"]["polyline_brush"][2]     = icon_polyline_brush
        self.tool["brush"]["bezier_brush"][2]       = icon_bezier_brush
        self.tool["brush"]["path_brush"][2]         = icon_path_brush
        self.tool["brush"]["dynamic_brush"][2]      = icon_dynamic_brush
        self.tool["brush"]["multi_brush"][2]        = icon_multi_brush
        # Transform
        self.tool["transform"]["transform_tool"][2] = icon_transform_tool
        self.tool["transform"]["move_tool"][2]      = icon_move_tool
        self.tool["transform"]["crop_tool"][2]      = icon_crop_tool
        # Color
        self.tool["color"]["gradient_tool"][2]      = icon_gradient_tool
        self.tool["color"]["sampler_tool"][2]       = icon_sampler_tool
        self.tool["color"]["colorize_tool"][2]      = icon_colorize_tool
        self.tool["color"]["patch_tool"][2]         = icon_patch_tool
        self.tool["color"]["fill_tool"][2]          = icon_fill_tool
        self.tool["color"]["enclose_tool"][2]       = icon_enclose_tool
        # Overlay
        self.tool["overlay"]["assistant_tool"][2]   = icon_assistant_tool
        self.tool["overlay"]["measure_tool"][2]     = icon_measure_tool
        self.tool["overlay"]["reference_tool"][2]   = icon_reference_tool
        # Select
        self.tool["select"]["rectangle_select"][2]  = icon_rectangle_select
        self.tool["select"]["elliptical_select"][2] = icon_elliptical_select
        self.tool["select"]["polygon_select"][2]    = icon_polygon_select
        self.tool["select"]["freehand_select"][2]   = icon_freehand_select
        self.tool["select"]["contiguous_select"][2] = icon_contiguous_select
        self.tool["select"]["color_select"][2]      = icon_color_select
        self.tool["select"]["bezier_select"][2]     = icon_bezier_select
        self.tool["select"]["magnetic_select"][2]   = icon_magnetic_select
        # Camera
        self.tool["camera"]["zoom_tool"][2]         = icon_zoom_tool
        self.tool["camera"]["pan_tool"][2]          = icon_pan_tool

        # Animation
        self.anim_play.setIcon(          ki.icon( "animation_play" ) )
        self.anim_onion.setIcon(         ki.icon( "onion_skin_options" ) )
        self.anim_cache.setIcon(         ki.icon( self.icon_anim_cache ) )
        self.anim_cleanup.setIcon(       ki.icon( self.icon_anim_cleanup ) )
        # Tool Box
        self.menu_krita.setIcon(         ki.icon( "hamburger_menu_dots" ) )
        self.menu_vector.setIcon(        self.tool["vector"][self.index_vector][2] )
        self.menu_brush.setIcon(         self.tool["brush"][self.index_brush][2] )
        self.menu_transform.setIcon(     self.tool["transform"][self.index_transform][2] )
        self.menu_color.setIcon(         self.tool["color"][self.index_color][2] )
        self.menu_overlay.setIcon(       self.tool["overlay"][self.index_overlay][2] )
        self.menu_select.setIcon(        self.tool["select"][self.index_select][2] )
        self.menu_camera.setIcon(        self.tool["camera"][self.index_camera][2] )
        self.menu_break.setIcon(         ki.icon( "hamburger_menu_dots" ) )
        # Extras
        self.menu_information.setIcon(   ki.icon( "selection-info" ) )
        self.menu_guide.setIcon(         ki.icon( "addlayer" ) )
        self.menu_color_picker.setIcon(  icon_color_picker )
        self.menu_mirror_fix.setIcon(    ki.icon( self.icon_mirrorfix ) )
        # Transform
        self.spt_free.setIcon(           ki.icon( "transform_icons_main" ) )
        self.spt_perspective.setIcon(    ki.icon( "transform_icons_perspective" ) )
        self.spt_warp.setIcon(           ki.icon( "transform_icons_warp" ) )
        self.spt_cage.setIcon(           ki.icon( "transform_icons_cage" ) )
        self.spt_liquify.setIcon(        ki.icon( "transform_icons_liquify_main" ) )
        self.spt_mesh.setIcon(           ki.icon( "transform_icons_mesh" ) )
        # Select
        self.sps_invert.setIcon(         ki.icon( "select-invert" ) )
        self.sps_all.setIcon(            ki.icon( "select-all" ) )
        self.sps_none.setIcon(           ki.icon( "select-clear" ) )
        self.sps_overlay.setIcon(        ki.icon( "selection-mode_mask" ) ) # selection-mode_ants
        # Hide
        self.menu_tela.setIcon(          ki.icon( "arrow-up" ) )

        # Manager
        self.ui_manage_shelf.shelf_remove.setIcon(  ki.icon( "arrow-right" ) )
        self.ui_manage_shelf.append_action.setIcon( ki.icon( "arrow-left" ) )
        self.ui_manage_shelf.append_icon.setIcon(   ki.icon( "arrow-left" ) )
    def Style_Theme( self ):
        # Read
        palette = QApplication.palette()
        base = palette.base().color()
        # Window
        w_alternate     = palette.alternateBase().color().name()
        w_base          = palette.base().color().name()
        w_button        = palette.button().color().name()
        w_dark          = palette.dark().color().name()
        w_light         = palette.light().color().name()
        w_mid           = palette.mid().color().name()
        w_midlight      = palette.midlight().color().name()
        w_shadow        = palette.shadow().color().name()
        w_tool_tip      = palette.toolTipBase().color().name()
        w_window        = palette.window().color().name()
        # Text
        t_bright        = palette.brightText().color().name()
        t_button        = palette.buttonText().color().name()
        t_highlighted   = palette.highlightedText().color().name()
        t_placeholder   = palette.placeholderText().color().name()
        t_text          = palette.text().color().name()
        t_tool_tip      = palette.toolTipText().color().name()
        t_window        = palette.windowText().color().name()
        # Color
        c_highlight     = palette.highlight().color().name()
        c_link          = palette.link().color().name()
        c_visited       = palette.linkVisited().color().name()
        # c_accent        = palette.accent().color().name() # qt6
        a_black         = "#00000000"

        # Colors
        win = palette.window().color().getHsvF()
        hue = palette.highlight().color().getHsvF()
        but = palette.button().color().getHsvF()
        if win[2] > 0.5:    h3 = -0.3; p3 = -0.1 # Light Theme
        else:               h3 = +0.3; p3 = +0.1 # Dark Theme
        handle = QColor().fromHsvF( but[0], but[1], but[2] + h3 ).name()
        page   = QColor().fromHsvF( but[0], but[1], but[2] + p3 ).name()

        # QPushbuttons
        self.Theme_Highlight( self.menu_vector,       "menu_vector",    c_highlight, t_bright )
        self.Theme_Highlight( self.menu_brush,        "menu_brush",     c_highlight, t_bright )
        self.Theme_Highlight( self.menu_transform,    "menu_transform", c_highlight, t_bright )
        self.Theme_Highlight( self.menu_color,        "menu_color",     c_highlight, t_bright )
        self.Theme_Highlight( self.menu_overlay,      "menu_overlay",   c_highlight, t_bright )
        self.Theme_Highlight( self.menu_select,       "menu_select",    c_highlight, t_bright )
        self.Theme_Highlight( self.menu_camera,       "menu_camera",    c_highlight, t_bright )
        # Progress Bar
        progress_bar_style_sheet = self.ProgressBar_StyleSheet( c_highlight, a_black )
        self.progress_bar.setStyleSheet( progress_bar_style_sheet )
        # Extra
        self.Theme_Highlight( self.menu_information,  "information",    c_highlight, t_bright )
        self.Theme_Highlight( self.menu_guide,        "guide",          c_highlight, t_bright )
        self.Theme_Highlight( self.menu_color_picker, "color_picker",   c_highlight, t_bright )
        self.Theme_Highlight( self.menu_mirror_fix,   "mirror_fix",     c_highlight, t_bright )

        # Color_Picker
        self.Theme_Slider( self.ui_color_picker.s1, handle, w_mid, page, page )
        self.Theme_Slider( self.ui_color_picker.s2, handle, w_mid, page, page )
        self.Theme_Slider( self.ui_color_picker.s3, handle, w_mid, page, page )
        self.ui_color_picker.setStyleSheet( "#color_picker{ background-color: " + w_button + "; }" )

    # Geometry
    def Size_Update( self ):
        if self.qmdiarea != None:
            # Geometry
            self.Geometry_Tela( self.show_animation, self.show_option, self.show_extra, self.hide_tela )
            # Information
            if self.show_information == True:
                self.Geometry_Information()
            # Guide
            if self.show_guide == True:
                self.Geometry_Guide()
            # Color Picker
            if self.show_colorpicker == True:
                wcp = self.ui_color_picker
                cp_w = wcp.width()
                cp_h = wcp.height()
                qpoint = self.menu_color_picker.geometry().topLeft()
                cp_x = qpoint.x()
                cp_y = qpoint.y() - cp_h - self.my
                self.Geometry_Picker( cp_x, cp_y, cp_w, cp_h )
    # Show Geometry
    def Show_Animation( self, boolean ):
        self.show_animation = boolean
        self.Update_Pulse()
        self.Geometry_Tela( boolean, self.show_option, self.show_extra, self.hide_tela )
        self.Kritarc_Write( EXTENSION_NAME, "show_animation", boolean )
    def Show_Option( self, boolean ):
        self.show_option = boolean
        self.Geometry_Tela( self.show_animation, boolean, self.show_extra, self.hide_tela )
        self.Kritarc_Write( EXTENSION_NAME, "show_option", boolean )
    def Show_Extra( self, boolean ):
        self.show_extra = boolean
        self.Geometry_Tela( self.show_animation, self.show_option, boolean, self.hide_tela )
        if boolean == False:
            self.Menu_Hide()
            self.Menu_False()
        self.Kritarc_Write( EXTENSION_NAME, "show_extra", boolean )
    # Show Extras
    def Extra_Information( self, boolean ):
        self.show_information = boolean
        if boolean == True:
            self.Menu_Reset()
            self.Size_Update()
            self.Information_Read()
            self.Extra_Exclusive( "information" )
            self.ui_information.show()
        else:
            self.ui_information.hide()
    def Extra_Guide( self, boolean ):
        self.show_guide = boolean
        self.Update_Pulse()
        if boolean == True:
            self.Menu_Reset()
            self.Size_Update()
            self.Extra_Exclusive( "guide" )
            self.ui_guide.show()
        else:
            self.ui_guide.hide()
    def Extra_Color_Picker( self, boolean ):
        self.show_colorpicker = boolean
        if boolean == True:
            self.Menu_Reset()
            self.Size_Update()
            self.Color_READ()
            self.Extra_Exclusive( "color_picker" )
            self.ui_color_picker.show()
        else:
            self.ui_color_picker.hide()
    def Extra_Exclusive( self, widget ):
        if widget != "information":     self.menu_information.setChecked( False )
        if widget != "guide":           self.menu_guide.setChecked( False )
        if widget != "color_picker":    self.menu_color_picker.setChecked( False )

    # Tela Geometry
    def Hide_Tela( self, boolean ):
        self.Geometry_Tela( self.show_animation, self.show_option, self.show_extra, boolean )
        if boolean == True:
            self.Menu_Hide()
            self.Menu_False()
        self.Kritarc_Write( EXTENSION_NAME, "hide_tela", boolean )
    def Geometry_Tela( self, show_animation, show_option, show_extra, hide_tela ):
        # Size Update
        self.show_animation = show_animation
        self.show_option = show_option
        self.show_extra = show_extra
        self.hide_tela = hide_tela

        # Geormetry
        if self.qmdiarea != None:
            # Canvas
            qmd_w = self.qmdiarea.width()
            qmd_h = self.qmdiarea.height()
            # Levels
            la = 120
            lb = la + 30
            lt = 90
            lp = 55
            lo = 50
            # Variables
            short = 20
            wide = 50
            offscreen = 200
            # Calculations
            w2 = ( self.pba * 2 ) + ( self.pbs * 1 )
            w3 = ( self.pba * 3 ) + ( self.pbs * 2 )
            w4 = ( self.pba * 4 ) + ( self.pbs * 3 )
            w5 = ( self.pba * 5 ) + ( self.pbs * 4 )
            w6 = ( self.pba * 6 ) + ( self.pbs * 5 )
            w7 = ( self.pba * 7 ) + ( self.pbs * 6 )
            px2 = qmd_w * 0.5 - w2 * 0.5
            px3 = qmd_w * 0.5 - w3 * 0.5
            px4 = qmd_w * 0.5 - w4 * 0.5
            px5 = qmd_w * 0.5 - w5 * 0.5
            px6 = qmd_w * 0.5 - w6 * 0.5
            px7 = qmd_w * 0.5 - w7 * 0.5
            pxk = px7 - self.pbc*1 - self.pbs*1
            d0 = int( hide_tela * offscreen )

            # Animation
            if self.show_animation == True: da = d0
            else:                           da = offscreen
            # Sub Panel Transform
            check_transform = self.show_option == True and self.menu_transform.isChecked() == True and self.index_transform == "transform_tool"
            if check_transform == True:     dt = d0
            else:                           dt = offscreen
            # Sub Panel Select
            check_select = self.show_option == True and self.menu_select.isChecked() == True # all select tools have the same options
            if check_select == True:        ds = d0
            else:                           ds = offscreen
            # Extra
            if self.show_extra == True:     de = d0
            else:                           de = offscreen

            # Animation
            self.anim_play.setGeometry(         int( px7 + self.pba*0 + self.pbs*0 ), int( qmd_h-lb+da ),    self.pba,  self.pbc )
            self.anim_onion.setGeometry(        int( px7 + self.pba*4 + self.pbs*4 ), int( qmd_h-lb+da ),    self.pba,  self.pbc )
            self.anim_cache.setGeometry(        int( px7 + self.pba*5 + self.pbs*5 ), int( qmd_h-lb+da ),    self.pba,  self.pbc )
            self.anim_cleanup.setGeometry(      int( px7 + self.pba*6 + self.pbs*6 ), int( qmd_h-lb+da ),    self.pba,  self.pbc )
            self.anim_timeline.setGeometry(     int( px7 ),                           int( qmd_h-la+da ),    int( w7 ), short )
            # Tool Box
            self.menu_krita.setGeometry(        int( pxk ),                           int( qmd_h-lt+d0 ),    self.pbc,  self.pba )
            self.menu_vector.setGeometry(       int( px7 ),                           int( qmd_h-lt+d0 ),    self.pba,  self.pba )
            self.menu_brush.setGeometry(        int( px7 + self.pba*1 + self.pbs*1 ), int( qmd_h-lt+d0 ),    self.pba,  self.pba )
            self.menu_transform.setGeometry(    int( px7 + self.pba*2 + self.pbs*2 ), int( qmd_h-lt+d0 ),    self.pba,  self.pba )
            self.menu_color.setGeometry(        int( px7 + self.pba*3 + self.pbs*3 ), int( qmd_h-lt+d0 ),    self.pba,  self.pba )
            self.menu_overlay.setGeometry(      int( px7 + self.pba*4 + self.pbs*4 ), int( qmd_h-lt+d0 ),    self.pba,  self.pba )
            self.menu_select.setGeometry(       int( px7 + self.pba*5 + self.pbs*5 ), int( qmd_h-lt+d0 ),    self.pba,  self.pba )
            self.menu_camera.setGeometry(       int( px7 + self.pba*6 + self.pbs*6 ), int( qmd_h-lt+d0 ),    self.pba,  self.pba )
            self.menu_break.setGeometry(        int( px7 + self.pba*7 + self.pbs*7 ), int( qmd_h-lt+d0 ),    self.pbc,  self.pba )
            # Progress Bar
            self.progress_bar.setGeometry(      int( px7 ),                           int( qmd_h-lp+d0 ),    int( w7 ), self.pbs )
            # Extras
            self.menu_information.setGeometry(  int( px7 + self.pba*8 + self.pbs*8 ), int( qmd_h-lt+de ),    self.pba,  self.pba )
            self.menu_guide.setGeometry(        int( px7 + self.pba*9 + self.pbs*9 ), int( qmd_h-lt+de ),    self.pba,  self.pba )
            self.menu_color_picker.setGeometry( int( px7 + self.pba*10+ self.pbs*10), int( qmd_h-lt+de ),    self.pba,  self.pba )
            self.menu_mirror_fix.setGeometry(   int( px7 + self.pba*8 + self.pbs*8 ), int( qmd_h-lo+de ),    self.pba,  self.pba )
            # Transform
            self.spt_free.setGeometry(          int( px6 ),                           int( qmd_h-lo+dt ),    self.pba,  self.pbb )
            self.spt_perspective.setGeometry(   int( px6 + self.pba*1 + self.pbs*1 ), int( qmd_h-lo+dt ),    self.pba,  self.pbb )
            self.spt_warp.setGeometry(          int( px6 + self.pba*2 + self.pbs*2 ), int( qmd_h-lo+dt ),    self.pba,  self.pbb )
            self.spt_cage.setGeometry(          int( px6 + self.pba*3 + self.pbs*3 ), int( qmd_h-lo+dt ),    self.pba,  self.pbb )
            self.spt_liquify.setGeometry(       int( px6 + self.pba*4 + self.pbs*4 ), int( qmd_h-lo+dt ),    self.pba,  self.pbb )
            self.spt_mesh.setGeometry(          int( px6 + self.pba*5 + self.pbs*5 ), int( qmd_h-lo+dt ),    self.pba,  self.pbb )
            # Select
            self.sps_invert.setGeometry(        int( px4 ),                           int( qmd_h-lo+ds ),    self.pba,  self.pbb )
            self.sps_all.setGeometry(           int( px4 + self.pba*1 + self.pbs*1 ), int( qmd_h-lo+ds ),    self.pba,  self.pbb )
            self.sps_none.setGeometry(          int( px4 + self.pba*2 + self.pbs*2 ), int( qmd_h-lo+ds ),    self.pba,  self.pbb )
            self.sps_overlay.setGeometry(       int( px4 + self.pba*3 + self.pbs*3 ), int( qmd_h-lo+ds ),    self.pba,  self.pbb )
            # Hide
            self.menu_tela.setGeometry(         int( qmd_w*0.5-wide*0.5 ),            int( qmd_h-self.pbc ), wide,      self.pba )
    # Extra Geometry
    def Geometry_Information( self ):
        wi = self.ui_information
        ww = wi.width()
        wh = wi.height()
        qpoint = self.menu_information.geometry().topLeft()
        px = qpoint.x()
        py = qpoint.y() - wh - self.my
        self.ui_information.setGeometry( int( px ), int( py ), int( ww ), int( wh ) )
    def Geometry_Guide( self ):
        wi = self.ui_guide
        ww = wi.width()
        wh = wi.height()
        qpoint = self.menu_guide.geometry().topLeft()
        px = qpoint.x()
        py = qpoint.y() - wh - self.my
        self.ui_guide.setGeometry( int( px ), int( py ), int( ww ), int( wh ) )
    def Picker_to_Cursor( self ):
        if self.qmdiarea != None:
            # Cursor
            position = QCursor().pos()
            cx = int( position.x() )
            cy = int( position.y() )
            # Canvas
            delta = self.qmdiarea.mapFromGlobal( QPoint( 0, 0 ) )
            dx = delta.x()
            dy = delta.y()
            # Widget
            widget = self.ui_color_picker
            ww = widget.width()
            wh = widget.height()
            # Color Panel
            colorpanel = self.ui_color_picker.color_panel
            cpx = colorpanel.x()
            cpy = colorpanel.y()
            cpw = colorpanel.width()
            cph = colorpanel.height()
            cp_cx = int( cpw * self.s2 )
            cp_cy = int( cph - cph * self.s3 )
            cp_cx = self.Limit_Range( cp_cx, 0, cpw, 0, -1 )
            cp_cy = self.Limit_Range( cp_cy, 0, cph, 0, -1 )

            # Relocate Color Picker
            self.Geometry_Picker( cx+dx-cpx-cp_cx, cy+dy-cpy-cp_cy, ww, wh )
            # Toggle Visibility
            check_visible = self.ui_color_picker.isVisible()
            if check_visible == False:      self.ui_color_picker.setVisible( True )
            else:                           self.ui_color_picker.setVisible( False )
    def Geometry_Picker( self, px, py, ww, wh ):
        self.ui_color_picker.setGeometry( px, py, ww, wh )

    #endregion
    #region ToolBox

    # Updates
    def Update_Pulse( self ):
        # Color Picker was opted out not to update like this
        boolean = ( self.show_animation == True ) or ( self.show_guide == True )
        if boolean == True:     self.qtimer_pulse.start( self.check_timer )
        if boolean == False:    self.qtimer_pulse.stop()
    def Update_Cycle( self ):
        try:check_canvas = self.Check_Canvas()
        except:check_canvas = False
        if check_canvas == True:
            ki = Krita.instance()
            ad = ki.activeDocument()
            if self.show_animation == True:     self.Update_Animation( ad )
            if self.show_guide == True:         self.Update_Guide( ki, ad )
    def Update_Animation( self, ad ):
        # Read
        anim_ctime = ad.currentTime()
        anim_stime = ad.playBackStartTime()
        anim_etime = ad.playBackEndTime()
        self.anim_delta = anim_stime
        # Update
        if self.anim_ctime != anim_ctime or self.anim_stime != anim_stime or self.anim_etime != anim_etime:
            self.anim_ctime = anim_ctime
            self.anim_stime = anim_stime
            self.anim_etime = anim_etime
            self.anim_timeline.blockSignals( True )
            self.anim_timeline.setValue( self.anim_ctime - self.anim_delta )
            self.anim_timeline.setMinimum( self.anim_stime - self.anim_delta )
            self.anim_timeline.setMaximum( self.anim_etime - self.anim_delta )
            self.anim_timeline.blockSignals( False )
    def Update_Guide( self, ki, ad ):
            # Read Document
            guide_config = ad.guidesConfig()
            guide_list_h = guide_config.horizontalGuides()
            guide_list_v = guide_config.verticalGuides()
            guide_ruler = ki.action( "view_ruler" ).isChecked()
            guide_show = ki.action( "view_show_guides" ).isChecked()
            guide_snap = ki.action( "view_snap_to_guides" ).isChecked()
            guide_lock = ki.action( "view_lock_guides" ).isChecked()
            # Correct lists error range
            for i in range( 0, len( guide_list_h ) ):
                guide_list_h[i] = round( guide_list_h[i] )
            for i in range( 0, len( guide_list_v ) ):
                guide_list_v[i] = round( guide_list_v[i] )
            guide_list_h.sort()
            guide_list_v.sort()
            # Update Document
            if self.guide_list_h != guide_list_h:
                self.Guide_UI_List_H( ad, guide_list_h )
            if self.guide_list_v != guide_list_v:
                self.Guide_UI_List_V( ad, guide_list_v )
            if self.guide_ruler != guide_ruler:
                self.guide_ruler = guide_ruler
                self.Guide_Ruler( guide_ruler )
                self.Guide_UI_Ruler( guide_ruler )
            if self.guide_show != guide_show:
                self.guide_show = guide_show
                self.Guide_Show( guide_show )
                self.Guide_UI_Show( guide_show )
            if self.guide_snap != guide_snap:
                self.guide_snap = guide_snap
                self.Guide_Snap( guide_snap )
                self.Guide_UI_Snap( guide_snap )
            if self.guide_lock != guide_lock:
                self.guide_lock = guide_lock
                self.Guide_Lock( guide_lock )
                self.Guide_UI_Lock( guide_lock )

    # Krita
    def Hold_Krita( self ):
        self.Menu_Reset()
        self.Timer_Start( self.Menu_Krita )
    def Release_Krita( self ):
        self.Menu_Reset()
    def Menu_Krita( self ):
        # Variables
        widget = self.menu_krita
        ki = Krita.instance()
        ad = ki.activeDocument()

        # Read State
        view_canvas_ui = ki.action( "view_show_canvas_only" ).isChecked()
        view_docker_ui = ki.action( "view_toggledockers" ).isChecked()
        # Read Layer
        layer_isolate = ki.action( "isolate_active_layer" ).isChecked()
        # Read Canvas
        canvas_mirror = ki.action( "mirror_canvas" ).isChecked()
        canvas_wrap = ki.action( "wrap_around_mode" ).isChecked()
        canvas_grid = ki.action( "view_pixel_grid" ).isChecked()
        # Read Guides
        guide_ruler = ki.action( "view_ruler" ).isChecked()
        guide_snap = ki.action( "view_snap_to_guides" ).isChecked()
        guide_show = ad.guidesVisible()
        guide_lock = ad.guidesLocked()
        # Read View
        view_painting_assistant = ki.action( "view_toggle_painting_assistants" ).isChecked()
        view_assitant_preview = ki.action( "view_toggle_assistant_previews" ).isChecked()
        view_reference_image = ki.action( "view_toggle_reference_images" ).isChecked()
        # Read Snap
        snap_to_guides = ki.action( "view_snap_to_guides" ).isChecked()
        snap_to_grid = ki.action( "view_snap_to_grid" ).isChecked()
        snap_to_pixel = ki.action( "view_snap_to_pixel" ).isChecked()
        snap_orthogonal = ki.action( "view_snap_orthogonal" ).isChecked()
        snap_node = ki.action( "view_snap_node" ).isChecked()
        snap_extension = ki.action( "view_snap_extension" ).isChecked()
        snap_intersection = ki.action( "view_snap_intersection" ).isChecked()
        snap_bounding_box = ki.action( "view_snap_bounding_box" ).isChecked()
        snap_image_bounds = ki.action( "view_snap_image_bounds" ).isChecked()
        snap_image_center = ki.action( "view_snap_image_center" ).isChecked()
        if self.snap_all == False:  snap_string = "Snap All"
        else:                       snap_string = "Snap None"

        # Menu
        self.qmenu = QMenu()

        # State
        action_view_canvas_ui = self.qmenu.addAction( "View Canvas" )
        action_view_canvas_ui.setCheckable( True )
        action_view_canvas_ui.setChecked( view_canvas_ui )
        action_view_docker_ui = self.qmenu.addAction( "View Dockers" )
        action_view_docker_ui.setCheckable( True )
        action_view_docker_ui.setChecked( view_docker_ui )
        # Layers
        action_layer_isolate = self.qmenu.addAction( "Layer Isolate" )
        action_layer_isolate.setCheckable( True )
        action_layer_isolate.setChecked( layer_isolate )
        # Canvas
        menu_canvas = self.qmenu.addMenu( "Canvas" )
        action_canvas_mirror = menu_canvas.addAction( "Mirror" )
        action_canvas_wrap = menu_canvas.addAction( "Wrap" )
        action_canvas_mirror.setCheckable( True )
        action_canvas_wrap.setCheckable( True )
        action_canvas_mirror.setChecked( canvas_mirror )
        action_canvas_wrap.setChecked( canvas_wrap )
        # View
        menu_view = self.qmenu.addMenu( "View" )
        action_view_painting_assistant = menu_view.addAction( "Painting Assistant" )
        action_view_assitant_preview = menu_view.addAction( "Assistant Preview" )
        action_view_reference_image = menu_view.addAction( "Reference Image" )
        action_view_painting_assistant.setCheckable( True )
        action_view_assitant_preview.setCheckable( True )
        action_view_reference_image.setCheckable( True )
        action_view_painting_assistant.setChecked( view_painting_assistant )
        action_view_assitant_preview.setChecked( view_assitant_preview )
        action_view_reference_image.setChecked( view_reference_image )
        # Snap
        menu_snap = self.qmenu.addMenu( "Snap" )
        action_snap_guide = menu_snap.addAction( "Guide" )
        action_snap_grid = menu_snap.addAction( "Grid" )
        action_snap_pixel = menu_snap.addAction( "Pixel" )
        action_snap_ortogonal = menu_snap.addAction( "Ortogonal" )
        action_snap_node = menu_snap.addAction( "Node" )
        action_snap_extension = menu_snap.addAction( "Extension" )
        action_snap_intersection = menu_snap.addAction( "intersection" )
        action_snap_bounding_box = menu_snap.addAction( "Bounding Box" )
        action_snap_image_bounds = menu_snap.addAction( "Image Bounds" )
        action_snap_image_center = menu_snap.addAction( "Image Center" )
        menu_snap.addSeparator()
        action_snap_all = menu_snap.addAction( snap_string )
        action_snap_guide.setCheckable( True )
        action_snap_grid.setCheckable( True )
        action_snap_pixel.setCheckable( True )
        action_snap_ortogonal.setCheckable( True )
        action_snap_node.setCheckable( True )
        action_snap_extension.setCheckable( True )
        action_snap_intersection.setCheckable( True )
        action_snap_bounding_box.setCheckable( True )
        action_snap_image_bounds.setCheckable( True )
        action_snap_image_center.setCheckable( True )
        action_snap_all.setCheckable( True )
        action_snap_guide.setChecked( snap_to_guides )
        action_snap_grid.setChecked( snap_to_grid )
        action_snap_pixel.setChecked( snap_to_pixel )
        action_snap_ortogonal.setChecked( snap_orthogonal )
        action_snap_node.setChecked( snap_node )
        action_snap_extension.setChecked( snap_extension )
        action_snap_intersection.setChecked( snap_intersection )
        action_snap_bounding_box.setChecked( snap_bounding_box )
        action_snap_image_bounds.setChecked( snap_image_bounds )
        action_snap_image_center.setChecked( snap_image_center )
        action_snap_all.setChecked( self.snap_all )

        # Mapping
        item = 6
        height = self.mi * item + self.my
        qpoint = widget.geometry().topLeft()
        pos = self.qmdiarea.mapToGlobal( qpoint )
        point = QPoint( pos.x(), pos.y() - height )
        action = self.qmenu.exec_( point )

        # State
        if action == action_view_canvas_ui:             self.View_Canvas_UI()
        if action == action_view_docker_ui:             self.View_Docker_UI()
        # Layers
        if action == action_layer_isolate:              self.Layer_Isolate()
        # Canvas
        if action == action_canvas_mirror:              self.Canvas_Mirror()
        if action == action_canvas_wrap:                self.Canvas_Wrap()
        # View
        if action == action_view_painting_assistant:    self.View_Painting_Assistant()
        if action == action_view_assitant_preview:      self.View_Assistant_Preview()
        if action == action_view_reference_image:       self.View_Reference_Image()
        # Snap
        if action == action_snap_guide:                 self.Snap_Guide()
        if action == action_snap_grid:                  self.Snap_Grid()
        if action == action_snap_pixel:                 self.Snap_Pixel()
        if action == action_snap_ortogonal:             self.Snap_Ortogonal()
        if action == action_snap_node:                  self.Snap_Node()
        if action == action_snap_extension:             self.Snap_Extension()
        if action == action_snap_intersection:          self.Snap_Intersection()
        if action == action_snap_bounding_box:          self.Snap_Bounding_Box()
        if action == action_snap_image_bounds:          self.Snap_Image_Bounds()
        if action == action_snap_image_center:          self.Snap_Image_Center()
        if action == action_snap_all:                   self.Snap_All( not self.snap_all )

        # Clean up
        self.Menu_Down()
    # Break
    def Hold_Break( self ):
        self.Menu_Reset()
        self.Timer_Start( self.Menu_Break )
    def Release_Break( self ):
        self.Menu_Reset()
    def Menu_Break( self ):
        # Variables
        widget = self.menu_break
        # Menu
        self.qmenu = QMenu()
        # Animation
        action_show_animation = self.qmenu.addAction( "Show Animation" )
        action_show_animation.setCheckable( True )
        action_show_animation.setChecked( self.show_animation )
        # Option
        action_show_option = self.qmenu.addAction( "Show Option" )
        action_show_option.setCheckable( True )
        action_show_option.setChecked( self.show_option )
        # Extra
        action_show_extra = self.qmenu.addAction( "Show Extra" )
        action_show_extra.setCheckable( True )
        action_show_extra.setChecked( self.show_extra )
        # Mapping
        item = 3
        height = self.mi * item + self.my
        qpoint = widget.geometry().topLeft()
        pos = self.qmdiarea.mapToGlobal( qpoint )
        point = QPoint( pos.x(), pos.y() - height )
        action = self.qmenu.exec_( point )
        # Action
        if action == action_show_animation: self.Show_Animation( not self.show_animation )
        if action == action_show_option:    self.Show_Option( not self.show_option )
        if action == action_show_extra:     self.Show_Extra( not self.show_extra )
        # Clean up
        self.Menu_Down()

    # Hold
    def Hold_Vector( self ):
        self.Menu_Reset()
        self.Timer_Start( self.Menu_Vector )
    def Hold_Brush( self ):
        self.Menu_Reset()
        self.Timer_Start( self.Menu_Brush )
    def Hold_Transform( self ):
        self.Menu_Reset()
        self.Timer_Start( self.Menu_Transform )
    def Hold_Color( self ):
        self.Menu_Reset()
        self.Timer_Start( self.Menu_Color )
    def Hold_Overlay( self ):
        self.Menu_Reset()
        self.Timer_Start( self.Menu_Overlay )
    def Hold_Select( self ):
        self.Menu_Reset()
        self.Timer_Start( self.Menu_Select )
    def Hold_Camera( self ):
        self.Menu_Reset()
        self.Timer_Start( self.Menu_Camera )
        
    # Release
    def Release_Vector( self ):
        self.Menu_Reset()
        self.action_tool_vector.setChecked( True )
        Krita.instance().action( self.operation["vector"] ).trigger()
        self.Geometry_Tela( self.show_animation, self.show_option, self.show_extra, self.hide_tela )
    def Release_Brush( self ):
        self.Menu_Reset()
        self.action_tool_brush.setChecked( True )
        Krita.instance().action( self.operation["brush"] ).trigger()
        self.Geometry_Tela( self.show_animation, self.show_option, self.show_extra, self.hide_tela )
    def Release_Transform( self ):
        self.Menu_Reset()
        self.action_tool_transform.setChecked( True )
        Krita.instance().action( self.operation["transform"] ).trigger()
        self.Geometry_Tela( self.show_animation, self.show_option, self.show_extra, self.hide_tela )
    def Release_Color( self ):
        self.Menu_Reset()
        self.action_tool_color.setChecked( True )
        Krita.instance().action( self.operation["color"] ).trigger()
        self.Geometry_Tela( self.show_animation, self.show_option, self.show_extra, self.hide_tela )
    def Release_Overlay( self ):
        self.Menu_Reset()
        self.action_tool_overlay.setChecked( True )
        Krita.instance().action( self.operation["overlay"] ).trigger()
        self.Geometry_Tela( self.show_animation, self.show_option, self.show_extra, self.hide_tela )
    def Release_Select( self ):
        self.Menu_Reset()
        self.action_tool_select.setChecked( True )
        Krita.instance().action( self.operation["select"] ).trigger()
        self.Geometry_Tela( self.show_animation, self.show_option, self.show_extra, self.hide_tela )
    def Release_Camera( self ):
        self.Menu_Reset()
        self.action_tool_camera.setChecked( True )
        Krita.instance().action( self.operation["camera"] ).trigger()
        self.Geometry_Tela( self.show_animation, self.show_option, self.show_extra, self.hide_tela )

    # Timer
    def Timer_Start( self, function ):
        self.menu_hold = QtCore.QTimer()
        self.menu_hold.setSingleShot( True )
        self.menu_hold.setInterval( self.press_time )
        self.menu_hold.timeout.connect( function )
        self.menu_hold.start()
    def Timer_Stop( self ):
        try:self.menu_hold.stop()
        except:pass

    # Menu
    def Menu_Reset( self ):
        self.Timer_Stop()
        self.Menu_Clear()
        self.Menu_Check()
    def Menu_Check( self ):
        self.action_tool_vector.setChecked( False )
        self.action_tool_brush.setChecked( False )
        self.action_tool_transform.setChecked( False )
        self.action_tool_color.setChecked( False )
        self.action_tool_overlay.setChecked( False )
        self.action_tool_select.setChecked( False )
        self.action_tool_camera.setChecked( False )
    def Menu_Down( self ):
        # Toolbox
        self.menu_krita.setDown( False )
        self.menu_vector.setDown( False )
        self.menu_brush.setDown( False )
        self.menu_transform.setDown( False )
        self.menu_color.setDown( False )
        self.menu_overlay.setDown( False )
        self.menu_select.setDown( False )
        self.menu_camera.setDown( False )
        self.menu_break.setDown( False )
        # Other
        self.menu_mirror_fix.setDown( False )
    def Menu_Hide( self ):
        self.ui_color_picker.hide()
        self.ui_information.hide()
        self.ui_guide.hide()
    def Menu_False( self ):
        self.menu_color_picker.setChecked( False )
        self.menu_information.setChecked( False )
        self.menu_guide.setChecked( False )
    def Menu_Clear( self ):
        try:self.qmenu.clear()
        except:pass

    # Menu
    def Menu_Vector( self ):
        self.Menu_Toolbox( "vector", self.menu_vector )
    def Menu_Brush( self ):
        self.Menu_Toolbox( "brush", self.menu_brush )
    def Menu_Transform( self ):
        self.Menu_Toolbox( "transform", self.menu_transform )
    def Menu_Color( self ):
        self.Menu_Toolbox( "color", self.menu_color )
    def Menu_Overlay( self ):
        self.Menu_Toolbox( "overlay", self.menu_overlay )
    def Menu_Select( self ):
        self.Menu_Toolbox( "select", self.menu_select )
    def Menu_Camera( self ):
        self.Menu_Toolbox( "camera", self.menu_camera )
    # Menu
    def Menu_Toolbox( self, mode, widget ):
        # Variables
        ki = Krita.instance()
        key = list( self.tool[mode].keys() )
        len_key = len( key )

        # Menu
        self.qmenu = QMenu()

        # Actions
        action_menu = list()
        for k in key:
            string = self.tool[mode][k][0]
            qicon = self.tool[mode][k][2]
            action_menu.append( QAction( qicon, string ) )
        self.qmenu.addActions( action_menu )

        # Mapping
        height = self.mi * len_key + self.my
        qpoint = widget.geometry().topLeft()
        pos = self.qmdiarea.mapToGlobal( qpoint )
        point = QPoint( pos.x(), pos.y() - height )
        action = self.qmenu.exec_( point )

        # Pin
        if action in action_menu:
            # Variables
            index = action_menu.index( action )
            tool = key[index]
            operation = self.tool[mode][tool][1]
            qicon = self.tool[mode][tool][2]
            # Tool
            ki.action( operation ).trigger()
            self.operation[mode] = operation
            # UI
            widget.setIcon( qicon )
            widget.setChecked( True )
            # Index
            if mode == "vector":    self.index_vector = tool
            if mode == "brush":     self.index_brush = tool
            if mode == "transform": self.index_transform = tool
            if mode == "color":     self.index_color = tool
            if mode == "overlay":   self.index_overlay = tool
            if mode == "select":    self.index_select = tool
            if mode == "camera":    self.index_camera = tool

        # Clean up
        self.Menu_Down()
        self.Geometry_Tela( self.show_animation, self.show_option, self.show_extra, self.hide_tela )

    # Progress Bar
    def Progress_Bar( self, value ):
        if value >= 99: value = 0
        self.progress_bar.setValue( int( value ) )

    # Eraser
    def Tool_Eraser( self, boolean ):
        # Krita Canvas mode flips the state of the ToolTipButton ( BUG )
        if self.state_canvas == True:   boolean = not boolean
        # Icons
        if boolean == True:             icon_eraser = "draw-eraser"
        else:                           icon_eraser = "hamburger_menu_dots"
        self.menu_krita.setIcon( Krita.instance().icon( icon_eraser ) )

    #endregion
    #region Shelf Action

    # Theme Read
    def Krita_Action_Icon_Read( self ):
        # Krita
        ki = Krita.instance()

        # Icon
        self.krita_icon = list()
        list_format = [ "*.svg","*.svgz","*.svz","*.png" ]
        # Read Files
        qdir = QDir( ":/pics/" ).entryList( list_format, QDir.Filter.Files )
        qdir += QDir( ":/" ).entryList( list_format, QDir.Filter.Files )
        # Cycle
        for tag in qdir:
            # Parse
            split = tag.split( '_', 1 )
            if any( icon_size == split[0] for icon_size in [ '16', '22', '24', '32', '48', '64', '128', '256', '512', '1048' ] ):
                tag = split[1]
            split = tag.split( '_', 1 )
            if any( icon_size == split[0] for icon_size in [ 'light', 'dark' ] ):
                tag = split[1]
            split = tag.split( '.' )
            tag = split[0]
            # List
            if tag not in self.krita_icon:
                self.krita_icon.append( tag )
        self.krita_icon.sort()

        # Action
        self.krita_action = list()
        list_action = ki.actions()
        for i in range( 0, len( list_action ) ):
            # Read
            action = list_action[i]
            name = action.objectName()
            tool_tip = action.toolTip()
            qicon = action.icon()
            tag = str()
            # List
            item = [ name, tool_tip, tag, qicon ]
            if item not in self.krita_action:
                self.krita_action.append( item )
        self.krita_action.sort()

        # Search the Tag for the QIcon
        for action in self.krita_action:
            try:
                data_a = self.qicon_to_data( action[3] )
                for tag in self.krita_icon:
                    data_i = self.qicon_to_data( ki.icon( tag ) )
                    if data_a == data_i:
                        action[2] = tag
                        break
            except:pass
            action = action[0:2]
        # Search Default state
        self.search_action = self.krita_action
        self.search_icon = self.krita_icon
    def qicon_to_data( self, qicon ):
        size = 24
        pixmap = qicon.pixmap( size, size )
        image = pixmap.toImage().convertToFormat( QImage.Format_RGBA8888 )
        data = image.bits().asstring( image.sizeInBytes() )
        return data

    # Menu
    def Menu_Shelf_Action( self ):
        # Krita
        ki = Krita.instance()
        # Variables
        len_item = len( self.shelf_action ) + 1

        # Menu
        self.qmenu = QMenu()
        self.qmenu.addSection( f"Shelf Action" )
        # Manage
        action_manage = self.qmenu.addAction( "Manage" )
        self.qmenu.addSeparator()
        # Actions
        list_shelf = list() # Actions
        for item in self.shelf_action:
            # Action
            name      = item[0] # name
            tool_tip  = item[1]
            qicon     = ki.icon( item[2] ) # tag
            # Action
            action = self.qmenu.addAction( name )
            action.setToolTip( tool_tip )
            action.setIcon( qicon )
            # List
            list_shelf.append( action )
        # Mapping
        pos = QCursor().pos()
        px = pos.x() - 100
        py = pos.y() - len_item * self.mi - self.shelf_margin
        qpoint = QPoint( px, py )
        action = self.qmenu.exec_( qpoint )
        # Trigger Action
        for i in range( 0, len( list_shelf ) ):
            action_i = list_shelf[i]
            if action == action_i:
                self.Action_Tag( self.shelf_action[i][0] )
                break
        # Manage Preset
        if action == action_manage:
            self.Shelf_Manage( show=True )
    # Manage
    def Shelf_Manage( self, show=False, shelf=False, action=False, icon=False ):
        # Krita
        ki = Krita.instance()
        # Shelf Action
        if show == True or shelf == True:
            self.ui_manage_shelf.shelf_action.clear()
            for item_s in self.shelf_action:
                name     = item_s[0]
                tool_tip = item_s[1]
                qicon    = ki.icon( item_s[2] )
                item = QListWidgetItem( qicon, name )
                item.setToolTip( tool_tip )
                item.setSizeHint( self.shelf_size )
                self.ui_manage_shelf.shelf_action.addItem( item )
        # Krita Action
        if show == True or action == True:
            self.ui_manage_shelf.krita_action.clear()
            for item_a in self.search_action:
                name     = item_a[0]
                tool_tip = item_a[1]
                qicon    = ki.icon( item_a[2] )
                item = QListWidgetItem( qicon, name )
                item.setToolTip( tool_tip )
                item.setSizeHint( self.shelf_size )
                self.ui_manage_shelf.krita_action.addItem( item )
        # Krita Icon
        if show == True or icon == True:
            self.ui_manage_shelf.krita_icon.clear()
            for item_i in self.search_icon:
                tag   = item_i
                qicon = ki.icon( tag )
                item = QListWidgetItem( qicon, tag )
                item.setSizeHint( self.shelf_size )
                self.ui_manage_shelf.krita_icon.addItem( item )
        # Interface
        index = -1
        self.ui_manage_shelf.shelf_action.setCurrentRow( index )
        self.ui_manage_shelf.krita_action.setCurrentRow( index )
        self.ui_manage_shelf.krita_icon.setCurrentRow( index )
        if show == True:
            self.ui_manage_shelf.search_action.setPlaceholderText( str( len( self.krita_action ) ) )
            self.ui_manage_shelf.search_icon.setPlaceholderText( str( len( self.krita_icon ) ) )
            self.ui_manage_shelf.show()
        # Memory
        self.Kritarc_Write( EXTENSION_NAME, "shelf_action", self.shelf_action )
    def Shelf_Remove( self ):
        # Read
        index = self.ui_manage_shelf.shelf_action.currentRow()
        count = self.ui_manage_shelf.shelf_action.count()
        # Logic
        check = 0 <= index <= count
        if check == True:
            self.shelf_action.pop( index )
            self.Shelf_Manage( shelf=True )
    def Shelf_Action( self ):
        # Read
        index = self.ui_manage_shelf.krita_action.currentRow()
        count = self.ui_manage_shelf.krita_action.count()
        # Logic
        check = 0 <= index <= count
        if check == True:
            # Variables
            action = self.search_action[index]
            name     = action[0]
            tool_tip = action[1]
            tag      = action[2]
            # List
            item = [ name, tool_tip, tag ]
            if item not in self.shelf_action:
                self.shelf_action.append( item )
            self.shelf_action.sort()
            # Update
            self.Shelf_Manage( shelf=True )
    def Shelf_Icon( self ):
        # Read Row
        index_shelf = self.ui_manage_shelf.shelf_action.currentRow()
        index_icon = self.ui_manage_shelf.krita_icon.currentRow()
        # Read Count
        count_shelf = self.ui_manage_shelf.shelf_action.count()
        count_icon = self.ui_manage_shelf.krita_icon.count()
        # Logic
        check = 0 <= index_shelf <= count_shelf and 0 <= index_icon <= count_icon
        if check == True:
            self.shelf_action[ index_shelf ][2] = self.search_icon[ index_icon ]
            self.Shelf_Manage( shelf=True )

    # Search
    def Search_Action( self, text ):
        text = text.lower()
        if text == str():
            self.search_action = self.krita_action
        else:
            self.search_action = list()
            for item in self.krita_action:
                if text in item[0].lower():
                    self.search_action.append( item )
        self.Shelf_Manage( action=True )
    def Search_Icon( self, text ):
        text = text.lower()
        if text == str():
            self.search_icon = self.krita_icon
        else:
            self.search_icon = list()
            for tag in self.krita_icon:
                if text in tag.lower():
                    self.search_icon.append( tag )
        self.Shelf_Manage( icon=True )

    #endregion
    #region Resource

    # Shelf Resource Presets
    def Menu_Shelf_ResourcePreset( self ):
        # Resource types = "pattern" "gradient" "brush" "preset" "palette" "workspace"

        # Krita
        ki = Krita.instance()
        av = ki.activeWindow().activeView()
        # Read
        self.resource_preset = ki.resources( "preset" )
        current_preset = av.currentBrushPreset().name()
        # Variables
        check_preset = current_preset in self.shelf_preset
        len_item = len( self.shelf_preset ) + 2

        # Menu
        self.qmenu = QMenu()
        self.qmenu.addSection( f"Shelf Resource Preset" )
        # Manage
        action_preset_append = self.qmenu.addAction( f"Append [ { current_preset } ]" )
        menu_manage = self.qmenu.addMenu( "Manage" )
        action_preset_remove = menu_manage.addAction( "Remove from List" )
        action_preset_delete = menu_manage.addAction( "Delete List" )
        self.qmenu.addSeparator()
        # Preset
        list_shelf = list() # Brush Preset
        for key in self.shelf_preset:
            try:  # Brush pack can be activated and deactivated
                # Resource
                resource = self.resource_preset[ key ]
                name = resource.name()
                qicon = QIcon( QPixmap().fromImage( resource.image() ) )
                # Action
                action = self.qmenu.addAction( name )
                action.setIcon( qicon )
                # List
                list_shelf.append( action )
            except:pass
        # State
        if check_preset == True:    action_preset_append.setEnabled( False )
        if check_preset == False:   action_preset_remove.setEnabled( False )
        # Mapping
        pos = QCursor().pos()
        px = pos.x() - 100
        py = pos.y() - len_item * self.mi - self.shelf_margin
        qpoint = QPoint( px, py )
        action = self.qmenu.exec_( qpoint )
        # Select Preset
        for i in range( 0, len( list_shelf ) ):
            action_i = list_shelf[i]
            if action == action_i:
                resource = self.resource_preset[ action_i.text() ]
                av.setCurrentBrushPreset( resource )
                break
        # Manage Preset
        if action == action_preset_append:
            self.shelf_preset.append( current_preset )
            self.shelf_preset.sort()
        if action == action_preset_remove:
            index = self.shelf_preset.index( current_preset )
            self.shelf_preset.pop( index )
        if action == action_preset_delete:
            self.shelf_preset = list()
        # Memory
        self.Kritarc_Write( EXTENSION_NAME, "shelf_preset", self.shelf_preset )

    #endregion
    #region Actions

    # Action
    def Action_Tag( self, tag ):
        Krita.instance().action( tag ).trigger()
        self.Message_Float( "ACTION", tag, "python" )

    # Animation
    def Animation_Play( self, boolean ):
        Krita.instance().action( "toggle_playback" ).trigger()
    def Animation_Onion( self ):
        Krita.instance().action( "toggle_onion_skin" ).trigger()
    def Animation_Cache( self ):
        Krita.instance().action( "clear_animation_cache" ).trigger()
        self.Message_Float( "ANIMATION", f"Animation cache cleared", self.icon_anim_cleanup )
    def Animation_Time( self, time ):
        Krita.instance().activeDocument().setCurrentTime( time + self.anim_delta )

    # Transform
    def Transform_Free( self ):
        Krita.instance().action( "KisToolTransformFree" ).trigger()
    def Transform_Perspective( self ):
        Krita.instance().action( "KisToolTransformPerspective" ).trigger()
    def Transform_Warp( self ):
        Krita.instance().action( "KisToolTransformWarp" ).trigger()
    def Transform_Cage( self ):
        Krita.instance().action( "KisToolTransformCage" ).trigger()
    def Transform_Liquify( self ):
        Krita.instance().action( "KisToolTransformLiquify" ).trigger()
    def Transform_Mesh( self ):
        Krita.instance().action( "KisToolTransformMesh" ).trigger()

    # Select
    def Select_All( self ):
        Krita.instance().action( "select_all" ).trigger()
    def Select_None( self ):
        Krita.instance().action( "deselect" ).trigger()
    def Select_Invert( self ):
        Krita.instance().action( "invert_selection" ).trigger()
    def Select_Overlay( self ):
        Krita.instance().action( "toggle-selection-overlay-mode" ).trigger()

    # Edit
    def Edit_Cut_Sharp( self ):
        Krita.instance().action( "cut_sharp" ).trigger()
    def Edit_Copy_Sharp( self ):
        Krita.instance().action( "copy_sharp" ).trigger()

    # Dockers
    def View_Canvas_UI( self ):
        Krita.instance().action( "view_show_canvas_only" ).trigger()
        # Krita Canvas mode flips the state of the ToolTipButton ( BUG )
        self.state_canvas = Krita.instance().action( "view_show_canvas_only" ).isChecked()
    def View_Docker_UI( self ):
        Krita.instance().action( "view_toggledockers" ).trigger()
    def View_Docker_Title( self ):
        Krita.instance().action( "view_toggledockertitlebars" ).trigger()
    # Layer
    def Layer_Isolate( self ):
        Krita.instance().action( "isolate_active_layer" ).trigger()
    # Canvas
    def Canvas_Mirror( self ):
        Krita.instance().action( "mirror_canvas" ).trigger()
    def Canvas_Wrap( self ):
        Krita.instance().action( "wrap_around_mode" ).trigger()
    # Guides
    def Guide_Ruler( self, boolean ):
        Krita.instance().action( "view_ruler" ).setChecked( boolean )
    def Guide_Snap( self, boolean ):
        Krita.instance().action( "view_snap_to_guides" ).setChecked( boolean )
    def Guide_Show( self, boolean ):
        Krita.instance().action( "view_show_guides" ).setChecked( boolean )
    def Guide_Lock( self, boolean ):
        Krita.instance().action( "view_lock_guides" ).setChecked( boolean )
    # View
    def View_Painting_Assistant( self ):
        Krita.instance().action( "view_toggle_painting_assistants" ).trigger()
    def View_Assistant_Preview( self ):
        Krita.instance().action( "view_toggle_assistant_previews" ).trigger()
    def View_Reference_Image( self ):
        Krita.instance().action( "view_toggle_reference_images" ).trigger()

    # Snap
    def Snap_Guide( self ):
        Krita.instance().action( "view_snap_to_guides" ).trigger()
    def Snap_Grid( self ):
        Krita.instance().action( "view_snap_to_grid" ).trigger()
    def Snap_Pixel( self ):
        Krita.instance().action( "view_snap_to_pixel" ).trigger()
    def Snap_Ortogonal( self ):
        Krita.instance().action( "view_snap_orthogonal" ).trigger()
    def Snap_Node( self ):
        Krita.instance().action( "view_snap_node" ).trigger()
    def Snap_Extension( self ):
        Krita.instance().action( "view_snap_extension" ).trigger()
    def Snap_Intersection( self ):
        Krita.instance().action( "view_snap_intersection" ).trigger()
    def Snap_Bounding_Box( self ):
        Krita.instance().action( "view_snap_bounding_box" ).trigger()
    def Snap_Image_Bounds( self ):
        Krita.instance().action( "view_snap_image_bounds" ).trigger()
    def Snap_Image_Center( self ):
        Krita.instance().action( "view_snap_image_center" ).trigger()
    def Snap_All( self, boolean ):
        self.snap_all = boolean
        Krita.instance().action( "view_snap_to_guides" ).setChecked( boolean )
        Krita.instance().action( "view_snap_to_grid" ).setChecked( boolean )
        Krita.instance().action( "view_snap_to_pixel" ).setChecked( boolean )
        Krita.instance().action( "view_snap_orthogonal" ).setChecked( boolean )
        Krita.instance().action( "view_snap_node" ).setChecked( boolean )
        Krita.instance().action( "view_snap_extension" ).setChecked( boolean )
        Krita.instance().action( "view_snap_intersection" ).setChecked( boolean )
        Krita.instance().action( "view_snap_bounding_box" ).setChecked( boolean )
        Krita.instance().action( "view_snap_image_bounds" ).setChecked( boolean )
        Krita.instance().action( "view_snap_image_center" ).setChecked( boolean )

    #endregion
    #region Animation

    def Animation_Frame( self ):
        # Active Document
        document = Krita.instance().activeDocument()
        # Animation Correction
        return_list = self.Read_Nodes( document )
        animation = False
        for i in range( 0, len( return_list ) ):
            animation = return_list[i].animated()
            if animation == True:
                self.Message_Float( "ANIMATION CLEANUP", f"Document has animation hence no action was taken", self.icon_anim_cleanup )
                break
        if animation == False:
            self.Message_Float( "ANIMATION CLEANUP", f"Document animation range was set to zero", self.icon_anim_cleanup )
            document.setFullClipRangeStartTime( 0 )
            document.setFullClipRangeEndTime( 0 )
    def Read_Nodes( self, document ):
        # Document
        top_nodes = document.topLevelNodes()
        # Top level Nodes
        new_nodes = list()
        for i in range( 0, len( top_nodes ) ):
            new_nodes.append( top_nodes[i] )
        # Variables
        check_again = True
        counter = 0
        node_dic = { 0 : new_nodes }
        # Infinite Cycle
        while check_again == True:
            # layer read
            new_nodes = list()
            nodes = node_dic[counter]
            # Layer Level
            for i in range( 0, len( nodes ) ):
                try:
                    child_nodes = nodes[i].childNodes()
                    if len( child_nodes ) > 0:
                        for cn in range( 0, len( child_nodes ) ):
                            new_nodes.append( child_nodes[cn] )
                except:pass
            # cycle control
            if len( new_nodes ) == 0:
                check_again = False
            else:
                counter += 1
                node_dic[counter] = new_nodes
        # Return List
        return_list = list()
        for i in range( 0, len( node_dic ) ):
            for j in range( 0, len( node_dic[i] ) ):
                node = node_dic[i][j]
                return_list.append( node )
        return return_list

    #endregion
    #region Information

    def Information_Read( self ):
        # Block Signals
        self.Information_Block_Signals( True )

        #region Variables

        # File
        self.file_name = str()
        self.file_version = str()
        # XML Document
        self.xml_title = str()
        self.xml_description = str()
        self.xml_subject = str()
        self.xml_keyword = str()
        self.xml_license = str()
        # XML Time
        self.xml_date = str()
        self.xml_creation_date = str()
        self.xml_editing_time = str()
        self.xml_editing_cycles = str()
        # XML Author
        self.xml_full_name = str() # Nickname
        self.xml_creator_first_name = str()
        self.xml_creator_last_name = str()
        self.xml_initial = str()
        self.xml_author_title = str()
        self.xml_position = str()
        self.xml_company = str()
        self.xml_contact = list()
        # Time
        self.info_date = str()
        self.info_creation_date = str()
        self.info_editing_time = str()
        self.info_delta_creation = str()
        self.info_name = str()
        # Redacted from UI
        self.xml_abstract = str()
        self.xml_language = str()
        self.xml_initial_creator = str()

        #endregion 
        #region Canvas

        # Active Document is Open
        try:check_canvas = self.Check_Canvas()
        except:check_canvas = False
        if check_canvas == True:
            # Active Document
            ki = Krita.instance()
            ad = ki.activeDocument()
            document_info = ad.documentInfo()

            # File
            path = ad.fileName()
            self.file_name = str( os.path.basename( path ) )
            try:
                target = "maindoc.xml"
                if zipfile.is_zipfile( path ):
                    archive = zipfile.ZipFile( path, "r" )
                    archive_open = archive.open( target )
                    ET = xml.etree.ElementTree
                    tree = ET.parse( archive_open )
                    root = tree.getroot()
                    attrib = root.attrib
                    self.file_version = attrib["kritaVersion"]
            except:
                pass
            # XML Data
            ET = xml.etree.ElementTree
            root = ET.fromstring( document_info )
            for group in root:
                for item in group:
                    # read
                    tag = item.tag.replace( "{http://www.calligra.org/DTD/document-info}", "" )
                    text = item.text
                    if text == None :
                        text = ""
                    # XML Document
                    if   tag == "title" :               self.xml_title = text
                    elif tag == "description" :         self.xml_description = text
                    elif tag == "subject" :             self.xml_subject = text
                    elif tag == "abstract" :            self.xml_abstract = text
                    elif tag == "keyword" :             self.xml_keyword = text
                    elif tag == "language" :            self.xml_language = text
                    elif tag == "license" :             self.xml_license = text
                    # XML Time
                    elif tag == "date" :                self.xml_date = text
                    elif tag == "creation-date" :       self.xml_creation_date = text
                    elif tag == "editing-time" :        self.xml_editing_time = text
                    elif tag == "editing-cycles" :      self.xml_editing_cycles = text
                    # XML Author
                    elif tag == "initial-creator" :     self.xml_initial_creator = text
                    elif tag == "full-name" :           self.xml_full_name = text
                    elif tag == "creator-first-name" :  self.xml_creator_first_name = text
                    elif tag == "creator-last-name" :   self.xml_creator_last_name = text
                    elif tag == "initial" :             self.xml_initial = text
                    elif tag == "author-title" :        self.xml_author_title = text
                    elif tag == "position" :            self.xml_position = text
                    elif tag == "company" :             self.xml_company = text
                    elif tag == "contact" :             self.xml_contact.append( text )

            # Time Calculations
            self.info_date = self.Display_Date( self.xml_date )
            self.info_creation_date = self.Display_Date( self.xml_creation_date )
            if self.xml_editing_time != "":
                self.info_editing_time = self.Time_to_String( self.Cycles_to_Time( int( self.xml_editing_time ) ) )
            if self.info_creation_date != "":
                self.info_delta_creation = self.Time_Delta(
                    int( self.info_creation_date[0:4] ),
                    int( self.info_creation_date[5:7] ),
                    int( self.info_creation_date[8:10] ),
                    int( self.info_creation_date[11:13] ),
                    int( self.info_creation_date[14:16] ),
                    int( self.info_creation_date[17:19] ),
                    int( self.info_date[0:4] ),
                    int( self.info_date[5:7] ),
                    int( self.info_date[8:10] ),
                    int( self.info_date[11:13] ),
                    int( self.info_date[14:16] ),
                    int( self.info_date[17:19] ),
                    )
            # Money Calculation ( Edit time avoids idle inflation cost )
            if self.xml_editing_time != "":     self.Money_Cost( self.Cycle_to_Hour( self.xml_editing_time ) )
            else:                               self.Money_Cost( 0 )
            # Author Variables
            self.info_name = self.xml_creator_first_name + " " + self.xml_creator_last_name

        #endregion
        #region Interface

        # Document
        self.ui_information.info_file_name.setText( self.file_name )
        self.ui_information.info_file_version.setText( self.file_version )
        # Header
        self.ui_information.info_title.setText( self.xml_title )
        self.ui_information.info_description.setText( self.xml_abstract ) # Abstract is Description inside Krita
        self.ui_information.info_subject.setText( self.xml_subject )
        self.ui_information.info_keyword.setText( self.xml_keyword )
        self.ui_information.info_license.setText( self.xml_license )
        # Time
        self.ui_information.info_date.setText( self.info_date )
        self.ui_information.info_creation.setText( self.info_creation_date + self.info_delta_creation )
        self.ui_information.info_edit_time.setText( str( self.xml_editing_time ) + str( self.info_editing_time ) )
        self.ui_information.info_edit_cycles.setText( str( self.xml_editing_cycles ) )
        # Author
        self.ui_information.info_nick_name.setText( self.xml_full_name )
        self.ui_information.info_full_name.setText( self.info_name )
        self.ui_information.info_initials.setText( self.xml_initial )
        self.ui_information.info_author_title.setText( self.xml_author_title )
        self.ui_information.info_position.setText( self.xml_position )
        self.ui_information.info_company.setText( self.xml_company )
        self.ui_information.info_contact.clear()
        for contact in self.xml_contact:
            self.ui_information.info_contact.addItem( str( contact ) )

        #endregion

        # Block Signals
        self.Information_Block_Signals( False )
    def Information_Save( self ):
        # Active Document is Open
        try:check_canvas = self.Check_Canvas()
        except:check_canvas = False
        if check_canvas == True:
            # Read widgets
            new_title = str( self.ui_information.info_title.text() )
            new_description = str( self.ui_information.info_description.toPlainText() )  # Description is Abstract inside Krita
            new_subject = str( self.ui_information.info_subject.text() )
            new_keyword = str( self.ui_information.info_keyword.text() )
            new_license = str( self.ui_information.info_license.text() )
            # Contacts
            list_contact = str()
            len_contact = len( self.xml_contact )
            for i in range( 0, len_contact ):
                list_contact += f"  <contact>{ self.xml_contact[i] }</contact>\n"
            # Document Info
            info_string = ( 
                f"<?xml version='1.0' encoding='UTF-8'?>\n"
                f"<!DOCTYPE document-info PUBLIC '-//KDE//DTD document-info 1.1//EN' 'http://www.calligra.org/DTD/document-info-1.1.dtd'>\n"
                f"<document-info xmlns='http://www.calligra.org/DTD/document-info'>\n"
                f" <about>\n"
                f"  <title>{ new_title }</title>\n"
                f"  <description>{ self.xml_abstract }</description>\n"
                f"  <subject>{ new_subject }</subject>\n"
                f"  <abstract><![CDATA[{ new_description }]]></abstract>\n"
                f"  <keyword>{ new_keyword }</keyword>\n"
                f"  <initial-creator>{ self.xml_initial_creator }</initial-creator>\n"
                f"  <language>{ self.xml_language }</language>\n"
                f"  <license>{ new_license }</license>\n"
                f" </about>\n"
                f" <author>\n"
                f"  <full-name>{ self.xml_full_name }</full-name>\n"
                f"  <creator-first-name>{ self.xml_creator_first_name }</creator-first-name>\n"
                f"  <creator-last-name>{ self.xml_creator_last_name }</creator-last-name>\n"
                f"  <initial>{ self.xml_initial } </initial>\n"
                f"  <author-title>{ self.xml_author_title }</author-title>\n"
                f"  <position>{ self.xml_position }</position>\n"
                f"  <company>{ self.xml_company }</company>\n"
                f"{ list_contact }"
                f" </author>\n"
                f"</document-info>" )
            text = Krita.instance().activeDocument().setDocumentInfo( info_string )
            # Reconstruct Items
            self.ui_information.info_contact.clear()
            for i in range( 0, len_contact ):
                self.ui_information.info_contact.addItem( str( self.xml_contact[i] ) )
    def Information_Copy( self, item ):
        contact = item.text()
        if contact != "":
            QApplication.clipboard().setText( contact )

    def Information_Block_Signals( self, boolean ):
        self.ui_information.info_title.blockSignals( boolean )
        self.ui_information.info_description.blockSignals( boolean )
        self.ui_information.info_subject.blockSignals( boolean )
        self.ui_information.info_keyword.blockSignals( boolean )
        self.ui_information.info_license.blockSignals( boolean )

    def Cycles_to_Time( self, cycles ):
        # Variables
        year = 0
        month = 0
        day = 0
        hour = 0
        minute = 0
        second = 0
        # Checks
        if ( cycles != "" and cycles != 0 and cycles != None ):
            cycles = int( cycles )
            while cycles >= sec_ano:        year += 1;      cycles -= sec_ano
            while cycles >= sec_mes:        month += 1;     cycles -= sec_mes
            while cycles >= sec_dia:        day += 1;       cycles -= sec_dia
            while cycles >= sec_hora:       hour += 1;      cycles -= sec_hora
            while cycles >= sec_minuto:     minute += 1;    cycles -= sec_minuto
            second = int( cycles )
        # Return
        time = [ year, month, day, hour, minute, second ]
        return time
    def Time_to_String( self, time ):
        # Variables
        aa = time[0]
        mo = time[1]
        dd = time[2]
        hh = time[3]
        mi = time[4]
        ss = time[5]
        # string constants
        suffix = str()
        seconds = str()
        minutes = str()
        hours = str()
        days = str()
        months = str()
        years = str()
        # strings
        if ( aa>0 or mo>0 or dd>0 or hh>0 or mi>0 or ss>0 ):
            suffix = " >> "
        if aa > 0:
            years = str( aa ).zfill( 1 ) + "Y "
        if mo > 0:
            months = str( mo ).zfill( 2 ) + "M "
        if dd > 0:
            days = str( dd ).zfill( 2 ) + "D "
        if hh > 0:
            hours = str( hh ).zfill( 2 ) + "h "
        if mi > 0:
            minutes = str( mi ).zfill( 2 ) + "m "
        if ss > 0:
            seconds = str( ss ).zfill( 2 ) + "s"
        # string missing
        if ( mo==0 and aa>0 ):
            months = "00M "
        if ( dd==0 and ( aa>0 or mo>0 ) ):
            days = "00D "
        if ( hh==0 and ( aa>0 or mo>0 or dd>0 ) ):
            hours = "00h "
        if ( mi==0 and ( aa>0 or mo>0 or dd>0 or hh>0 ) ):
            minutes = "00m "
        if ( ss==0 and ( aa>0 or mo>0 or dd>0 or hh>0 or ss>0 ) ):
            seconds = "00s"
        # return
        string = suffix + years + months + days + hours + minutes + seconds
        return string
    def Display_Date( self, date ):
        if ( date != "" and date != None ):
            numbers = date.replace( "T", " " )
            string = numbers
        else:
            string = ""
        return string
    def Time_Delta( self, year1, month1, day1, hour1, minute1, second1, year2, month2, day2, hour2, minute2, second2 ):
        date_start = datetime.datetime( year1, month1, day1, hour1, minute1, second1 )
        date_now = datetime.datetime( year2, month2, day2, hour2, minute2, second2 )
        delta = date_now - date_start
        string = self.Time_to_String( self.Cycles_to_Time( ( delta.days * 86400 ) + delta.seconds ) )
        return string

    def Cycle_to_Hour( self, cycles ):
        # Variables
        hour = 0
        # Checks
        if ( cycles != "" and cycles != 0 and cycles != None ):
            cycles = int( cycles )
            while cycles >= sec_hora:
                hour += 1
                cycles -= sec_hora
            resto = cycles / sec_hora
            work_hours = hour + resto
        else:
            work_hours = 0
        return work_hours
    def Money_Cost( self, work_hours ):
        # Variables
        self.work_hours = work_hours
        rate = self.ui_information.menu_money_rate.value()
        # Calculations
        total = rate * self.work_hours
        # Signals
        self.Money_Block_Signals( True )
        self.ui_information.menu_money_total.setValue( total )
        self.Money_Block_Signals( False )
    def Money_Rate( self, rate ):
        total = rate * self.work_hours
        # Signals
        self.Money_Block_Signals( True )
        self.ui_information.menu_money_total.setValue( total )
        self.Money_Block_Signals( False )
    def Money_Total( self, total ):
        if self.work_hours > 0:
            rate = total / self.work_hours
        else:
            rate = 0
        # Signals
        self.Money_Block_Signals( True )
        self.ui_information.menu_money_rate.setValue( rate )
        self.Money_Block_Signals( False )
    def Money_Block_Signals( self, boolean ):
        self.ui_information.menu_money_rate.blockSignals( boolean )
        self.ui_information.menu_money_total.blockSignals( boolean )

    #endregion
    #region Guide

    # Interface
    def Guide_Mirror_Horizontal( self, boolean ):
        # Krita
        ad = Krita.instance().activeDocument()
        # Variables
        self.guide_mirror_h = boolean
        # Interface
        if boolean == True:
            # Interface
            self.ui_guide.guide_mirror_h.setText( "Horizontal [Mirror]" )
            # Document
            height = ad.height()
            h2 = height * 0.5
            # Mirror
            for guide in self.guide_list_h:
                value = height - guide
                if ( value not in self.guide_list_h ) and ( value != h2 ):
                    self.guide_list_h.append( value )
            self.guide_list_h.sort()
            self.Guide_Write_H( ad, self.guide_list_h )
        else:
            self.ui_guide.guide_mirror_h.setText( "Horizontal" )
        # Lists
        self.Guide_UI_List_H( ad, self.guide_list_h )
    def Guide_Mirror_Vertical( self, boolean ):
        # Krita
        ad = Krita.instance().activeDocument()
        # Variables
        self.guide_mirror_v = boolean
        # Interface
        if boolean == True:
            # Interface
            self.ui_guide.guide_mirror_v.setText( "Vertical [Mirror]" )
            # Document
            width = ad.width()
            w2 = width * 0.5
            # Mirror
            for guide in self.guide_list_v:
                value = width - guide
                if ( value not in self.guide_list_v ) and ( value != w2 ):
                    self.guide_list_v.append( value )
            self.guide_list_v.sort()
            self.Guide_Write_V( ad, self.guide_list_v )
        else:
            self.ui_guide.guide_mirror_v.setText( "Vertical" )
        # Lists
        ad = Krita.instance().activeDocument()
        self.Guide_UI_List_V( ad, self.guide_list_v )
    def Guide_UI_List_H( self, ad, lista ):
        # Interface
        self.ui_guide.guide_list_h.clear()
        # Variables
        height = ad.height()
        len_old = len( self.guide_list_h )
        len_new = len( lista )
        # Changed
        dif_i = None
        inv_i = None
        for i in range( 0, len_new ):
            guide = lista[i]
            invert = height - guide
            if ( guide not in self.guide_list_h ):                                  dif_i = i
            if ( guide in self.guide_list_h ) and ( invert not in lista ):          inv_i = i
        # Mirror
        if self.guide_mirror_h == True:
            if ( len_old == len_new ) and ( dif_i != None ) and ( inv_i != None ):  lista[inv_i] = height - lista[dif_i]
            elif ( len_old < len_new ) and ( dif_i != None ):                       lista.append( height - lista[dif_i] )
            elif ( len_old > len_new ) and ( inv_i != None ):                       lista.pop( inv_i )
        # Prepare for next Cycle
        self.guide_list_h = lista.copy()
        self.guide_list_h.sort()
        self.Guide_Write_H( ad, self.guide_list_h )
        # Widget List
        for value in lista:
            item = QListWidgetItem( str( value ) )
            self.ui_guide.guide_list_h.addItem( item )
        if dif_i != None:
            self.ui_guide.guide_list_h.setCurrentRow( dif_i )
    def Guide_UI_List_V( self, ad, lista ):
        # Interface
        self.ui_guide.guide_list_v.clear()
        # Variables
        width = ad.width()
        len_old = len( self.guide_list_v )
        len_new = len( lista )
        # Changed
        dif_i = None
        inv_i = None
        for i in range( 0, len_new ):
            guide = lista[i]
            invert = width - guide
            if ( guide not in self.guide_list_v ):                                  dif_i = i
            if ( guide in self.guide_list_v ) and ( invert not in lista ):          inv_i = i
        # Mirror
        if self.guide_mirror_h == True:
            if ( len_old == len_new ) and ( dif_i != None ) and ( inv_i != None ):  lista[inv_i] = width - lista[dif_i]
            elif ( len_old < len_new ) and ( dif_i != None ):                       lista.append( width - lista[dif_i] )
            elif ( len_old > len_new ) and ( inv_i != None ):                       lista.pop( inv_i )
        # Prepare for next Cycle
        self.guide_list_v = lista.copy()
        self.guide_list_v.sort()
        self.Guide_Write_V( ad, self.guide_list_v )
        # Widget List
        for value in lista:
            item = QListWidgetItem( str( value ) )
            self.ui_guide.guide_list_v.addItem( item )
        if dif_i != None:
            self.ui_guide.guide_list_v.setCurrentRow( dif_i )
    def Guide_UI_Ruler( self, boolean ):
        self.ui_guide.guide_ruler.setChecked( boolean )
    def Guide_UI_Show( self, boolean ):
        self.ui_guide.guide_show.setChecked( boolean )
    def Guide_UI_Snap( self, boolean ):
        self.ui_guide.guide_snap.setChecked( boolean )
    def Guide_UI_Lock( self, boolean ):
        self.ui_guide.guide_lock.setChecked( boolean )

    # Functions
    def Guide_Value_Horizontal( self ):
        # Variables
        ad = Krita.instance().activeDocument()
        height = ad.height()
        row = self.ui_guide.guide_list_h.currentRow()
        item = self.ui_guide.guide_list_h.item( row )
        lista = self.guide_list_h.copy()
        # Item
        if item is not None:
            # Input Value
            text = item.text()
            title = f"Guide = { text }"
            num_read = int( float( text ) )
            number, ok = QInputDialog.getInt( self.ui_guide, "Input Guide Value", title, num_read )
            number = self.Limit_Range( number, 0, height )
            # Update
            if ( ok == True ) and ( 0 <= number <= height ):    lista[row] = number
            else:                                               lista.pop( row )
            lista.sort()
            self.Guide_UI_List_H( ad, lista )
    def Guide_Value_Vertical( self ):
        # Variables
        ad = Krita.instance().activeDocument()
        width = ad.width()
        row = self.ui_guide.guide_list_v.currentRow()
        item = self.ui_guide.guide_list_v.item( row )
        lista = self.guide_list_v.copy()
        # Item
        if item is not None:
            # Input Value
            text = item.text()
            title = f"Guide = { text }"
            num_read = int( float( text ) )
            number, ok = QInputDialog.getInt( self.ui_guide, "Input Guide Value", title, num_read )
            number = self.Limit_Range( number, 0, width )
            # Update
            if ( ok == True ) and ( 0 <= number <= width ):     lista[row] = number
            else:                                               lista.pop( row )
            lista.sort()
            self.Guide_UI_List_V( ad, lista )
    def Guide_Write_H( self, ad, lista ):
        ad.setHorizontalGuides( lista ) # deprecated but still works best
        # ad.guidesConfig().setHorizontalGuides( lista )
    def Guide_Write_V( self, ad, lista ):
        ad.setVerticalGuides( lista ) # deprecated but still works best
        # ad.guidesConfig().setVerticalGuides( lista )

    #endregion
    #region Color Picker

    # Module
    def Import_Pigment_O( self ):
        try:
            # Tela
            self.menu_color_picker.setEnabled( False )
            # Krita
            ki = Krita.instance()
            docker_list = ki.dockers()
            for docker in docker_list:
                if docker.objectName() == self.pigmento_picker_pyid:
                    # Variables
                    self.pigmento_picker = docker
                    # Styling
                    self.menu_color_picker.setEnabled( True )
                    self.menu_color_picker.setIcon( ki.icon( "krita_tool_ellipse" ) )
                    break
        except:
            pass

    # Color Panel
    def Color_Panel_Preview( self, lista ):
        self.Color_Sliders_READ( lista[0], lista[1], lista[2] )
        self.Color_WRITE( self.wheel_space, self.s1, self.s2, self.s3, False )
    def Color_Panel_Apply( self, lista ):
        self.Color_Sliders_READ( lista[0], lista[1], lista[2] )
        self.Color_WRITE( self.wheel_space, self.s1, self.s2, self.s3, True )

    # Sliders Read
    def CS1_R( self, value ):
        self.s1 = value
        self.ui_color_picker.s1.blockSignals( True )
        self.ui_color_picker.s1.setValue( int( self.s1 * self.hue ) )
        self.ui_color_picker.s1.blockSignals( False )
    def CS2_R( self, value ):
        self.s2 = value
        self.ui_color_picker.s2.blockSignals( True )
        self.ui_color_picker.s2.setValue( int( self.s2 * self.svl ) )
        self.ui_color_picker.s2.blockSignals( False )
    def CS3_R( self, value ):
        self.s3 = value
        self.ui_color_picker.s3.blockSignals( True )
        self.ui_color_picker.s3.setValue( int( self.s3 * self.svl ) )
        self.ui_color_picker.s3.blockSignals( False )
    def Color_Sliders_READ( self, s1, s2, s3 ):
        self.s1 = s1
        self.s2 = s2
        self.s3 = s3
        self.ui_color_picker.s1.blockSignals( True )
        self.ui_color_picker.s2.blockSignals( True )
        self.ui_color_picker.s3.blockSignals( True )
        self.ui_color_picker.s1.setValue( int( self.s1 * self.hue ) )
        self.ui_color_picker.s2.setValue( int( self.s2 * self.svl ) )
        self.ui_color_picker.s3.setValue( int( self.s3 * self.svl ) )
        self.ui_color_picker.s1.blockSignals( False )
        self.ui_color_picker.s2.blockSignals( False )
        self.ui_color_picker.s3.blockSignals( False )
    # Sliders Write
    def CS1_W( self, action ):
        self.s1 = self.ui_color_picker.s1.value() / self.hue
        self.Color_WRITE( self.wheel_space, self.s1, self.s2, self.s3, action )
    def CS2_W( self, action ):
        self.s2 = self.ui_color_picker.s2.value() / self.svl
        self.Color_WRITE( self.wheel_space, self.s1, self.s2, self.s3, action )
    def CS3_W( self, action ):
        self.s3 = self.ui_color_picker.s3.value() / self.svl
        self.Color_WRITE( self.wheel_space, self.s1, self.s2, self.s3, action )
    def Color_Sliders_WRITE( self, s1, s2, s3 ):
        self.s1 = s1 / self.hue
        self.s2 = s2 / self.svl
        self.s3 = s3 / self.svl
        self.Color_WRITE( self.wheel_space, self.s1, self.s2, self.s3 )

    # Read and Write
    def Color_READ( self ):
        if self.pigmento_picker != None:
            # Read
            self.cor = self.pigmento_picker.API_Request_FG()
            wheel_space = self.pigmento_picker.API_Request_Wheel_Space()

            # Wheel Space
            if wheel_space != self.wheel_space:
                # Variables
                self.wheel_space = wheel_space
                panel_path = self.directory_plugin.replace( "tela", "pigment_o\\PANEL")
                zip_path = os.path.join( panel_path, f"SRGB_{ self.wheel_space }_S4.zip" )
                # QPixmap List
                self.qpixmap_list = self.Read_Zip( zip_path )
                self.color_panel.Set_Gradient( self.qpixmap_list )

            # Variables
            hex6 = self.cor["display"]
            if self.wheel_space == "HSV":
                s1 = self.cor["hsv_1"]
                s2 = self.cor["hsv_2"]
                s3 = self.cor["hsv_3"]
            elif self.wheel_space == "HSL":
                s1 = self.cor["hsl_1"]
                s2 = self.cor["hsl_2"]
                s3 = self.cor["hsl_3"]
            elif self.wheel_space == "HCY":
                s1 = self.cor["hcy_1"]
                s2 = self.cor["hcy_2"]
                s3 = self.cor["hcy_3"]
            elif self.wheel_space == "ARD":
                s1 = self.cor["ard_1"]
                s2 = self.cor["ard_2"]
                s3 = self.cor["ard_3"]

            # Preview
            self.color_display.Set_Color( hex6 )
            # Panel
            self.color_panel.Set_Color( s1, s2, s3 )
            # Sliders
            self.Color_Sliders_READ( s1, s2, s3 )
    def Color_WRITE( self, wheel_space, s1, s2, s3, action=True ):
        if self.pigmento_picker != None:
            # Pigment.O
            if action == False: self.cor = self.pigmento_picker.API_Input_Preview( str( wheel_space ), float( s1 ), float( s2 ), float( s3 ), 0.0 )
            if action == True:  self.cor = self.pigmento_picker.API_Input_Apply( str( wheel_space ), float( s1 ), float( s2 ), float( s3 ), 0.0 )
            # Update
            self.color_display.Set_Color( self.cor["display"] )
            self.color_panel.Set_Color( s1, s2, s3 )

    # Extras
    def Color_BlockSignals( self, boolean ):
        self.ui_color_picker.color_display.blockSignals( boolean )
        self.ui_color_picker.color_panel.blockSignals( boolean )
        self.ui_color_picker.s1.blockSignals( boolean )
        self.ui_color_picker.s2.blockSignals( boolean )
        self.ui_color_picker.s3.blockSignals( boolean )
    def Read_Zip( self, url ):
        list_qpixmap = list()
        try:
            if zipfile.is_zipfile( url ):
                archive = zipfile.ZipFile( url, "r" )
                name_list = archive.namelist()
                name_list.sort()
                for name in name_list:
                    # Archive
                    extract = archive.open( name )
                    image_data = extract.read()
                    # Buffer
                    byte_array = QByteArray( image_data )
                    buffer = QBuffer()
                    buffer.setData( byte_array )
                    buffer.open( QIODevice.OpenModeFlag.ReadOnly )
                    # Image
                    reader = QImageReader( buffer )
                    qpixmap = QPixmap().fromImageReader( reader )
                    list_qpixmap.append( qpixmap )
        except Exception as e:
            try:QtCore.qDebug( f"TELA | ERROR request failed\n{ e }" )
            except:pass
        return list_qpixmap

    #endregion
    #region Mirror Fix

    def MirrorFix_Side( self, SIGNAL_SIDE ):
        self.Menu_Reset()
        check_canvas = self.Check_Canvas()
        if check_canvas == True:
            boolean = QMessageBox.question( None, "TELA", f"Mirror Fix Selected Layer(s) ?\nSource = { SIGNAL_SIDE }", QMessageBox.Yes, QMessageBox.No )
            if ( boolean == QMessageBox.Yes and SIGNAL_SIDE != None ):
                self.MirrorFix_Run( SIGNAL_SIDE )
    def MirrorFix_Run( self, side ):
        check_canvas = self.Check_Canvas()
        if check_canvas == True:
            # Warnning
            self.Message_Float( "MIRROR FIX", f"START", self.icon_mirrorfix )

            # State
            ki = Krita.instance()
            ad = ki.activeDocument()
            av = ki.activeWindow().activeView()
            # Variables
            width = int( ad.width() )
            height = int( ad.height() )
            w2 = int( width * 0.5 )
            h2 = int( height * 0.5 )

            # Selection
            ss = ad.selection()
            if ss == None: # Square
                state = True
                # Correction
                if side in ( "LEFT", "RIGHT" ):
                    r = width % 2
                    if r == 0:m = 0
                    else:m = 1
                if side in ( "TOP", "DOWN" ):
                    r = height % 2
                    if r == 0:m = 0
                    else:m = 1
                # Variables
                if side == "LEFT":
                    px = 0
                    py = 0
                    pw = w2 + m
                    ph = height
                if side == "RIGHT":
                    px = w2
                    py = 0
                    pw = w2 + m
                    ph = height
                if side == "TOP":
                    px = 0
                    py = 0
                    pw = width
                    ph = h2 + m
                if side == "DOWN":
                    px = 0
                    py = h2
                    pw = width
                    ph = h2 + m
                # Selection
                sel = Selection()
                sel.select( int( px ), int( py ), int( pw ), int( ph ), 255 )
                ad.setSelection( sel )
            else: # Custom
                state = False
                sel = ss
                px = sel.x()
                py = sel.y()
                pw = sel.width()
                ph = sel.height()
            sel.invert()
            selection_data = sel.pixelData( 0, 0, width, height )
            ki.action( 'deselect' ).trigger()

            # Cycle
            old_node_list = av.selectedNodes()
            for old_node in old_node_list:
                node_type = old_node.type()
                if str( node_type ) == "paintlayer":
                    # Variables
                    old_name = old_node.name()
                    new_name = f"Mirror Fix : { old_name }"
                    parent = old_node.parentNode()
                    # Old Node
                    ad.setActiveNode( old_node )
                    self.Wait( ad )
                    # New Node
                    new_node = ad.createNode( new_name, "paintLayer" )
                    parent.addChildNode( new_node, old_node )
                    # Copy Paste
                    if state == True:
                        pixel_array = old_node.pixelData( int( px ), int( py ), int( pw ), int( ph ) )
                        new_node.setPixelData( pixel_array, int( px ), int( py ), int( pw ), int( ph ) )
                    if state == False:
                        pixel_array = old_node.pixelData( int( 0 ), int( 0 ), int( width ), int( height ) )
                        new_node.setPixelData( pixel_array, int( 0 ), int( 0 ), int( width ), int( height ) )

            # Re-Select
            sel = Selection()
            sel.setPixelData( selection_data, 0, 0, width, height )
            ad.setSelection( sel )
            # Cycle
            for old_node in old_node_list:
                node_type = old_node.type()
                if str( node_type ) == "paintlayer":
                    # Old Node
                    ad.setActiveNode( old_node )
                    self.Wait( ad )
                    # Clear
                    ki.action( "clear" ).trigger()
            # De-Select
            ki.action( "deselect" ).trigger()

            # Cycle
            for old_node in old_node_list:
                node_type = old_node.type()
                if str( node_type ) == "paintlayer":
                    # Variables
                    old_name = old_node.name()
                    new_name = f"Mirror Fix : { old_name }"
                    # Old Node
                    ad.setActiveNode( old_node )
                    self.Wait( ad )
                    # Mirror
                    if ( side == "LEFT" or side == "RIGHT" ):
                        ki.action( "mirrorNodeX" ).trigger()
                    if ( side == "TOP" or side == "DOWN" ):
                        ki.action( "mirrorNodeY" ).trigger()
                    self.Wait( ad )
                    # Re-Order
                    ki.action( "move_layer_up" ).trigger()
                    self.Wait( ad )
                    # Merge ( this solves a alpha compositing issue )
                    ki.action( "merge_layer" ).trigger()
                    self.Wait( ad )
                    # Merge
                    merge_node = ad.nodeByName( new_name )
                    self.Wait( ad )
                    ad.setActiveNode( merge_node )
                    self.Wait( ad )
                    merge_node.setName( old_name )
                    self.Wait( ad )

            # Warnning
            self.Message_Float( "MIRROR FIX", "END", self.icon_mirrorfix )
    def Wait( self, active_document ):
        active_document.waitForDone()
        active_document.refreshProjection()

    def MirrorFix_Explanation( self ):
        self.Menu_Reset()
        self.Message_Float( "MIRROR FIX", f"Press and hold LMB then do a vertical or horizontal drag and release", self.icon_mirrorfix )
        self.Menu_Clear()

    #endregion
    #region Export Selection ( WIP )

    def Export_Selection( self ):
        if ( self.canvas() != None ) and ( self.canvas().view() != None ):
            # File
            file_dialog = QFileDialog( QWidget( self ) )
            file_dialog.setFileMode( QFileDialog.FileMode.AnyFile )
            save_path = file_dialog.getSaveFileName( self, "Export Location", "", "*.png" )[0]

            # Run the Export
            if save_path != None:
                self.Export_RUN( save_path )
    def Export_RUN( self, save_path ):
        # Read
        ki = Krita.instance()
        ad = ki.activeDocument()
        node = ad.activeNode()
        adw = ad.width()
        adh = ad.height()

        # Selection
        ss = ad.selection()
        if ss == None: # Create a selection
            px = 0
            py = 0
            pw = ad.width()
            ph = ad.height()
        else: # Custom
            px = ss.x()
            py = ss.y()
            pw = ss.width()
            ph = ss.height()

        # QImage
        qimage_thumbnail = ad.thumbnail( adw, adh )
        qimage_selection = qimage_thumbnail.copy( int( px ), int( py ), int( pw ), int( ph ) )
        mode = Qt.SmoothTransformation
        if ( self.export_width_state == True and self.export_height_state == False ):
            qimage_scale = qimage_selection.scaledToWidth( int( self.export_width_value ), mode )
        elif ( self.export_width_state == False and self.export_height_state == True ):
            qimage_scale = qimage_selection.scaledToHeight( int( self.export_height_value ), mode )
        else:
            qimage_scale = qimage_selection
        qimage_scale.save( save_path )

    #endregion
    #region Notifier

    def Application_Closing( self ):
        pass
    def Configuration_Changed( self ):
        pass
    def Image_Closed( self ):
        pass
    def Image_Created( self ):
        pass
    def Image_Saved( self ):
        self.Information_Read()
    def View_Closed( self ):
        pass
    def View_Created( self ):
        pass
    def Window_Created( self ):
        # Window
        ki = Krita.instance()
        self.window = ki.activeWindow()

        # Signals
        self.window.activeViewChanged.connect( self.View_Changed )
        self.window.themeChanged.connect( self.Theme_Changed )
        self.window.windowClosed.connect( self.Window_Closed )

        # Tela
        self.Tela_Display()
        self.Tela_Button()
        self.Tela_Filter_Install()
        self.Tela_Load()
    def Window_IsBeingCreated( self ):
        pass

    # Window
    def View_Changed( self ):
        self.Menu_Reset()
        self.Tool_Update()
        self.Information_Read()
        self.Theme_Changed()
    def Theme_Changed( self ):
        self.Style_Theme()
        self.Style_Icon()
        self.Krita_Action_Icon_Read()
    def Window_Closed( self ):
        pass

    #endregion
    #region Widget Events

    def eventFilter( self, source, event ):
        # Variables
        et = event.type()
        # Geometry ( resize )
        if self.qmdiarea != None:
            if ( event.type() == QEvent.Resize and source == self.qmdiarea ):
                self.Size_Update()
        # Krita ToolBox Signals
        if ( et in [ QEvent.MouseButtonPress, QEvent.MouseButtonRelease, QEvent.PaletteChange ] and source in self.krita_toolbox ):
            self.Tool_Update()
        # Eraser
        if ( et in [ 24, 12, 184 ] ) and ( source == self.krita_eraser ):
            self.Tool_Eraser( self.krita_eraser.isChecked() )
        # Color Picker
        if ( et == QEvent.Enter and source == self.ui_color_picker ):
            self.Color_READ()
            return True
        return super().eventFilter( source, event )

    #endregion
    #region Actions

    def createActions(self, window):
        # Main Menu
        menu_tela = QtWidgets.QMenu( "tela_menu", window.qwindow() )
        action_tela = window.createAction( "tela_menu", "Tela", "tools/scripts" )
        action_tela.setMenu( menu_tela )
        # Tool Menu
        menu_toolbox = QtWidgets.QMenu( "tela_toolbox_menu", window.qwindow() )
        action_toolbox = window.createAction( "tela_toolbox_menu", "Toolbox", "tools/scripts/tela_menu" )
        action_toolbox.setMenu( menu_toolbox )
        # Canvas Menus
        menu_canvas = QtWidgets.QMenu( "tela_canvas_menu", window.qwindow() )
        action_canvas = window.createAction( "tela_canvas_menu", "Canvas", "tools/scripts/tela_menu" )
        action_canvas.setMenu( menu_canvas )
        # Mirror Fix Menu
        menu_mirror_fix = QtWidgets.QMenu( "tela_mirror_fix_menu", window.qwindow() )
        action_mirror_fix = window.createAction( "tela_mirror_fix_menu", "Mirror Fix", "tools/scripts/tela_menu" )
        action_mirror_fix.setMenu( menu_mirror_fix )

        # Toolbox Tools
        self.action_tool_vector    = window.createAction( "tela_extension_tool1_vector",    "Tool1 Vector",    "tools/scripts/tela_menu/tela_toolbox_menu" )
        self.action_tool_brush     = window.createAction( "tela_extension_tool2_brush",     "Tool2 Brush",     "tools/scripts/tela_menu/tela_toolbox_menu" )
        self.action_tool_transform = window.createAction( "tela_extension_tool3_transform", "Tool3 Transform", "tools/scripts/tela_menu/tela_toolbox_menu" )
        self.action_tool_color     = window.createAction( "tela_extension_tool4_color",     "Tool4 Color",     "tools/scripts/tela_menu/tela_toolbox_menu" )
        self.action_tool_overlay   = window.createAction( "tela_extension_tool5_overlay",   "Tool5 Overlay",   "tools/scripts/tela_menu/tela_toolbox_menu" )
        self.action_tool_select    = window.createAction( "tela_extension_tool6_select",    "Tool6 Select",    "tools/scripts/tela_menu/tela_toolbox_menu" )
        self.action_tool_camera    = window.createAction( "tela_extension_tool7_camera",    "Tool7 Camera",    "tools/scripts/tela_menu/tela_toolbox_menu" )
        self.action_tool_vector.setCheckable( True )
        self.action_tool_brush.setCheckable( True )
        self.action_tool_transform.setCheckable( True )
        self.action_tool_color.setCheckable( True )
        self.action_tool_overlay.setCheckable( True )
        self.action_tool_select.setCheckable( True )
        self.action_tool_camera.setCheckable( True )
        self.action_tool_vector.triggered.connect( self.Release_Vector )
        self.action_tool_brush.triggered.connect( self.Release_Brush )
        self.action_tool_transform.triggered.connect( self.Release_Transform )
        self.action_tool_color.triggered.connect( self.Release_Color )
        self.action_tool_overlay.triggered.connect( self.Release_Overlay )
        self.action_tool_select.triggered.connect( self.Release_Select )
        self.action_tool_camera.triggered.connect( self.Release_Camera )

        # Actions Shelf Action Menu
        action_shelf_action = window.createAction( "tela_extension_shelf_action", "Shelf Action", "tools/scripts/tela_menu/tela_canvas_menu" )
        action_shelf_action.triggered.connect( self.Menu_Shelf_Action )
        # Actions Resource Preset
        action_shelf_preset = window.createAction( "tela_extension_shelf_resource_preset", "Shelf Resource Preset", "tools/scripts/tela_menu/tela_canvas_menu" )
        action_shelf_preset.triggered.connect( self.Menu_Shelf_ResourcePreset )

        # Actions Mirror Fix
        action_mirror_fix_left  = window.createAction( "tela_extension_mirror_fix_left",  "Mirror Fix [LEFT]",  "tools/scripts/tela_menu/tela_mirror_fix_menu" )
        action_mirror_fix_right = window.createAction( "tela_extension_mirror_fix_right", "Mirror Fix [RIGHT]", "tools/scripts/tela_menu/tela_mirror_fix_menu" )
        action_mirror_fix_top   = window.createAction( "tela_extension_mirror_fix_top",   "Mirror Fix [TOP]",   "tools/scripts/tela_menu/tela_mirror_fix_menu" )
        action_mirror_fix_down  = window.createAction( "tela_extension_mirror_fix_down",  "Mirror Fix [DOWN]",  "tools/scripts/tela_menu/tela_mirror_fix_menu" )
        action_mirror_fix_left.triggered.connect( lambda: self.MirrorFix_Side( "LEFT" ) )
        action_mirror_fix_right.triggered.connect( lambda: self.MirrorFix_Side( "RIGHT" ) )
        action_mirror_fix_top.triggered.connect( lambda: self.MirrorFix_Side( "TOP" ) )
        action_mirror_fix_down.triggered.connect( lambda: self.MirrorFix_Side( "DOWN" ) )

        # Actions Picker
        action_picker_to_cursor = window.createAction( "tela_extension_picker_to_cursor", "Picker to Cursor", "tools/scripts/tela_menu" )
        action_picker_to_cursor.triggered.connect( self.Picker_to_Cursor )

    #endregion
    #region Notes

    """
    # Label Message
    self.layout.label.setText( "message" )

    # Pop Up Message
    QMessageBox.information( QWidget(), i18n( "Warnning" ), i18n( "message" ) )

    # Log Viewer Message
    QtCore.qDebug( f"value = { value }" )
    QtCore.qDebug( "message" )
    QtCore.qWarning( "message" )
    QtCore.qCritical( "message" )

    """

    """
    # self.setWindowFlags( QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint )
    """

    """
    QTimer.singleShot( 0, lambda: self.MirrorFix_Invert( ki, ad, side, new_node ) )
    """

    """
    # Docker
    pyid = "ToolBox"
    dockers = Krita.instance().dockers()
    for d in dockers:
        if d.objectName() == pyid:
            tool_box = d
            break
    # Krita Tool Box
    key_mg = self.tool.keys()
    for mg in key_mg:
        key_sg = self.tool[mg].keys()
        for sg in key_sg:
            item = self.tool[mg][sg][1]
            child = tool_box.findChild( QToolButton, item )
            self.krita_toolbox.append( child )
            child.installEventFilter( self )
    """

    """
    if hide_tela == True:
        for i in range( 0, limit+1, +1 ):
            index = ( i / limit ) ** curve
            self.Geometry_Tela( show_extra, index, True )
            self.ui_color_picker.hide()
    if hide_tela == False:
        for i in range( limit, -1, -1 ):
            index = ( i / limit ) ** curve
            self.Geometry_Tela( show_extra, index, True )
    """

    """
    def Connect_Animation( self ):
        # Cannot connect because Krita developers don't name their widgets
        ki = Krita.instance()
        docker_list = ki.dockers()
        for docker in docker_list:
            name = docker.objectName()
            if name == "TimelineDocker":
                widget_list = docker.findChildren( QSpinBox )
                # QtCore.qDebug( f"amount = { len( widget_list ) }" )
                for widget in widget_list:
                    try:
                        tool_tip = widget.toolTip()
                        if tool_tip == "Frame register":
                            # self.animation_frame = widget
                            pass
                    except:
                        pass
    """

    """
    ET = xml.etree.ElementTree
    root = ET.fromstring( document_info )
    QtCore.qDebug( f"root = { root }" )
    QtCore.qDebug( f"r_tag = { root.tag }" )
    QtCore.qDebug( f"r_len = { len(root) }" )

    QtCore.qDebug( f"r_abo = { root[0] }" )
    QtCore.qDebug( f"r_tit = { root[0][0] }" )
    QtCore.qDebug( f"r_tag = { root[0][0].tag }" )
    QtCore.qDebug( f"r_tex = { root[0][0].text }" )
    """

    #endregion

""" 
Krita:
- Krita changed guides info from document to guidesGonfig module. however you read with guideConfig but set with the deprecated document.

ToDo:
- Exporter

New:
- Lighter Pulse Cycle and Eraser Checks 
- Shelf Brush Preset
- Shelf Action
- Guide Refactor
"""
