"""
This code is from
stackoverflow.com/questions/4940351/gtk-treeview-place-image-buttons-on-rows
This is a custom pixbuf cellrenderer to make click available in
a treeview...
"""
import gobject
import gtk


class CellRendererClickablePixbuf(gtk.CellRendererPixbuf):
    """Adding click signal for custom cellrenderer"""
    __gsignals__ = {'clicked':
                    (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                     (gobject.TYPE_STRING,))}

    def __init__(self):
        gtk.CellRendererPixbuf.__init__(self)
        self.set_property('mode', gtk.CELL_RENDERER_MODE_ACTIVATABLE)

    def do_activate(self, event, widget, path, background_area,
                    cell_area, flags):
        """Emitting click signal"""
        self.emit('clicked', path)
