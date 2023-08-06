import os
import pygame


key_map = {"PSB_CROSS":2,"PSB_CIRCLE":1,"PSB_SQUARE":3,"PSB_TRIANGLE":0,"PSB_L1":4,
           "PSB_R1":5,"PSB_L2":6,"PSB_R2":7,"PSB_SELECT":8,"PSB_START":9,"PSB_L3":10,
           "PSB_R3":11}
"""
@PS2遥控手柄类
"""
class Mypygame:
    def __init__(self,js):
        self.js=js
        pygame.display.init()
        pygame.joystick.init()
        if os.path.exists("/dev/input/js0") is True:
            js = pygame.joystick.Joystick(0)
            if pygame.joystick.get_count() > 0:
                js.init()
            else:
                pygame.joystick.quit()
        else:
            js.quit()
            pygame.joystick.quit()
        self.js = pygame.joystick.Joystick(0)

    """
    @得到遥控手柄的按键值，根据返回值对应遥控手柄上面得按键值
    """
    def get_key(self):
        
        pygame.event.pump()
        hat = self.js.get_hat(0)
        button0 = self.js.get_button(0)
        button1 = self.js.get_button(1)
        button2 = self.js.get_button(2)
        button3 = self.js.get_button(3)
        button4 = self.js.get_button(4)
        button5 = self.js.get_button(5)
        button6 = self.js.get_button(6)
        button7 = self.js.get_button(7)
        
        if hat[0] > 0:                             #判断向右箭头按键是否按下
            return 'right'
        if hat[0] < 0:                             #判断向左箭头按键是否按下
            return 'left'
        if hat[1] > 0:                             #判断向上箭头是否被按下
            return 'up'
        if hat[1] < 0:  
            return 'down'
        if button0 == 1:
           return '△'
        if button1 == 1:
           return '○'
        if button2 == 1:
           return 'X'
        if button3 == 1:
           return '□'
        if button4 == 1:
           return 'L1'
        if button5 == 1:
           return 'R1'
        if button6 == 1:
           return 'L2'
        if button7 == 1:
           return 'R2'
        else:
            return '0'