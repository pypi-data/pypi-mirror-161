import serial, time, serial.tools.list_ports


class Serial():
    def __init__(self):
        self._Port     = None
        self._Bandrate = 115200
        self._Timeout  = 0.5

    # def Port_Opend(self):
    #     def 

    def Get_Port(self,type:int=0):
    #****************************
    # 获取串口号，并以列表形式返回
    # type = 0 仅返回COM号(默认)
    # type = 1 返回端口完整信息
    #****************************
        try:
            _Port_List = list(serial.tools.list_ports.comports())             # 该列表中元素为对象信息
            _Port_Str_List = []
            for i in range(len(_Port_List)):
                _Port_Str_List.append(str(_Port_List[i]))                     # 单独提出各个元素后变为字符串格式
            if type == 0:
                _Com_List = []
                for i in range(len(_Port_Str_List)):
                    _Com_List.append(str(_Port_Str_List[i]).split(" ")[0])    # 单独分割出端口号
                return _Com_List
            if type == 1:
                return _Port_Str_List
        except:
            print("bcy_pack_serial Serial Get_Port 获取端口失败")
            return 0

    def Open_Port(self,Comport,Bandrate,Timeout=0.5):
        self._Port = None
        try:
            self._Port = serial.Serial(Comport,Bandrate,timeout=Timeout)
            # print(self._Port)
            return 1
        except:
            print("打开串口 {} 失败".format(Comport))
            return 0

    def Close_Port(self):
        if self._Port != None:
            try:
                self._Port.close()
                return 1
            except:
                print("关闭串口失败")
                return 0
        else:
            print("串口未打开")
            return 0

    def Set_DTR(self,state=False):
    #********************************
    # state = True     拉低DTR
    # state = False    拉高DTR
        if self._Port != None:
            try:
                pass
            except:
                pass

    def Read_Str_InWaiting(self):
    #********************************
    # 获取串口buffer数据
    # 

        try:
            _Read_Str_IW = self._Port.read(self._Port.in_waiting)
            if _Read_Str_IW != None:
                try:
                    return _Read_Str_IW#.decode("gbk")
                except:
                    print("串口接收数据 dbk 解码错误")
                    return 0
            print("串口buffer为空")
            return 0
        except:
            print("读取串口数据失败")
            return 0

    def Send_Command(self,data,NewLine=1):
    #******************************************
    # 发送指令
    # NewLine = 0 ，不发送 "\r\n"
    # NewLine = 1 ，发送 指令+"\r\n" (默认)
    #******************************************
        try:
            if NewLine == 1:
                self._Port.write((data+"\r\n").encode("utf-8"))
            if NewLine == 0:
                self._Port.write(data.encode("utf-8"))
            return 1
        except:
            print("AT发送失败")
            return 0

    def Clear_Input_Buffer(self):
        try:
            self._Port.reset_input_buffer()
            return 1
        except:
            print("清除接收buffer失败")
            return 0

    def Clear_Output_Buffer(self):
        try:
            self._Port.reset_output_buffer()
            return 1
        except:
            print("清除发送buffer失败")
            return 0





if __name__ =="__main__":
    pass
    Ser = Serial()
    # Ser.Open_Port("COM260",115200)
    # # Ser.Open_Port("COM433",921600)
    # for i in range(2):
    #     Ser.Send_Command("AT+CPSI?\r\n",NewLine=0)
    #     time.sleep(1)
    #     # print(Ser.Read_Str_InWaiting())
    #     # Ser.Clear_Input_Buffer()
    # print(Ser.Read_Str_InWaiting())
    # time.sleep(2)
    # Ser.Close_Port()


    print(Ser._Port)
    Ser.Open_Port("COM260",115200)
    print(Ser._Port)
    Ser.Close_Port()
    print(Ser._Port)
