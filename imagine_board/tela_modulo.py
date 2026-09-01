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

# Python
import math
# Krita
from krita import *
# PyQt5
from PyQt5 import QtWidgets, QtCore, QtGui, uic

#endregion


#region MirrorFix

class MirrorFix_Button( QWidget ):
    SIGNAL_SIDE = QtCore.pyqtSignal( str )
    SIGNAL_NEUTRAL = QtCore.pyqtSignal( str )

    # Initilization
    def __init__( self, parent ):
        super( MirrorFix_Button, self ).__init__( parent )
        # Variables
        self.origin_x = 0
        self.origin_y = 0
        self.side = None

    # Mouse Events
    def mousePressEvent( self, event ):
        # Read
        self.origin_x = event.x()
        self.origin_y = event.y()

        # Neutral
        if ( event.modifiers() == QtCore.Qt.NoModifier and event.buttons() == QtCore.Qt.LeftButton ):
            self.Cursor_Side( event )
    def mouseMoveEvent( self, event ):
        if ( event.modifiers() == QtCore.Qt.NoModifier and event.buttons() == QtCore.Qt.LeftButton ):
            self.Cursor_Side( event )
    def mouseDoubleClickEvent( self, event ):
        if ( event.modifiers() == QtCore.Qt.NoModifier and event.buttons() == QtCore.Qt.LeftButton ):
            self.Cursor_Side( event )
    def mouseReleaseEvent( self, event ):
        # Emite
        if self.side != None:
            self.Cursor_Signal( self.side )
        else:
            self.Cursor_Neutral()
        # Variables
        self.origin_x = 0
        self.origin_y = 0
        self.side = None

    # Mouse Operation
    def Cursor_Side( self, event ):
        # Read
        ex = event.x()
        ey = event.y()

        # Calculations
        delta_x = ex - self.origin_x
        delta_y = ey - self.origin_y
        dist = abs( delta_x ) + abs( delta_y )

        limit = 30
        if dist >= limit:
            if abs( delta_x ) > abs( delta_y ): # Horizontal
                if ex < self.origin_x:
                    self.side = "RIGHT"
                else:
                    self.side = "LEFT"
            else: # Vertical
                if ey < self.origin_y:
                    self.side = "DOWN"
                else:
                    self.side = "TOP"
        else:
            self.side = None
    def Cursor_Signal( self, side ):
        self.SIGNAL_SIDE.emit( side )
    def Cursor_Neutral( self ):
        self.SIGNAL_NEUTRAL.emit( "" )

#endregion
#region Color Picker

class Color_Display( QWidget ):

    # Init
    def __init__( self, parent ):
        super( Color_Display, self ).__init__( parent )
        self.Variables()
    def sizeHint( self ):
        return QtCore.QSize( 200, 20 )
    def Variables( self ):
        self.hex6 = QColor( "#000000" )
        self.ww = 200
        self.hh = 20

    # Relay
    def Set_Color( self, hex6 ):
        self.hex6 = QColor( hex6 )
        self.update()

    # Mouse Interaction
    def mousePressEvent( self, event ):
        self.update()
    def mouseMoveEvent( self, event ):
        self.update()
    def mouseReleaseEvent( self, event ):
        self.update()
    def mouseDoubleClickEvent( self, event ):
        self.update()

    # Paint Style
    def paintEvent( self, event ):
        painter = QPainter( self )
        painter.setRenderHint( QtGui.QPainter.Antialiasing, True )
        painter.setPen( QtCore.Qt.NoPen )
        painter.setBrush( QBrush( self.hex6 ) )
        painter.drawRect( 0, 0, int( self.ww ), int( self.hh ) )
        painter.end()

class Color_Panel( QWidget ):
    SIGNAL_PREVIEW = QtCore.pyqtSignal( list )
    SIGNAL_APPLY = QtCore.pyqtSignal( list )

    # Init
    def __init__( self, parent ):
        super( Color_Panel, self ).__init__( parent )
        self.Variables()
    def sizeHint( self ):
        return QtCore.QSize( 200, 200 )
    def Variables( self ):
        # Widget
        self.ww = 150
        self.hh = 150
        self.w2 = int( self.ww * 0.5 )
        self.h2 = int( self.hh * 0.5 )
        # Interaction
        self.ex = 0
        self.ey = 0
        self.origin_x = self.ex
        self.origin_y = self.ey
        self.origin_hue = 0
        self.operation = None
        # Sliders
        self.s1 = 0
        self.s2 = 0
        self.s3 = 0
        # Pixmaps
        self.qpixmap_list = list()
        self.qpixmap_neutral = QPixmap()
        # Colors
        self.hue_circle = False
        self.colors = [
            [1, 0, 0],   # Index = 0 > red
            [1, 0.5, 0], # Index = 1 > orange
            [1, 1, 0],   # Index = 2 > yellow
            [0, 1, 0],   # Index = 3 > green
            [0, 1, 1],   # Index = 4 > cyan
            [0, 0, 1],   # Index = 5 > blue
            [1, 0, 1],   # Index = 6 > magenta
            ]
        self.color_1 = QColor( "#e5e5e5" )
        self.color_2 = QColor( "#191919" )
        hex_theme = "#31363b"
        self.color_theme = QColor( hex_theme )
        self.color_alpha = QColor( hex_theme )
        self.color_alpha.setAlpha( 200 )

    # Relay
    def Set_Color( self, s1, s2, s3 ):
        # Color
        self.s1 = s1
        self.s2 = s2
        self.s3 = ( 1 - s3 )
        # Interaction
        self.ex = int( self.s2 * self.ww )
        self.ey = int( self.s3 * self.hh )
        # Update
        self.update()
    def Set_Gradient( self, qpixmap_list ):
        self.qpixmap_list = qpixmap_list
        self.update()

    # Math
    def Limit_Range( self, value, mini, maxi ):
        if value <= mini:
            value = mini
        if value >= maxi:
            value = maxi
        return value
    def Limit_Cycle( self, value, limit ):
        if ( value < 0 ) or ( value > limit ):
            value = ( value % 1 ) * limit
        return value
    def Trig_2D_Angle_Circle( self, px, py, side, radius, angle ):
        # px - Circle center in X (pixels)
        # py - Circle center in Y (pixels)
        # side - length of the square containning the circle (pixels)
        # radius - how far from the center (0-1)
        # angle - angle delta (0-360)
        circle_x = ( px ) - ( ( side * radius ) * math.cos( math.radians( angle ) ) )
        circle_y = ( py ) - ( ( side * radius ) * math.sin( math.radians( angle ) ) )
        return circle_x, circle_y

    # Mouse Interaction
    def mousePressEvent( self, event ):
        # Read
        ex = event.x()
        ey = event.y()
        self.origin_x = ex
        self.origin_y = ey
        self.origin_hue = self.s1
        # Interaction
        if ( event.modifiers() == QtCore.Qt.ControlModifier and event.buttons() == QtCore.Qt.LeftButton ):
            self.hue_circle = True
            self.operation = "color_1"
        if ( event.modifiers() == QtCore.Qt.NoModifier and event.buttons() == QtCore.Qt.LeftButton ):
            self.hue_circle = False
            self.operation = "color_23"
            self.Color_23( ex, ey, False )
        self.update()
    def mouseMoveEvent( self, event ):
        # Read
        ex = event.x()
        ey = event.y()
        # Operation
        if self.operation == "color_1":
            self.Color_1( ex, ey, False )
        if self.operation == "color_23":
            self.Color_23( ex, ey, False )
        self.update()
    def mouseReleaseEvent( self, event ):
        # Read
        ex = event.x()
        ey = event.y()
        # Operation
        if self.operation == "color_1":
            self.Color_1( ex, ey, True )
        if self.operation == "color_23":
            self.Color_23( ex, ey, True )
        # Finish
        self.hue_circle = False
        self.update()
    # Operations
    def Color_1( self, ex, ey, apply ):
        # Variables
        delta = ( ex - self.origin_x ) / self.ww
        self.s1 = self.Limit_Cycle( self.origin_hue + delta, 1 )
        # Signals
        inv_s3 = ( 1 - self.s3 )
        if apply == False:  self.SIGNAL_PREVIEW.emit( [ self.s1, self.s2, inv_s3 ] )
        else:               self.SIGNAL_APPLY.emit( [ self.s1, self.s2, inv_s3 ] )
    def Color_23( self, ex, ey, apply ):
        # Variables
        self.ex = self.Limit_Range( ex, 0, self.ww )
        self.ey = self.Limit_Range( ey, 0, self.hh )
        self.s2 = self.ex / self.ww
        self.s3 = self.ey / self.hh
        # Signals
        inv_s3 = ( 1 - self.s3 )
        if apply == False:  self.SIGNAL_PREVIEW.emit( [ self.s1, self.s2, inv_s3 ] )
        else:               self.SIGNAL_APPLY.emit( [ self.s1, self.s2, inv_s3 ] )

    # Paint Style
    def paintEvent( self, event ):
        # Variables
        hue_index = int( self.s1 * 360 )
        side = self.ww

        # Start Painter
        painter = QPainter( self )
        painter.setRenderHint( QtGui.QPainter.Antialiasing, True )

        # Draw Gradient
        if len( self.qpixmap_list ) > 0:
            painter.setPen( QtCore.Qt.NoPen )
            painter.setBrush( QtCore.Qt.NoBrush )
            qpixmap = self.qpixmap_list[hue_index]
            if qpixmap.isNull() == False:
                render = qpixmap.scaled( self.ww, self.hh, QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.FastTransformation )
                painter.drawPixmap( 0, 0, render )

        # Draw Colors
        if self.hue_circle == True:
            # Background
            painter.setPen( QtCore.Qt.NoPen )
            painter.setBrush( QBrush( self.color_alpha ) )
            painter.drawRect( 0, 0, int( self.ww ), int( self.hh ) )

            # Variables
            line_width = 4
            margin = 0
            side = int( self.ww - ( margin * 2 ) )
            circle_0, circle_1, circle_2, circle_3 = self.Circles( painter, margin, margin, side )
            circle_01 = circle_0.subtracted( circle_1 )
            circle_02 = circle_0.subtracted( circle_2 )
            circle_12 = circle_1.subtracted( circle_2 )
            circle_13 = circle_1.subtracted( circle_3 )

            # Circle Points
            radius = 0.5
            px, py = self.Trig_2D_Angle_Circle( self.w2, self.h2, side, radius, hue_index )

            # Dark Border
            painter.setPen( QtCore.Qt.NoPen )
            painter.setBrush( QBrush( self.color_theme ) )
            painter.drawPath( circle_02 )

            # Light Line
            painter.setPen( QPen( self.color_1, line_width, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin ) )
            painter.setBrush( QtCore.Qt.NoBrush )
            line_gray = QPainterPath()
            line_gray.moveTo( int( self.w2 ), int( self.h2 ) )
            line_gray.lineTo( int( px ), int( py ) )
            painter.setClipPath( circle_13 )
            painter.drawPath( line_gray )

            # Hue Gradient
            painter.setPen( QtCore.Qt.NoPen )
            d = 255
            hue = QConicalGradient( QPoint( int( self.w2 ), int( self.h2 ) ), 180 )
            hue.setColorAt( 0.000, QColor( int( self.colors[0][0] * d ), int( self.colors[0][1] * d ), int( self.colors[0][2] * d ) ) ) # RED
            hue.setColorAt( 0.166, QColor( int( self.colors[6][0] * d ), int( self.colors[6][1] * d ), int( self.colors[6][2] * d ) ) ) # MAGENTA
            hue.setColorAt( 0.333, QColor( int( self.colors[5][0] * d ), int( self.colors[5][1] * d ), int( self.colors[5][2] * d ) ) ) # BLUE
            hue.setColorAt( 0.500, QColor( int( self.colors[4][0] * d ), int( self.colors[4][1] * d ), int( self.colors[4][2] * d ) ) ) # CYAN
            hue.setColorAt( 0.666, QColor( int( self.colors[3][0] * d ), int( self.colors[3][1] * d ), int( self.colors[3][2] * d ) ) ) # GREEN
            hue.setColorAt( 0.833, QColor( int( self.colors[2][0] * d ), int( self.colors[2][1] * d ), int( self.colors[2][2] * d ) ) ) # YELLOW
            hue.setColorAt( 1.000, QColor( int( self.colors[0][0] * d ), int( self.colors[0][1] * d ), int( self.colors[0][2] * d ) ) ) # RED
            painter.setBrush( QBrush( hue ) )
            painter.setClipPath( circle_01 )
            painter.drawRect( 0, 0, int( self.ww ), int( self.hh ) )
            # Dark Line over Hue
            painter.setPen( QPen( self.color_theme, line_width, Qt.SolidLine, Qt.SquareCap, Qt.MiterJoin ) )
            painter.setBrush( QtCore.Qt.NoBrush )
            painter.setClipPath( circle_01 )
            painter.drawLine( int( px ), int( py ), int( self.w2 ), int( self.h2 ) )
        else:
            # Cursor
            self.Cursor( painter )

        # Painter
        painter.end()
    def Circles( self, painter, px, py, side ):
        # Circle 0 ( Everything )
        v0a = 0.02
        v0b = 1 - ( 2*v0a )
        circle_0 = QPainterPath()
        circle_0.addEllipse( int( px + side * v0a ), int( py + side * v0a ), int( side * v0b ), int( side * v0b ) )
        # Circle 1 ( Outter Most Region )
        v1a = 0.06
        v1b = 1 - ( 2*v1a )
        circle_1 = QPainterPath()
        circle_1.addEllipse( int( px + side * v1a ), int( py + side * v1a ), int( side * v1b ), int( side * v1b ) )
        # Circle 2 ( Inner Most Region )
        v2a = 0.12
        v2b = 1 - ( 2*v2a )
        circle_2 = QPainterPath()
        circle_2.addEllipse( int( px + side * v2a ), int( py + side * v2a ), int( side * v2b ), int( side * v2b ) )
        # Circle 3 ( Central Dot )
        v3a = 0.18
        v3b = 1 - ( 2*v3a )
        circle_3 = QPainterPath()
        circle_3.addEllipse( int( px + side * v3a ), int( py + side * v3a ), int( side * v3b ), int( side * v3b ) )

        # Return
        return circle_0, circle_1, circle_2, circle_3
    def Cursor ( self, painter ):
        size = 10
        w1 = 2
        w2 = w1 * 2
        w4 = w1 * 4
        size2 = size * 2
        # Mask
        mask = QPainterPath()
        mask.addEllipse( 
            int( self.ex - size ),
            int( self.ey - size ),
            int( size2 ),
            int( size2 ),
            )
        mask.addEllipse( 
            int( self.ex - size + w2 ),
            int( self.ey - size + w2 ),
            int( size2 - w4 ),
            int( size2 - w4 ),
            )
        painter.setClipPath( mask )
        # Black Circle
        painter.setPen( QtCore.Qt.NoPen )
        painter.setBrush( QBrush( QColor( "#000000" ) ) )
        painter.drawEllipse( 
            int( self.ex - size ),
            int( self.ey - size ),
            int( size2 ),
            int( size2 ),
            )
        # White Circle
        painter.setPen( QtCore.Qt.NoPen )
        painter.setBrush( QBrush( QColor( "#ffffff" ) ) )
        painter.drawEllipse( 
            int( self.ex - size + w1 ),
            int( self.ey - size + w1 ),
            int( size2 - w2 ),
            int( size2 - w2 ),
            )

#endregion
