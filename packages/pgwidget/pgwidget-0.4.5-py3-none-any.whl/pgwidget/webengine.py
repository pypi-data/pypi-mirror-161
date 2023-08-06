import os.path
import random
import threading

import remi.gui as gui
from remi import start, App



def new_rectangle(color,pos,size,width=0):
    container = gui.Container()
    container.style['left'] = str(pos[0])+'px'
    container.style['top'] = str(pos[1])+'px'
    container.style['height'] = str(size[0]-2*width)+'px'
    container.style['width'] = str(size[1]-2*width)+'px'
    container.style['position'] = 'absolute'
    if width==0:
        container.style['background-color'] = "rgb"+str(color)
    else:
        container.style['background-color'] = 'transparent'
        container.style['border'] = str(width)+'px solid rgb'+str(color)
        container.style['opacity'] = str(1)
    return(container)


def new_image(pos,size,img_path):
    image = gui.Image('/png:'+img_path)
    image.style['left'] = str(pos[0])+'px'
    image.style['top'] = str(pos[1])+'px'
    image.style['position'] = 'absolute'
    image.set_size(size[0], size[1])
    return(image)
        

class MyApp(App):
    def __init__(self, *args):
        res_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'png')
        super(MyApp, self).__init__(*args, static_file_path={'png': res_path})

    def display_time(self):
        #self.lblTime.set_text('Play time: ' + str(self.time_count))
        self.time += 1
        print(self.main_container.css_top)
        print(self.main_container.css_left)
        print(self.main_container.style.get('left', None))
        print(self.container.style)
        #print(self.container.)
        if not self.stop_flag:
            threading.Timer(1, self.display_time).start()
            
    def add_container(self,container):
        self.main_container.append(container)

    def main(self):
        # the arguments are    width - height - layoutOrientationOrizontal
        self.main_container = gui.Container(margin='0px auto')
        self.main_container.set_size(1600, 900)
        self.main_container.set_layout_orientation(gui.Container.LAYOUT_VERTICAL)
        self.main_container.style['position']='relative'
        

        self.container = gui.Container()
        self.container.style['display'] = 'block'
        self.container.style['overflow'] = 'auto'
        self.container.style['background-color'] = 'blue'
        
        self.container.style['position'] = 'absolute'
        
        self.container.set_layout_orientation(gui.Container.LAYOUT_HORIZONTAL)
        self.container.style['margin'] = '20px'
        self.container.style['width'] = '20px'
        self.container.style['height'] = '20px'
        
        #self.container.style['border'] = '5px solid red' #
        
        
        
        
        #self.container.onclick.do(test)


        self.container2 = gui.Container()
        #self.container2.style['display'] = 'block'
        #self.container2.style['overflow'] = 'auto'
        self.container2.style['background-color'] = 'red'
        
        #self.container2.set_layout_orientation(gui.Container.LAYOUT_HORIZONTAL)
        #self.container2.style['margin-top'] = '-50px'
        
        #self.container.style['overflow'] = 'auto'
        self.container2.style['position'] = 'absolute'
        self.container2.style['left'] = '1550px'
        self.container2.style['top'] = '850px'
        self.container2.style['height'] = '20px'
        self.container2.style['width'] = '20px'
        #self.container2.style['margin'] ='30px'
        #self.container2.onclick.do(test)


        self.container3=new_rectangle((255,0,0),[150,150],[200,200],10)

        #self.container4=new_rectangle((150,100,200),[150,150],[200,200],0)
        #self.add_container(new_rectangle((150,100,200),[150,150],[200,200],0))
        self.add_container(new_rectangle((255,0,100),[500,150],[20,20],0))
        self.add_container(new_rectangle((0,255,10),[800,350],[20,20],0))
        self.add_container(new_rectangle((150,100,200),[550,700],[20,20],0))
        self.add_container(new_rectangle((150,100,200),[340,280],[20,20],0))

        self.horizontal_container = gui.Container()
        self.horizontal_container.style['display'] = 'block'
        self.horizontal_container.style['overflow'] = 'auto'
        self.horizontal_container.set_layout_orientation(gui.Container.LAYOUT_HORIZONTAL)
        self.horizontal_container.style['margin'] = '10px'
        #self.horizontal_container.append(self.info)

        

        
        self.lblMineCount = gui.Label('Forloop.ai')
        self.lblMineCount.set_size(100, 30)
        self.lblMineCount.style['position'] = 'absolute'
        self.lblMineCount.style['left'] = '1250px'
        self.lblMineCount.style['top'] = '850px'
        self.lblMineCount.style['height'] = '20px'
        self.lblMineCount.style['width'] = '20px'
        #self.title.style['font-size'] = '25px'
        #self.title.style['font-weight'] = 'bold'
        
        
        svg0 = gui.Svg()
        #svg0.attr_class = "Svg"
        #svg0.attr_editor_newclass = False
        svg0.css_height = "900px"
        svg0.css_order = "124983688"
        svg0.css_position = "static"
        svg0.css_top = "20px"
        svg0.css_width = "1000px"
        svg0.variable_name = "svg0"
        
        
        circle = gui.SvgCircle(700, 200, 20)
        circle.set_fill('red')
        circle.set_stroke(1, 'black')
        svg0.append(circle)
        
        
        line = gui.SvgLine(150,300,550,800)
        line.set_stroke(2, 'blue')
        svg0.append( line )
        
        
        forloop_logo = gui.Image('/png:new_logo_transparent.png')
        forloop_logo.set_size(132, 39)
        self.horizontal_container.append([forloop_logo, self.lblMineCount])
        
        
        self.add_container(new_image([800,400],[80,80],"click.png"))
        
        
        self.time=0
        
        self.main_container.append([self.horizontal_container,self.container, self.container2,svg0,circle,line])
        
        self.stop_flag = False
        self.display_time()
        # returning the root widget
        return self.main_container




    def on_close(self):
        self.stop_flag = True
        super(MyApp, self).on_close()


    def new_game(self, widget):
        self.time_count = 0
       
        self.set_root_widget(self.main_container)




if __name__ == "__main__":
    start(MyApp, multiple_instance=True, address='0.0.0.0', port=0, debug=True, start_browser=True)
