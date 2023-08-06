import os
import vlc
import pigpio
import pygame
import serial
import time
import Adafruit_PCA9685  #导入舵机模块



"""
@本类是用于树莓派IO引脚控制PCA9685芯片产生PWM波形，控制舵机转动大约0~~290的角度
"""
class Servo:
    pwm = Adafruit_PCA9685.PCA9685()
    pwm.set_pwm_freq(60)
    def __init__(self):
        pass
    """
    @servo_channel: 是舵机的通道，取值范围：1、2、3、4、5、6
    @angle: 舵机转动的大概角度，值不与实际的角度对应，方便微调，取值范围：0~~290
    """
    def set_servo(self,servo_channel,angle):
        if (servo_channel > 0) and (servo_channel < 7):
            if (angle >= 0) and (angle < 291):
                self.pwm.set_pwm(servo_channel, 0,int(angle*1.72+100))
            else:
                print('\033[31m warning: servo angle must be 0,1,2...290 \033[0m')
        
        else:
            print('\033[31m warning: servo channel must be 1,2,3,4,5,6\033[0m')


"""
@本类是树莓派与单片机直接串口通信接口类，可从单片机接收到传感器数据，可发送命令给单片机
@本类的获取传感器数据方法时，请不断调用get_data()方法，以便从串口拿到数据，
@另外get_data()方法中必须有0.15S的延时来保证每次数据接收完整，如在每个获取传感器数据方法中调用get_data()方法则读取多个
@传感器数据时候代码执行周期会变慢
"""
class Myserial:
    ser = serial.Serial('/dev/ttyAMA0',115200)
    ser.flushInput()
    Com_list = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
    SerialCount = 0
    Com_RGB1 = [0x01,0x10,0x00,0x5B,0x00,0x1C,0x38,0x00,0x01,0x00,0x55,0x00,0xAA,0x00,0x55,0xAA,0x55,0x00,0xAA,0x00,0x55,0xAA,0x55,0x00,0xAA,0x00,0x55,0xAA,0x55,0x00,0xAA,0x00,0x55,0xAA,0x55,0x00,0xAA,0x00,0x55,0xAA,0x55,0x00,0xAA,0x00,0x55,0xAA,0x55,0x00,0xAA,0x00,0x55,0xAA,0x55,0x00,0xAA,0x00,0x55,0xAA,0x55,0x00,0xAA,0x00,0x55,0x0D,0x0A]
    Com_RGB2 = [0x01,0x10,0x00,0x5B,0x00,0x1C,0x38,0x00,0x02,0x00,0x55,0x00,0xAA,0x00,0x55,0xAA,0x55,0x00,0xAA,0x00,0x55,0xAA,0x55,0x00,0xAA,0x00,0x55,0xAA,0x55,0x00,0xAA,0x00,0x55,0xAA,0x55,0x00,0xAA,0x00,0x55,0xAA,0x55,0x00,0xAA,0x00,0x55,0xAA,0x55,0x00,0xAA,0x00,0x55,0xAA,0x55,0x00,0xAA,0x00,0x55,0xAA,0x55,0x00,0xAA,0x00,0x55,0x0D,0x0A]
    def __init__(self):
        pass

    """
    @得到串口发送数据的方法，每次拿传感器数据时需先调用这个方法
    """
    def get_data(self):
        
        time.sleep(0.15)
        SerialCount = self.ser.inWaiting()
        if SerialCount !=0:
            Serialdata = self.ser.read(SerialCount)
            
        try:
            if Serialdata[0] is 0xA0 and Serialdata[1] is 0x0B and Serialdata[20] is 0x0D and Serialdata[21] is 0x0A:
                self.Com_list.clear()
                for data in Serialdata:
                    self.Com_list.append(int(data))
        except IndexError:
            print('Index Less')

    """
    @得到温湿度传感器的湿度值
    @channel: 传感器接口的通道，取值范围1、2、3、4
    """
    def get_humidity(self,channel):
        
        if (channel > 0) and (channel < 5):
            return (self.Com_list[4*channel]*256 + self.Com_list[4*channel+1])/10
        else:
            print('\033[31m warning: channel value must be 1,2,3,4 \033[0m')

    """
    @得到温湿度传感器的温度值
    @channel: 传感器接口的通道，取值范围1，2，3，4
    """
    def get_temperature(self,channel):
        
        if (channel > 0) and (channel < 5):
            return (self.Com_list[4*channel+2]*256 + self.Com_list[4*channel+3])/10
        else:
            print('\033[31m warning: channel value must be 1,2,3,4 \033[0m')

    """
    @得到超声波传感器的测距距离
    @channel: 传感器接口的通道，取值范围1、2、3、4
    """
    def get_ultrasonic(self,channel):
        
        if (channel > 0) and (channel < 5):
            return (self.Com_list[4*channel+1]*100 + self.Com_list[4*channel+2]*10 + self.Com_list[4*channel+3])
        else:
            print('\033[31m warning: channel value must be 1,2,3,4 \033[0m')

    """
    @得到灰度传感器的值
    @channel: 传感器接口的通道，取值范围1、2、3、4
    """
    def get_gray(self,channel):
        
        if (channel > 0) and (channel < 5):
            return self.Com_list[4*channel+3]
        else:
            print('\033[31m warning: channel value must be 1,2,3,4 \033[0m')

    """
    @得到火焰传感器的值
    @channel: 传感器接口的通道，取值范围1、2、3、4
    """
    def get_fire(self,channel):
        
        if (channel > 0) and (channel < 5):
            return self.Com_list[4*channel+3]
        else:
            print('\033[31m warning: channel value must be 1,2,3,4 \033[0m')

    """
    @得到土壤湿度传感器的值
    @channel: 传感器接口的通道，取值范围1、2、3、4
    """
    def get_soil_moisture(self,channel):
        
        if (channel > 0) and (channel < 5):
            return self.Com_list[4*channel+3]
        else:
            print('\033[31m warning: channel value must be 1,2,3,4 \033[0m')

    """
    @得到颜色识别传感器的红色值
    @channel: 传感器接口的通道，取值范围1、2、3、4
    """
    def get_red(self,channel):
        
        if (channel > 0) and (channel < 5):
            return self.Com_list[4*channel+1]
        else:
            print('\033[31m warning: channel value must be 1,2,3,4 \033[0m')

    """
    @得到颜色识别传感器的绿色值
    @channel: 传感器接口的通道，取值范围1、2、3、4
    """
    def get_green(self,channel):
      
        if (channel > 0) and (channel < 5):
            return self.Com_list[4*channel+2]
        else:
            print('\033[31m warning: channel value must be 1,2,3,4 \033[0m')

    """
    @得到颜色识别传感器的蓝色值
    @channel: 传感器接口的通道，取值范围1、2、3、4
    """
    def get_blue(self,channel):
       
        if (channel > 0) and (channel < 5):
            return self.Com_list[4*channel+3]
        else:
            print('\033[31m warning: channel value must be 1,2,3,4 \033[0m')

    """
    @控制外部扩展1、扩展电机2控制口的开关
    @channel: 外部扩展通道号，取值范围1，2
    @switch: 开关状态，0：关闭，1：打开
    """
    def extend_control(self,channel,switch):
        if channel == 1:
           if switch == 0:
               self.ser.write(([0x01,0x10,0x00,0x48,0x00,0x02,0x04,0x00,0x00,0x01,0x00,0x0D,0x0A]))
           if switch == 1:
               self.ser.write(([0x01,0x10,0x00,0x48,0x00,0x02,0x04,0x00,0x00,0x01,0x01,0x0D,0x0A]))
           elif (switch < 0) or (switch > 1):
            print('\033[31m warning: extend switch value must be 0,1 \033[0m')
            
        if channel == 2:
           if switch == 0:
               self.ser.write(([0x01,0x10,0x00,0x48,0x00,0x02,0x04,0x00,0x00,0x02,0x00,0x0D,0x0A]))
           if switch == 1:
               self.ser.write(([0x01,0x10,0x00,0x48,0x00,0x02,0x04,0x00,0x00,0x02,0x01,0x0D,0x0A]))
           
           elif (switch < 0) or (switch > 1):
            print('\033[31m warning: extend switch value must be 0,1 \033[0m')
           
           
        elif (channel < 1) or (channel > 2):
            print('\033[31m warning: extend channel value must be 1,2 \033[0m')

    """
    @设置RGB灯带每个灯的RGB值
    @channel:灯带的通道值，取值范围1、2
    @num:表示灯带上面第几个灯，取值范围：1，2，3....18
    @r、g、b: 设置灯的R、G、B值，取值范围均为：0，1，2.....255
    """
    def rgb(self,channel,num,r,g,b):
        if channel == 1:
           if num > 0 and num < 19:
               self.Com_RGB1[9+(num-1)*3] = r
               self.Com_RGB1[9+(num-1)*3+1] = g
               self.Com_RGB1[9+(num-1)*3+2] = b
               
               self.ser.write(self.Com_RGB1)
          
           elif (num < 0) or (num > 18):
            print('\033[31m warning: rgb num value must be 1,2,3...18 \033[0m')
            
        if channel == 2:
           if num > 0 and num < 19:
               self.Com_RGB2[9+(num-1)*3] = r
               self.Com_RGB2[9+(num-1)*3+1] = g
               self.Com_RGB2[9+(num-1)*3+2] = b
               
               self.ser.write(self.Com_RGB2)
          
           elif (num < 0) or (num > 18):
            print('\033[31m warning: rgb num value must be 1,2,3...18 \033[0m')
           
           
        elif (channel < 1) or (channel > 2):
            print('\033[31m warning: rgb channel value must be 1,2 \033[0m')


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
            

"""
@树莓派上面四路电机的速度PWM值控制
"""
class Carmotor(object):
    def __init__(self,in1 = 26,in2 = 18,in3 = 7,in4 = 8,in5 = 12,in6 = 13,in7 = 20,in8 = 16): #这是BCM编码序号，分别对应树莓派扩展接口的P37、P12、P26、P24，四个GPIO连接到L298P芯片
        self.Pi = pigpio.pi()
        self.In1 = in1
        self.In2 = in2
        self.In3 = in3
        self.In4 = in4
        self.In5 = in5
        self.In6 = in6
        self.In7 = in7
        self.In8 = in8

        self.Pi.set_PWM_range(self.In1,100) #pwm范围
        self.Pi.set_PWM_range(self.In2,100) #pwm范围
        self.Pi.set_PWM_range(self.In3,100) #pwm范围
        self.Pi.set_PWM_range(self.In4,100) #pwm范围
        self.Pi.set_PWM_range(self.In5,100) #pwm范围
        self.Pi.set_PWM_range(self.In6,100) #pwm范围
        self.Pi.set_PWM_range(self.In7,100) #pwm范围
        self.Pi.set_PWM_range(self.In8,100) #pwm范围

        self.Pi.set_PWM_frequency(self.In1,10000) #频率10Khz
        self.Pi.set_PWM_frequency(self.In2,10000)
        self.Pi.set_PWM_frequency(self.In3,10000)
        self.Pi.set_PWM_frequency(self.In4,10000)
        self.Pi.set_PWM_frequency(self.In5,10000) #频率10Khz
        self.Pi.set_PWM_frequency(self.In6,10000)
        self.Pi.set_PWM_frequency(self.In7,10000)
        self.Pi.set_PWM_frequency(self.In8,10000)
        

        self.Pi.set_PWM_dutycycle(self.In1,0) #暂停PWM输出
        self.Pi.set_PWM_dutycycle(self.In2,0)
        self.Pi.set_PWM_dutycycle(self.In3,0)
        self.Pi.set_PWM_dutycycle(self.In4,0)
        self.Pi.set_PWM_dutycycle(self.In5,0) #暂停PWM输出
        self.Pi.set_PWM_dutycycle(self.In6,0)
        self.Pi.set_PWM_dutycycle(self.In7,0)
        self.Pi.set_PWM_dutycycle(self.In8,0)

    """
    @设置四个电机的速度PWM值大小
    """
    def set_speed(self, Front_Left, Front_Right, Back_Left, Back_Right):
        
        Front_Left  = -100 if Front_Left < -100  else Front_Left #超出范围按边界值设置
        Front_Left  = 100  if Front_Left > 100   else Front_Left
        Front_Right = 100  if Front_Right > 100  else Front_Right
        Front_Right = -100 if Front_Right < -100 else Front_Right
        
        Back_Left  = -100 if Back_Left < -100  else Back_Left #超出范围按边界值设置
        Back_Left  = 100  if Back_Left > 100   else Back_Left
        Back_Right = 100  if Back_Right > 100  else Back_Right
        Back_Right = -100 if Back_Right < -100 else Back_Right
        

        DutyIn1 = 0 if Front_Left < 0 else Front_Left
        DutyIn2 = 0 if Front_Left > 0 else -Front_Left
        DutyIn3 = 0 if Front_Right < 0 else Front_Right
        DutyIn4 = 0 if Front_Right > 0 else -Front_Right
        
        DutyIn5 = 0 if Back_Left < 0 else Back_Left
        DutyIn6 = 0 if Back_Left > 0 else -Back_Left
        DutyIn7 = 0 if Back_Right < 0 else Back_Right
        DutyIn8 = 0 if Back_Right > 0 else -Back_Right

        self.Pi.set_PWM_dutycycle(self.In1,DutyIn1) #设置PWM输出的占空比
        self.Pi.set_PWM_dutycycle(self.In2,DutyIn2)
        self.Pi.set_PWM_dutycycle(self.In3,DutyIn3)
        self.Pi.set_PWM_dutycycle(self.In4,DutyIn4)
        
        self.Pi.set_PWM_dutycycle(self.In5,DutyIn5) #设置PWM输出的占空比
        self.Pi.set_PWM_dutycycle(self.In6,DutyIn6)
        self.Pi.set_PWM_dutycycle(self.In7,DutyIn7)
        self.Pi.set_PWM_dutycycle(self.In8,DutyIn8)

    """
    @四个电机停止
    """
    def stop(self):
        self.set_speed(0,0,0,0)

    """
    @设置前进
    @src：速度PWM值取值范围40~~100，一般启动速度PWM值得大于65
    """
    def go_ahead(self,src):
        if (src >39) and (src < 101):
            self.set_speed(-src,src,-src,src)
        else:
            print('\033[31m warning: speed value must be 40,41...100 \033[0m')

    """
    @设置后退
    @src：速度PWM值取值范围40~~100，一般启动速度PWM值得大于65
    """
    def go_back(self,src):
        if (src >39) and (src < 101):
            self.set_speed(src,-src,src,-src)
        else:
            print('\033[31m warning: speed value must be 40,41...100 \033[0m')

    """
    @设置向左转
    @src：速度PWM值取值范围40~~100，一般启动速度PWM值得大于65
    """
    def turn_left(self,src):
        if (src >39) and (src < 101):
            self.set_speed(src,src,src,src)
        else:
            print('\033[31m warning: speed value must be 40,41...100 \033[0m')

    """
    @设置向右转
    @src：速度PWM值取值范围40~~100，一般启动速度PWM值得大于65
    """
    def turn_right(self,src):
        if (src >39) and (src < 101):
            self.set_speed(-src,-src,-src,-src)
        else:
            print('\033[31m warning: speed value must be 40,41...100 \033[0m')

    """
    @设置左漂移
    @src：速度PWM值取值范围40~~100，一般启动速度PWM值得大于65
    """
    def shift_left(self,src):
        if (src >39) and (src < 101):
            self.set_speed(src,src,-src,-src)
        else:
            print('\033[31m warning: speed value must be 40,41...100 \033[0m')

    """
    @设置右漂移
    @src：速度PWM值取值范围40~~100，一般启动速度PWM值得大于65
    """
    def shift_right(self,src):
        if (src >39) and (src < 101):
            self.set_speed(-src,-src,src,src)
        else:
            print('\033[31m warning: speed value must be 40,41...100 \033[0m')

    """
    @设置向左中心轴转
    @src：速度PWM值取值范围40~~100，一般启动速度PWM值得大于65
    """
    def circle_left(self,src):
        if (src >39) and (src < 101):
            self.set_speed(src,src,0,0)
        else:
            print('\033[31m warning: speed value must be 40,41...100 \033[0m')

    """
    @设置向右中心轴转
    @src：速度PWM值取值范围40~~100，一般启动速度PWM值得大于65
    """
    def circle_right(self,src):
        if (src >39) and (src < 101):
            self.set_speed(-src,-src,0,0)
        else:
            print('\033[31m warning: speed value must be 40,41...100 \033[0m')
        

music = {
    '蓝色':'file:///home/pi/AiCar/music/blue.mp3',
    '青色':'file:///home/pi/AiCar/music/cyan.mp3',
    '橙色': 'file:///home/pi/AiCar/music/orange.mp3',
    '红色': 'file:///home/pi/AiCar/music/red.mp3',
    '紫色': 'file:///home/pi/AiCar/music/violet.mp3',
    '黄色': 'file:///home/pi/AiCar/music/yellow.mp3',
    '绿色':'file:///home/pi/AiCar/music/green.mp3',
    '火灾':'file:///home/pi/AiCar/music/Fire.mp3',
    '前进': 'file:///home/pi/AiCar/music/forward.mp3',
    '倒车': 'file:///home/pi/AiCar/music/Reversing.mp3',
    '左转': 'file:///home/pi/AiCar/music/Turn_left.mp3',
    '右转': 'file:///home/pi/AiCar/music/Turn_right.mp3',
    '允许通行': 'file:///home/pi/AiCar/music/Allow passage.mp3',
    '禁止通行':'file:///home/pi/AiCar/music/No allow passage.mp3'
}

"""
@设置声音播报
"""
class Sound:
    
    def __init__(self):
        self.vlc_obj = vlc.Instance()
        self.vlc_player = self.vlc_obj.media_player_new()
        self.vlc_media = self.vlc_obj.media_new('')

    """
    @播放某一段声音
    """
    def play(self,src):
        self.vlc_media = self.vlc_obj.media_new(src)
        self.vlc_player.set_media(self.vlc_media)
        self.vlc_player.play()

    """
    @停止播放某一段声音
    """
    def stop(self,src):
        self.vlc_media = self.vlc_obj.media_new(src)
        self.vlc_player.set_media(self.vlc_media)
        self.vlc_player.stop()

    """
    @播放允许通行音频
    """
    def allow(self):
        self.stop(music['允许通行'])
        self.play(music['允许通行'])

    """
    @播放蓝色音频
    """
    def blue(self):
        self.stop(music['蓝色'])
        self.play(music['蓝色'])

    """
    @播放青色音频
    """
    def cyan(self):
        self.stop(music['青色'])
        self.play(music['青色'])

    """
    @播放有火灾音频
    """
    def fire(self):
        self.stop(music['火灾'])
        self.play(music['火灾'])

    """
    @播放前进音频
    """
    def forward(self):
        self.stop(music['前进'])
        self.play(music['前进'])

    """
    @播放绿色音频
    """
    def green(self):
        self.stop(music['绿色'])
        self.play(music['绿色'])

    """
    @播放禁止通行音频
    """
    def notAllow(self):
        self.stop(music['禁止通行'])
        self.play(music['禁止通行'])

    """
    @播放橙色音频
    """
    def orange(self):
        self.stop(music['橙色'])
        self.play(music['橙色'])

    """
    @播放红色音频
    """
    def red(self):
        self.stop(music['红色'])
        self.play(music['红色'])

    """
    @播放倒车音频
    """
    def reversing(self):
        self.stop(music['倒车'])
        self.play(music['倒车'])

    """
    @播放左转音频
    """
    def turn_left(self):
        self.stop(music['左转'])
        self.play(music['左转'])

    """
    @播放右转音频
    """
    def turn_right(self):
        self.stop(music['右转'])
        self.play(music['右转'])

    """
    @播放紫色音频
    """
    def violet(self):
        self.stop(music['紫色'])
        self.play(music['紫色'])

    """
    @播放黄色音频
    """
    def yellow(self):
        self.stop(music['黄色'])
        self.play(music['黄色'])

    """
    @
    """
    def stopMedia(self):
        self.vlc_player.stop()


