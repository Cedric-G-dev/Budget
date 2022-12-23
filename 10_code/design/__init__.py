import os


path = os.path.dirname(__file__)

#Path to screen definition
screens_path = os.path.join(path, f'screens{os.sep}')
#Path to app widget
widgets_path = os.path.join(path, f'widgets{os.sep}')

import design.factory_registers