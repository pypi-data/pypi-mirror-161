import time
import serial


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