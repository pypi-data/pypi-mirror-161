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
