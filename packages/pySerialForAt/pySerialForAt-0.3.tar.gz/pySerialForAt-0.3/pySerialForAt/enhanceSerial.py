from base import Serial

class enhanceSerial(Serial):
    def __init__(self):
        super().__init__()
    def Send_and_Recv_AT(self,data,timeout=0.1,*res):
        pass
    

if __name__ =="__main__":
    pass
    Ser = enhanceSerial()
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
