#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2021 Eugenio Parodi <ceccopierangiolieugenio AT googlemail DOT com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import signal
import time
import queue

from TermTk.TTkCore.TTkTerm.input import TTkInput
from TermTk.TTkCore.TTkTerm.term import TTkTerm
from TermTk.TTkCore.constant import TTkK
from TermTk.TTkCore.log import TTkLog
from TermTk.TTkCore.cfg import *
from TermTk.TTkCore.timer import *
from TermTk.TTkTheme.theme import TTkTheme
from TermTk.TTkWidgets.widget import *

class TTk(TTkWidget):
    __slots__ = ('_name', '_running', '_input', '_events', '_key_events', '_mouse_events', '_screen_events', '_title' )

    def __init__(self, *args, **kwargs):
        TTkWidget.__init__(self, *args, **kwargs)
        self._name = kwargs.get('name' , 'TTk' )
        self._running = False
        self._input = TTkInput()
        self._events = queue.Queue()
        self._key_events = queue.Queue()
        self._mouse_events = queue.Queue()
        self._screen_events = queue.Queue()
        self._title = kwargs.get('title','TermTk')
        self.setFocusPolicy(TTkK.ClickFocus)
        self.hide()
        try:
            size = os.get_terminal_size()
            self.setGeometry(0,0,size.columns,size.lines)
        except OSError as e:
            print(f'ERROR: {e}')
        TTkCfg.theme = TTkTheme()
        TTkHelper.registerRootWidget(self)

    frame = 0
    time = time.time()
    def _fps(self):
        curtime = time.time()
        self.frame+=1
        delta = curtime - self.time
        if delta > 5:
            TTkLog.debug(f"fps: {int(self.frame/delta)}")
            self.frame = 0
            self.time  = curtime

    def mainloop(self):
        '''Enters the main event loop and waits until :meth:`~quit` is called or the main widget is destroyed.'''
        TTkLog.debug( "" )
        TTkLog.debug( "         ████████╗            ████████╗    " )
        TTkLog.debug( "         ╚══██╔══╝            ╚══██╔══╝    " )
        TTkLog.debug( "            ██║  ▄▄  ▄ ▄▄ ▄▄▖▄▖  ██║ █ ▗▖  " )
        TTkLog.debug( "    ▞▀▚ ▖▗  ██║ █▄▄█ █▀▘  █ █ █  ██║ █▟▘   " )
        TTkLog.debug( "    ▙▄▞▐▄▟  ██║ ▀▄▄▖ █    █ ▝ █  ██║ █ ▀▄  " )
        TTkLog.debug( "    ▌    ▐  ╚═╝                  ╚═╝       " )
        TTkLog.debug( "      ▚▄▄▘                                 " )
        TTkLog.debug( "" )
        TTkLog.debug(f"  Version: {TTkCfg.version}" )
        TTkLog.debug( "" )
        TTkLog.debug( "Starting Main Loop..." )
        # Register events
        try:
            signal.signal(signal.SIGTSTP, self._SIGSTOP) # Ctrl-Z
            signal.signal(signal.SIGCONT, self._SIGCONT) # Resume
            signal.signal(signal.SIGINT,  self._SIGINT)  # Ctrl-C
        except Exception as e:
            TTkLog.error(f"{e}")
            exit(1)
        else:
            TTkLog.debug("Signal Event Registered")


        TTkTerm.registerResizeCb(self._win_resize_cb)
        threading.Thread(target=self._input_thread, daemon=True).start()
        self._timer = TTkTimer()
        self._timer.timeout.connect(self._time_event)
        self._timer.start(0.1)
        self.show()

        self._running = True
        # Keep track of the multiTap to avoid the extra key release
        lastMultiTap = False
        TTkTerm.init(title=self._title)
        while self._running:
            # Main Loop
            evt = self._events.get()
            if   evt is TTkK.MOUSE_EVENT:
                mevt = self._mouse_events.get()
                # Upload the global mouse position
                # Mainly used by the drag pixmap display
                TTkHelper.setMousePos((mevt.x,mevt.y))

                # Avoid to broadcast a key release after a multitap event
                if mevt.evt == TTkK.Release and lastMultiTap: continue
                lastMultiTap = mevt.tap > 1

                if ( TTkHelper.isDnD() and
                     mevt.evt != TTkK.Drag   and
                     mevt.evt != TTkK.Release ):
                    # Clean Drag Drop status for any event that is not
                    # Mouse Drag, Key Release
                    TTkHelper.dndEnd()

                # Mouse Events forwarded straight to the Focus widget:
                #  - Drag
                #  - Move
                #  - Release
                focusWidget = TTkHelper.getFocus()
                if ( focusWidget is not None and
                     mevt.evt != TTkK.Press  and
                     mevt.key != TTkK.Wheel  and
                     not TTkHelper.isDnD()   ) :
                    x,y = TTkHelper.absPos(focusWidget)
                    nmevt = mevt.clone(pos=(mevt.x-x, mevt.y-y))
                    focusWidget.mouseEvent(nmevt)
                else:
                    # Sometimes the release event is not retrieved
                    if ( focusWidget and
                         focusWidget._pendingMouseRelease and
                         not TTkHelper.isDnD() ):
                        focusWidget.mouseEvent(nmevt.clone(evt=TTkK.Release))
                        focusWidget._pendingMouseRelease = False
                    # Adding this Crappy logic to handle a corner case in the drop routine
                    # where the mouse is leaving any widget able to handle the drop event
                    if not self.mouseEvent(mevt):
                        if dndw := TTkHelper.dndWidget():
                            dndw.dragLeaveEvent(TTkHelper.dndGetDrag().getDragLeaveEvent(mevt))
                            TTkHelper.dndEnter(None)
                        if mevt.evt == TTkK.Press and focusWidget:
                            focusWidget.clearFocus()

                # Clean the Drag and Drop in case of mouse release
                if mevt.evt == TTkK.Release:
                    TTkHelper.dndEnd()
            elif evt is TTkK.KEY_EVENT:
                keyHandled = False
                kevt = self._key_events.get()
                # TTkLog.debug(f"Key: {kevt}")
                focusWidget = TTkHelper.getFocus()
                TTkLog.debug(f"{focusWidget}")
                if focusWidget is not None:
                    TTkHelper.execShortcut(kevt.key,focusWidget)
                    keyHandled = focusWidget.keyEvent(kevt)
                else:
                    TTkHelper.execShortcut(kevt.key)
                # Handle Next Focus Key Binding
                if not keyHandled and \
                   ((kevt.key == TTkK.Key_Tab and kevt.mod == TTkK.NoModifier) or
                   ( kevt.key == TTkK.Key_Right )):
                        TTkHelper.nextFocus(focusWidget if focusWidget else self)
                # Handle Prev Focus Key Binding
                if not keyHandled and \
                   ((kevt.key == TTkK.Key_Tab and kevt.mod == TTkK.ShiftModifier) or
                   ( kevt.key == TTkK.Key_Left )):
                        TTkHelper.prevFocus(focusWidget if focusWidget else self)
            elif evt is TTkK.TIME_EVENT:
                size = os.get_terminal_size()
                self.setGeometry(0,0,size.columns,size.lines)
                TTkHelper.paintAll()
                self._timer.start(1/TTkCfg.maxFps)
                self._fps()
                pass
            elif evt is TTkK.SCREEN_EVENT:
                self.setGeometry(0,0,TTkGlbl.term_w,TTkGlbl.term_h)
                TTkLog.info(f"Resize: w:{TTkGlbl.term_w}, h:{TTkGlbl.term_h}")
            elif evt is TTkK.QUIT_EVENT:
                TTkLog.debug("Quit.")
                break
            else:
                TTkLog.error(f"Unhandled Event {evt}")
                break
        TTkTerm.exit()

    def _time_event(self):
        self._events.put(TTkK.TIME_EVENT)

    def _win_resize_cb(self, width, height):
        TTkGlbl.term_w = int(width)
        TTkGlbl.term_h = int(height)
        self._events.put(TTkK.SCREEN_EVENT)

    def _input_thread(self):
        def _inputCallback(kevt=None, mevt=None):
            if kevt is not None:
                self._key_events.put(kevt)
                self._events.put(TTkK.KEY_EVENT)
            if mevt is not None:
                self._mouse_events.put(mevt)
                self._events.put(TTkK.MOUSE_EVENT)
            return self._running
        # Start input key loop
        self._input.get_key(_inputCallback)

    def _canvas_thread(self):
        pass

    def quit(self):
        '''Tells the application to exit with a return code.'''
        self._events.put(TTkK.QUIT_EVENT)
        self._input.close()
        TTkTimer.quitAll()
        self._running = False

    def _SIGSTOP(self, signum, frame):
        """Reset terminal settings and stop background input read before putting to sleep"""
        TTkLog.debug("Captured SIGSTOP <CTRL-z>")
        TTkTerm.stop()
        # TODO: stop the threads
        os.kill(os.getpid(), signal.SIGSTOP)

    def _SIGCONT(self, signum, frame):
        """Set terminal settings and restart background input read"""
        TTkLog.debug("Captured SIGCONT 'fg/bg'")
        TTkTerm.cont()
        # TODO: Restart threads
        # TODO: Redraw the screen

    def _SIGINT(self, signum, frame):
        TTkLog.debug("Captured SIGINT <CTRL-C>")
        # Deregister the handler
        # so CTRL-C can be redirected to the default handler if the app does not exit
        signal.signal(signal.SIGINT,  signal.SIG_DFL)
        self.quit()
