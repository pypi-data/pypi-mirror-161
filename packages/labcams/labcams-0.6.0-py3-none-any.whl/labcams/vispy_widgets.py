from .widgets import *
from vispy import scene
from vispy.scene import SceneCanvas
from vispy.scene.visuals import Text


class VispyCamWidget(QWidget):
    def __init__(self,
                 frame,
                 iCam = 0,
                 parent = None,
                 parameters = None,
                 invertX = False):
        super(VispyCamWidget,self).__init__()
        self.parent = parent
        self.iCam = iCam
        self.cam = self.parent.cams[self.iCam]
        self.nchan = frame.shape[-1]
        if hasattr(self.cam,'excitation_trigger'):
            self.nchan = self.cam.excitation_trigger.nchannels.value
            self.frame_buffer = None
        self.displaychannel = -1  # default show all channels
        self.roiwidget = None
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        if invertX:
            print('Not implemented')
        canvas = SceneCanvas(bgcolor='w')
        self.view = canvas.central_widget.add_view()
        self.image = scene.visuals.Image(self.cam.get_img(),
                                         parent=self.view.scene)
        self.view.camera = scene.PanZoomCamera(aspect=1)
        self.text = scene.visuals.Text('0', parent=self.view.scene, color=colors[0])
        # flip y-axis to have correct aligment
        self.view.camera.flip = (0, 1, 0)
        self.view.camera.set_range()
        self.layout.addWidget(canvas.native,0,0)
        @canvas.events.resize.connect
        def resize(event=None):
            self.view.pos = 1, canvas.size[1] // 2 - 1
            self.view.size = canvas.size[0] - 2, canvas.size[1] // 2 - 2
        self.canvas = canvas
        #self.show()
    def update(self):
        # handle the excitation module
        if hasattr(self.cam,'excitation_trigger'):
            if self.frame_buffer is None:
                self.frame_buffer = np.zeros([
                    self.cam.cam.h.value,
                    self.cam.cam.w.value,
                    3], dtype = self.cam.cam.dtype)
            cframe = self.cam.nframes.value
            tmp = self.cam.get_img(cframe)
            nchan = self.cam.excitation_trigger.nchannels.value
            self.frame_buffer[:,:,
                              np.mod(cframe,
                                     nchan)] = tmp.squeeze()
            return self.image(self.frame_buffer,cframe)
        else:
            frame = self.cam.get_img()
        if not frame is None:
            self.image.set_data(frame)
            self.text.text = str(self.cam.nframes.value)
            self.canvas.update()
