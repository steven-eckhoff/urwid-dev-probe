import urwid
import os
from lib.device import Device
from lib.i2c_pirate_bus import I2CPirateBus


###################
### Config Data ###
###################

config_list = ['devices', 'adapters']
device_list = os.listdir('./config/devices/')
adapter_list = os.listdir('./config/adapters/')
tty_usb_list = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3']


##############
### Colors ###
##############

pal = [
    ('button focus', 'standout', ''),
    ('odd', 'light green', 'black'),
    ('even', 'light magenta', 'black'),
    ('odd reversed', 'black', 'light green'),
    ('even reversed', 'black', 'light magenta'),
]


###############
### Helpers ###
###############

def boxify(w):
    return urwid.Overlay(urwid.AttrMap(w, 'odd reversed'), 
                         urwid.AttrMap(urwid.SolidFill(u'\N{MEDIUM SHADE}'), 'even reversed'),
        align='center', width=('relative', 60),
        valign='middle', height=('relative', 60),
        min_width=20, min_height=9)

def button_builder(label, cb=None, data=None, align='center'):
        btn = urwid.Button(label, cb, data)
        btn._label.align = align
        btn = urwid.AttrMap(btn, None, focus_map='button focus')
        return btn

def menu_builder(title, choices, cb):
    widget_list = [urwid.Text(title, 'center'), urwid.Divider()] + [button_builder(c, cb, c, align='left') for c in choices]
    list_walker = urwid.SimpleFocusListWalker(widget_list)
    list_box = urwid.ListBox(list_walker)
    padding = urwid.Padding(list_box, left=2, right=2)
    overlay = boxify(padding)
    return overlay

def toggle_string_gen(strings):
    if len(strings) != 2:
        raise Exception("Two strings are needed")
    count = 0
    while True:
        yield strings[count % 2]
        count = count + 1


############
### Home ###
############

def home_show():
    main_view.update_body(main_body)

def home_btn_cb(button):
    main_view.update_body(main_body)


#################
### Congigure ###
#################

def configure_menu_show():
    main_view.update_body(menu_builder('Configure', config_list, config_menu_cb))

def configure_btn_cb(button):
    configure_menu_show()

def config_menu_cb(button, choice):
    if choice == 'devices':
        main_view.update_body(menu_builder('Devices', device_list, device_menu_cb))
    elif choice == 'adapters':
        main_view.update_body(menu_builder('Adapters', adapter_list, adapter_menu_cb))

dev_name = None
dev_cfg_path = None
reg_cfg_path = None
device = None

reg_attr_gen = toggle_string_gen(['odd', 'even'])

reg_map = dict() 

def device_menu_cb(button, choice):
    global dev_name
    global device
    device = None
    reg_map.clear()
    dev_name = choice
    dev_cfg_path = './config/devices/' + dev_name + '/dev.cfg'
    reg_cfg_path = './config/devices/' + dev_name + '/reg.cfg'
    try:
        device = Device(dev_cfg_path, reg_cfg_path)
        regs_list_box.body[:] = []
        for reg_name in device.reg_names:
            reg = Register(reg_name)
            reg_map[reg_name] = reg
            regs_list_box.body.append(urwid.AttrMap(reg, next(reg_attr_gen)))
        configure_menu_show()
    except Exception as e:
        log_exception(e)
        configure_menu_show()

def bus_pirate_dev_menu_cb(buttton, choice):
    try:
        device.connect(I2CPirateBus(choice, 115200))
    except Exception as e:
        log_exception(e)
    configure_menu_show()

adapter = None
def adapter_menu_cb(button, choice):
    global adapter
    adapter = choice
    if device:
        if adapter == 'bus_pirate_i2c':
            main_view.update_body(menu_builder(u'Choose Dev', tty_usb_list, bus_pirate_dev_menu_cb))
    else:
        log_add('Configure device before adapter')
        configure_menu_show()


#################
### Registers ###
#################

def reg_read_cb(button, reg):
    try:
        val = device.reg_read(reg.name)
        reg.editText.set_edit_pos(0)
        reg.editText.set_edit_text(val)
    except Exception as e:
        log_exception(e)

def reg_write_cb(button, reg):
    try:
        device.reg_write(reg.name, reg.editText.edit_text)
    except Exception as e:
        log_exception(e)

class Register(urwid.Columns):

    def __init__(self, name, val=''):
        self.name = name
        self.label = urwid.Text(name)
        self.checkBox = urwid.CheckBox(u'')
        self.readButton = button_builder(u'Read', reg_read_cb, self, 'center')
        self.writeButton = button_builder(u'Write', reg_write_cb, self, 'center')
        self.editText = urwid.Edit(u'Value: ', val, wrap='clip')
        widgetList = [(10, self.checkBox),
                (25, self.label), (10, self.readButton),
                (10, self.writeButton), (15, self.editText)]
        super().__init__(widgetList, 3)

def regs_load_menu_cb(button, choice):
    reg_vals_file_path = './config/devices/' + dev_name + '/reg_vals/' + choice
    try:
        with open(reg_vals_file_path, 'r') as f:
            for line in f:
                (name, val) = line.split()
                reg = reg_map[name]
                reg.editText.set_edit_pos(0)
                reg.editText.set_edit_text(val)
    except Exception as e:
        log_exception(e)
    registers_show()

global_check_state = False
def regs_sel_toggle_cb(button):
    global global_check_state
    if device:
        global_check_state = not global_check_state
        for attr_map in regs_list_box.body:
            reg = attr_map.original_widget
            reg.checkBox.set_state(global_check_state, False)
    else:
        log_add('Configure device before loading registers')

def regs_load_cb(button):
    if device:
        try:
            reg_vals_file_list = os.listdir('./config/devices/' + dev_name + '/reg_vals/')
            main_view.update_body(menu_builder('Load', reg_vals_file_list, regs_load_menu_cb))
        except Exception as e:
            log_exception(e)
    else:
        log_add('Configure device before loading registers')

def regs_dump_cb(button):
    if device:
        with open('./regs_dump', 'w') as dump_file:
            for attr_map in regs_list_box.body:
                reg = attr_map.original_widget
                val = reg.editText.get_edit_text()
                if val:
                    dump_file.write(reg.name + ' ' + val + '\n')
    else:
        log_add('Configure device before loading registers')

def regs_read_cb(button):
    for attr_map in regs_list_box.body:
        reg = attr_map.original_widget
        if reg.checkBox.get_state():
            reg_read_cb(button, reg)

def regs_write_cb(button):
    for attr_map in regs_list_box.body:
        reg = attr_map.original_widget
        if reg.checkBox.get_state():
            reg_write_cb(button, reg)

regs_list_box = urwid.ListBox(urwid.SimpleFocusListWalker([]))
regs_sel_toggle_btn = button_builder(u'X', regs_sel_toggle_cb, align='center')
regs_load_btn = button_builder(u'Load', regs_load_cb, align='center')
regs_dump_btn = button_builder(u'Dump', regs_dump_cb, align='center')
regs_read_btn = button_builder(u'Read', regs_read_cb, align='center')
regs_write_btn = button_builder(u'Write', regs_write_cb, align='center')
regs_view_header = urwid.AttrMap(urwid.Columns([regs_sel_toggle_btn,
                                                regs_load_btn,
                                                regs_dump_btn,
                                                regs_read_btn,
                                                regs_write_btn]),
                                                'even reversed')
regs_view = urwid.Frame(regs_list_box, regs_view_header)

def registers_show():
    main_view.update_body(regs_view)

def  registers_btn_cb(button):
    registers_show()


###########
### Log ###
###########

log_attr_gen = toggle_string_gen(['odd', 'even'])

log = urwid.ListBox(urwid.SimpleFocusListWalker([]))

def log_add(msg):
    log.body.append(urwid.AttrMap(button_builder(msg, align='left'), next(log_attr_gen)))

def log_exception(e):
    log_add('Exception: {}'.format(e))

def log_btn_cb(button):
    main_view.update_body(log)


##################
### Main Frame ###
##################

home_btn = button_builder(u"Home", home_btn_cb)
configure_btn = button_builder(u"Configure", configure_btn_cb)
registers_btn = button_builder(u"Registers", registers_btn_cb)
log_btn = button_builder(u"Log", log_btn_cb)

header_widgets = [home_btn, configure_btn, registers_btn, log_btn]

header = urwid.AttrMap(urwid.Columns(header_widgets), 'odd reversed')

main_body = urwid.Filler(urwid.Text(u"Urwid device probe!", align='center'))

main_body = boxify(main_body)

class Main(urwid.Frame):

    def __init__(self):
        body = urwid.Pile([main_body])
        super().__init__(body, header)

    def update_body(self, w):
        del self.body.contents[0]
        self.body.contents.append((w, self.body.options()))

main_view = Main()


###########
### Run ###
###########

def exit_on_q(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()

urwid.MainLoop(main_view, palette = pal, unhandled_input=exit_on_q).run()

