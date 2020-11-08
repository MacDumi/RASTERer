import numpy as np

class ZoomPan:
        def __init__(self):
                self.press = None
                self.cur_xlim = None
                self.cur_ylim = None
                self.x0 = None
                self.y0 = None
                self.x1 = None
                self.y1 = None
                self.xpress = None
                self.ypress = None
                self.xzoom = True
                self.yzoom = True
                self.cidBP = None
                self.cidBR = None
                self.cidBM = None
                self.cidKeyP = None
                self.cidKeyR = None
                self.cidScroll = None

        def zoom_factory(self, ax, base_scale = 2.):
                def zoom(event):
                        cur_xlim = ax.get_xlim()
                        cur_ylim = ax.get_ylim()

                        xdata = event.xdata # get event x location
                        ydata = event.ydata # get event y location
                        if(xdata is None):
                                return()
                        if(ydata is None):
                                return()

                        if event.button == 'up':
                                # deal with zoom in
                                scale_factor = 1 / base_scale
                        elif event.button == 'down':
                                #deal with zoom out
                                scale_factor = base_scale
                        else:
                                # deal with something that should never happen
                                scale_factor = 1
                                print(event.button)

                        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
                        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

                        relx = (cur_xlim[1] - xdata)/(cur_xlim[1] - cur_xlim[0])
                        rely = (cur_ylim[1] - ydata)/(cur_ylim[1] - cur_ylim[0])

                        lim = [xdata - new_width * (1-relx), xdata + new_width * (relx)]
                        ax.set_xlim(lim)

                        #Get the line
                        line = ax.lines[0]
                        data = [line.get_xdata(), line.get_ydata()]
                        try:
                            idx_0 = np.where(data[0][:] >= lim[0])[0][0]
                            idx_1 = np.where(data[0][:] >= lim[1])[0][0]
                            limits = [data[1][idx_0:idx_1].min()*0.9, data[1][idx_0:idx_1].max()*1.1]
                            ax.set_ylim(limits)
                        except IndexError:
                            pass
                        ax.figure.canvas.draw()
                        ax.figure.canvas.flush_events()


                fig = ax.get_figure() # get the figure of interest

                self.cidScroll = fig.canvas.mpl_connect('scroll_event', zoom)

                return zoom

        def pan_factory(self, ax):
                def onPress(event):
                        if event.inaxes != ax: return
                        if event.button == 2:
                                self.cur_xlim = ax.get_xlim()
                                self.press = self.x0, self.y0, event.xdata, event.ydata
                                self.x0, self.y0, self.xpress, self.ypress = self.press


                def onRelease(event):
                        self.press = None
                        ax.figure.canvas.draw()

                def onMotion(event):
                        if self.press is None: return
                        if event.inaxes != ax: return
                        dx = event.xdata - self.xpress
                        self.cur_xlim -= dx
                        ax.set_xlim(self.cur_xlim)
                        #Get the line
                        line = ax.lines[0]
                        data = [line.get_xdata(), line.get_ydata()]
                        try:
                            idx_0 = np.where(data[0][:] >= self.cur_xlim[0])[0][0]
                            idx_1 = np.where(data[0][:] >= self.cur_xlim[1])[0][0]
                            limits = [data[1][idx_0:idx_1].min()*0.9,
                                                    data[1][idx_0:idx_1].max()*1.1]
                            ax.set_ylim(limits)
                        except IndexError:
                            pass
                        ax.set_ylim(self.cur_ylim)

                        ax.figure.canvas.draw()
                        ax.figure.canvas.flush_events()

                fig = ax.get_figure() # get the figure of interest

                self.cidBP = fig.canvas.mpl_connect('button_press_event',onPress)
                self.cidBR = fig.canvas.mpl_connect('button_release_event',onRelease)
                self.cidBM = fig.canvas.mpl_connect('motion_notify_event',onMotion)
                # attach the call back

                #return the function
                return onMotion



