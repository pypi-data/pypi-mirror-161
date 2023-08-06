from ..base import Serial
import time
class enhaneSerialbydlx(Serial):
    def __init__(self):
        super().__init__()
    @staticmethod
    def GetTimefloat():
        '''
        返回当前时间(s)
        '''
        return time.time()
    def _send_and_recv_confirm_single_key(self,at_send:str,at_recv:str):
        '''
        返回[bool,data]
        '''
        self._Port.write("{}\r".format(at_send).encode("gbk"))
        get_data = self._Port.readall()#.decode("gbk")
        # print(str(get_data))
        if at_recv.encode("GBK") in get_data:
            return [True,get_data]
        else:
            return [False,get_data]
    def _send_and_recv_confirm_single_key_split_while(self,at_send:str,at_recv:str,time_s:int=10):
        '''
        返回 data
        '''
        start_time = self.GetTimefloat()
        while self.GetTimefloat()-start_time<time_s:
            self._Port.write("{}\r".format(at_send).encode("gbk"))
            get_data = self._Port.readall().decode("gbk")
            print(str(get_data))
            if at_recv in get_data.split(","):
                return get_data
            time.sleep(1)
        raise Exception("超时",time_s)
    def _send_and_recv_confirm_single_key_split_none_space_while(self,at_send:str,at_recv:str,time_s:int=10):
        '''
        返回 data
        '''
        start_time = self.GetTimefloat()
        while self.GetTimefloat()-start_time<time_s:
            self._Port.write("{}\r".format(at_send).encode("gbk"))
            get_data = self._Port.readall().decode("gbk")
            print(str(get_data))
            if at_recv in get_data.split(","):
                return get_data
            time.sleep(1)
        raise Exception("超时",time_s)
    def _send_and_recv_confirm_single_key_while(self,at_send:str,at_recv:str,time_s:int=10):
        '''
        返回 data
        '''
        start_time = self.GetTimefloat()
        while self.GetTimefloat()-start_time<time_s:
            self._Port.write("{}\r".format(at_send).encode("gbk"))
            get_data = self._Port.readall().decode("gbk")
            print(str(get_data))
            if at_recv in get_data:
                return get_data
            time.sleep(1)
        raise Exception("超时",time_s,get_data)
    def _send_and_recv_confirm_single_key_idx_list_split_while(self,at_send:str,at_recv:str,index:int,ted:list,time_s:int=10):
        '''
        返回 data
        '''
        start_time = self.GetTimefloat()
        while self.GetTimefloat()-start_time<time_s:
            self._Port.write("{}\r".format(at_send).encode("gbk"))
            get_data = self._Port.readall().decode("gbk")
            get_data_list = get_data.split(",")
            try:
                if at_recv in get_data_list[index] and get_data_list[index] not in ted:
                    return get_data_list[index]
            except:
                pass
            time.sleep(1)
        raise Exception("超时",time_s,get_data)
    def _send_and_recv_confirm_multiple_key(self,at_send:str,at_key_list:list):
        '''
        输入(at_command,at_key_list)
        '''
        send_num=self._Port.write("{}\r".format(at_send).encode("gbk"))
        print("send_num{}".format(send_num))
        get_data = self._Port.readall()#.decode("gbk")
        # print(str(get_data))
        for idx in at_key_list:
            if idx.encode("GBK") in get_data:
                pass
            else:
                return False
        return True
    
if __name__=="__main__":
    xe = enhaneSerialbydlx()
    xe.Open_Port()