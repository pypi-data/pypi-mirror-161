import pigpio


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
        
